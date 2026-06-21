from __future__ import annotations

import json
import math
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "airline-passengers.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "airline_passengers_features.csv"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"

RANDOM_SEED = 42
TEST_MONTHS = 24
LAGS = [1, 2, 3, 6, 12]
ROLLING_WINDOWS = [3, 6, 12]


def ensure_directories() -> None:
    for path in [
        RAW_DATA_PATH.parent,
        PROCESSED_DATA_PATH.parent,
        FIGURE_DIR,
        TABLE_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def load_dataset() -> pd.DataFrame:
    if not RAW_DATA_PATH.exists():
        urlretrieve(DATA_URL, RAW_DATA_PATH)

    df = pd.read_csv(RAW_DATA_PATH)
    df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m")
    df["Passengers"] = pd.to_numeric(df["Passengers"], errors="coerce")
    df = df.sort_values("Month").drop_duplicates(subset=["Month"]).reset_index(drop=True)
    return df


def build_preprocessing_summary(df: pd.DataFrame, feature_df: pd.DataFrame, test_start: pd.Timestamp) -> pd.DataFrame:
    summary = {
        "raw_rows": len(df),
        "processed_rows_after_lags": len(feature_df),
        "start_month": df["Month"].min().strftime("%Y-%m"),
        "end_month": df["Month"].max().strftime("%Y-%m"),
        "missing_month_values": int(df["Month"].isna().sum()),
        "missing_passenger_values": int(df["Passengers"].isna().sum()),
        "duplicate_months_removed": int(len(df) - df["Month"].nunique()),
        "train_end": (test_start - pd.offsets.MonthBegin(1)).strftime("%Y-%m"),
        "test_start": test_start.strftime("%Y-%m"),
        "test_months": TEST_MONTHS,
        "engineered_feature_count": int(feature_df.drop(columns=["Month", "Passengers"]).shape[1]),
    }
    return pd.DataFrame([summary])


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    feature_df = df.copy()
    feature_df["time_index"] = np.arange(len(feature_df))
    feature_df["year"] = feature_df["Month"].dt.year
    feature_df["month"] = feature_df["Month"].dt.month
    feature_df["quarter"] = feature_df["Month"].dt.quarter
    feature_df["month_sin"] = np.sin(2 * np.pi * feature_df["month"] / 12)
    feature_df["month_cos"] = np.cos(2 * np.pi * feature_df["month"] / 12)

    for lag in LAGS:
        feature_df[f"lag_{lag}"] = feature_df["Passengers"].shift(lag)

    shifted = feature_df["Passengers"].shift(1)
    for window in ROLLING_WINDOWS:
        feature_df[f"rolling_mean_{window}"] = shifted.rolling(window=window).mean()
        feature_df[f"rolling_std_{window}"] = shifted.rolling(window=window).std()

    feature_df["diff_1"] = feature_df["Passengers"].diff(1)
    feature_df["pct_change_1"] = feature_df["Passengers"].pct_change(1)
    feature_df["expanding_mean"] = shifted.expanding(min_periods=3).mean()

    return feature_df.dropna().reset_index(drop=True)


def get_test_start(df: pd.DataFrame) -> pd.Timestamp:
    return df["Month"].max() - pd.DateOffset(months=TEST_MONTHS - 1)


def plot_time_series(df: pd.DataFrame, test_start: pd.Timestamp) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    train = df[df["Month"] < test_start]
    test = df[df["Month"] >= test_start]
    ax.plot(train["Month"], train["Passengers"], color="#1f77b4", linewidth=2, label="Training period")
    ax.plot(test["Month"], test["Passengers"], color="#ff7f0e", linewidth=2, label="Test period")
    ax.axvline(test_start, color="#444444", linestyle="--", linewidth=1)
    ax.set_title("Monthly Airline Passengers Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Passengers")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "01_time_series_train_test.png", dpi=180)
    plt.close(fig)


def plot_distribution(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    values = df["Passengers"]
    ax.hist(values, bins=18, color="#4c78a8", edgecolor="white", alpha=0.9)
    ax.axvline(values.mean(), color="#e45756", linewidth=2, label=f"Mean: {values.mean():.1f}")
    ax.axvline(values.median(), color="#54a24b", linewidth=2, linestyle="--", label=f"Median: {values.median():.1f}")
    ax.set_title("Passenger Count Distribution")
    ax.set_xlabel("Passengers")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "02_passenger_distribution.png", dpi=180)
    plt.close(fig)


