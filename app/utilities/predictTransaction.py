import pandas as pd
import numpy as np
from xgboost import XGBRegressor
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class prediction:
  @staticmethod
  async def predictTransaction(datafixForecastHelper1:pd.DataFrame, datafixForecastHelper2:pd.DataFrame, datafixForecastShift1:pd.DataFrame, datafixForecastShift2:pd.DataFrame):
    # datafix = pd.read_csv('/content/drive/MyDrive/ML Balibul/Dataset Qasir/Solo/datafix_2020-2024-sol_with_prev_week.csv')
    logging.info(f"after repo: {datafixForecastHelper2}")
    logging.info(f"after repo: {datafixForecastShift1}")
    datafixForecastHelper1.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)
    datafixForecastHelper2.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)
    datafixForecastShift1.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)
    datafixForecastShift2.rename(columns={"Jumlah_Transaksi":"Jumlah Transaksi"},inplace=True)
    logging.info(f"after rename: {datafixForecastHelper2}")
    logging.info(f"after rename: {datafixForecastShift1}")    
    model1Path: str = "./model/XGBRegressor-Forecast-city_code=sol-forecast_year=2024-forecast_month=5-param_col=['Months','Days','Prev_Week_Transactions','Holiday','Weekend','Ramadhan']-shift=1.json"
    model2Path: str = "./model/XGBRegressor-Forecast-city_code=sol-forecast_year=2024-forecast_month=5-param_col=['Months','Days','Prev_Week_Transactions','Holiday','Weekend','Ramadhan']-shift=2.json"

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
      pred_res_shift1 = model1.predict(datafixForecastShift1[idx:idx + 1][['Months','Days','Prev_Week_Transactions','Holiday','Weekend','Ramadhan']])

      # Set Result to Forecast Data
      datafixForecastShift1.loc[idx, 'Jumlah Transaksi'] = round(pred_res_shift1.flatten()[0])
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
      pred_res_shift2 = model2.predict(datafixForecastShift2[idx:idx + 1][['Months','Days','Prev_Week_Transactions','Holiday','Weekend','Ramadhan']])

      # Set Result to Forecast Data
      datafixForecastShift2.loc[idx, 'Jumlah Transaksi'] = round(pred_res_shift2.flatten()[0])
    logging.info(f"RETURNNYAAAA: {datafixForecastShift1}")
    logging.info(f"RETURNNYAAAA: {datafixForecastShift2}")

    datafixForecast = pd.concat(
        [
            datafixForecastShift1,
            datafixForecastShift2
        ],
        ignore_index=True
    ).reset_index(drop=True)
    datafixForecast['Tanggal'] = datafixForecast['Tanggal'].dt.strftime('%Y-%m-%d')
    logging.info(f"RETURNNYAAAA: {datafixForecast}")
    return datafixForecast.to_dict(orient='records')
    
      
    
    

