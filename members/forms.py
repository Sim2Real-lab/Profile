import os
import datetime
from django import forms
from django.core.exceptions import ValidationError
from members.models import Member, Skill, Project, SIG_CHOICES

# Pre-defined Skill Mapping as per agent.md spec
DEFAULT_SIG_SKILLS = {
    'Website': [
        'HTML', 'CSS', 'JavaScript', 'React', 'Node.js',
        'Python', 'Django', 'SQL', 'MongoDB', 'Git', 'GitHub', 'Figma','Nginx','Docker','CI/CD',
    ],
    'Automation': [
        'ROS', 'Linux', 'Gazebo', 'C', 'Python',
        'Git', 'GitHub', 'Yarp','OpenCv','Path Planning','Open motion  planning library','EDGE SDK','Nav2','SLAM','Movelt2'
    ],
    'Electronics and Programming': [
        'C', 'C++', 'Arduino', 'Raspberry Pi', 'ESP32',
        'PCB Design', 'Microcontrollers', 'IoT', 'Sensors', 'Embedded Systems'
    ],
    'Media': [
        'Photography', 'Videography', 'Video Editing', 'Premiere Pro',
        'After Effects', 'Photoshop', 'Illustrator', 'Graphic Design'
    ],
    'Marketing': [
        'Social Media Management', 'Content Writing', 'SEO',
        'Event Management', 'Public Relations', 'Copywriting', 'Campaign Management'
    ]
}

def seed_default_skills():
    """Ensure skills exist in DB."""
    for sig, skill_list in DEFAULT_SIG_SKILLS.items():
        for skill_name in skill_list:
            Skill.objects.get_or_create(name=skill_name, sig=sig)


class MemberProformaForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.filter(active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Skills & Expertise"
    )
    sig = forms.MultipleChoiceField(
        choices=SIG_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Special Interest Group (SIG)"
    )

    class Meta:
        model = Member
        fields = [
            'name', 'roll_no', 'branch', 'dob', 'phone', 'email', 'photo',
            'linkedin', 'instagram', 'sig', 'previous_core', 'y26_core',
            'learning_review', 'changes_review'
        ]
        # DOB date limits: must be at least 18 years old, and born after 1985
        today = datetime.date.today()
        max_dob = today.replace(year=today.year - 18)
        min_dob = datetime.date(1985, 1, 1)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'dob': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': str(min_dob),
                'max': str(max_dob),
                'required': True,
            }),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/jpg', 'required': True}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_core': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'y26_core': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'learning_review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'changes_review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo:
            raise ValidationError("Member photo is required.")

        # 1. File extension check
        ext = os.path.splitext(photo.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            raise ValidationError("Only JPG, JPEG, and PNG image files are allowed.")

        # 2. File size check (5MB)
        if photo.size > 5 * 1024 * 1024:
            raise ValidationError("Photo file size must not exceed 5MB.")

        # 3. Magic byte / file signature check (sanitize fake extensions)
        photo.seek(0)
        header = photo.read(8)
        photo.seek(0)
        jpeg_magic = (header[:2] == b'\xff\xd8')  # JPEG/JPG signature
        png_magic = (header[:8] == b'\x89PNG\r\n\x1a\n')  # PNG signature
        if ext in ['.jpg', '.jpeg'] and not jpeg_magic:
            raise ValidationError("The file does not appear to be a valid JPEG image.")
        if ext == '.png' and not png_magic:
            raise ValidationError("The file does not appear to be a valid PNG image.")
        if not (jpeg_magic or png_magic):
            raise ValidationError("Only genuine JPEG or PNG image files are accepted.")

        return photo

    def clean_roll_no(self):
        roll_no = self.cleaned_data.get('roll_no', '').strip().upper()
        if not roll_no:
            raise ValidationError("Roll number is required.")
        # Check uniqueness on creation
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if Member.objects.filter(roll_no=roll_no).exclude(pk=instance.pk).exists():
                raise ValidationError(f"A member with roll number '{roll_no}' has already submitted a proforma.")
        else:
            if Member.objects.filter(roll_no=roll_no).exists():
                raise ValidationError(f"A member with roll number '{roll_no}' has already submitted a proforma.")
        return roll_no

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise ValidationError("Date of birth is required.")
        today = datetime.date.today()
        min_dob = datetime.date(1985, 1, 1)
        max_dob = today.replace(year=today.year - 18)
        if dob < min_dob:
            raise ValidationError("Date of birth must be after January 1, 1985.")
        if dob > max_dob:
            raise ValidationError("You must be at least 18 years old to submit a proforma.")
        return dob

    def clean_sig(self):
        sig = self.cleaned_data.get('sig')
        if not sig:
            raise ValidationError("Please select at least one SIG.")
        return ", ".join(sig)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'contribution']
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contribution': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


ProjectFormSet = forms.inlineformset_factory(
    Member,
    Project,
    form=ProjectForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)
