import os
from datetime import datetime
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
      naive_datetime = datetime.fromisoformat(date[:-1])  # Removing the 'Z' assuming date is in UTC
      # logging.info(f"Fetching data for Branch ID: {branchId} on Date: {date}")
      timezone = pytz.timezone("Asia/Jakarta")  # Example: Use your database's timezone
      aware_datetime = naive_datetime.replace(tzinfo=pytz.utc).astimezone(timezone)
      date_only = aware_datetime.date()  
      companyQuery = """
          SELECT c.name FROM branches b
          JOIN companies c ON b.companyid = c.id
          WHERE b.id = $1
          """
      companyName = await self.connection.fetchval(companyQuery, branchId)
      # logging.info(f"Company Name: {companyName}")

      branchNameQuery = "SELECT name from branches where id = $1"
      branchName = await self.connection.fetchval(branchNameQuery, branchId)
      # logging.info(f"Branch Name: {branchName}")

      dailyAnalyticsQuery = "SELECT * FROM dailyanalytics WHERE branchid = $1 AND date = $2"
      dailyResults = await self.connection.fetch(dailyAnalyticsQuery, branchId, date_only)
      # logging.info(f"Daily Analytics Results: {dailyResults}")

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

      await self.close()
      return {
        "companyName": companyName,
        "branchName": branchName,
        "dailyanalytics": dailyResults,
        "dailyItemsAnalytics": itemResults,
      }
    except Exception as e:
      # logging.error(f"Failed to fetch data: {e}")
      raise
