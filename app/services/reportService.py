from app.repositories.reportRepository import ReportRepository
from app.utilities.pdfGenerator import PDFGenerator
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportService:
  def __init__(self):
    self.reportRepository = ReportRepository()
    
  async def generateDailyReport(self, branchId: int, date: str):
    reportData = await self.reportRepository.getDailyReportData(branchId, date)
    pdfFile = await PDFGenerator.createPdf(reportData)
    return pdfFile
  