import secrets
import string
from members.models import Member

# Character set excluding ambiguous characters (0, O, 1, I, l)
ALLOWED_PASSWORD_CHARS = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"

def generate_password(length=8):
    """Generate a readable, secure random password without ambiguous characters."""
    return ''.join(secrets.choice(ALLOWED_PASSWORD_CHARS) for _ in range(length))

def generate_member_id(roll_no):
    """
    Generate a unique Member ID based on Roll Number.
    Example: RBT26-231MI001
    """
    clean_roll = str(roll_no).strip().upper().replace(" ", "")
    base_id = f"RBT26-{clean_roll}"
    
    candidate = base_id
    counter = 1
    while Member.objects.filter(member_id=candidate).exists():
        candidate = f"{base_id}-{counter}"
        counter += 1
        
    return candidate

def generate_username(member_id):
    """
    Generate a unique username based on Member ID.
    Example: rbt26-231mi001
    """
    base_user = member_id.lower()
    candidate = base_user
    counter = 1
    
    from django.contrib.auth.models import User
    while User.objects.filter(username=candidate).exists() or Member.objects.filter(username=candidate).exists():
        candidate = f"{base_user}{counter}"
        counter += 1
        
    return candidate
