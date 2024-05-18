from datetime import datetime, timedelta  # Imports the datetime and timedelta classes from the datetime module.
import pandas as pd  # Imports the pandas library under the alias 'pd'.
import asyncpg  # Imports the asyncpg library for asynchronous PostgreSQL database operations.
# @title Imports
import requests
from bs4 import BeautifulSoup
import numpy as np
from hijridate import Gregorian

final_df = pd.DataFrame({
    'Tanggal': pd.date_range(start='2024-05-01', end='2024-05-31', freq='D'),
    'Shift': [1, 2] * 15 + [1],
    'Jumlah_Transaksi': np.random.randint(100, 200, 31),
    'Prev_Week_Transactions': np.random.randint(50, 150, 31),
    'Holiday': [False] * 31,
    'Weekend': [False] * 31,
    'DayType': ['Non-Holiday+Non-Weekend'] * 31
})

holiday_df = pd.read_csv('./static/holiday/holidays_2024.csv', parse_dates=['Tanggal'])
# Initialize the 'Holiday' and 'Weekend' columns
final_df['Holiday'] = False
final_df['Weekend'] = False
# Set 'Holiday' where the date is in the holiday DataFrame
final_df.loc[final_df['Tanggal'].isin(holiday_df['Tanggal']), 'Holiday'] = True
# Set 'Weekend' for Saturdays and Sundays
final_df.loc[final_df['Tanggal'].dt.dayofweek.isin([5, 6]), 'Weekend'] = True
# Define DayType based on Holiday and Weekend columns
conditions = [
    (final_df['Holiday'] & final_df['Weekend']),
    (final_df['Holiday'] & ~final_df['Weekend']),
    (~final_df['Holiday'] & final_df['Weekend']),
    (~final_df['Holiday'] & ~final_df['Weekend'])
]
choices = ['Holiday+Weekend', 'Holiday', 'Weekend', 'Non-Holiday+Non-Weekend']
final_df['DayType'] = np.select(conditions, choices)
final_df['Months'] = final_df['Tanggal'].dt.month  # Extracts the month from the date
final_df['Days'] = final_df['Tanggal'].dt.dayofweek  # Extracts the day of the week, where Monday is 0 and Sunday is 6\
final_df['Ramadhan'] = final_df['Tanggal'].apply(lambda x: Gregorian(x.year, x.month, x.day).to_hijri().month_name() == "Ramadhan")

print(final_df)

