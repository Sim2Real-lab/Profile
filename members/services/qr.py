import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

def generate_member_qr(member):
    """
    Generate QR code for member pointing to their secure profile verification URL.
    Returns a ContentFile suitable for saving to ImageField.
    """
    domain = getattr(settings, 'PROFORMA_DOMAIN', 'https://robotech.nitk.ac.in').rstrip('/')
    script_prefix = getattr(settings, 'FORCE_SCRIPT_NAME', '/proforma') or '/proforma'
    if not script_prefix.startswith('/'):
        script_prefix = '/' + script_prefix
    script_prefix = script_prefix.rstrip('/')
    
    # Secure token URL format: https://robotech.nitk.ac.in/proforma/member/<secure-token>/
    verify_url = f"{domain}{script_prefix}/member/{member.secure_token}/"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    filename = f"qr_{member.member_id}.png"
    return ContentFile(buffer.getvalue(), name=filename), verify_url
