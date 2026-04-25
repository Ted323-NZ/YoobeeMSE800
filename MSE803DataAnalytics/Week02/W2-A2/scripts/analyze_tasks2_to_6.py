from __future__ import annotations

import argparse
import csv
import io
import json
import os
from array import array
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

import numpy as np

if "MPLCONFIGDIR" not in os.environ:
    mpl_dir = Path("/tmp") / "mse803_matplotlib"
    mpl_dir.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(mpl_dir)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = Path.home() / "Downloads" / "beijing+multi+site+air+quality+data.zip"
OUTPUT_DIR = ROOT / "output"
FIGURES_DIR = ROOT / "figures"
MISSING_MARKERS = {"", "NA", "N/A", "NULL", "NaN", "nan"}

COLUMNS = [
    "No",
    "year",
    "month",
    "day",
    "hour",
    "PM2.5",
    "PM10",
    "SO2",
    "NO2",
    "CO",
    "O3",
    "TEMP",
    "PRES",
    "DEWP",
    "RAIN",
    "wd",
    "WSPM",
    "station",
]

ANALYSIS_COLUMNS = [
    "PM2.5",
    "PM10",
    "SO2",
    "NO2",
    "CO",
    "O3",
    "TEMP",
    "PRES",
    "DEWP",
    "RAIN",
    "WSPM",
]


@dataclass
class PairwiseStats:
    n: int = 0
    sum_x: float = 0.0
    sum_y: float = 0.0
    sum_x2: float = 0.0
    sum_y2: float = 0.0
    sum_xy: float = 0.0

    def update(self, x: float, y: float) -> None:
        self.n += 1
        self.sum_x += x
        self.sum_y += y
        self.sum_x2 += x * x
        self.sum_y2 += y * y
        self.sum_xy += x * y

    def correlation(self) -> float:
        if self.n < 2:
            return float("nan")
        numerator = self.n * self.sum_xy - self.sum_x * self.sum_y
        denominator_x = self.n * self.sum_x2 - self.sum_x * self.sum_x
        denominator_y = self.n * self.sum_y2 - self.sum_y * self.sum_y
        if denominator_x <= 0 or denominator_y <= 0:
            return float("nan")
        return numerator / np.sqrt(denominator_x * denominator_y)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tasks 2-6 statistical analysis for the Beijing Multi-Site Air Quality dataset."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to the downloaded dataset zip file.",
    )
    return parser.parse_args()


def is_missing(value: str | None) -> bool:
    return value is None or value.strip() in MISSING_MARKERS


def as_float(value: str | None) -> float | None:
    if is_missing(value):
        return None
    return float(value)  # type: ignore[arg-type]


def iter_csv_rows(dataset_path: Path) -> Iterable[dict[str, str]]:
    with ZipFile(dataset_path) as outer_zip:
        inner_name = next(
            name
            for name in outer_zip.namelist()
            if name.endswith(".zip") and "PRSA2017" in name
        )
        inner_bytes = io.BytesIO(outer_zip.read(inner_name))
        with ZipFile(inner_bytes) as inner_zip:
            csv_names = sorted(name for name in inner_zip.namelist() if name.endswith(".csv"))
            for csv_name in csv_names:
                with inner_zip.open(csv_name) as handle:
                    reader = csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8"))
                    for row in reader:
                        yield row


