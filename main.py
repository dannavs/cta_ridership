#
#
# CTA RIDERSHIP DATA ANALYSIS by Dan Navarro (2/28/2026)
#
# Using Chicago Transit Authority ridership data file CTA_-_Ridership_-_Daily_Boarding_Totals_20260226.xlsx
# Downloaded from https://data.cityofchicago.org/Transportation/CTA-Ridership-Daily-Boarding-Totals/6iiy-9s97
# 
# 
#
import pandas as pd
import os
import logging
import matplotlib.pyplot as plt
from matplotlib.widgets import Button



logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("run_log.txt", mode='w'), # Creates/Overwrites the log
        logging.StreamHandler()                        # Keeps output on screen
    ]
)

file = "CTA_-_Ridership_-_Daily_Boarding_Totals_20260226.xlsx"

# Check if file exists before processing
if not os.path.exists(file):
    logging.info(f"Error: File named '{file}' not found in the current directory")
    logging.info("Please download the file from https://data.cityofchicago.org/Transportation/CTA-Ridership-Daily-Boarding-Totals/6iiy-9s97 and place it in the same directory as this script.")
    exit()

# Read in Excel file using pandas and show the shape, first five rows, and data types
df = pd.read_excel(file, header=0)
logging.info(f"\nDataset shape: {df.shape[0]} rows x {df.shape[1]} columns")

logging.info(df.head())
logging.info(f"\nData types in dataframe:\n{df.dtypes}")

# Check for missing values in each column
missing_values = df.isnull().sum()
logging.info(f"\nMissing values in each column:\n{missing_values}")

# Define date_column and get count of date and confirm count of unique dates in the 'service_date' column
date_column = 'service_date'
date_count = df[date_column].count()
unique_dates = df[date_column].nunique()
logging.info(f"\nTotal Dates: {date_count} vs Unique Dates: {unique_dates}")
if date_count == unique_dates:
    logging.info("All dates are unique.")
else:
    logging.info("There are duplicate dates in the dataset.")

# Descriptive statistics for ridership columns
logging.info("\nDescriptive Statistics for Ridership Data:")
logging.info(df[['bus', 'rail_boardings', 'total_rides']].describe())

# CTA Ridership min/max over all dates
logging.info(f"Bus ridership range: {df['bus'].min()} to {df['bus'].max()}")
logging.info(f"El train ridership range: {df['rail_boardings'].min()} to {df['rail_boardings'].max()}")
logging.info(f"Total CTA rides range: {df['total_rides'].min()} to {df['total_rides'].max()}")

# Check for negative values
negative_check = (df[['bus', 'rail_boardings', 'total_rides']] < 0).any()
if negative_check.any():
    logging.info(f"***** Warning: Negative values found in: {negative_check[negative_check].index.tolist()}")
else:
    logging.info(f"+ No negative values detected in ridership columns")

# Ensure that total_rides equals bus + rail_boardings for each row
df['calculated_total'] = df['bus'] + df['rail_boardings']
discrepancies = df[df['total_rides'] != df['calculated_total']]
if not discrepancies.empty:
    logging.info(f"***** Warning: Discrepancies found in total_rides calculation for {len(discrepancies)} rows")
else:
    logging.info("+ All total_rides values correctly match the sum of bus and rail_boardings.")

# Ensure that the date column is in datetime format
logging.info(f"Converting '{date_column}' to datetime format.")
df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

# Create a new column for the day of the week, represent in numbers (Monday - 0 through Sunday - 6)
df['day_of_week'] = df[date_column].dt.dayofweek
logging.info("\nCreated a day_of_week column to represent the day numerically (Monday - 0 through Sunday - 6):")
logging.info(df[['service_date', 'day_of_week']].head())

# Convert each day_type to a numerical value (Weekday - 0, Saturday - 1, Sunday/Holiday - 2)
day_type_mapping = {'W': 0, 'A': 1, 'U': 2}
df['day_type_num'] = df['day_type'].map(day_type_mapping)
logging.info("\nRepresent the type of day numerically (Weekday - 0, Saturday - 1, Sunday/Holiday - 2):")
logging.info(df[['day_type', 'day_of_week', 'day_type_num']].head(14))

# Extract month and year variables from the date column
df['month'] = df[date_column].dt.month
df['year'] = df[date_column].dt.year

# Get some initial statistics grouped by the day of the week, week vs. weekend and holiday, and by month
logging.info("\nAverage overall ridership by day of the week (Monday - 0 through Sunday - 6):")
logging.info(df.groupby('day_of_week')[['bus', 'rail_boardings', 'total_rides']].mean())
logging.info("\nAverage overall ridership by day type (Weekday - 0, Saturday - 1, Sunday/Holiday - 2):")
logging.info(df.groupby('day_type_num')[['bus', 'rail_boardings', 'total_rides']].mean())
logging.info("\nAverage overall ridership by month:")
logging.info(df.groupby('month')[['bus', 'rail_boardings', 'total_rides']].mean())

# Calculate the top 10 busiest days for the three most recent calendar years and compare them with the day of the week and day type
recent_years = df['year'].unique()[-3:]
for year in recent_years:
    logging.info(f"\nTop 10 busiest days in {year}:")
    top_days = df[df['year'] == year].nlargest(10, 'total_rides')
    logging.info(top_days[['service_date', 'total_rides', 'day_of_week', 'day_type_num']])

# Calculate the aggregate monthly statistics for the 12 months of the 2024 calendar year and compare them with the day of the week and day type
the_year = 2024
logging.info(f"\nAggregate monthly statistics for {the_year}:")
monthly_stats = df[df['year'] == the_year].groupby('month')[['bus', 'rail_boardings', 'total_rides']].agg(['mean', 'sum'])
logging.info(monthly_stats)

