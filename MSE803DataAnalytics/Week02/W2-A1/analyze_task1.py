from __future__ import annotations

import argparse
import csv
import html
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile


DEFAULT_DATASET = Path.home() / "Downloads" / "beijing+multi+site+air+quality+data.zip"
MISSING_MARKERS = {"", "NA", "N/A", "NULL", "NaN", "nan"}


@dataclass
class AnalysisResult:
    dataset_source: str
    csv_file_count: int
    csv_file_names: list[str]
    columns: list[str]
    sample_rows: list[dict[str, str]]
    column_types: dict[str, str]
    total_rows: int
    total_columns: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Task 1 analysis for the Beijing Multi-Site Air Quality dataset."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to the dataset zip file or an extracted dataset directory.",
    )
    parser.add_argument(
        "--save-output",
        type=Path,
        default=None,
        help="Optional path to save the plain-text report.",
    )
    parser.add_argument(
        "--save-html",
        type=Path,
        default=None,
        help="Optional path to save the HTML report used for the screenshot.",
    )
    return parser.parse_args()


def merge_types(current: str | None, new_type: str | None) -> str | None:
    if new_type is None:
        return current
    if current is None:
        return new_type
    order = {"int": 0, "float": 1, "string": 2}
    return current if order[current] >= order[new_type] else new_type


def infer_type(value: str) -> str | None:
    value = value.strip()
    if value in MISSING_MARKERS:
        return None
    if value.lstrip("+-").isdigit():
        return "int"
    try:
        float(value)
    except ValueError:
        return "string"
    return "float"


def analyze_rows(csv_sources: Iterable[tuple[str, io.TextIOBase]]) -> AnalysisResult:
    sample_rows: list[dict[str, str]] = []
    columns: list[str] | None = None
    column_types: dict[str, str | None] = {}
    total_rows = 0
    csv_file_names: list[str] = []

    for name, text_stream in csv_sources:
        csv_file_names.append(name)
        reader = csv.DictReader(text_stream)
        if columns is None:
            columns = reader.fieldnames or []
            column_types = {column: None for column in columns}

        for row in reader:
            if len(sample_rows) < 5:
                sample_rows.append(dict(row))
            total_rows += 1
            for column, value in row.items():
                column_types[column] = merge_types(column_types[column], infer_type(value))

    if columns is None:
        raise ValueError("No CSV rows were found in the dataset.")

    finalized_types = {
        column: (column_types[column] or "unknown")
        for column in columns
    }

    return AnalysisResult(
        dataset_source="",
        csv_file_count=len(csv_file_names),
        csv_file_names=csv_file_names,
        columns=columns,
        sample_rows=sample_rows,
        column_types=finalized_types,
        total_rows=total_rows,
        total_columns=len(columns),
    )


def analyze_from_directory(dataset_dir: Path) -> AnalysisResult:
    preferred_csv_files = sorted(dataset_dir.rglob("PRSA_Data_*.csv"))
    if preferred_csv_files:
        csv_files = preferred_csv_files
    else:
        zip_files = sorted(dataset_dir.rglob("*.zip"))
        preferred_zip_files = [
            zip_file
            for zip_file in zip_files
            if "PRSA2017" in zip_file.name or "PRSA" in zip_file.name
        ]
        if preferred_zip_files:
            return analyze_from_path(preferred_zip_files[0])
        csv_files = sorted(dataset_dir.rglob("*.csv"))
        if not csv_files:
            if zip_files:
                return analyze_from_path(zip_files[0])
            raise FileNotFoundError(f"No CSV or ZIP files found in {dataset_dir}")

    def open_streams() -> Iterable[tuple[str, io.TextIOBase]]:
        for csv_file in csv_files:
            yield str(csv_file.name), csv_file.open("r", encoding="utf-8", newline="")

    streams = list(open_streams())
    try:
        result = analyze_rows(streams)
    finally:
        for _, stream in streams:
            stream.close()

    result.dataset_source = str(dataset_dir)
    return result


def analyze_from_zip(dataset_zip: Path) -> AnalysisResult:
    with ZipFile(dataset_zip) as archive:
        nested_zip_names = sorted(name for name in archive.namelist() if name.endswith(".zip"))

        if nested_zip_names:
            nested_name = next(
                (name for name in nested_zip_names if "PRSA2017" in name or "PRSA" in name),
                nested_zip_names[0],
            )
            nested_bytes = io.BytesIO(archive.read(nested_name))
            with ZipFile(nested_bytes) as nested_archive:
                csv_names = sorted(name for name in nested_archive.namelist() if name.endswith(".csv"))
                streams = [
                    (
                        name,
                        io.TextIOWrapper(nested_archive.open(name), encoding="utf-8", newline=""),
                    )
                    for name in csv_names
                ]
                try:
                    result = analyze_rows(streams)
                finally:
                    for _, stream in streams:
                        stream.close()
            result.dataset_source = f"{dataset_zip} -> {nested_name}"
            return result

        csv_names = sorted(name for name in archive.namelist() if name.endswith(".csv"))
        streams = [
            (name, io.TextIOWrapper(archive.open(name), encoding="utf-8", newline=""))
            for name in csv_names
        ]
        try:
            result = analyze_rows(streams)
        finally:
            for _, stream in streams:
                stream.close()

    result.dataset_source = str(dataset_zip)
    return result


