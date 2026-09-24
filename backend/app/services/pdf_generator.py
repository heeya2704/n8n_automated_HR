import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_offer_letter_pdf(
    candidate_name: str,
    candidate_email: str,
    job_title: str,
    output_directory: str = "offer-letters",
    salary: str = "$95,000 / annum",
    joining_date: str = None
) -> str:
    """
    Generates a professional PDF offer letter for selected candidates.
    Returns the absolute filepath to the created PDF.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    filename = f"Offer_Letter_{candidate_name.replace(' ', '_')}_{int(datetime.now().timestamp())}.pdf"
    filepath = os.path.join(output_directory, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    if not joining_date:
        # Default 2 weeks from today
        future_date = datetime.now()
        joining_date = future_date.strftime("%B %d, %Y")

    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'CompanyHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )
    
    subheader_style = ParagraphStyle(
        'CompanySubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )

    title_style = ParagraphStyle(
        'DocumentTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=25
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#334155'),
        spaceAfter=14
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    elements = []

    # Header
    elements.append(Paragraph("TECHCORP SOLUTIONS", header_style))
    elements.append(Paragraph("100 Innovation Way, Suite 400 • Tech Valley, CA 94016 • hr@techcorp.com", subheader_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=20))

    # Date
    today_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"<b>Date:</b> {today_str}", body_style))
    elements.append(Paragraph(f"<b>To:</b> {candidate_name} ({candidate_email})", body_style))
    elements.append(Spacer(1, 15))

    # Title
    elements.append(Paragraph("OFFER OF EMPLOYMENT", title_style))

    # Body
    p1 = f"Dear <b>{candidate_name}</b>,<br/><br/>" \
         f"We are delighted to extend an offer of employment for the position of " \
         f"<b>{job_title}</b> at <b>TechCorp Solutions</b>. " \
         f"Your performance in our online assessment and technical evaluation demonstrated your exceptional skills and qualifications."
    elements.append(Paragraph(p1, body_style))

    # Offer Details Table
    details_data = [
        [Paragraph("<b>Position</b>", bold_body), Paragraph(job_title, body_style)],
        [Paragraph("<b>Compensation</b>", bold_body), Paragraph(salary, body_style)],
        [Paragraph("<b>Joining Date</b>", bold_body), Paragraph(joining_date, body_style)],
        [Paragraph("<b>Employment Type</b>", bold_body), Paragraph("Full-Time", body_style)],
        [Paragraph("<b>Work Location</b>", bold_body), Paragraph("Hybrid / Remote", body_style)],
    ]

    t = Table(details_data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    p2 = "Please review this offer letter. To accept this offer, please sign and return a copy of this document " \
         "within 5 business days."
    elements.append(Paragraph(p2, body_style))
    elements.append(Spacer(1, 25))

    # Signature section
    sig_data = [
        [Paragraph("<b>Sincerely,</b>", body_style), Paragraph("<b>Candidate Acceptance,</b>", body_style)],
        [Spacer(1, 30), Spacer(1, 30)],
        [Paragraph("___________________________<br/><b>HR Director</b><br/>TechCorp Solutions", body_style),
         Paragraph(f"___________________________<br/><b>{candidate_name}</b><br/>Date: _____________", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    return os.path.abspath(filepath)