def plot_monthly_seasonality(df: pd.DataFrame) -> None:
    pivot = df.assign(year=df["Month"].dt.year, month=df["Month"].dt.month).pivot(
        index="month", columns="year", values="Passengers"
    )
    fig, ax = plt.subplots(figsize=(11, 6))
    for year in pivot.columns:
        ax.plot(pivot.index, pivot[year], linewidth=1.3, alpha=0.6)
    ax.plot(pivot.index, pivot.mean(axis=1), color="#111111", linewidth=3, label="Average by month")
    ax.set_title("Seasonality Pattern by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Passengers")
    ax.set_xticks(range(1, 13))
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "03_monthly_seasonality.png", dpi=180)
    plt.close(fig)


def plot_lag_correlation(feature_df: pd.DataFrame) -> None:
    corr_cols = ["Passengers"] + [f"lag_{lag}" for lag in LAGS] + [
        f"rolling_mean_{window}" for window in ROLLING_WINDOWS
    ]
    corr = feature_df[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr_cols)))
    ax.set_yticks(range(len(corr_cols)))
    ax.set_xticklabels(corr_cols, rotation=45, ha="right")
    ax.set_yticklabels(corr_cols)
    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("Correlation Between Target and Lag Features")
    fig.colorbar(image, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "04_lag_correlation.png", dpi=180)
    plt.close(fig)


def run_eda(df: pd.DataFrame, feature_df: pd.DataFrame, test_start: pd.Timestamp) -> None:
    plot_time_series(df, test_start)
    plot_distribution(df)
    plot_monthly_seasonality(df)
    plot_lag_correlation(feature_df)


def split_features(feature_df: pd.DataFrame, test_start: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    feature_cols = [
        col
        for col in feature_df.columns
        if col not in {"Month", "Passengers", "diff_1", "pct_change_1"}
    ]
    train_df = feature_df[feature_df["Month"] < test_start].copy()
    test_df = feature_df[feature_df["Month"] >= test_start].copy()
    return train_df[feature_cols], test_df[feature_cols], train_df["Passengers"], test_df["Passengers"]


@dataclass
class SeriesScaler:
    mean_: float
    std_: float

    @classmethod
    def fit(cls, values: np.ndarray) -> "SeriesScaler":
        std = float(np.std(values))
        if std == 0:
            std = 1.0
        return cls(mean_=float(np.mean(values)), std_=std)

    def transform(self, values: np.ndarray) -> np.ndarray:
        return (values - self.mean_) / self.std_

    def inverse_transform(self, values: np.ndarray) -> np.ndarray:
        return values * self.std_ + self.mean_


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -50, 50)
    return 1.0 / (1.0 + np.exp(-values))


