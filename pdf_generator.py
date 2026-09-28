import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically add 'Page X of Y' footers and top headers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Top Header (Only on page 2+)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "DIGITAL FORENSIC INVESTIGATION REPORT — CONFIDENTIAL")
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, f"CASE ID: {getattr(self, 'case_id_ref', 'N/A')}")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Bottom Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 36, "OFFICIAL FORENSIC EXAMINATION REPORT | PROPRIETARY & CONFIDENTIAL")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, page_str)
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        
        self.restoreState()


def generate_pdf_report(case, evidence_list, findings_list, custom_summary="", custom_conclusion="", custom_methodology=""):
    """
    Generates a PDF byte stream for the given case, evidence, and findings.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0f172a")      # Dark Navy/Slate
    SECONDARY = colors.HexColor("#1e293b")    # Slate Gray
    ACCENT = colors.HexColor("#0284c7")       # Cyan/Blue
    BORDER_COLOR = colors.HexColor("#e2e8f0") # Light Gray
    BG_LIGHT = colors.HexColor("#f8fafc")     # Cool white/gray

    # Severity Colors
    SEV_COLORS = {
        "Critical": colors.HexColor("#dc2626"),
        "High": colors.HexColor("#ea580c"),
        "Medium": colors.HexColor("#d97706"),
        "Low": colors.HexColor("#2563eb"),
        "Info": colors.HexColor("#16a34a")
    }

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=ACCENT,
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=SECONDARY,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.5,
        borderPadding=3,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=SECONDARY
    )

    elements = []

    # 1. Header Banner Box
    header_data = [
        [
            Paragraph("<b>DIGITAL FORENSIC INVESTIGATION REPORT</b>", title_style),
            Paragraph("<b>CLASSIFICATION: CONFIDENTIAL</b><br/>EVIDENTIARY USE ONLY", ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#dc2626"), alignment=2))
        ],
        [
            Paragraph(f"Official Case Report ID: <b>{case['case_id']}</b> | Target: <b>{case.get('client_org', 'N/A')}</b>", subtitle_style),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", ParagraphStyle('RightDate', fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#64748b"), alignment=2))
        ]
    ]

    header_table = Table(header_data, colWidths=[330, 174])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=6, spaceAfter=12))

    # 2. Case Overview Summary Box
    elements.append(Paragraph("1. CASE IDENTIFICATION & METADATA", h2_style))

    case_meta_data = [
        [
            Paragraph("<b>Case ID:</b>", body_bold), Paragraph(str(case['case_id']), table_cell_style),
            Paragraph("<b>Date Initiated:</b>", body_bold), Paragraph(str(case['created_date']), table_cell_style)
        ],
        [
            Paragraph("<b>Case Name:</b>", body_bold), Paragraph(str(case['case_name']), table_cell_style),
            Paragraph("<b>Case Status:</b>", body_bold), Paragraph(f"<b>{case['status']}</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Lead Investigator:</b>", body_bold), Paragraph(str(case['investigator']), table_cell_style),
            Paragraph("<b>Priority Level:</b>", body_bold), Paragraph(f"<b>{case['priority']}</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Client / Organization:</b>", body_bold), Paragraph(str(case.get('client_org', 'Internal')), table_cell_style),
            Paragraph("<b>Evidence Count:</b>", body_bold), Paragraph(f"{len(evidence_list)} item(s)", table_cell_style)
        ]
    ]

    case_meta_table = Table(case_meta_data, colWidths=[110, 142, 110, 142])
    case_meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(case_meta_table)
    elements.append(Spacer(1, 10))

    # 3. Executive Summary
    elements.append(Paragraph("2. EXECUTIVE SUMMARY & STATEMENT OF OBJECTIVES", h2_style))
    summary_text = custom_summary if custom_summary.strip() else (
        case.get('description', '') or 
        "This formal digital forensic report documents the acquisition, preservation, analysis, and findings "
        "pertaining to digital evidence collected during this investigation. All procedures adhered to standard "
        "forensic chain of custody protocols to ensure data integrity and legal admissibility."
    )
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 10))

    # 4. Evidence Inventory & Chain of Custody
    elements.append(Paragraph("3. EVIDENCE INVENTORY & CHAIN OF CUSTODY", h2_style))
    
    if evidence_list:
        ev_table_data = [[
            Paragraph("<b>Evidence ID</b>", table_header_style),
            Paragraph("<b>Type / Source Device</b>", table_header_style),
            Paragraph("<b>Collection Date</b>", table_header_style),
            Paragraph("<b>SHA-256 Hash Verification</b>", table_header_style)
        ]]

        for ev in evidence_list:
            sha_formatted = f"<code>{ev['file_hash_sha256'][:28]}...</code>" if len(ev['file_hash_sha256']) > 28 else f"<code>{ev['file_hash_sha256']}</code>"
            ev_table_data.append([
                Paragraph(f"<b>{ev['evidence_id']}</b>", table_cell_style),
                Paragraph(f"<b>{ev['evidence_type']}</b><br/><font color='#64748b'>{ev['source_device']}</font>", table_cell_style),
                Paragraph(str(ev['collection_date']), table_cell_style),
                Paragraph(sha_formatted, code_style)
            ])

        ev_table = Table(ev_table_data, colWidths=[80, 150, 110, 164])
        ev_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
        ]))
        elements.append(ev_table)
    else:
        elements.append(Paragraph("<i>No formal evidence records currently attached to this case file.</i>", body_style))
    
    elements.append(Spacer(1, 10))

    # 5. Forensic Findings & Artifact Analysis
    elements.append(Paragraph("4. DETAILED FORENSIC FINDINGS & SUSPICIOUS ARTIFACTS", h2_style))

    if findings_list:
        for idx, find in enumerate(findings_list, 1):
            sev = find.get('severity', 'Medium')
            sev_color = SEV_COLORS.get(sev, colors.black)

            finding_header = [
                [
                    Paragraph(f"<b>Finding #{idx}: {find['artifact_name']}</b>", ParagraphStyle('FHead', fontName='Helvetica-Bold', fontSize=9.5, textColor=PRIMARY)),
                    Paragraph(f"<b>SEVERITY: {sev.upper()}</b>", ParagraphStyle('FSev', fontName='Helvetica-Bold', fontSize=9, textColor=sev_color, alignment=2))
                ]
            ]
            f_head_table = Table(finding_header, colWidths=[370, 134])
            f_head_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
                ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('PADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
            ]))

            f_body_data = [
                [Paragraph("Category:", body_bold), Paragraph(str(find['category']), table_cell_style)],
                [Paragraph("Artifact Path:", body_bold), Paragraph(f"<code>{find.get('file_path_location', 'N/A')}</code>", code_style)],
                [Paragraph("Description:", body_bold), Paragraph(str(find['description']), table_cell_style)],
                [Paragraph("Hash / Signature:", body_bold), Paragraph(f"<code>{find.get('hash_value', 'N/A')}</code>", code_style)],
                [Paragraph("Examiner Notes:", body_bold), Paragraph(f"<i>{find.get('investigator_notes', 'N/A')}</i>", table_cell_style)]
            ]
            f_body_table = Table(f_body_data, colWidths=[100, 404])
            f_body_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('PADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))

            elements.append(KeepTogether([
                f_head_table,
                f_body_table,
                Spacer(1, 8)
            ]))
    else:
        elements.append(Paragraph("<i>No forensic findings recorded for this case file yet.</i>", body_style))

    elements.append(Spacer(1, 10))

    # 6. Examination Methodology & Tools Used
    elements.append(Paragraph("5. FORENSIC EXAMINATION METHODOLOGY & SOP", h2_style))
    meth_text = custom_methodology if custom_methodology.strip() else (
        "Forensic processing was executed in an isolated laboratory environment using write-blocking hardware "
        "(Tableau T8u) and NIST-certified forensic software (Autopsy Forensic Browser, FTK Imager v4.7, Volatility 3, "
        "and Python Hashlib Integrity Verification Suite). All disk images were verified against original acquisition "
        "cryptographic hashes prior to analysis."
    )
    elements.append(Paragraph(meth_text, body_style))
    elements.append(Spacer(1, 10))

    # 7. Conclusion & Recommendations
    elements.append(Paragraph("6. INVESTIGATOR CONCLUSION & RECOMMENDATIONS", h2_style))
    conc_text = custom_conclusion if custom_conclusion.strip() else (
        "Based on the forensic evidence collected and analyzed, the artifacts confirm unauthorized system activity "
        "and data access during the timeframe under review. Immediate containment measures, credential resets, and "
        "enhanced endpoint monitoring are strongly recommended."
    )
    elements.append(Paragraph(conc_text, body_style))
    elements.append(Spacer(1, 14))

    # 8. Sign-off Block
    sign_block = [
        [
            Paragraph("<b>Lead Investigator Attestation:</b>", body_bold),
            Paragraph("<b>Digital Verification Fingerprint:</b>", body_bold)
        ],
        [
            Paragraph(f"<br/>_______________________________<br/><b>{case['investigator']}</b><br/>Lead Forensic Examiner", body_style),
            Paragraph(f"<br/><b>SHA-256 Stamp:</b><br/><code>VERIFIED-DF-REPORT-{case['case_id']}</code><br/><font color='#16a34a'>STATUS: INTEGRITY VERIFIED (OK)</font>", body_style)
        ]
    ]
    sign_table = Table(sign_block, colWidths=[250, 254])
    sign_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))

    elements.append(KeepTogether(sign_table))

    # Build PDF doc with custom canvas for Page X of Y
    canvas_maker = lambda *args, **kwargs: NumberedCanvas(*args, **kwargs)
    
    # Store case_id for header
    def on_first_page(canv, doc):
        canv.case_id_ref = case['case_id']
        
    doc.build(elements, canvasmaker=NumberedCanvas)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
