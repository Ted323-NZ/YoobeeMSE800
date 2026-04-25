# Week 2 Activity 2 - Statistical Analysis Summary

## Assumed Task 2-6 Scope

- Task 2: missing-value and data quality review
- Task 3: descriptive statistics for the main pollutant and weather variables
- Task 4: monthly and hourly trend analysis
- Task 5: correlation analysis across pollutants and weather variables
- Task 6: station comparison and insight summary

## Dataset Overview

- Total rows analysed: 420,768
- Total columns: 18
- Monitoring stations: 12

## Key Insights

- Highest missing-rate column: **CO** (4.92%)
- Highest average PM2.5 station: **Dongsi** (86.19)
- Lowest average PM2.5 station: **Dingling** (65.99)
- Peak PM2.5 month: **Dec** (104.58)
- Peak O3 month: **Jul** (95.09)
- Peak PM2.5 hour: **22** (88.89)
- Peak O3 hour: **16** (102.31)
- Strongest positive PM2.5 relationship: **PM10** (0.88)
- Strongest negative PM2.5 relationship: **WSPM** (-0.27)

## Descriptive Statistics Snapshot

| Column | Mean | Median | Std | Min | Max | Missing % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PM2.5 | 79.79 | 55.00 | 80.82 | 2.00 | 999.00 | 2.08 |
| PM10 | 104.60 | 82.00 | 91.77 | 2.00 | 999.00 | 1.53 |
| SO2 | 15.83 | 7.00 | 21.65 | 0.29 | 500.00 | 2.14 |
| NO2 | 50.64 | 43.00 | 35.13 | 1.03 | 290.00 | 2.88 |
| CO | 1230.77 | 900.00 | 1160.18 | 100.00 | 10000.00 | 4.92 |
| O3 | 57.37 | 45.00 | 56.66 | 0.21 | 1071.00 | 3.16 |

## Top 5 Stations by Average PM2.5

| Rank | Station | Avg PM2.5 |
| --- | --- | ---: |
| 1 | Dongsi | 86.19 |
| 2 | Wanshouxigong | 85.02 |
| 3 | Nongzhanguan | 84.84 |
| 4 | Gucheng | 83.85 |
| 5 | Wanliu | 83.37 |

## Generated Figures

- `figures/missing_rate_by_column.png`
- `figures/monthly_pm25_o3.png`
- `figures/hourly_pm25_o3.png`
- `figures/station_pm25_ranking.png`
- `figures/correlation_heatmap.png`