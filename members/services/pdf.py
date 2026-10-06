import os
import logging
from io import BytesIO
from PIL import Image, ImageOps
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings

logger = logging.getLogger(__name__)

def process_member_photo(photo_field):
    """
    Process uploaded member photo: resize & crop into portrait 3:4 aspect ratio.
    """
    if not photo_field or not hasattr(photo_field, 'path') or not os.path.exists(photo_field.path):
        return None
        
    try:
        img = Image.open(photo_field.path)
        img = ImageOps.exif_transpose(img)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
            
        # Target portrait dimensions (300 x 400)
        target_size = (300, 400)
        fitted_img = ImageOps.fit(img, target_size, Image.Resampling.LANCZOS)
        
        fitted_img.save(photo_field.path, quality=90, optimize=True)
        return photo_field.path
    except Exception as e:
        logger.error(f"Error processing member photo: {e}")
        return None

def generate_proforma_pdf(member, plaintext_password):
    """
    Generates official A4 PDF for member proforma using WeasyPrint (with ReportLab fallback).
    Returns ContentFile ready to save into member.pdf_file.
    """
    # 1. Process photo if exists
    if member.photo:
        process_member_photo(member.photo)

    # 2. Gather context
    skills_by_sig = member.member_skills.select_related('skill').all()
    skills_list = [ms.skill.name for ms in skills_by_sig]
    projects_list = member.projects.all()

    nitk_logo_path = os.path.join(settings.BASE_DIR, 'nitk.jpg')
    robotech_logo_path = os.path.join(settings.BASE_DIR, 'robotech.jpg')

    context = {
        'member': member,
        'plaintext_password': plaintext_password,
        'skills': skills_list,
        'projects': projects_list,
        'PROFORMA_DOMAIN': getattr(settings, 'PROFORMA_DOMAIN', 'https://robotech.nitk.ac.in'),
        'nitk_logo': nitk_logo_path if os.path.exists(nitk_logo_path) else None,
        'robotech_logo': robotech_logo_path if os.path.exists(robotech_logo_path) else None,
    }

    # 3. Try WeasyPrint HTML/CSS rendering
    pdf_bytes = None
    weasyprint_success = False

    try:
        from weasyprint import HTML, CSS
        html_string = render_to_string('pdf/proforma_template.html', context)
        # Base URL for static/media assets
        base_url = str(settings.BASE_DIR)
        html_obj = HTML(string=html_string, base_url=base_url)
        pdf_bytes = html_obj.write_pdf()
        weasyprint_success = True
        logger.info(f"PDF generated via WeasyPrint for {member.member_id}")
    except Exception as e:
        logger.warning(f"WeasyPrint PDF generation failed/unavailable ({e}). Using ReportLab fallback generator.")

    # 4. Fallback to ReportLab if WeasyPrint is unavailable or missing native DLLs
    if not weasyprint_success or not pdf_bytes:
        pdf_bytes = _generate_pdf_reportlab(member, plaintext_password, skills_list, projects_list)

    filename = f"proforma_{member.member_id}.pdf"
    return ContentFile(pdf_bytes, name=filename)