class NumpyLSTMRegressor:
    """Small LSTM regressor for one-step-ahead univariate forecasting."""

    def __init__(
        self,
        hidden_size: int = 16,
        epochs: int = 500,
        learning_rate: float = 0.015,
        seed: int = RANDOM_SEED,
    ) -> None:
        self.hidden_size = hidden_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.rng = np.random.default_rng(seed)
        self.input_size: int | None = None
        self.params: dict[str, np.ndarray] = {}

    def _initialize(self, input_size: int) -> None:
        self.input_size = input_size
        concat_size = self.hidden_size + input_size
        scale = 1 / math.sqrt(concat_size)
        self.params = {
            "Wf": self.rng.normal(0, scale, (self.hidden_size, concat_size)),
            "Wi": self.rng.normal(0, scale, (self.hidden_size, concat_size)),
            "Wg": self.rng.normal(0, scale, (self.hidden_size, concat_size)),
            "Wo": self.rng.normal(0, scale, (self.hidden_size, concat_size)),
            "bf": np.ones(self.hidden_size) * 0.5,
            "bi": np.zeros(self.hidden_size),
            "bg": np.zeros(self.hidden_size),
            "bo": np.zeros(self.hidden_size),
            "Wy": self.rng.normal(0, scale, (1, self.hidden_size)),
            "by": np.zeros(1),
        }

    def _forward(self, x: np.ndarray) -> tuple[float, list[dict[str, np.ndarray]]]:
        if self.input_size is None:
            raise RuntimeError("Model is not initialized.")

        h_prev = np.zeros(self.hidden_size)
        c_prev = np.zeros(self.hidden_size)
        caches: list[dict[str, np.ndarray]] = []

        for x_t in x:
            z = np.concatenate([h_prev, x_t])
            f = sigmoid(self.params["Wf"] @ z + self.params["bf"])
            i = sigmoid(self.params["Wi"] @ z + self.params["bi"])
            g = np.tanh(self.params["Wg"] @ z + self.params["bg"])
            o = sigmoid(self.params["Wo"] @ z + self.params["bo"])
            c = f * c_prev + i * g
            h = o * np.tanh(c)
            caches.append(
                {
                    "z": z,
                    "f": f,
                    "i": i,
                    "g": g,
                    "o": o,
                    "c": c,
                    "c_prev": c_prev,
                    "h": h,
                }
            )
            h_prev = h
            c_prev = c

        prediction = (self.params["Wy"] @ h_prev + self.params["by"]).item()
        return prediction, caches

    def fit(self, x_train: np.ndarray, y_train: np.ndarray) -> "NumpyLSTMRegressor":
        self._initialize(x_train.shape[2])
        n_samples = x_train.shape[0]

        for epoch in range(self.epochs):
            indices = self.rng.permutation(n_samples)
            epoch_losses = []
            for idx in indices:
                x = x_train[idx]
                y = float(y_train[idx])
                pred, caches = self._forward(x)
                error = pred - y
                epoch_losses.append(error * error)

                grads = {name: np.zeros_like(value) for name, value in self.params.items()}
                h_last = caches[-1]["h"]
                dy = np.array([error])
                grads["Wy"] += np.outer(dy, h_last)
                grads["by"] += dy
                dh_next = (self.params["Wy"].T @ dy).ravel()
                dc_next = np.zeros(self.hidden_size)

                for cache in reversed(caches):
                    z = cache["z"]
                    f = cache["f"]
                    i = cache["i"]
                    g = cache["g"]
                    o = cache["o"]
                    c = cache["c"]
                    c_prev = cache["c_prev"]

                    tanh_c = np.tanh(c)
                    do = dh_next * tanh_c
                    do_raw = do * o * (1 - o)

                    dc = dh_next * o * (1 - tanh_c * tanh_c) + dc_next
                    df = dc * c_prev
                    df_raw = df * f * (1 - f)
                    di = dc * g
                    di_raw = di * i * (1 - i)
                    dg = dc * i
                    dg_raw = dg * (1 - g * g)

                    grads["Wf"] += np.outer(df_raw, z)
                    grads["Wi"] += np.outer(di_raw, z)
                    grads["Wg"] += np.outer(dg_raw, z)
                    grads["Wo"] += np.outer(do_raw, z)
                    grads["bf"] += df_raw
                    grads["bi"] += di_raw
                    grads["bg"] += dg_raw
                    grads["bo"] += do_raw

                    dz = (
                        self.params["Wf"].T @ df_raw
                        + self.params["Wi"].T @ di_raw
                        + self.params["Wg"].T @ dg_raw
                        + self.params["Wo"].T @ do_raw
                    )
                    dh_next = dz[: self.hidden_size]
                    dc_next = dc * f

                for name, grad in grads.items():
                    np.clip(grad, -1.0, 1.0, out=grad)
                    self.params[name] -= self.learning_rate * grad

            if epoch > 60 and np.mean(epoch_losses) < 0.01:
                break

        return self

    def predict(self, x_test: np.ndarray) -> np.ndarray:
        return np.array([self._forward(x)[0] for x in x_test])


def make_lstm_windows(values: np.ndarray, months: np.ndarray, sequence_length: int = 12) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_values = []
    y_values = []
    target_months = []
    for idx in range(sequence_length, len(values)):
        x_values.append(values[idx - sequence_length : idx].reshape(sequence_length, 1))
        y_values.append(values[idx])
        target_months.append(months[idx])
    return np.array(x_values), np.array(y_values), np.array(target_months)


def train_lstm(df: pd.DataFrame, test_start: pd.Timestamp) -> pd.Series:
    train_values = df[df["Month"] < test_start]["Passengers"].to_numpy(dtype=float)
    scaler = SeriesScaler.fit(train_values)
    scaled_values = scaler.transform(df["Passengers"].to_numpy(dtype=float))
    months = df["Month"].to_numpy()
    x_all, y_all, target_months = make_lstm_windows(scaled_values, months, sequence_length=12)
    train_mask = target_months < np.datetime64(test_start)
    test_mask = target_months >= np.datetime64(test_start)

    model = NumpyLSTMRegressor(hidden_size=18, epochs=650, learning_rate=0.012)
    model.fit(x_all[train_mask], y_all[train_mask])
    predictions_scaled = model.predict(x_all[test_mask])
    predictions = scaler.inverse_transform(predictions_scaled)
    prediction_months = pd.to_datetime(target_months[test_mask])
    return pd.Series(predictions, index=prediction_months, name="LSTM")