def month_name(month_number: int) -> str:
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return names[month_number - 1]


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def save_missingness_chart(missing_rows: list[dict[str, object]]) -> Path:
    labels = [row["column"] for row in missing_rows if row["missing_rate_pct"] > 0]
    values = [row["missing_rate_pct"] for row in missing_rows if row["missing_rate_pct"] > 0]

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(labels, values, color="#9c6644")
    ax.set_title("Missing Value Rate by Column")
    ax.set_ylabel("Missing rate (%)")
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()

    out_path = FIGURES_DIR / "missing_rate_by_column.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def save_monthly_trend_chart(monthly_pm25: dict[int, float], monthly_o3: dict[int, float]) -> Path:
    months = list(range(1, 13))
    labels = [month_name(month) for month in months]
    pm25_values = [monthly_pm25.get(month, float("nan")) for month in months]
    o3_values = [monthly_o3.get(month, float("nan")) for month in months]

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.plot(labels, pm25_values, marker="o", linewidth=2.5, color="#9c6644", label="PM2.5")
    ax1.set_ylabel("Average PM2.5")
    ax1.set_title("Monthly Average PM2.5 and O3")
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(labels, o3_values, marker="s", linewidth=2.0, color="#3f88c5", label="O3")
    ax2.set_ylabel("Average O3")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")
    fig.tight_layout()

    out_path = FIGURES_DIR / "monthly_pm25_o3.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def save_hourly_pattern_chart(hourly_pm25: dict[int, float], hourly_o3: dict[int, float]) -> Path:
    hours = list(range(24))
    pm25_values = [hourly_pm25.get(hour, float("nan")) for hour in hours]
    o3_values = [hourly_o3.get(hour, float("nan")) for hour in hours]

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(hours, pm25_values, marker="o", linewidth=2.5, color="#9c6644", label="PM2.5")
    ax.plot(hours, o3_values, marker="s", linewidth=2.0, color="#3f88c5", label="O3")
    ax.set_title("Hourly Average PM2.5 and O3")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Average concentration")
    ax.set_xticks(range(0, 24, 2))
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend()
    fig.tight_layout()

    out_path = FIGURES_DIR / "hourly_pm25_o3.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def save_station_chart(station_pm25_rows: list[dict[str, object]]) -> Path:
    labels = [row["station"] for row in station_pm25_rows]
    values = [row["avg_pm25"] for row in station_pm25_rows]

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(labels, values, color="#5f0f40")
    ax.set_title("Average PM2.5 by Station")
    ax.set_xlabel("Average PM2.5")
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    fig.tight_layout()

    out_path = FIGURES_DIR / "station_pm25_ranking.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def save_correlation_heatmap(correlation_matrix: np.ndarray) -> Path:
    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(correlation_matrix, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_title("Correlation Matrix")
    ax.set_xticks(range(len(ANALYSIS_COLUMNS)))
    ax.set_xticklabels(ANALYSIS_COLUMNS, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(ANALYSIS_COLUMNS)))
    ax.set_yticklabels(ANALYSIS_COLUMNS, fontsize=8)

    for i in range(len(ANALYSIS_COLUMNS)):
        for j in range(len(ANALYSIS_COLUMNS)):
            value = correlation_matrix[i, j]
            text = "nan" if np.isnan(value) else f"{value:.2f}"
            ax.text(j, i, text, ha="center", va="center", fontsize=7, color="#1f2933")

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()

    out_path = FIGURES_DIR / "correlation_heatmap.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_summary_markdown(summary: dict[str, object]) -> str:
    descriptive_rows = summary["descriptive_stats"][:6]
    station_rows = summary["station_pm25_ranking"][:5]
    insights = summary["key_insights"]

    lines = [
        "# Week 2 Activity 2 - Statistical Analysis Summary",
        "",
        "## Assumed Task 2-6 Scope",
        "",
        "- Task 2: missing-value and data quality review",
        "- Task 3: descriptive statistics for the main pollutant and weather variables",
        "- Task 4: monthly and hourly trend analysis",
        "- Task 5: correlation analysis across pollutants and weather variables",
        "- Task 6: station comparison and insight summary",
        "",
        "## Dataset Overview",
        "",
        f"- Total rows analysed: {summary['row_count']:,}",
        f"- Total columns: {summary['column_count']}",
        f"- Monitoring stations: {summary['station_count']}",
        "",
        "## Key Insights",
        "",
        f"- Highest missing-rate column: **{insights['highest_missing_column']}** ({insights['highest_missing_rate_pct']:.2f}%)",
        f"- Highest average PM2.5 station: **{insights['highest_pm25_station']}** ({insights['highest_pm25_value']:.2f})",
        f"- Lowest average PM2.5 station: **{insights['lowest_pm25_station']}** ({insights['lowest_pm25_value']:.2f})",
        f"- Peak PM2.5 month: **{insights['peak_pm25_month']}** ({insights['peak_pm25_month_value']:.2f})",
        f"- Peak O3 month: **{insights['peak_o3_month']}** ({insights['peak_o3_month_value']:.2f})",
        f"- Peak PM2.5 hour: **{insights['peak_pm25_hour']}** ({insights['peak_pm25_hour_value']:.2f})",
        f"- Peak O3 hour: **{insights['peak_o3_hour']}** ({insights['peak_o3_hour_value']:.2f})",
        f"- Strongest positive PM2.5 relationship: **{insights['pm25_strongest_positive_correlation_column']}** ({insights['pm25_strongest_positive_correlation_value']:.2f})",
        f"- Strongest negative PM2.5 relationship: **{insights['pm25_strongest_negative_correlation_column']}** ({insights['pm25_strongest_negative_correlation_value']:.2f})",
        "",
        "## Descriptive Statistics Snapshot",
        "",
        "| Column | Mean | Median | Std | Min | Max | Missing % |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in descriptive_rows:
        lines.append(
            f"| {row['column']} | {row['mean']:.2f} | {row['median']:.2f} | {row['std']:.2f} | {row['min']:.2f} | {row['max']:.2f} | {row['missing_rate_pct']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Top 5 Stations by Average PM2.5",
            "",
            "| Rank | Station | Avg PM2.5 |",
            "| --- | --- | ---: |",
        ]
    )

    for row in station_rows:
        lines.append(f"| {row['rank']} | {row['station']} | {row['avg_pm25']:.2f} |")

    lines.extend(
        [
            "",
            "## Generated Figures",
            "",
            "- `figures/missing_rate_by_column.png`",
            "- `figures/monthly_pm25_o3.png`",
            "- `figures/hourly_pm25_o3.png`",
            "- `figures/station_pm25_ranking.png`",
            "- `figures/correlation_heatmap.png`",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    ensure_dirs()

    row_count = 0
    station_names: set[str] = set()
    missing_counts = {column: 0 for column in COLUMNS}
    numeric_values = {column: array("d") for column in ANALYSIS_COLUMNS}

    monthly_sum_pm25 = defaultdict(float)
    monthly_count_pm25 = defaultdict(int)
    monthly_sum_o3 = defaultdict(float)
    monthly_count_o3 = defaultdict(int)

    hourly_sum_pm25 = defaultdict(float)
    hourly_count_pm25 = defaultdict(int)
    hourly_sum_o3 = defaultdict(float)
    hourly_count_o3 = defaultdict(int)

    station_sum_pm25 = defaultdict(float)
    station_count_pm25 = defaultdict(int)

    pairwise_stats = {
        (left, right): PairwiseStats()
        for left in ANALYSIS_COLUMNS
        for right in ANALYSIS_COLUMNS
        if ANALYSIS_COLUMNS.index(left) <= ANALYSIS_COLUMNS.index(right)
    }

    for row in iter_csv_rows(args.dataset):
        row_count += 1
        station_name = row["station"]
        station_names.add(station_name)

        for column in COLUMNS:
            if is_missing(row.get(column)):
                missing_counts[column] += 1

        numeric_row: dict[str, float | None] = {}
        for column in ANALYSIS_COLUMNS:
            value = as_float(row.get(column))
            numeric_row[column] = value
            if value is not None:
                numeric_values[column].append(value)

        month_number = int(row["month"])
        hour_number = int(row["hour"])

        pm25 = numeric_row["PM2.5"]
        if pm25 is not None:
            monthly_sum_pm25[month_number] += pm25
            monthly_count_pm25[month_number] += 1
            hourly_sum_pm25[hour_number] += pm25
            hourly_count_pm25[hour_number] += 1
            station_sum_pm25[station_name] += pm25
            station_count_pm25[station_name] += 1

        o3 = numeric_row["O3"]
        if o3 is not None:
            monthly_sum_o3[month_number] += o3
            monthly_count_o3[month_number] += 1
            hourly_sum_o3[hour_number] += o3
            hourly_count_o3[hour_number] += 1

        present_values = [
            (column, value)
            for column, value in numeric_row.items()
            if value is not None
        ]
        for index, (left_column, left_value) in enumerate(present_values):
            for right_column, right_value in present_values[index:]:
                pairwise_stats[(left_column, right_column)].update(left_value, right_value)

    missing_rows = []
    for column in COLUMNS:
        missing_count = missing_counts[column]
        missing_rate_pct = missing_count / row_count * 100
        missing_rows.append(
            {
                "column": column,
                "missing_count": missing_count,
                "missing_rate_pct": round(missing_rate_pct, 4),
            }
        )

    descriptive_rows: list[dict[str, object]] = []
    for column in ANALYSIS_COLUMNS:
        values = np.fromiter(numeric_values[column], dtype=float)
        descriptive_rows.append(
            {
                "column": column,
                "count": int(values.size),
                "missing_count": missing_counts[column],
                "missing_rate_pct": round(missing_counts[column] / row_count * 100, 4),
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "std": float(np.std(values, ddof=0)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }
        )

    monthly_avg_pm25 = {
        month: monthly_sum_pm25[month] / monthly_count_pm25[month]
        for month in monthly_count_pm25
    }
    monthly_avg_o3 = {
        month: monthly_sum_o3[month] / monthly_count_o3[month]
        for month in monthly_count_o3
    }
    hourly_avg_pm25 = {
        hour: hourly_sum_pm25[hour] / hourly_count_pm25[hour]
        for hour in hourly_count_pm25
    }
    hourly_avg_o3 = {
        hour: hourly_sum_o3[hour] / hourly_count_o3[hour]
        for hour in hourly_count_o3
    }

    station_pm25_rows = []
    for rank, station_name in enumerate(
        sorted(station_sum_pm25, key=lambda name: station_sum_pm25[name] / station_count_pm25[name], reverse=True),
        start=1,
    ):
        avg_pm25 = station_sum_pm25[station_name] / station_count_pm25[station_name]
        station_pm25_rows.append({"rank": rank, "station": station_name, "avg_pm25": round(avg_pm25, 4)})

    correlation_matrix = np.full((len(ANALYSIS_COLUMNS), len(ANALYSIS_COLUMNS)), np.nan)
    for i, left in enumerate(ANALYSIS_COLUMNS):
        for j, right in enumerate(ANALYSIS_COLUMNS):
            key = (left, right) if i <= j else (right, left)
            correlation_matrix[i, j] = pairwise_stats[key].correlation()

    pm25_index = ANALYSIS_COLUMNS.index("PM2.5")
    pm25_correlations = []
    for column_index, column in enumerate(ANALYSIS_COLUMNS):
        if column == "PM2.5":
            continue
        value = correlation_matrix[pm25_index, column_index]
        if not np.isnan(value):
            pm25_correlations.append((column, float(value)))
    pm25_strongest_positive = max(pm25_correlations, key=lambda item: item[1])
    pm25_strongest_negative = min(pm25_correlations, key=lambda item: item[1])

    highest_missing = max(missing_rows, key=lambda row: row["missing_rate_pct"])
    highest_station = station_pm25_rows[0]
    lowest_station = station_pm25_rows[-1]
    peak_pm25_month = max(monthly_avg_pm25.items(), key=lambda item: item[1])
    peak_o3_month = max(monthly_avg_o3.items(), key=lambda item: item[1])
    peak_pm25_hour = max(hourly_avg_pm25.items(), key=lambda item: item[1])
    peak_o3_hour = max(hourly_avg_o3.items(), key=lambda item: item[1])

    summary = {
        "assumption_note": "Blackboard task wording was not locally available, so Tasks 2-6 were implemented as a standard statistical-analysis sequence.",
        "dataset_path": str(args.dataset),
        "row_count": row_count,
        "column_count": len(COLUMNS),
        "station_count": len(station_names),
        "stations": sorted(station_names),
        "missing_summary": missing_rows,
        "descriptive_stats": descriptive_rows,
        "monthly_avg_pm25": {month_name(month): round(value, 4) for month, value in sorted(monthly_avg_pm25.items())},
        "monthly_avg_o3": {month_name(month): round(value, 4) for month, value in sorted(monthly_avg_o3.items())},
        "hourly_avg_pm25": {str(hour): round(value, 4) for hour, value in sorted(hourly_avg_pm25.items())},
        "hourly_avg_o3": {str(hour): round(value, 4) for hour, value in sorted(hourly_avg_o3.items())},
        "station_pm25_ranking": station_pm25_rows,
        "correlation_columns": ANALYSIS_COLUMNS,
        "correlation_matrix": np.round(correlation_matrix, 4).tolist(),
        "key_insights": {
            "highest_missing_column": highest_missing["column"],
            "highest_missing_rate_pct": highest_missing["missing_rate_pct"],
            "highest_pm25_station": highest_station["station"],
            "highest_pm25_value": highest_station["avg_pm25"],
            "lowest_pm25_station": lowest_station["station"],
            "lowest_pm25_value": lowest_station["avg_pm25"],
            "peak_pm25_month": month_name(peak_pm25_month[0]),
            "peak_pm25_month_value": round(peak_pm25_month[1], 4),
            "peak_o3_month": month_name(peak_o3_month[0]),
            "peak_o3_month_value": round(peak_o3_month[1], 4),
            "peak_pm25_hour": int(peak_pm25_hour[0]),
            "peak_pm25_hour_value": round(peak_pm25_hour[1], 4),
            "peak_o3_hour": int(peak_o3_hour[0]),
            "peak_o3_hour_value": round(peak_o3_hour[1], 4),
            "pm25_strongest_positive_correlation_column": pm25_strongest_positive[0],
            "pm25_strongest_positive_correlation_value": round(pm25_strongest_positive[1], 4),
            "pm25_strongest_negative_correlation_column": pm25_strongest_negative[0],
            "pm25_strongest_negative_correlation_value": round(pm25_strongest_negative[1], 4),
        },
    }

    write_csv(
        OUTPUT_DIR / "missing_summary.csv",
        ["column", "missing_count", "missing_rate_pct"],
        [[row["column"], row["missing_count"], row["missing_rate_pct"]] for row in missing_rows],
    )
    write_csv(
        OUTPUT_DIR / "descriptive_statistics.csv",
        ["column", "count", "missing_count", "missing_rate_pct", "mean", "median", "std", "min", "max"],
        [
            [
                row["column"],
                row["count"],
                row["missing_count"],
                row["missing_rate_pct"],
                row["mean"],
                row["median"],
                row["std"],
                row["min"],
                row["max"],
            ]
            for row in descriptive_rows
        ],
    )
    write_csv(
        OUTPUT_DIR / "station_pm25_ranking.csv",
        ["rank", "station", "avg_pm25"],
        [[row["rank"], row["station"], row["avg_pm25"]] for row in station_pm25_rows],
    )
    write_csv(
        OUTPUT_DIR / "correlation_matrix.csv",
        ["column", *ANALYSIS_COLUMNS],
        [
            [column, *[f"{value:.4f}" if not np.isnan(value) else "nan" for value in correlation_matrix[index]]]
            for index, column in enumerate(ANALYSIS_COLUMNS)
        ],
    )

    summary["generated_figures"] = {
        "missing_rate_by_column": str(save_missingness_chart(missing_rows).relative_to(ROOT)),
        "monthly_pm25_o3": str(save_monthly_trend_chart(monthly_avg_pm25, monthly_avg_o3).relative_to(ROOT)),
        "hourly_pm25_o3": str(save_hourly_pattern_chart(hourly_avg_pm25, hourly_avg_o3).relative_to(ROOT)),
        "station_pm25_ranking": str(save_station_chart(station_pm25_rows).relative_to(ROOT)),
        "correlation_heatmap": str(save_correlation_heatmap(correlation_matrix).relative_to(ROOT)),
    }

    (OUTPUT_DIR / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "analysis_summary.md").write_text(
        generate_summary_markdown(summary),
        encoding="utf-8",
    )

    print("Week 2 Activity 2 summary")
    print("=========================")
    print(f"Rows analysed: {row_count:,}")
    print(f"Stations analysed: {len(station_names)}")
    print(
        f"Highest missing-rate column: {summary['key_insights']['highest_missing_column']} "
        f"({summary['key_insights']['highest_missing_rate_pct']:.2f}%)"
    )
    print(
        f"Highest average PM2.5 station: {summary['key_insights']['highest_pm25_station']} "
        f"({summary['key_insights']['highest_pm25_value']:.2f})"
    )
    print(
        f"Peak PM2.5 month: {summary['key_insights']['peak_pm25_month']} "
        f"({summary['key_insights']['peak_pm25_month_value']:.2f})"
    )
    print(
        f"Peak O3 month: {summary['key_insights']['peak_o3_month']} "
        f"({summary['key_insights']['peak_o3_month_value']:.2f})"
    )
    print(
        f"PM2.5 strongest positive correlation: {summary['key_insights']['pm25_strongest_positive_correlation_column']} "
        f"({summary['key_insights']['pm25_strongest_positive_correlation_value']:.2f})"
    )
    print(
        f"PM2.5 strongest negative correlation: {summary['key_insights']['pm25_strongest_negative_correlation_column']} "
        f"({summary['key_insights']['pm25_strongest_negative_correlation_value']:.2f})"
    )
    print("Figures saved:")
    for label, rel_path in summary["generated_figures"].items():
        print(f"- {label}: {rel_path}")


if __name__ == "__main__":
    main()