def _generate_pdf_reportlab(member, password, skills_list, projects_list):
    """
    High-end ReportLab PDF generator with nitk.jpg (left) & robotech.jpg (right) top logos,
    modern typography, custom badges, T&C disclaimer, and signature blocks.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # Premium Color Palette
    NAVY = colors.HexColor("#0f172a")
    PRIMARY_BLUE = colors.HexColor("#0284c7")
    CYAN_LIGHT = colors.HexColor("#e0f2fe")
    CYAN_TEXT = colors.HexColor("#0369a1")
    TEXT_DARK = colors.HexColor("#1e293b")
    TEXT_MUTED = colors.HexColor("#475569")
    BG_CARD = colors.HexColor("#f8fafc")
    BORDER_COLOR = colors.HexColor("#cbd5e1")
    BORDER_LIGHT = colors.HexColor("#e2e8f0")

    # Typography Styles
    header_org_style = ParagraphStyle(
        'HeaderOrg',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        leading=9
    )

    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        textColor=NAVY,
        alignment=TA_CENTER,
        leading=20
    )

    header_sub_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=PRIMARY_BLUE,
        alignment=TA_CENTER,
        leading=11
    )

    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=4,
        leading=13
    )

    lbl_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=TEXT_MUTED,
        leading=12
    )

    val_style = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=TEXT_DARK,
        leading=12
    )

    val_bold = ParagraphStyle(
        'FieldValueBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=NAVY,
        leading=12
    )

    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=CYAN_TEXT,
        alignment=TA_CENTER
    )

    body_text = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=TEXT_DARK,
        leading=12
    )

    ans_box_style = ParagraphStyle(
        'AnsBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor("#334155"),
        leading=12
    )

    story = []

    # 1. Header with Top-Left (nitk.jpg) and Top-Right (robotech.jpg) Logos
    nitk_logo_path = os.path.join(settings.BASE_DIR, 'nitk.jpg')
    robotech_logo_path = os.path.join(settings.BASE_DIR, 'robotech.jpg')

    # Left Logo (NITK)
    if os.path.exists(nitk_logo_path):
        try:
            nitk_img = RLImage(nitk_logo_path, width=51, height=48)
        except Exception:
            nitk_img = Paragraph("<b>NITK</b>", ParagraphStyle('ErrL', fontName='Helvetica-Bold', fontSize=10, textColor=NAVY))
    else:
        nitk_img = Paragraph("<b>NITK</b>", ParagraphStyle('ErrL', fontName='Helvetica-Bold', fontSize=10, textColor=NAVY))

    # Right Logo (Robotech)
    if os.path.exists(robotech_logo_path):
        try:
            robotech_img = RLImage(robotech_logo_path, width=48, height=48)
        except Exception:
            robotech_img = Paragraph("<b>ROBOTECH</b>", ParagraphStyle('ErrR', fontName='Helvetica-Bold', fontSize=10, textColor=NAVY, alignment=TA_RIGHT))
    else:
        robotech_img = Paragraph("<b>ROBOTECH</b>", ParagraphStyle('ErrR', fontName='Helvetica-Bold', fontSize=10, textColor=NAVY, alignment=TA_RIGHT))

    header_center_content = [
        Paragraph("NATIONAL INSTITUTE OF TECHNOLOGY KARNATAKA, SURATHKAL", header_org_style),
        Spacer(1, 2),
        Paragraph("ROBOTECH NITK", header_title_style),
        Spacer(1, 1),
        Paragraph("OFFICIAL MEMBER PROFORMA RECORD", header_sub_style),
    ]

    header_table = Table([[nitk_img, header_center_content, robotech_img]], colWidths=[65, 392, 65])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(header_table)

    # Sleek Navy Meta Bar (Member ID & Date)
    meta_left_style = ParagraphStyle(
        'MetaLeft',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.white,
        leading=11
    )

    meta_right_style = ParagraphStyle(
        'MetaRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor("#94a3b8"),
        alignment=TA_RIGHT,
        leading=11
    )

    meta_left = Paragraph(f"Member ID: <font color='#38bdf8'><b>{member.member_id}</b></font>", meta_left_style)
    meta_right = Paragraph(f"Submitted: <b>{member.created_at.strftime('%d %B %Y')}</b>", meta_right_style)

    meta_table = Table([[meta_left, meta_right]], colWidths=[261, 261])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (0,0), 10),
        ('RIGHTPADDING', (1,0), (1,0), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 2. Personal Info & Photo Card
    if hasattr(member.dob, 'strftime'):
        dob_str = member.dob.strftime('%d %B %Y')
    else:
        dob_str = str(member.dob)

    info_matrix = [
        [Paragraph("FULL NAME:", lbl_style), Paragraph(f"<b>{member.name}</b>", val_bold), Paragraph("ROLL NO:", lbl_style), Paragraph(member.roll_no, val_style)],
        [Paragraph("BRANCH:", lbl_style), Paragraph(member.branch, val_style), Paragraph("DOB:", lbl_style), Paragraph(dob_str, val_style)],
        [Paragraph("PHONE:", lbl_style), Paragraph(member.phone, val_style), Paragraph("EMAIL:", lbl_style), Paragraph(member.email, val_style)],
        [Paragraph("LINKEDIN:", lbl_style), Paragraph(member.linkedin or 'N/A', val_style), Paragraph("INSTAGRAM:", lbl_style), Paragraph(member.instagram or 'N/A', val_style)],
    ]

    info_inner_table = Table(info_matrix, colWidths=[68, 127, 65, 127])
    info_inner_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))

    # Photo Box
    photo_element = None
    if member.photo and os.path.exists(member.photo.path):
        try:
            photo_element = RLImage(member.photo.path, width=95, height=125)
        except Exception:
            photo_element = Paragraph("<font color='#64748b' size=8><b>[ Photo ]</b></font>", ParagraphStyle('PhtErr', alignment=TA_CENTER))
    else:
        photo_element = Paragraph("<font color='#64748b' size=8><b>[ No Photo ]</b></font>", ParagraphStyle('PhtErr', alignment=TA_CENTER))

    profile_card_data = [[info_inner_table, photo_element]]
    profile_card = Table(profile_card_data, colWidths=[395, 127])
    profile_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(profile_card)
    story.append(Spacer(1, 6))

    # 3. Club Status & SIG Badges
    sig_badge = Table([[Paragraph(f"SIG: <b>{member.sig}</b>", badge_style)]], colWidths=[160])
    sig_badge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CYAN_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, PRIMARY_BLUE),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))

    prev_badge = Table([[Paragraph(f"Previous Core: <b>{'Yes' if member.previous_core else 'No'}</b>", val_style)]], colWidths=[150])
    prev_badge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    y26_badge = Table([[Paragraph(f"Y26 Core: <b>{'Yes' if member.y26_core else 'No'}</b>", val_style)]], colWidths=[150])
    y26_badge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    status_table = Table([[sig_badge, prev_badge, y26_badge]], colWidths=[170, 160, 160])
    status_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 6))

    # 4. Technical Skills Section
    story.append(Paragraph("TECHNICAL & SIG SKILLS", sec_title))
    skills_text = ", ".join(skills_list) if skills_list else "None specified"
    skills_table = Table([[Paragraph(f"<b>Skills:</b> {skills_text}", body_text)]], colWidths=[522])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 6))

    # 5. Projects Contributed Table
    if projects_list:
        story.append(Paragraph("PROJECTS CONTRIBUTED", sec_title))
        p_headers = [Paragraph("<b>PROJECT NAME</b>", ParagraphStyle('PHead1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
                     Paragraph("<b>CONTRIBUTION / ROLE</b>", ParagraphStyle('PHead2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white))]
        p_data = [p_headers]
        
        for p in projects_list:
            p_data.append([
                Paragraph(f"<b>{p.project_name}</b>", val_bold),
                Paragraph(p.contribution.replace('\n', '<br/>'), body_text)
            ])
            
        p_table = Table(p_data, colWidths=[180, 342])
        p_table_style = [
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
            ('PADDING', (0,0), (-1,-1), 5),
        ]
        for row_idx in range(1, len(p_data)):
            if row_idx % 2 == 0:
                p_table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), BG_CARD))
            else:
                p_table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.white))
                
        p_table.setStyle(TableStyle(p_table_style))
        story.append(p_table)
        story.append(Spacer(1, 6))

    # 6. Reflection & Feedback Section
    story.append(Paragraph("REFLECTION & CLUB FEEDBACK", sec_title))
    
    q1_html = f"<b>Q1: What have you learnt from the club?</b><br/><font color='#334155'>{member.learning_review.replace(chr(10), '<br/>')}</font>"
    q1_table = Table([[Paragraph(q1_html, ans_box_style)]], colWidths=[522])
    q1_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#bae6fd")),
        ('LINELEFT', (0,0), (0,-1), 3, PRIMARY_BLUE),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(q1_table)
    story.append(Spacer(1, 4))

    q2_html = f"<b>Q2: What changes would you like to see or implement in the club?</b><br/><font color='#334155'>{member.changes_review.replace(chr(10), '<br/>')}</font>"
    q2_table = Table([[Paragraph(q2_html, ans_box_style)]], colWidths=[522])
    q2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#bae6fd")),
        ('LINELEFT', (0,0), (0,-1), 3, PRIMARY_BLUE),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(q2_table)
    story.append(Spacer(1, 8))

    # 7. Credentials & Verification QR Card
    qr_element = None
    if member.qr_code and os.path.exists(member.qr_code.path):
        try:
            qr_element = RLImage(member.qr_code.path, width=80, height=80)
        except Exception:
            qr_element = Paragraph("<font size=8 color='#64748b'>[ QR Code ]</font>", body_text)
    else:
        qr_element = Paragraph("<font size=8 color='#64748b'>[ QR Code ]</font>", body_text)

    cred_text = f"""
    <b><font size=9.5 color='#0f172a'>SYSTEM CREDENTIALS & AUTHENTICATION</font></b><br/>
    <b>Username:</b> {member.username} &nbsp;&nbsp;|&nbsp;&nbsp;
    <b>Password:</b> <font face='Courier-Bold' color='#0284c7'>{password}</font><br/>
    <b>Member ID:</b> {member.member_id}<br/>
    <font size=7.5 color='#64748b'>Scan the QR code to verify this proforma document on the official Robotech portal.</font>
    """

    cred_table_data = [[Paragraph(cred_text, body_text), qr_element]]
    cred_table = Table(cred_table_data, colWidths=[410, 112])
    cred_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY_BLUE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))

    # 8. Terms & Conditions Disclaimer
    tnc_style = ParagraphStyle(
        'TNCStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
        leading=10
    )

    tnc_text = "<b>Declaration & Terms:</b> By submitting this proforma, you agree to follow and abide by all the rules and code of conduct set by <b>NITK</b> and <b>Robotech NITK</b>."
    tnc_table = Table([[Paragraph(tnc_text, tnc_style)]], colWidths=[522])
    tnc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    # 9. Signatures Block
    sig_title_style = ParagraphStyle(
        'SigTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=NAVY,
        alignment=TA_CENTER,
        leading=11
    )

    sig_left = Paragraph("<br/><br/>_____________________________________<br/><b>Convenor / Co-Convenor</b><br/><font color='#64748b' size=7.5>Robotech NITK</font>", sig_title_style)
    sig_right = Paragraph("<br/><br/>_____________________________________<br/><b>Faculty Advisor</b><br/><font color='#64748b' size=7.5>Robotech NITK</font>", sig_title_style)

    sig_table_data = [[sig_left, sig_right]]
    sig_table = Table(sig_table_data, colWidths=[261, 261])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    # Keep bottom elements together cleanly
    story.append(KeepTogether([
        cred_table,
        Spacer(1, 6),
        tnc_table,
        Spacer(1, 8),
        sig_table
    ]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
