from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFGenerator:
  @staticmethod
  async def createPdf(data):
    c = canvas.Canvas("report.pdf", pagesize = letter)
    c.drawString(100, 750, f"Branch ID: {data['branchId']}")
    c.drawString(100, 730, f"Total Sales: {data['totalSales']}")
    c.drawString(100, 710, f"Transactions: {data['transactions']}")
    c.save
    
    return "report.pdf"