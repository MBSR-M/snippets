import os
from datetime import datetime, timedelta
import pandas as pd

# Constants for paths and date range
FILE_PATH = r"C:\Users\MustafaMubashir\OneDrive - Cyan Connode Ltd\Documents\output11.csv"
OUTPUT_DIR = r"C:\Users\MustafaMubashir\OneDrive - Cyan Connode Ltd\Documents\lastgaspjan2025"
START_DAY = 739617
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 1, 31)

# Get file size in MB and print
file_size_mb = os.path.getsize(FILE_PATH) / (1024 * 1024)
print(f"File size: {file_size_mb:.2f} MB")

# Define column names and read CSV into DataFrame
column_names = ['id', 'day_local', 'server_time', 'alarm_time', 'msn', 'node_id', 'alarm_status']
df = pd.read_csv(FILE_PATH, header=None, names=column_names)

# Map 'day_local' to 'YYYY-MM-DD' format using a dictionary comprehension
date_mapping = {
    day: (START_DATE + timedelta(days=day - START_DAY)).strftime('%Y-%m-%d')
    for day in range(START_DAY, START_DAY + 31)
}
df['day_local'] = df['day_local'].map(date_mapping)

# Validate and convert 'server_time' and 'alarm_time' to datetime
df[['server_time', 'alarm_time']] = df[['server_time', 'alarm_time']].apply(
    lambda col: pd.to_datetime(col, errors='coerce', utc=True)
)

# Drop rows with invalid datetime values
df.dropna(subset=['server_time', 'alarm_time'], inplace=True)

# Convert to Asia/Kolkata timezone
df[['server_time', 'alarm_time']] = df[['server_time', 'alarm_time']].apply(
    lambda col: col.dt.tz_convert('Asia/Kolkata')
)

# Remove timezone information (make them timezone-unaware)
df[['server_time', 'alarm_time']] = df[['server_time', 'alarm_time']].apply(
    lambda col: col.dt.tz_localize(None)
)

# Filter data for 'Last Gasp' alarms
filtered_data = df[df['alarm_status'] == 'Last Gasp']

# Columns to include in the final report
final_columns = ['msn', 'node_id', 'alarm_time', 'server_time', 'alarm_status']

# Save filtered data for each day in January into separate Excel files
for current_date in pd.date_range(START_DATE, END_DATE):
    date_str = current_date.strftime('%Y-%m-%d')
    formatted_file_name = f"Last-GASP-Alarm-Report-{date_str}.xlsx"

    # Filter data for the specific day
    day_data = filtered_data[filtered_data['day_local'] == date_str]

    # Select only the required columns
    day_data = day_data[final_columns]

    # Save to Excel if there is data
    if not day_data.empty:
        output_path = os.path.join(OUTPUT_DIR, formatted_file_name)
        day_data.to_excel(output_path, sheet_name="Last Gasp Data", index=False)
        print(f"File saved: {formatted_file_name}")
    else:
        print(f"No data for {date_str}, skipping file creation.")
