import csv
import io
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from ..models.expense import Expense


def generate_csv_export(expenses: List[Expense]) -> str:
    """Generate CSV text output for a list of expenses."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["ID", "Date", "Category", "Description", "Amount (INR)", "Payment Method", "Notes"])
    
    for exp in expenses:
        category_name = exp.category.name if exp.category else "Unassigned"
        writer.writerow([
            exp.id,
            exp.date.strftime("%Y-%m-%d"),
            category_name,
            exp.description,
            f"{exp.amount:.2f}",
            exp.payment_method or "-",
            exp.notes or "",
        ])
    
    return output.getvalue()


def generate_pdf_export(expenses: List[Expense]) -> bytes:
    """Generate PDF binary stream output for a list of expenses using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=18,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
    )
    header_cell_style = ParagraphStyle(
        "HeaderCell",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    elements = []
    
    # Title & Header
    elements.append(Paragraph("ExpenseFlow — Expense Report", title_style))
    elements.append(Paragraph(f"Generated Total Records: {len(expenses)}", subtitle_style))
    
    # Table Data
    table_data = [[
        Paragraph("Date", header_cell_style),
        Paragraph("Category", header_cell_style),
        Paragraph("Description", header_cell_style),
        Paragraph("Amount (₹)", header_cell_style),
        Paragraph("Payment Method", header_cell_style),
    ]]
    
    total_amount = 0.0
    for exp in expenses:
        amt = float(exp.amount)
        total_amount += amt
        cat_name = exp.category.name if exp.category else "Unassigned"
        table_data.append([
            Paragraph(exp.date.strftime("%Y-%m-%d"), cell_style),
            Paragraph(cat_name, cell_style),
            Paragraph(exp.description, cell_style),
            Paragraph(f"₹{amt:,.2f}", cell_style),
            Paragraph(exp.payment_method or "-", cell_style),
        ])
        
    # Summary Row
    table_data.append([
        Paragraph("<b>Total</b>", cell_style),
        Paragraph("", cell_style),
        Paragraph("", cell_style),
        Paragraph(f"<b>₹{total_amount:,.2f}</b>", cell_style),
        Paragraph("", cell_style),
    ])

    # Table Layout & Styling
    col_widths = [80, 100, 180, 90, 90]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#E2E8F0")),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#0F172A")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F8FAFC")),
    ])
    
    # Alternate row colors
    for i in range(1, len(expenses) + 1):
        if i % 2 == 0:
            t_style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFC"))
            
    table.setStyle(t_style)
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
