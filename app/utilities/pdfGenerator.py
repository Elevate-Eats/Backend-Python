import io
import os
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFGenerator:
  @staticmethod
  async def createPdf(data):
    try:
      # Basic data extraction
      companyName = data["companyName"]
      branchName = data["branchName"]
      dailyResults = data["dailyanalytics"][0] if data["dailyanalytics"] else None
      if not dailyResults:
        raise ValueError("No daily analytics data available")
      
      date = dailyResults['date'].isoformat() if isinstance(dailyResults['date'], datetime) else dailyResults['date']
      totalRevenue = dailyResults['totalsales']
      totalTransactions = dailyResults['numberoftransactions']
      totalItemsSold = dailyResults['numberofitemssold']
      itemsData = data["dailyItemsAnalytics"]
      font_paths = [
        'app/utilities/fonts/Montserrat-Regular.ttf',
        'app/utilities/fonts/Montserrat-Bold.ttf',
        'app/utilities/fonts/Montserrat-SemiBold.ttf'
      ]

      # Check if all font files exist
      for font_path in font_paths:
        if not os.path.isfile(font_path):
          logging.error(f"Font file not found: {font_path}")
        else:
          logging.info(f"Font file exists: {font_path}")
      # Document setup
      buffer = io.BytesIO()
      doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
      elements = []

      # Custom styles
      pdfmetrics.registerFont(TTFont('Montserrat-Regular', 'app/utilities/fonts/Montserrat-Regular.ttf'))
      pdfmetrics.registerFont(TTFont('Montserrat-Bold', 'app/utilities/fonts/Montserrat-Bold.ttf'))
      pdfmetrics.registerFont(TTFont('Montserrat-SemiBold', 'app/utilities/fonts/Montserrat-SemiBold.ttf'))
      # Custom styles
      styles = getSampleStyleSheet()
      title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Montserrat-Bold', fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=12)
      header_style = ParagraphStyle('Header', parent=styles['Normal'], fontName='Montserrat-SemiBold', fontSize=12, leading=14, alignment=TA_CENTER, spaceAfter=12)
      subheader_style = ParagraphStyle('Subheader', parent=styles['Normal'], fontName='Montserrat-Regular', fontSize=11, leading=13, alignment=TA_RIGHT)

      # Title and Headers
      elements.append(Paragraph(companyName.upper(), title_style))
      elements.append(Paragraph(f"Daily Report - {branchName}", header_style))
      elements.append(Paragraph(f"Date: {date}", subheader_style))

      # Summary Table
      summary_data = [["Total Revenue (IDR)", "Total Transactions", "Total Items Sold"], [f"{totalRevenue:,.2f}", totalTransactions, totalItemsSold]]
      summary_table = Table(summary_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch], hAlign='CENTER')
      summary_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
          ('FONTSIZE', (0, 0), (-1, -1), 11),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
          ('GRID', (0, 0), (-1, -1), 1, colors.black),
      ]))
      elements.append(Spacer(1, 24))
      elements.append(summary_table)
      elements.append(Spacer(1, 24))

      # Chart
      chart_buffer = io.BytesIO()
      fig, ax = plt.subplots(figsize=(6, 0.5 * len(itemsData)))
      ax.barh([item['name'] for item in itemsData], [item['sold'] for item in itemsData], color='skyblue')
      plt.xlabel('Quantity Sold', fontsize=9)
      plt.xticks(fontsize=8)
      plt.yticks(fontsize=8)
      ax.set_title('Sales Per Item Today', fontsize=10)
      plt.tight_layout()
      plt.savefig(chart_buffer, format='png', dpi=150)
      plt.close(fig)
      chart_buffer.seek(0)

      chart_image = Image(chart_buffer, width=6*inch, height=0.5*inch * len(itemsData))
      elements.append(chart_image)
      elements.append(PageBreak())

      # Repeat headers on new page for consistency
      elements.append(Paragraph(companyName.upper(), title_style))
      elements.append(Paragraph(f"Daily Report - {branchName}", header_style))
      elements.append(Paragraph(f"Date: {date}", subheader_style))
      elements.append(Spacer(1, 12))

      # Detailed items table with improved style
      item_data_for_table = [
        ['Name', 'Sold', 'Revenue'],  # Adding column headers here
        ] + [
        [item['name'], item['sold'], f"{item['revenue']:,.2f}"] for item in itemsData
        ]
      detailed_item_table = Table(
          item_data_for_table,
          colWidths=[3*inch, 1.5*inch, 1.5*inch],
          hAlign='CENTER'
      )
      detailed_item_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
          ('FONTNAME', (0, 1), (-1, -1), 'Montserrat-SemiBold'),
          ('FONTSIZE', (0, 0), (-1, -1), 10),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
          ('BOX', (0, 0), (-1, -1), 1, colors.black),
          ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
      ]))
      elements.append(detailed_item_table)

      # Build the PDF and return the binary data
      doc.build(elements)
      pdf_value = buffer.getvalue()
      buffer.close()
      return pdf_value
    except Exception as e:
      raise ValueError(f"Failed to Generate PDF: {e}")
