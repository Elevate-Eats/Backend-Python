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
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def add_footer(canvas, doc):
    # Get the width and height of the document
    page_width = doc.pagesize[0]
    page_height = doc.pagesize[1]

    # Footer Text Setup
    current_date = datetime.now().strftime("%Y-%m-%d")
    footer_text = f"Page {doc.page} - Printed on {current_date}"
    
    # Footer Text Settings
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(page_width / 2.0, 15, footer_text)
    canvas.restoreState()
    
def add_header(canvas, doc):
    # Load and set up the app logo
    base_path = os.path.dirname(__file__)
    app_logo_path = os.path.join(base_path, '../../static/image/Logo.png')
    app_logo = Image(app_logo_path, width=100, height=50)
    
    # Define styles inside the function
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = styles['Heading2']
    subheader_style = styles['BodyText']

    # Modify the existing styles or create new ones
    title_style.fontName = 'Montserrat-Bold'
    title_style.fontSize = 18
    title_style.leading = 22
    title_style.alignment = TA_CENTER
    header_style.fontName = 'Montserrat-Bold'
    header_style.fontSize = 12
    header_style.leading = 14
    header_style.alignment = TA_CENTER
    subheader_style.fontName = 'Montserrat-Regular'
    subheader_style.fontSize = 11
    subheader_style.leading = 13
    subheader_style.alignment = TA_RIGHT

    # Prepare the header text using Paragraphs
    title_text = Paragraph(f"{doc.companyName.upper()}", title_style)
    header_text = Paragraph(f"Daily Report<br/>{doc.branchName} Branch", header_style)
    subheader_text = Paragraph(f"Date: {doc.date.strftime('%Y-%m-%d')}", subheader_style)

    # Construct a table for layout
    header_data = [[app_logo, title_text, header_text, subheader_text]]
    header_table = Table(header_data, colWidths=[100, None, None, None], rowHeights=50)
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (-1, -1), 10)
    ]))

    header_table.wrap(doc.width, doc.topMargin)
    header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - 50)

def add_header_and_footer(canvas, doc):
    add_header(canvas, doc)
    add_footer(canvas, doc)

