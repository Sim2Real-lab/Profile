from django.conf import settings

def proforma_settings(request):
    return {
        'PROFORMA_DOMAIN': getattr(settings, 'PROFORMA_DOMAIN', 'https://robotech.nitk.ac.in'),
        'FORCE_SCRIPT_NAME': getattr(settings, 'FORCE_SCRIPT_NAME', '/proforma') or '',
    }