def train_arima(df: pd.DataFrame, test_start: pd.Timestamp) -> tuple[pd.Series, str]:
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError as exc:
        raise RuntimeError("statsmodels is required for ARIMA. Install requirements.txt first.") from exc

    train = df[df["Month"] < test_start].set_index("Month")["Passengers"].asfreq("MS")
    test_months = df[df["Month"] >= test_start]["Month"]

    best_aic = np.inf
    best_fit = None
    best_order = None
    candidate_orders = [
        (p, d, q)
        for p in range(0, 4)
        for d in range(0, 3)
        for q in range(0, 4)
        if not (p == 0 and d == 0 and q == 0)
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for order in candidate_orders:
            try:
                fit = ARIMA(train, order=order).fit()
            except Exception:
                continue
            if fit.aic < best_aic:
                best_aic = fit.aic
                best_fit = fit
                best_order = order

    if best_fit is None or best_order is None:
        raise RuntimeError("ARIMA model selection failed for all candidate orders.")

    forecast = best_fit.forecast(steps=len(test_months))
    forecast.index = pd.to_datetime(test_months)
    return pd.Series(forecast.to_numpy(), index=forecast.index, name="ARIMA"), f"ARIMA{best_order}"


def calculate_metrics(y_true: pd.Series, y_pred: pd.Series, model_name: str) -> dict[str, float | str]:
    aligned = pd.concat([y_true.rename("actual"), y_pred.rename("predicted")], axis=1).dropna()
    actual = aligned["actual"].to_numpy(dtype=float)
    predicted = aligned["predicted"].to_numpy(dtype=float)
    return {
        "model": model_name,
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "MAE": float(mean_absolute_error(actual, predicted)),
        "R2": float(r2_score(actual, predicted)),
        "MAPE": float(np.mean(np.abs((actual - predicted) / actual)) * 100),
    }


def train_supervised_models(
    feature_df: pd.DataFrame, test_start: pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    x_train, x_test, y_train, y_test = split_features(feature_df, test_start)
    test_months = feature_df[feature_df["Month"] >= test_start]["Month"]

    models = {
        "Linear Regression": Pipeline(
            [("scaler", StandardScaler()), ("model", LinearRegression())]
        ),
        "ANN": TransformedTargetRegressor(
            regressor=Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "model",
                        MLPRegressor(
                            hidden_layer_sizes=(32, 16),
                            activation="relu",
                            solver="adam",
                            alpha=0.01,
                            learning_rate_init=0.001,
                            early_stopping=True,
                            validation_fraction=0.15,
                            max_iter=5000,
                            random_state=RANDOM_SEED,
                        ),
                    ),
                ]
            ),
            transformer=StandardScaler(),
        ),
    }

    try:
        from xgboost import XGBRegressor

        models["XGBoost"] = XGBRegressor(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=RANDOM_SEED,
        )
    except ImportError as exc:
        raise RuntimeError("xgboost is required. Install requirements.txt first.") from exc

    predictions = pd.DataFrame({"Month": test_months.to_numpy(), "Actual": y_test.to_numpy()})
    metrics = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=ConvergenceWarning)
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for model_name, model in models.items():
            model.fit(x_train, y_train)
            pred = pd.Series(model.predict(x_test), index=pd.to_datetime(test_months), name=model_name)
            predictions[model_name] = pred.to_numpy()
            metrics.append(calculate_metrics(pd.Series(y_test.to_numpy(), index=pred.index), pred, model_name))

    return predictions, pd.DataFrame(metrics)


