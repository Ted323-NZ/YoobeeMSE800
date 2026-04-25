# Week 2 Activity 2 - 3 Minute Presentation Script

## Slide 1 - Title

Hello everyone. This presentation summarises my Week 2 Activity 2 work using the Beijing Multi-Site Air Quality dataset. I continued from Activity 1 and focused on Tasks 2 to 6, turning the analysis into a short insight story. The dataset contains hourly records from 12 Beijing monitoring stations, with 420,768 rows in total.

## Slide 2 - Dataset and Scope

The original download contains an outer ZIP file and a nested ZIP with 12 CSV files, one for each station. Because the Blackboard wording for Tasks 2 to 6 was not available locally, I used a standard statistical analysis workflow. I treated the tasks as data quality checking, descriptive statistics, temporal trend analysis, correlation analysis, and station comparison.

## Slide 3 - Data Quality and Summary Statistics

My first step was to check data quality. The column with the highest missing rate was CO at 4.92 percent, which means the dataset has some missing pollutant values but is still usable for analysis. The overall averages also show that pollution levels are substantial. For example, the mean PM2.5 value is 79.79 and the mean PM10 value is 104.60. The means are generally higher than the medians, which suggests that pollution spikes pull the averages upward.

## Slide 4 - Monthly Trends

The monthly pattern shows the clearest story. PM2.5 is highest in December, where the average reaches 104.58. In contrast, O3 reaches its highest average in July at 95.09. This suggests that particulate pollution is more serious in the colder season, while ozone becomes more serious in the warmer season. The two pollutants do not peak at the same time, so they should not be interpreted as one single problem.

## Slide 5 - Hourly Patterns and Correlation

The hourly chart shows that PM2.5 peaks late in the evening at 22:00, while O3 peaks in the afternoon at 16:00. This daily contrast matches the seasonal story, because O3 is linked to sunlight while PM2.5 often builds up under different conditions. In the correlation matrix, PM2.5 has its strongest positive relationship with PM10 at 0.88, and its strongest negative relationship with wind speed at minus 0.27. This suggests that particulate pollution rises together and tends to reduce when air movement is stronger.

## Slide 6 - Station Comparison and Conclusion

The station comparison shows that Dongsi has the highest average PM2.5 at 86.19, while Dingling has the lowest at 65.99. So, the final story from this dataset is that winter particulate pollution is the biggest PM2.5 issue, summer ozone is the biggest O3 issue, and pollution is not equally distributed across stations. All code, figures, tables, and slides are included in the GitHub folder shown on this slide. Thank you.