# Create ridership tiers based on total_rides (Low: 0-500,000, Medium: 500,001-1,000,000, High: 1,000,001+)
def ridership_tier(total):
    if total <= 500000:
        return 'Low'
    elif total <= 1000000:
        return 'Medium'
    else:
        return 'High'
df['ridership_tier'] = df['total_rides'].apply(ridership_tier)

# logging.info a sample month showing ridership tiers for February 2024
logging.info("\nSample of February 2024 Ridership Tiers:")
month_year = (df['year'] == 2024) & (df['month'] == 2)
logging.info(df[['service_date', 'total_rides', 'ridership_tier']][month_year].head(20))

# Calculate monthly summary statistics
monthly_summary = df.groupby('month').agg({'total_rides': ['mean', 'sum', 'min', 'max']})
monthly_summary.columns = ['mean_total_rides', 'sum_total_rides', 'min_total_rides', 'max_total_rides']
monthly_summary = monthly_summary.reset_index()
logging.info("\nMonthly Summary Statistics:")
logging.info(monthly_summary)
df_merged = df.merge(monthly_summary, on='month', how='left')
logging.info(f"Original Columns: {df.columns.tolist()}")
logging.info(f"Merged Columns: {df_merged.columns.tolist()}")
logging.info("\nSample of merged dataframe:")
logging.info(df_merged.head(10))

# Generate a ridership report dataframe for each month
monthly_reports = []
for year in df['year'].unique():
    for month in df['month'].unique():
        month_year_data = df[(df['year'] == year) & (df['month'] == month)]
        if not month_year_data.empty:
            total_rides_month = int(month_year_data['total_rides'].sum())
            average_daily_rides = month_year_data['total_rides'].mean()
            days_in_month = int(month_year_data.shape[0])
            monthly_reports.append({
                'year': year,
                'month': month,
                'total_rides_month': total_rides_month,
                'average_daily_rides': average_daily_rides,
                'days_in_month': days_in_month
            })
monthly_report_df = pd.DataFrame(monthly_reports)

# Create monthly ridership data for plotting
monthly_ridership = df.groupby(['year', 'month'])[['bus', 'rail_boardings', 'total_rides']].sum().reset_index()
monthly_ridership['year_month'] = monthly_ridership['year'].astype(str) + '-' + monthly_ridership['month'].astype(str).str.zfill(2)

# Interactive dashboard with year selector
unique_years = sorted(monthly_ridership['year'].unique())
current_year = 2020

def update_plot(year):
    ax.clear()
    year_data = monthly_ridership[monthly_ridership['year'] == year].sort_values('month')
    x = range(len(year_data))
    bar_width = 0.25
    ax.bar([i - bar_width for i in x], year_data['total_rides'], width=bar_width, color='black', label='Total Ridership')
    ax.bar(x, year_data['bus'], width=bar_width, color='darkred', label='Bus Ridership')
    ax.bar([i + bar_width for i in x], year_data['rail_boardings'], width=bar_width, color='darkblue', label='Train Ridership')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(m)}" for m in year_data['month']], rotation=45, ha='right')
    ax.set_ylabel('Total Ridership')
    ax.set_title(f'Monthly CTA Ridership for {year}: Total, Bus, and Train')
    ax.legend()
    plt.draw()

fig, ax = plt.subplots(figsize=(14, 7))
update_plot(current_year)

# Add navigation buttons
axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
bprev = Button(axprev, 'Previous')
bnext = Button(axnext, 'Next')

def prev(event):
    global current_year
    idx = unique_years.index(current_year)
    if idx > 0:
        current_year = unique_years[idx - 1]
        update_plot(current_year)

def next(event):
    global current_year
    idx = unique_years.index(current_year)
    if idx < len(unique_years) - 1:
        current_year = unique_years[idx + 1]
        update_plot(current_year)

bprev.on_clicked(prev)
bnext.on_clicked(next)

plt.tight_layout()
plt.show()
year_2020 = df[df['year'] == 2020]
year_2021 = df[df['year'] == 2021]
year_2022 = df[df['year'] == 2022]
year_2023 = df[df['year'] == 2023]
year_2024 = df[df['year'] == 2024]

# Concatenate the five individual years
post_covid_data = pd.DataFrame() # Create an empty dataframe to hold the concatenated data
post_covid_data = pd.concat([post_covid_data, year_2020, year_2021, year_2022, year_2023, year_2024], ignore_index=True)
logging.info(post_covid_data.head())

# Look for anomalies in the data creating a rolling 7-day average
# Flag any days when the total number of rides is more than 2 standard deviations from the rolling average
df['rolling_avg'] = df['total_rides'].rolling(window=7).mean()
df['rolling_std'] = df['total_rides'].rolling(window=7).std()
df['anomaly'] = (df['total_rides'] > df['rolling_avg'] + 2 * df['rolling_std']) | (df['total_rides'] < df['rolling_avg'] - 2 * df['rolling_std'])
anomalies = df[df['anomaly']]
logging.info(f"\nAnomalies detected: {len(anomalies)}")
logging.info(anomalies[['service_date', 'total_rides', 'rolling_avg', 'rolling_std', 'anomaly']])

logging.info(f"Final types of all columns in the dataframe:\n{df.dtypes}")

# Export the cleaned and processed dataframe to a new CSV file
output_file = "CTA_Ridership_Analysis_Output.csv"
df.to_csv(output_file, index=False)
logging.info(f"\nCleaned and processed data exported to '{output_file}'")

# Export the monthly summary report as a CSV file
report_file = "CTA_Monthly_Summary_Report.csv"
monthly_report_df.to_csv(report_file, index=False)
logging.info(f"Monthly aggregate report exported to '{report_file}'")



