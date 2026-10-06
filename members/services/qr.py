import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

def generate_member_qr(member, password=None):
    """
    Generate QR code for member encoding their credentials as text.
    Returns a ContentFile suitable for saving to ImageField.
    """
    domain = getattr(settings, 'PROFORMA_DOMAIN', 'https://robotech.nitk.ac.in').rstrip('/')
    if 'localhost' in domain or '127.0.0.1' in domain:
        domain = 'https://robotech.nitk.ac.in'
        
    script_prefix = getattr(settings, 'FORCE_SCRIPT_NAME', '/proforma') or '/proforma'
    if not script_prefix.startswith('/'):
        script_prefix = '/' + script_prefix
    script_prefix = script_prefix.rstrip('/')
    
    # Secure verification URL format: https://robotech.nitk.ac.in/proforma/member/<secure-token>/
    verify_url = f"{domain}{script_prefix}/member/{member.secure_token}/"
    
    # Build credentials text to encode in QR code
    qr_lines = [
        "ROBOTECH NITK MEMBER CREDENTIALS",
        f"Member ID: {member.member_id}",
        f"Full Name: {member.name}",
        f"Roll No: {member.roll_no}",
        f"Username: {member.username}",
    ]
    if password:
        qr_lines.append(f"Password: {password}")
    qr_lines.append(f"Verify: {verify_url}")

    qr_text = "\n".join(qr_lines)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    filename = f"qr_{member.member_id}.png"
    return ContentFile(buffer.getvalue(), name=filename), verify_url
