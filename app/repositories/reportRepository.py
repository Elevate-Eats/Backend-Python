class ReportRepository:
  async def getDailyReportData(self, branchId:int):
    return {"branchId": branchId, "totalSales": 12345, "transactions": 123}