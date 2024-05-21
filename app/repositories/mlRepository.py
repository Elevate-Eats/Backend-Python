import os
from datetime import datetime, timedelta
import asyncio
import asyncpg
import pandas as pd
from dotenv import load_dotenv
from hijridate import Gregorian
import numpy as np
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MLRepository:
  def __init__(self):
    self.db_user = os.getenv("PG_USER")
    self.db_password = os.getenv("PG_PASSWORD") 
    self.db_host = os.getenv("PG_HOST")
    self.db_port = os.getenv("PG_PORT")
    self.db_database = os.getenv("PG_DATABASE")

  async def connect(self):
    try:
      self.connection = await asyncpg.connect(
          user=self.db_user,
          password=self.db_password,
          host=self.db_host,
          port=self.db_port,
          database=self.db_database
      )
      # logging.info("Connected to PostgreSQL")
    except Exception as e:
      # logging.error(f"Failed to connect to PostgreSQL: {e}")
      raise

  async def close(self):
    await self.connection.close()

  async def fetchData(self, branchId: int, startDate: str, endDate: str):
    await self.connect()
    dateFormat = '%Y-%m-%d'
    queryDate = datetime.strptime(startDate, dateFormat)
    queryDate = queryDate - timedelta(days=1)
    endDateObj = datetime.strptime(endDate, dateFormat)
    twoWeeksBeforeStartDate = queryDate - timedelta(days=14)
    neededData = queryDate - timedelta(days=7)
    fetchQuery = """
        SELECT
          date(datetime) as workday,
          CASE
            WHEN extract(hour from datetime) BETWEEN 8 AND 13 THEN 1
            WHEN extract(hour from datetime) BETWEEN 14 AND 22 THEN 2
            ELSE 0
          END as shift,
          sum(numberoftransactions) as jumlah_transaksi,
          sum(totalsales) as total
        FROM
          hourlyanalytics 
        WHERE
          date(datetime) BETWEEN $1 AND $2 AND
          branchid = $3 AND
          extract(hour from datetime) BETWEEN 8 AND 22
        GROUP BY
          workday, shift
        ORDER BY
          workday, shift;
    """
    transactionDataRaw = await self.connection.fetch(fetchQuery, twoWeeksBeforeStartDate, queryDate, branchId)
    print(transactionDataRaw)
    await self.close()

    df_raw = pd.DataFrame(transactionDataRaw, columns=['Tanggal', 'Shift', 'Jumlah_Transaksi', 'Total'])
    df_raw['Tanggal'] = pd.to_datetime(df_raw['Tanggal'])
    df_raw['Prev_Week_Transactions'] = 0
    desired_order = ['Tanggal', 'Shift', 'Jumlah_Transaksi', 'Prev_Week_Transactions', 'Total']
    df_raw = df_raw[desired_order]
    date_range_for_calculation = pd.date_range(start=twoWeeksBeforeStartDate + timedelta(days=7), end=queryDate, freq='D')
    for date in date_range_for_calculation:
        for shift in [1, 2]:
            current_date = date.strftime(dateFormat)
            previous_week_start = (date - timedelta(days=7)).strftime(dateFormat)
            filtered_transactions = df_raw[(df_raw['Tanggal'] >= previous_week_start) & (df_raw['Tanggal'] < current_date) & (df_raw['Shift'] == shift)]
            df_raw.loc[(df_raw['Tanggal'] == current_date) & (df_raw['Shift'] == shift), 'Prev_Week_Transactions'] = filtered_transactions['Jumlah_Transaksi'].sum()
    # logging.info(f"DFRaw: {df_raw}")

    final_df = pd.DataFrame()
    for date in pd.date_range(start=neededData, end=endDateObj, freq='D'):
        for shift in [1, 2]:
            if date <= queryDate:
                row = df_raw[(df_raw['Tanggal'] == date.strftime(dateFormat)) & (df_raw['Shift'] == shift)]
                final_df = pd.concat([final_df, row], ignore_index=True)
            else:
                new_row = pd.DataFrame({
                    'Tanggal': [date.date()],
                    'Shift': [shift],
                    'Jumlah_Transaksi': [0],
                    'Prev_Week_Transactions': [0],
                    'Total': [0],
                })
                final_df = pd.concat([final_df, new_row], ignore_index=True)

    holiday_df = pd.read_csv('./static/holiday/holidays_2024.csv', parse_dates=['Tanggal'])
    final_df['Tanggal'] = pd.to_datetime(final_df['Tanggal'])

    final_df['Holiday'] = final_df['Tanggal'].isin(holiday_df['Tanggal'])
    final_df['Weekend'] = final_df['Tanggal'].dt.dayofweek.isin([5, 6])
    conditions = [
        (final_df['Holiday'] & final_df['Weekend']),
        (final_df['Holiday'] & ~final_df['Weekend']),
        (~final_df['Holiday'] & final_df['Weekend']),
        (~final_df['Holiday'] & ~final_df['Weekend'])
    ]
    choices = ['Holiday+Weekend', 'Holiday', 'Weekend', 'Non-Holiday+Non-Weekend']
    final_df['DayType'] = np.select(conditions, choices)
    final_df['Months'] = final_df['Tanggal'].dt.month
    final_df['Days'] = final_df['Tanggal'].dt.dayofweek
    final_df['Ramadhan'] = final_df['Tanggal'].apply(lambda x: Gregorian(x.year, x.month, x.day).to_hijri().month_name() == "Ramadhan")
    df_helper = final_df[final_df['Jumlah_Transaksi'] > 0]
    df_predict = final_df[final_df['Jumlah_Transaksi'] == 0]
    df_helper1 = df_helper[df_helper['Shift']==1].reset_index(drop=True)
    df_helper2 = df_helper[df_helper['Shift']==2].reset_index(drop=True)
    df_predict1 = df_predict[df_predict['Shift']==1].reset_index(drop=True)
    df_predict2 = df_predict[df_predict['Shift']==2].reset_index(drop=True)
    # logging.info(f"DFDF: {df_helper1}")
    # logging.info(f"DFDF: {df_helper2}")
    # logging.info(f"DFDF: {df_predict1}")
    # logging.info(f"DFDF: {df_predict2}")

    return df_helper1, df_helper2, df_predict1, df_predict2
  
# If this script is run directly (not imported), execute the following:
if __name__ == "__main__":
    repo = MLRepository()
    # Setup to run the fetchData asynchronously
    async def main():
        df1,df2,df3,df4 = await repo.fetchData(11, '2024-04-24', '2024-04-30')
        print(df1)
        print(df2)
        print(df3)
        print(df4)

    asyncio.run(main())
# # df =  mlRepo.fetchData(6, '2020-10-05','2020-10-10')
# # print(df)