class PDFGenerator:
  @staticmethod
  async def createPdf(data):
    try:
      # Basic data extraction
      companyName = data["companyName"]
      branchName = data["branchName"]
      dailyResults = data["dailyanalytics"][0] if data["dailyanalytics"] else None
      expensesData = data["expensesRecord"]
      hourlyData = data["hourlyanalytics"]
      if not hourlyData:
          raise ValueError("No hourly analytics data available")
      
      # Mapping 24-hour format to "8a" or "14p" format
      hourLabels = {str(i): f"{i}a" if i < 12 else f"{i-12}p" if i != 12 else "12p" for i in range(8, 22)}
      # Initialize all transaction counts to 0 for the range 8 AM to 9 PM
      TransactionsByHour = {hourLabels[str(i)]: 0 for i in range(8, 22)}

      # Fill the data received
      for entry in hourlyData:
          hour = entry['datetime'].strftime('%H')  # Convert datetime to hour string
          formatted_hour = hourLabels.get(hour)
          if formatted_hour:
              TransactionsByHour[formatted_hour] += entry['numberoftransactions']
      hoursOfTransactions = list(TransactionsByHour.keys())
      transactionsByHour = list(TransactionsByHour.values())
      logging.info(f'${hoursOfTransactions}, {transactionsByHour}')
      if not dailyResults:
        raise ValueError("No daily analytics data available")
      date = dailyResults['date'].isoformat() if isinstance(dailyResults['date'], datetime) else dailyResults['date']
      grossRevenue = dailyResults['totalsales']
      totalExpenses = sum(expenses['total'] if expenses['total'] is not None else 0 for expenses in expensesData)
      totalRevenue = grossRevenue - totalExpenses
      totalTransactions = dailyResults['numberoftransactions']
      totalItemsSold = dailyResults['numberofitemssold']
      itemsData = data["dailyItemsAnalytics"]
      transactionsData = data["transactionData"]
      font_paths = [
        'app/utilities/fonts/Montserrat-Regular.ttf',
        'app/utilities/fonts/Montserrat-Bold.ttf',
        'app/utilities/fonts/Montserrat-SemiBold.ttf'
      ]
      custom_color = HexColor("#103164")
      # Check if all font files exist
      for font_path in font_paths:
        if not os.path.isfile(font_path):
          logging.error(f"Font file not found: {font_path}")
        else:
          logging.info(f"Font file exists: {font_path}")
      # Document setup
      buffer = io.BytesIO()
      styles = getSampleStyleSheet()
      
      # Custom styles
      pdfmetrics.registerFont(TTFont('Montserrat-Regular', 'app/utilities/fonts/Montserrat-Regular.ttf'))
      pdfmetrics.registerFont(TTFont('Montserrat-Bold', 'app/utilities/fonts/Montserrat-Bold.ttf'))
      pdfmetrics.registerFont(TTFont('Montserrat-SemiBold', 'app/utilities/fonts/Montserrat-SemiBold.ttf'))
      
      
      doc = SimpleDocTemplate(
          buffer,
          pagesize=letter,
          rightMargin=36,
          leftMargin=36,
          topMargin=72,
          bottomMargin=36,
      )
      doc.companyName = companyName
      doc.branchName = branchName
      doc.date = datetime.now()
      doc.title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Montserrat-Bold', fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=12)
      doc.header_style = ParagraphStyle('Header', parent=styles['Normal'], fontName='Montserrat-SemiBold', fontSize=12, leading=14, alignment=TA_CENTER, spaceAfter=12)
      doc.subheader_style = ParagraphStyle('Subheader', parent=styles['Normal'], fontName='Montserrat-Regular', fontSize=11, leading=13, alignment=TA_RIGHT)
      elements = []
      title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Montserrat-Bold', fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=12)
      header_style = ParagraphStyle('Header', parent=styles['Normal'], fontName='Montserrat-SemiBold', fontSize=12, leading=14, alignment=TA_CENTER, spaceAfter=12)
      subheader_style = ParagraphStyle('Subheader', parent=styles['Normal'], fontName='Montserrat-Regular', fontSize=11, leading=13, alignment=TA_RIGHT)
      # Title and Headers
      elements.append(Spacer(1, 24))
      elements.append(Paragraph(f"Daily Summary", header_style))
      # Summary Table
      summary_data = [["Total Transactions", "Total Items Sold"], [totalTransactions, totalItemsSold]]
      summary_table = Table(summary_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch], hAlign='CENTER',)
      summary_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), custom_color),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
          ('FONTSIZE', (0, 0), (-1, -1), 11),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.white),
          ('GRID', (0, 0), (-1, -1), 1, colors.black),
      ]))
      elements.append(summary_table)
      elements.append(Spacer(1, 24))
      # Revenue Table
      summary_data = [["Expenses (IDR)", "Gross Revenue (IDR)", "Net Revenue (IDR)"], [f"{totalExpenses:,.0f}", f"{grossRevenue:,.0f}", f"{totalRevenue:,.0f}"]]
      summary_table = Table(summary_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch], hAlign='CENTER',)
      summary_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), custom_color),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
          ('FONTSIZE', (0, 0), (-1, -1), 11),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.white),
          ('GRID', (0, 0), (-1, -1), 1, colors.black),
      ]))
      elements.append(summary_table)
      elements.append(Spacer(1, 24))
      
      elements.append(Paragraph(f"Hourly Performance Chart", header_style))

      #Hourly chart
      hours = hoursOfTransactions
      values = transactionsByHour
      # Hourly Performance Chart
      fig, ax = plt.subplots()
      ax.bar(hoursOfTransactions, transactionsByHour, color='#72B2C9')
      ax.set_ylabel('Number of Transactions')
      ax.set_xticks(hoursOfTransactions)
      ax.set_xticklabels(hoursOfTransactions, rotation=45)

      chart_buffer = io.BytesIO()
      plt.tight_layout()
      plt.savefig(chart_buffer, format='png', dpi=150)
      plt.close(fig)
      chart_buffer.seek(0)

      chart_image = Image(chart_buffer, width=6*inch, height=3*inch)  # Adjusted size as needed
      elements.append(chart_image)
      elements.append(PageBreak())
      elements.append(Paragraph(f"Item Performance Chart", header_style))
      
      # Chart
      chart_buffer = io.BytesIO()
      fig, ax = plt.subplots(figsize=(6, 0.5 * len(itemsData)))
      ax.barh([item['name'] for item in itemsData], [item['sold'] for item in itemsData], color='#72B2C9')
      plt.xlabel('Quantity Sold', fontsize=9)
      plt.xticks(fontsize=8)
      plt.yticks(fontsize=8)
      plt.tight_layout()
      plt.savefig(chart_buffer, format='png', dpi=150)
      plt.close(fig)
      chart_buffer.seek(0)

      chart_image = Image(chart_buffer, width=6*inch, height=0.5*inch * len(itemsData))
      elements.append(chart_image)
      elements.append(PageBreak())

      elements.append(Spacer(1, 24))

      # Detailed items table with improved style
      total_sold = sum(item['sold'] for item in itemsData)
      total_revenue = sum(item['revenue'] for item in itemsData)

      # Append total row to the item_data_for_table
      item_data_for_table = [
          ['Name', 'Sold', 'Revenue']
      ] + [
          [item['name'], item['sold'], f"{item['revenue']:,.2f}"] for item in itemsData
      ]
      # Append the total row
      item_data_for_table.append(['Total', total_sold, f"{total_revenue:,.2f}"])
      bottom_row_index = len(item_data_for_table) - 1  # Index of the last row
      # Update table creation and styling as needed
      detailed_item_table = Table(
          item_data_for_table,
          colWidths=[3*inch, 1.5*inch, 1.5*inch],
          hAlign='CENTER',
          repeatRows=1  

      )
      detailed_item_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), custom_color),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
          ('FONTNAME', (0, 1), (-1, -1), 'Montserrat-SemiBold'),
          ('FONTSIZE', (0, 0), (-1, -1), 10),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.white),
          ('BOX', (0, 0), (-1, -1), 1, colors.black),
          ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
          ('BACKGROUND', (0, bottom_row_index), (-1, bottom_row_index), colors.lightblue),
      ]))
      elements.append(Paragraph(f"Daily Items Table", header_style))
      elements.append(detailed_item_table)
      elements.append(PageBreak())
      elements.append(Spacer(1, 24))
      transactions_data_for_table = [
          ['Time', 'Customer Name', 'Payment Method', 'Discount', 'Total'],  # Column headers
      ] + [
          [
              transaction['time'],
              transaction['customerName'][:10],  # Slice to the first 10 characters
              'Cash' if transaction['paymentMethod'] == '0'  else 'Transfer',
              f"{transaction['discount']:,.2f}" if transaction['discount'] is not None else '0.00',
              f"{transaction['total']:,.2f}"
          ] for transaction in transactionsData
      ]
      # Calculate the totals for Discount and Total columns, treating None as 0
      total_discount = sum(transaction['discount'] if transaction['discount'] is not None else 0 for transaction in transactionsData)
      total_amount = sum(transaction['total'] if transaction['total'] is not None else 0 for transaction in transactionsData)

      # Add the total row to the transactions data table
      transactions_data_for_table.append([
          "Total", "", "", f"{total_discount:,.2f}", f"{total_amount:,.2f}"
      ])

      # Create the table
      detailed_transaction_table = Table(
          transactions_data_for_table,
          colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1.5*inch],
          hAlign='CENTER',
          repeatRows=1  
      )

      # Calculate the index for the bottom row which is always the last one
      bottom_row_index = len(transactions_data_for_table) - 1  # Index of the last row

      # Define the table style, including custom styling for the total row
      detailed_transaction_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), custom_color),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
          ('FONTNAME', (0, 1), (-1, -1), 'Montserrat-SemiBold'),
          ('FONTSIZE', (0, 0), (-1, -1), 10),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.white),
          ('BOX', (0, 0), (-1, -1), 1, colors.black),
          ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
          # Custom background color for the total row
          ('BACKGROUND', (0, bottom_row_index), (-1, bottom_row_index), colors.lightblue),
      ]))
      elements.append(Paragraph(f"Daily Transactions Table", header_style))
      elements.append(detailed_transaction_table)
      elements.append(PageBreak())
      elements.append(Spacer(1, 24))
      expenses_data_for_table = [
        ['Name', 'Count','Price', 'Total'],  # Adding column headers here
        ] + [
        [expense['name'], expense['count'], f"{expense['total']:,.2f}", f"{expense['total']:,.2f}"] for expense in expensesData
        ]
      expenses_data_for_table.append([
          "Total", "", "", f"{totalExpenses:,.2f}"
      ])
      detailed_expenses_table = Table(
          expenses_data_for_table,
          colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch],
          hAlign='CENTER',
          repeatRows=1  # Repeat headers on each new page
      )

      # Calculate the index for the bottom row, which is always the last one
      bottom_row_index = len(expenses_data_for_table) - 1

      # Apply the style, mirroring the style used for the transaction table
      detailed_expenses_table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), custom_color),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
          ('FONTNAME', (0, 1), (-1, -1), 'Montserrat-SemiBold'),
          ('FONTSIZE', (0, 0), (-1, -1), 10),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.white),
          ('BOX', (0, 0), (-1, -1), 1, colors.black),
          ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
          # Custom background color for the total row
          ('BACKGROUND', (0, bottom_row_index), (-1, bottom_row_index), colors.lightblue),
      ]))

      elements.append(Paragraph(f"Daily Expenses Table", header_style))
      elements.append(detailed_expenses_table)
      # Build the PDF and return the binary data
      doc.build(elements, onFirstPage=add_header_and_footer, onLaterPages=add_header_and_footer)
      pdf_value = buffer.getvalue()
      buffer.close()
      return pdf_value
    except Exception as e:
      raise ValueError(f"Failed to Generate PDF: {e}")
