from app.repositories.reportRepository import ReportRepository
from app.utilities.pdfGenerator import PDFGenerator

class ReportService:
  def __init__(self):
    self.reportRepository = ReportRepository()
    
  async def generateDailyReport(self, branchId: int):
    reportData = await self.reportRepository.getDailyReportData(branchId)
    pdfFile = await PDFGenerator.createPdf(reportData)
    return pdfFile
