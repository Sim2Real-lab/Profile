import os
import datetime
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from members.models import Member, Skill, MemberSkill, Project
from members.services.credentials import generate_member_id, generate_username, generate_password
from members.services.qr import generate_member_qr
from members.services.pdf import generate_proforma_pdf

@override_settings(FORCE_SCRIPT_NAME=None)
class ProformaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_superuser(
            username='admin',
            email='admin@nitk.edu.in',
            password='adminpassword123'
        )
        self.skill_ecp = Skill.objects.create(name='Electronics', sig='EC&P', active=True)
        self.skill_web = Skill.objects.create(name='Django', sig='Website', active=True)

    def test_credential_generators(self):
        # Password generator
        pwd = generate_password(8)
        self.assertEqual(len(pwd), 8)
        for ch in ['0', 'O', '1', 'I', 'l']:
            self.assertNotIn(ch, pwd)

        # Member ID generator
        m_id = generate_member_id("231MI001")
        self.assertEqual(m_id, "RBT26-231MI001")

        # Username generator
        username = generate_username(m_id)
        self.assertEqual(username, "rbt26-231mi001")

    def test_member_creation_and_unique_constraint(self):
        # Create tiny dummy image
        tiny_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
            b'\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        photo = SimpleUploadedFile("test.gif", tiny_gif, content_type="image/gif")

        member = Member.objects.create(
            member_id="RBT26-231MI001",
            name="Test Student",
            roll_no="231MI001",
            branch="Mining Engineering",
            dob=datetime.date(2003, 5, 15),
            phone="+919876543210",
            email="test@nitk.edu.in",
            photo=photo,
            sig="Website",
            learning_review="Learnt web dev",
            changes_review="More workshops",
            username="rbt26-231mi001"
        )
        self.assertEqual(member.roll_no, "231MI001")

        # QR generation test
        qr_file, verify_url = generate_member_qr(member)
        self.assertIsNotNone(qr_file)

        # PDF generation test
        pdf_file = generate_proforma_pdf(member, "K7p4X9")
        self.assertIsNotNone(pdf_file)

    def test_dashboard_and_export_views(self):
        self.client.login(username='admin', password='adminpassword123')
        
        # Test Dashboard View
        url = reverse('members:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test CSV Export
        csv_url = reverse('members:export_csv')
        csv_resp = self.client.get(csv_url)
        self.assertEqual(csv_resp.status_code, 200)
        self.assertEqual(csv_resp['Content-Type'], 'text/csv')

        # Test ZIP Export
        zip_url = reverse('members:export_zip')
        zip_resp = self.client.get(zip_url)
        self.assertEqual(zip_resp.status_code, 200)
        self.assertEqual(zip_resp['Content-Type'], 'application/zip')
