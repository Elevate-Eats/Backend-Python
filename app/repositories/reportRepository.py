import os
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
import asyncpg
import logging
import pytz
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportRepository:
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

  async def getDailyReportData(self, branchId:int, date:str):
    try:
      await self.connect()
      naive_datetime = datetime.fromisoformat(date[:-1])
      logging.info(f"Fetching data for Branch ID: {branchId} on Date: {date}")
      timezone = pytz.timezone("Asia/Jakarta") 
      aware_datetime = naive_datetime.replace(tzinfo=pytz.utc).astimezone(timezone)
      date_only = aware_datetime.date()  
      #date for summary
      # Create UTC datetime for 17:00:00 UTC
      startOfDay = datetime.combine(aware_datetime.date(), time(0, 0, 0), tzinfo=timezone)
      endOfDay = startOfDay + timedelta(days=1)
      startOfDay2 = datetime.combine(aware_datetime.date(), time(0, 0, 0), tzinfo=pytz.utc)
      endOfDay2 = startOfDay2 + timedelta(days=1)
      companyQuery = """
          SELECT c.name FROM branches b
          JOIN companies c ON b.companyid = c.id
          WHERE b.id = $1
          """
      logging.info(f"Fetching data for Branch ID: {branchId} on Date: {endOfDay}")
      companyName = await self.connection.fetchval(companyQuery, branchId)
      # logging.info(f"Company Name: {companyName}")

      branchNameQuery = "SELECT name from branches where id = $1"
      branchName = await self.connection.fetchval(branchNameQuery, branchId)
      # logging.info(f"Branch Name: {branchName}")
      #fetch hourly
      hourlyAnalyticsQuery = "SELECT * FROM hourlyanalytics WHERE branchid = $1 AND datetime >= $2 AND datetime <= $3"
      hourlyResults = await self.connection.fetch(hourlyAnalyticsQuery, branchId, startOfDay2, endOfDay2)
      logging.info(f"Hourly: {hourlyResults}")
      #fetch daily
      dailyAnalyticsQuery = """
          SELECT * FROM dailyanalytics 
          WHERE branchid = $1 AND date >= $2 AND date <= $3
      """      
      dailyResults = await self.connection.fetch(dailyAnalyticsQuery, branchId, startOfDay, endOfDay)
      logging.info(f"Daily Analytics Results: {dailyResults}")
      
      # Fetch Daily Expenses
      dailyExpensesQuery = "Select * FROM expenses where branchid = $1 AND date = $2"
      expensesResults = await self.connection.fetch(dailyExpensesQuery, branchId, date_only)
      #logging.info(f"Daily Expenses Results: {expensesResults}")
      
      itemAnalyticsQuery= """
          SELECT m.name, dai.menuid, dai.numberofitemssold as sold, dai.totalsales as revenue
          FROM dailyitemanalytics dai
          JOIN menus m ON dai.menuid = m.id
          WHERE dai.branchid = $1 AND dai.date = $2
          ORDER BY dai.numberofitemssold DESC
          """
      itemResultsRaw = await self.connection.fetch(itemAnalyticsQuery, branchId, date_only)
      # logging.info(f"Fetched {len(itemResultsRaw)} items from dailyitemanalytics")

      itemResults = [{
          'name': result['name'],
          'sold': result['sold'],
          'revenue': float(result['revenue'])
      } for result in itemResultsRaw]
      
      transactionDataQuery ="""
        SELECT
            to_char(transactiondate, 'HH12:MI PM') as time,
            totalprice,
            paymentmethod,
            customername,
            discount
        FROM transactions
        WHERE branchid = $1 AND date(transactiondate) = $2
        ORDER BY transactiondate
      """
      transactionDataRaw = await self.connection.fetch(transactionDataQuery, branchId, date_only)
      transactionData = [{
        'time': result['time'],
        'total': float(result['totalprice']),
        'paymentMethod': result['paymentmethod'],
        'customerName': result['customername'],
        'discount': float(result['discount']) if result['discount'] else None
      } for result in transactionDataRaw]
      await self.close()
      return {
        "companyName": companyName,
        "branchName": branchName,
        "hourlyanalytics": hourlyResults,
        "dailyanalytics": dailyResults,
        "expensesRecord": expensesResults,
        "dailyItemsAnalytics": itemResults,
        "transactionData": transactionData,
      }
    except Exception as e:
      # logging.error(f"Failed to fetch data: {e}")
      raise
