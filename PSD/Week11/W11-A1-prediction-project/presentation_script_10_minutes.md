# 10-Minute Presentation Script

## Slide 1 - Title

Introduce the project as a Data Analytics prediction pipeline for monthly airline passenger demand. State that the goal is to compare Linear Regression, XGBoost, ANN, LSTM, and ARIMA using the same train/test split and evaluation metrics.

Estimated time: 45 seconds.

## Slide 2 - Presentation Flow

Briefly explain the structure: dataset, preprocessing, EDA, methodology, model results, and recommendations. Mention that the focus is on evidence from visualizations and metrics, not only code.

Estimated time: 40 seconds.

## Slide 3 - Dataset Understanding and Preparation

Explain that the dataset has 144 monthly records from 1949 to 1960. The target is passenger count. Preprocessing included datetime parsing, chronological sorting, missing-value checks, and feature engineering. Point out the passenger distribution and lag correlation charts.

Estimated time: 1 minute.

## Slide 4 - Trend and Train/Test Split

Discuss the upward trend in passengers over time. Explain why the last 24 months were used as the test set: this is forecasting, so a chronological split is required. Highlight that the test set contains high-demand months, making extrapolation challenging.

Estimated time: 1 minute.

## Slide 5 - Seasonality

Explain the repeated mid-year seasonal peaks. Connect this to the feature engineering choices: month, quarter, sine/cosine encoding, lag-12, and rolling summaries. State that seasonality is one of the most important patterns in the dataset.

Estimated time: 1 minute.

## Slide 6 - Methodology

Walk through the pipeline: prepare data, engineer features, train models, evaluate metrics. Define RMSE, MAE, R2, and MAPE in simple terms. Mention that lower RMSE/MAE/MAPE is better, while higher R2 is better.

Estimated time: 1 minute.

## Slide 7 - Model Comparison Results

Present the ranking. ANN is best with RMSE 27.37 and MAPE 4.50%. Linear Regression is second and remains a strong interpretable baseline. XGBoost, ARIMA, and LSTM perform worse in this experiment.

Estimated time: 1 minute 15 seconds.

## Slide 8 - Actual vs Predicted

Use the actual-vs-predicted chart to show that the better models follow the seasonal rises and falls. Explain that errors increase near peak months, which shows the difficulty of forecasting future high-demand periods.

Estimated time: 1 minute.

## Slide 9 - Strengths and Limitations

Compare model behavior. ANN performs best but is less interpretable. Linear Regression is easier to explain. XGBoost struggles with extrapolation. ARIMA and LSTM are appropriate model families but underfit in this short dataset and simple setup.

Estimated time: 1 minute 10 seconds.

## Slide 10 - Key Findings and Recommendations

Summarize the main conclusion: ANN is the best model for this experiment, with about 4.50% MAPE. Recommend keeping Linear Regression as a benchmark and testing SARIMA/SARIMAX in future work for stronger seasonal time-series modeling.

Estimated time: 1 minute.

## Slide 11 - GitHub Submission and Readiness

Close by listing the submitted deliverables: source code, README, processed data, output tables, visualizations, supporting documentation, and PowerPoint slides. State the GitHub project link after pushing.

Estimated time: 40 seconds.

## Short Q&A Preparation

Possible question: Why did ANN perform best?
Answer: It captured nonlinear interactions between trend, seasonality, lag features, and rolling averages after scaling.

Possible question: Why did XGBoost not win?
Answer: Tree-based models can struggle when the test period has values above the training range, because they do not naturally extrapolate trend.

Possible question: What would improve ARIMA?
Answer: A seasonal ARIMA or SARIMAX model would better reflect the yearly passenger pattern.

Possible question: Is the result reliable?
Answer: It is reliable for this classroom experiment, but more robust validation would use rolling-origin evaluation and more historical data.
