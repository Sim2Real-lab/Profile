import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

SIG_CHOICES = [
    ('Design', 'Design'),
    ('Website', 'Website'),
    ('Automation', 'Automation'),
    ('Electronics and Programming', 'Electronics and Programming'),
    ('Media', 'Media'),
    ('Marketing', 'Marketing'),
]

class Skill(models.Model):
    name = models.CharField(max_length=100)
    sig = models.CharField(max_length=50, choices=SIG_CHOICES)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sig', 'name']
        unique_together = ('name', 'sig')

    def __str__(self):
        return f"{self.name} ({self.sig})"

class Member(models.Model):
    member_id = models.CharField(max_length=50, unique=True, db_index=True)
    secure_token = models.CharField(max_length=64, unique=True, default=uuid.uuid4, db_index=True)
    
    # Personal Info
    name = models.CharField(max_length=150, verbose_name="Full Name")
    roll_no = models.CharField(
        max_length=30, 
        unique=True, 
        db_index=True,
        verbose_name="Roll Number",
        help_text="e.g. 231MI001"
    )
    branch = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    email = models.EmailField()
    photo = models.ImageField(upload_to='photos/%Y/%m/')
    
    # Socials
    linkedin = models.URLField(blank=True, null=True, verbose_name="LinkedIn Profile")
    instagram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Instagram Handle")

    # Club Information
    sig = models.CharField(max_length=255, verbose_name="Special Interest Group (SIG)")
    previous_core = models.BooleanField(default=False, verbose_name="Previous Core Member")
    y26_core = models.BooleanField(default=False, verbose_name="Part of Y26 Core")

    # Reflection
    learning_review = models.TextField(verbose_name="What have you learnt from the club?")
    changes_review = models.TextField(verbose_name="What changes would you like to see or implement in the club?")

    # Generated Authentication Credentials
    username = models.CharField(max_length=150, unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_profile')
    
    # Generated Assets
    qr_code = models.ImageField(upload_to='qrcodes/%Y/%m/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/%Y/%m/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.member_id})"

class MemberSkill(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='member_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_members')

    class Meta:
        unique_together = ('member', 'skill')

    def __str__(self):
        return f"{self.member.name} - {self.skill.name}"

class Project(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='projects')
    project_name = models.CharField(max_length=200, verbose_name="Project Name")
    contribution = models.TextField(verbose_name="Contribution / Role")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.project_name} ({self.member.name})"
