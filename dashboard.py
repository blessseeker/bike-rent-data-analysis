import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

time_ranges = {
    '05-13': (5, 13),
    '06-14': (6, 14),
    '07-15': (7, 15),
    '08-16': (8, 16),
    '09-17': (9, 17),
    '10-18': (10, 18),
    '11-19': (11, 19),
    '12-20': (12, 20),
    '13-21': (13, 21),
    '14-22': (14, 22)
}
def create_opening_wd_hours_df(df):
    working_day_df = df[df['workingday'] == 1]
    time_range_wd_dfs = create_time_range_dfs(working_day_df)
    return time_range_wd_dfs

def create_opening_hd_hours_df(df):
    holiday_df = df[df['holiday'] == 1]
    time_range_hd_dfs = create_time_range_dfs(holiday_df)
    return time_range_hd_dfs

def create_time_range_dfs(df):
    opening_hours_df = df[(df['hr'] >= 5) & (df['hr'] <= 22)]
    time_range_dfs = {}
    for range_name, (start_hour, end_hour) in time_ranges.items():
        range_df = opening_hours_df[
            (opening_hours_df['hr'] >= start_hour) & (opening_hours_df['hr'] <= end_hour)]
        if not range_df.empty:  # Check if the DataFrame is not empty
            time_range_dfs[range_name] = range_df
    return time_range_dfs

def create_casual_monthly_bookings(df):
    casual_monthly_bookings = create_monthly_bookings(df, 'casual')
    return casual_monthly_bookings

def create_registered_monthly_bookings(df):
    registered_monthly_bookings = create_monthly_bookings(df, 'registered')
    return registered_monthly_bookings

def create_monthly_bookings(df, type):
    recent_bookings = df[(df[type] > 0)].copy()
    recent_bookings['month'] = recent_bookings['dteday'].dt.strftime('%Y-%m')
    monthly_bookings = recent_bookings.groupby('month')[type].sum().reset_index()
    return monthly_bookings

bike_rents_per_hour_df = pd.read_csv("hour.csv")

datetime_columns = ["dteday"]
bike_rents_per_hour_df.sort_values(by="dteday", inplace=True)
bike_rents_per_hour_df.reset_index(inplace=True)

for column in datetime_columns:
    bike_rents_per_hour_df[column] = pd.to_datetime(bike_rents_per_hour_df[column])

min_date = bike_rents_per_hour_df["dteday"].min()
max_date = bike_rents_per_hour_df["dteday"].max()

with st.sidebar:

    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = bike_rents_per_hour_df[(bike_rents_per_hour_df["dteday"] >= str(start_date)) &
                (bike_rents_per_hour_df["dteday"] <= str(end_date))]

opening_wd_hours_df = create_opening_wd_hours_df(main_df)
opening_hd_hours_df = create_opening_hd_hours_df(main_df)

st.subheader("Best Opening Hours")
wd_time_ranges = []
wd_order_counts = []

for range_name, range_df in opening_wd_hours_df.items():
    wd_time_ranges.append(range_name)
    wd_order_counts.append(range_df['cnt'].sum())

wd_data_df = pd.DataFrame({'Time Range': wd_time_ranges, 'Order Counts': wd_order_counts})

hd_time_ranges = []
hd_order_counts = []

for range_name, range_df in opening_hd_hours_df.items():
    hd_time_ranges.append(range_name)
    hd_order_counts.append(range_df['cnt'].sum())

hd_data_df = pd.DataFrame({'Time Range': hd_time_ranges, 'Order Counts': hd_order_counts})

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

wd_colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3",
             "#D3D3D3"]

sns.barplot(x='Order Counts', y='Time Range', data=wd_data_df, palette=wd_colors, ax=ax[0], hue="Time Range")
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Total Order Counts for Each Time Range (Working Days)", loc="center", fontsize=15)
ax[0].tick_params(axis='y', labelsize=12)

hd_colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3", "#D3D3D3",
             "#D3D3D3"]

sns.barplot(x='Order Counts', y='Time Range', data=hd_data_df, palette=hd_colors, ax=ax[1], hue="Time Range")
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Total Order Counts for Each Time Range (Holidays)", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

st.pyplot(fig)

st.subheader("Casual vs Registered Orders in Last 5 Months")

casual_monthly_bookings = create_casual_monthly_bookings(main_df)
registered_monthly_bookings = create_registered_monthly_bookings(main_df)

fig2 = plt.figure(figsize=(10, 6))
plt.plot(casual_monthly_bookings['month'], casual_monthly_bookings['casual'], label='Casual Orders', marker='o')
plt.plot(registered_monthly_bookings['month'], registered_monthly_bookings['registered'], label='Registered Orders', marker='o')
plt.xlabel('Month')
plt.ylabel('Number of Orders')
plt.title('Monthly Casual vs Registered Orders 5 Bulan Terakhir')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.legend()
plt.grid(True)  # Add grid
plt.tight_layout()  # Adjust layout to prevent clipping of labels

st.pyplot(fig2)
st.caption('Copyright (c) Dicoding 2024')