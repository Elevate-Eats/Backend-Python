import io
import logging
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

class PDFGenerator:
  @staticmethod
  async def createPdf(data):
    logging.info("Received data for PDF generation: %s", data)
    try:
      companyName = data["companyName"]
      branchName = data["branchName"]
      dailyResults = data["dailyanalytics"][0] if data["dailyanalytics"] else None
      if not dailyResults:
        logging.error("No daily analytics data available")
        raise ValueError("No daily analytics data available")

      # Correcting date handling
      date = dailyResults['date'].isoformat() if isinstance(dailyResults['date'], datetime) else dailyResults['date']
      totalRevenue = dailyResults['totalsales']
      totalTransactions = dailyResults['numberoftransactions']
      totalItemsSold = dailyResults['numberofitemssold']
      
      itemsData = data["dailyItemsAnalytics"]  # Unpacking items data

      buffer = io.BytesIO()
      doc = SimpleDocTemplate(buffer, pagesize=letter)
      
      elements = []
      styles = getSampleStyleSheet()
      centered_style = ParagraphStyle(name="centered", parent=styles["Normal"], alignment=TA_CENTER)
      
      elements.append(Paragraph(companyName, centered_style))
      elements.append(Paragraph(f"Daily Report - {branchName}", centered_style))
      elements.append(Paragraph(f"Date: {date}", centered_style))
      elements.append(Spacer(1, 12))
      
      table_data = [
        ["Total Revenue (IDR)", "Total Transactions", "Total Items Sold"],
        [f"{totalRevenue:.2f}", f"{totalTransactions}", f"{totalItemsSold}"]
      ]
      t = Table(table_data)
      t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
      ]))
      elements.append(t)
      elements.append(Spacer(1, 12))
      
      # Creating the bar chart
      plt.figure(figsize=(4, 3))
      plt.bar([item['name'] for item in itemsData], [item['sold'] for item in itemsData], color='blue')
      plt.xlabel('Items')
      plt.ylabel('Quantity Sold')
      plt.title('Sales Per Item Today')
      plt.tight_layout()

      # Save the plot to a BytesIO object
      chart_buffer = io.BytesIO()
      plt.savefig(chart_buffer, format='png')
      chart_buffer.seek(0)
      plt.close()

      # Load image from buffer
      chart_image = Image(chart_buffer)
      elements.append(Paragraph("Sales Per Item Today", centered_style))
      elements.append(Spacer(1, 12))
      elements.append(chart_image)

      # Creating the table for daily items analytics
      item_data_for_table = [[item['name'], item['sold'], item['revenue']] for item in itemsData]
      item_table = Table(item_data_for_table, colWidths=[200, 100, 100])
      item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
      ]))
      elements.append(item_table)

      doc.build(elements)
      pdf_value = buffer.getvalue()
      buffer.close()
      
      return pdf_value

    except Exception as e:
        logging.error(f"Failed to Generate PDF: {e}")
        raise
