import pandas as pd
import numpy as np
from xgboost import XGBRegressor
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class prediction:
  @staticmethod
  async def predictTransaction(datafixForecastHelper1:pd.DataFrame, datafixForecastHelper2:pd.DataFrame, datafixForecastShift1:pd.DataFrame, datafixForecastShift2:pd.DataFrame):
    # datafix = pd.read_csv('/content/drive/MyDrive/ML Balibul/Dataset Qasir/Solo/datafix_2020-2024-sol_with_prev_week.csv')

    datafixForecastHelper1.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)
    datafixForecastHelper2.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)
    datafixForecastShift1.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)
    datafixForecastShift2.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)

    model1Path: str = "./model/sol-shift1.json"
    model2Path: str = "./model/sol-shift2.json"
    param = ["Months", "Days", "Prev_Week_Transactions", "Holiday", "Weekend", "Ramadhan"]
    pred = ["Jumlah Transaksi", "Total"]
    model1 = XGBRegressor()
    model2 = XGBRegressor()

    model1.load_model(model1Path)
    model2.load_model(model2Path)

    for idx in range(len(datafixForecastShift1)):
      # Combine Data of Helper and Forecast
      dataPastForecast = pd.concat(
          [
              datafixForecastHelper1,
              datafixForecastShift1
          ],
          ignore_index=True
      ).reset_index(drop=True)

      # Get Current Date of Predict
      pred_cur_date = datafixForecastShift1.loc[idx, 'Tanggal']
      start_prev_week_date = pred_cur_date - pd.Timedelta(days=7)
      end_prev_week_date = pred_cur_date - pd.Timedelta(days=1)

      # Calculat Prev Week Tranc for Current Predict
      total_tranc = dataPastForecast.query(
          '''
          Tanggal >= @start_prev_week_date and \
          Tanggal <= @end_prev_week_date
          '''
      )['Jumlah Transaksi'].sum()

      # Set Result of Prev Week Tranc
      datafixForecastShift1.loc[idx, 'Prev_Week_Transactions'] = total_tranc
      # Predict Jumlah Transaksi
      jmlTrPred, totalPred = model1.predict(
          datafixForecastShift1[idx : idx + 1][param]
      ).flatten()
      datafixForecastShift1.loc[idx, "Jumlah Transaksi"] = round(jmlTrPred)
      datafixForecastShift1.loc[idx, "Total"] = round(totalPred)

    for idx in range(len(datafixForecastShift2)):
      # Combine Data of Helper and Forecast
      dataPastForecast = pd.concat(
          [
              datafixForecastHelper2,
              datafixForecastShift2
          ],
          ignore_index=True
      ).reset_index(drop=True)

      # Get Current Date of Predict
      pred_cur_date = datafixForecastShift2.loc[idx, 'Tanggal']
      start_prev_week_date = pred_cur_date - pd.Timedelta(days=7)
      end_prev_week_date = pred_cur_date - pd.Timedelta(days=1)
      # logging.info(idx)
      # Calculat Prev Week Tranc for Current Predict
      total_tranc = dataPastForecast.query(
          '''
          Tanggal >= @start_prev_week_date and \
          Tanggal <= @end_prev_week_date
          '''
      )['Jumlah Transaksi'].sum()

      # Set Result of Prev Week Tranc
      datafixForecastShift2.loc[idx, 'Prev_Week_Transactions'] = total_tranc

      # Predict Jumlah Transaksi
      jmlTrPred, totalPred = model1.predict(
          datafixForecastShift2[idx : idx + 1][param]
      ).flatten()
      datafixForecastShift2.loc[idx, "Jumlah Transaksi"] = round(jmlTrPred)
      datafixForecastShift2.loc[idx, "Total"] = round(totalPred)
    datafixForecast = pd.concat(
        [
            datafixForecastShift1,
            datafixForecastShift2
        ],
        ignore_index=True
    ).reset_index(drop=True)
    datafixForecast['Tanggal'] = datafixForecast['Tanggal'].dt.strftime('%Y-%m-%d')
    return datafixForecast.to_dict(orient='records')
    
      
    
    