def combine_all_model_predictions(
    df: pd.DataFrame,
    feature_df: pd.DataFrame,
    supervised_predictions: pd.DataFrame,
    supervised_metrics: pd.DataFrame,
    test_start: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    test_actual = df[df["Month"] >= test_start].set_index("Month")["Passengers"]
    combined = supervised_predictions.copy()
    combined["Month"] = pd.to_datetime(combined["Month"])

    lstm_pred = train_lstm(df, test_start)
    arima_pred, arima_label = train_arima(df, test_start)

    combined = combined.set_index("Month")
    combined["LSTM"] = lstm_pred
    combined["ARIMA"] = arima_pred
    combined = combined.reset_index()

    metrics = supervised_metrics.copy()
    for name in ["LSTM", "ARIMA"]:
        metrics = pd.concat(
            [
                metrics,
                pd.DataFrame([calculate_metrics(test_actual, combined.set_index("Month")[name], name)]),
            ],
            ignore_index=True,
        )

    metrics = metrics.sort_values("RMSE").reset_index(drop=True)
    return combined, metrics, arima_label


def plot_actual_vs_predicted(predictions: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(predictions["Month"], predictions["Actual"], color="#111111", linewidth=3, label="Actual")
    model_colors = {
        "Linear Regression": "#4c78a8",
        "XGBoost": "#f58518",
        "ANN": "#54a24b",
        "LSTM": "#b279a2",
        "ARIMA": "#e45756",
    }
    for model_name, color in model_colors.items():
        ax.plot(predictions["Month"], predictions[model_name], linewidth=1.8, alpha=0.9, label=model_name, color=color)
    ax.set_title("Actual vs Predicted Passenger Values")
    ax.set_xlabel("Month")
    ax.set_ylabel("Passengers")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "05_actual_vs_predicted.png", dpi=180)
    plt.close(fig)


def plot_metric_comparison(metrics: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    error_metrics = metrics.set_index("model")[["RMSE", "MAE", "MAPE"]]
    error_metrics.plot(kind="bar", ax=axes[0], color=["#4c78a8", "#f58518", "#54a24b"])
    axes[0].set_title("Error Metrics by Model")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Lower is better")
    axes[0].tick_params(axis="x", rotation=35)
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].bar(metrics["model"], metrics["R2"], color="#72b7b2")
    axes[1].set_title("R-squared by Model")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Higher is better")
    axes[1].tick_params(axis="x", rotation=35)
    axes[1].grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "06_model_metric_comparison.png", dpi=180)
    plt.close(fig)


def plot_residuals(predictions: pd.DataFrame, best_model: str) -> None:
    residuals = predictions["Actual"] - predictions[best_model]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.axhline(0, color="#222222", linewidth=1)
    ax.bar(predictions["Month"], residuals, color="#4c78a8", width=20)
    ax.set_title(f"Residuals for Best RMSE Model: {best_model}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Actual - Predicted")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "07_best_model_residuals.png", dpi=180)
    plt.close(fig)


def write_project_summary(df: pd.DataFrame, metrics: pd.DataFrame, arima_label: str) -> None:
    best = metrics.iloc[0].to_dict()
    summary = {
        "dataset": "Monthly international airline passengers",
        "source_url": DATA_URL,
        "rows": int(len(df)),
        "start_month": df["Month"].min().strftime("%Y-%m"),
        "end_month": df["Month"].max().strftime("%Y-%m"),
        "test_months": TEST_MONTHS,
        "best_model_by_rmse": best["model"],
        "best_rmse": round(float(best["RMSE"]), 3),
        "best_mae": round(float(best["MAE"]), 3),
        "best_r2": round(float(best["R2"]), 3),
        "best_mape": round(float(best["MAPE"]), 3),
        "selected_arima_order": arima_label,
        "key_insights": [
            "Passenger demand increases strongly over time, so trend features are important.",
            "The dataset has clear yearly seasonality, with repeated mid-year peaks.",
            "Lag and rolling average features are highly correlated with the target.",
            "Tree-based and neural models can capture nonlinear seasonal effects, but the small dataset limits model complexity.",
            "ARIMA is useful as a statistical baseline, although plain ARIMA may not capture all yearly seasonality as well as feature-based models.",
        ],
    }
    with (TABLE_DIR / "project_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)


def main() -> None:
    np.random.seed(RANDOM_SEED)
    ensure_directories()
    df = load_dataset()
    test_start = get_test_start(df)
    feature_df = engineer_features(df)
    feature_df.to_csv(PROCESSED_DATA_PATH, index=False)

    preprocessing_summary = build_preprocessing_summary(df, feature_df, test_start)
    preprocessing_summary.to_csv(TABLE_DIR / "preprocessing_summary.csv", index=False)
    feature_df.head(15).to_csv(TABLE_DIR / "feature_sample.csv", index=False)

    run_eda(df, feature_df, test_start)

    supervised_predictions, supervised_metrics = train_supervised_models(feature_df, test_start)
    predictions, metrics, arima_label = combine_all_model_predictions(
        df, feature_df, supervised_predictions, supervised_metrics, test_start
    )

    predictions.to_csv(TABLE_DIR / "model_predictions.csv", index=False)
    metrics.to_csv(TABLE_DIR / "model_metrics.csv", index=False)

    plot_actual_vs_predicted(predictions)
    plot_metric_comparison(metrics)
    plot_residuals(predictions, metrics.iloc[0]["model"])
    write_project_summary(df, metrics, arima_label)

    print("Pipeline complete.")
    print(f"Processed data: {PROCESSED_DATA_PATH}")
    print(f"Metrics: {TABLE_DIR / 'model_metrics.csv'}")
    print(f"Best model by RMSE: {metrics.iloc[0]['model']}")


if __name__ == "__main__":
    main()
