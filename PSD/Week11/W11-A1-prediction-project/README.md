# Week 11 Activity 1.1 - Airline Passenger Prediction Project

This project builds a data analytics prediction pipeline for the monthly
international airline passengers dataset. It covers data loading,
preprocessing, EDA, feature engineering, model development, model comparison,
and a PowerPoint presentation.

Dataset source:
https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv

## Project Structure

```text
W11-A1-prediction-project/
  data/
    raw/                         # cached source CSV
    processed/                   # feature-engineered dataset
  outputs/
    figures/                     # EDA and model comparison charts
    tables/                      # metrics, predictions, preprocessing summary
  presentation/                  # final PowerPoint deck
  src/
    run_pipeline.py              # full prediction pipeline
  requirements.txt
  README.md
```

## Models Included

- Linear Regression
- XGBoost Regressor
- Artificial Neural Network (ANN)
- Long Short-Term Memory (LSTM)
- ARIMA

## Evaluation Metrics

- RMSE
- MAE
- R-squared
- MAPE

## How to Run

From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py
```

The script will create:

- `data/raw/airline-passengers.csv`
- `data/processed/airline_passengers_features.csv`
- `outputs/tables/model_metrics.csv`
- `outputs/tables/model_predictions.csv`
- EDA and model comparison charts in `outputs/figures/`

## GitHub Submission Note

After the dataset loading and preprocessing are complete, commit and push this
folder to GitHub. Share the repository URL with the tutor, for example:

```text
https://github.com/Ted323-NZ/YoobeeMSE800/tree/main/PSD/Week11/W11-A1-prediction-project
```

This GitHub folder should include the source code, data outputs, charts,
supporting documentation, and PowerPoint slides.

## Final Results Summary

| Rank | Model | RMSE | MAE | R2 | MAPE |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | ANN | 27.37 | 20.08 | 0.866 | 4.50% |
| 2 | Linear Regression | 42.12 | 39.01 | 0.682 | 8.86% |
| 3 | XGBoost | 64.74 | 56.07 | 0.248 | 11.81% |
| 4 | ARIMA | 88.16 | 64.01 | -0.394 | 12.56% |
| 5 | LSTM | 94.96 | 77.32 | -0.617 | 16.38% |

Key finding: ANN was the best-performing model in this experiment. Linear
Regression was the strongest simple and interpretable baseline.

## Presentation

The final PowerPoint presentation is saved in:

```text
presentation/Week11_Activity_1_1_Airline_Prediction.pptx
```

The 10-minute presentation script is saved in:

```text
presentation_script_10_minutes.md
```