def analyze_from_path(dataset_path: Path) -> AnalysisResult:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")
    if dataset_path.is_dir():
        return analyze_from_directory(dataset_path)
    if dataset_path.suffix.lower() == ".zip":
        return analyze_from_zip(dataset_path)
    raise ValueError("Dataset path must be a directory or a .zip file.")


def format_plain_table(headers: list[str], rows: list[list[str]]) -> str:
    widths: list[int] = []
    for index, header in enumerate(headers):
        candidates = [len(str(header))]
        candidates.extend(len(str(row[index])) for row in rows)
        widths.append(max(candidates))

    header_row = " | ".join(str(header).ljust(width) for header, width in zip(headers, widths))
    separator_row = "-+-".join("-" * width for width in widths)
    body_rows = [
        " | ".join(str(value).ljust(width) for value, width in zip(row, widths))
        for row in rows
    ]
    return "\n".join([header_row, separator_row, *body_rows])


def build_text_report(result: AnalysisResult) -> str:
    sample_table_rows = [
        [row.get(column, "") for column in result.columns]
        for row in result.sample_rows
    ]
    type_rows = [[column, dtype] for column, dtype in result.column_types.items()]

    sections = [
        "Beijing Multi-Site Air Quality - Task 1",
        "=" * 40,
        f"Dataset source: {result.dataset_source}",
        f"CSV files loaded: {result.csv_file_count}",
        "",
        "Data structure",
        "-" * 14,
        "The outer download contains a nested data ZIP.",
        f"The nested dataset contains {result.csv_file_count} CSV files, one per monitoring station.",
        "Each row represents one hourly observation at one Beijing air-quality monitoring site.",
        "Missing values are marked as NA in the raw data.",
        "",
        "Task 1 Results",
        "-" * 14,
        "1. First 5 rows",
        format_plain_table(result.columns, sample_table_rows),
        "",
        "2. Column names and inferred data types",
        format_plain_table(["Column", "Data Type"], type_rows),
        "",
        "3. Total rows and columns",
        f"Total rows: {result.total_rows:,}",
        f"Total columns: {result.total_columns}",
    ]
    return "\n".join(sections)


def build_html_report(result: AnalysisResult) -> str:
    sample_rows_html = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(row.get(column, ''))}</td>" for column in result.columns)
        + "</tr>"
        for row in result.sample_rows
    )
    types_html = "".join(
        f"<tr><td>{html.escape(column)}</td><td>{html.escape(dtype)}</td></tr>"
        for column, dtype in result.column_types.items()
    )
    header_cells = "".join(f"<th>{html.escape(column)}</th>" for column in result.columns)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Beijing Air Quality Task 1</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f1ea;
      --panel: #fffaf2;
      --ink: #1f2933;
      --muted: #52606d;
      --accent: #9c6644;
      --line: #d9cbb9;
    }}
    body {{
      margin: 0;
      padding: 32px;
      background: radial-gradient(circle at top left, #f9e6d3, var(--bg) 42%);
      color: var(--ink);
      font: 15px/1.45 "SF Mono", "Menlo", "Consolas", monospace;
    }}
    .wrap {{
      max-width: 1700px;
      margin: 0 auto;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 18px 50px rgba(58, 36, 24, 0.08);
      overflow: hidden;
    }}
    .hero {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(156, 102, 68, 0.12), rgba(255, 250, 242, 0.9));
    }}
    h1, h2 {{
      margin: 0 0 10px;
      font-weight: 700;
    }}
    p {{
      margin: 6px 0;
      color: var(--muted);
    }}
    .section {{
      padding: 24px 32px;
    }}
    .stats {{
      display: flex;
      gap: 16px;
      margin-top: 16px;
      flex-wrap: wrap;
    }}
    .card {{
      min-width: 190px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.6);
    }}
    .card strong {{
      display: block;
      font-size: 24px;
      color: var(--accent);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      table-layout: fixed;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
      word-break: break-word;
    }}
    th {{
      background: #f7eee4;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>Beijing Multi-Site Air Quality - Task 1</h1>
      <p>Dataset source: {html.escape(result.dataset_source)}</p>
      <p>12 station CSV files combined into one analysis-ready view.</p>
      <div class="stats">
        <div class="card"><span>Total rows</span><strong>{result.total_rows:,}</strong></div>
        <div class="card"><span>Total columns</span><strong>{result.total_columns}</strong></div>
        <div class="card"><span>CSV files</span><strong>{result.csv_file_count}</strong></div>
      </div>
    </div>

    <div class="section">
      <h2>Data Structure</h2>
      <p>The download package contains a nested ZIP file, and the nested ZIP contains one CSV file per Beijing monitoring station.</p>
      <p>Each row is a single hourly observation with pollutant values, meteorological readings, and the station name. Missing values are recorded as <code>NA</code>.</p>
    </div>

    <div class="section">
      <h2>First 5 Rows</h2>
      <table>
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{sample_rows_html}</tbody>
      </table>
    </div>

    <div class="section">
      <h2>Column Names and Inferred Data Types</h2>
      <table>
        <thead><tr><th>Column</th><th>Data Type</th></tr></thead>
        <tbody>{types_html}</tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    result = analyze_from_path(args.dataset)
    report = build_text_report(result)
    print(report)

    if args.save_output:
        write_file(args.save_output, report)
    if args.save_html:
        write_file(args.save_html, build_html_report(result))


if __name__ == "__main__":
    main()
