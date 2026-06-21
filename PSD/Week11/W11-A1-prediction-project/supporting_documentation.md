# Supporting Documentation - Airline Passenger Prediction Project

## GitHub Submission Link

After pushing this folder to GitHub, share this project link:

https://github.com/Ted323-NZ/YoobeeMSE800/tree/main/PSD/Week11/W11-A1-prediction-project

## Dataset

- Source: https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv
- Records: 144 monthly observations
- Period: January 1949 to December 1960
- Target variable: `Passengers`
- Forecast test period: January 1959 to December 1960

## Data Understanding and Preprocessing

The dataset is a monthly time series with one date column and one numeric target column. The preprocessing pipeline:

- Loaded and cached the source CSV.
- Parsed `Month` into a datetime field.
- Sorted records chronologically.
- Checked for missing passenger values and duplicate months.
- Created supervised learning features from the time series.
- Held out the last 24 months as the test period.

The processed dataset contains 132 rows after lag and rolling-window features are created.

## Feature Engineering

Features used for supervised models include:

- Time trend index.
- Year, month, and quarter.
- Sine/cosine month encoding for seasonality.
- Lag features: 1, 2, 3, 6, and 12 months.
- Rolling means and standard deviations: 3, 6, and 12 months.
- Expanding mean based on prior observations.

## Models Compared

- Linear Regression
- XGBoost Regressor
- Artificial Neural Network (ANN)
- Long Short-Term Memory model (LSTM)
- ARIMA

## Final Model Results

| Rank | Model | RMSE | MAE | R2 | MAPE |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | ANN | 27.37 | 20.08 | 0.866 | 4.50% |
| 2 | Linear Regression | 42.12 | 39.01 | 0.682 | 8.86% |
| 3 | XGBoost | 64.74 | 56.07 | 0.248 | 11.81% |
| 4 | ARIMA | 88.16 | 64.01 | -0.394 | 12.56% |
| 5 | LSTM | 94.96 | 77.32 | -0.617 | 16.38% |

## Key Findings

ANN achieved the best test performance after scaling both input features and the target variable. It captured nonlinear relationships between trend, seasonality, lag values, and rolling averages.

Linear Regression was the strongest simple baseline. Its performance was good because trend and lag features explain much of the passenger demand pattern.

XGBoost performed worse than Linear Regression because tree-based models can struggle to extrapolate into unseen higher demand levels.

ARIMA and LSTM were useful baselines, but the plain ARIMA setup and small custom LSTM underperformed on this short seasonal dataset.

## Recommendations

- Use ANN as the best-performing model from this experiment.
- Keep Linear Regression as an interpretable benchmark.
- Add SARIMA or SARIMAX in future work to better model yearly seasonality.
- Use more historical data if available.
- Consider rolling-origin validation for a more robust time-series evaluation.

## Deliverables

- Source code: `src/run_pipeline.py`
- Requirements: `requirements.txt`
- Processed data: `data/processed/airline_passengers_features.csv`
- Model results: `outputs/tables/model_metrics.csv`
- Prediction outputs: `outputs/tables/model_predictions.csv`
- Visualizations: `outputs/figures/`
- Presentation: `presentation/Week11_Activity_1_1_Airline_Prediction.pptx`
- 10-minute speaker script: `presentation_script_10_minutes.md`
