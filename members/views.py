import os
import io
import zipfile
import csv
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from django.conf import settings

from members.models import Member, Skill, MemberSkill, Project, SIG_CHOICES
from members.forms import MemberProformaForm, ProjectFormSet, seed_default_skills
from members.services.credentials import generate_member_id, generate_username, generate_password
from members.services.qr import generate_member_qr
from members.services.pdf import generate_proforma_pdf

logger = logging.getLogger(__name__)

def proforma_form_view(request):
    """
    Main Multi-Step Proforma Submission View.
    """
    # Ensure skills exist in DB
    seed_default_skills()
    skills_by_sig = {}
    for sig_code, _ in SIG_CHOICES:
        skills_by_sig[sig_code] = list(Skill.objects.filter(sig=sig_code, active=True).values('id', 'name'))

    if request.method == 'POST':
        form = MemberProformaForm(request.POST, request.FILES)
        project_formset = ProjectFormSet(request.POST)

        if form.is_valid() and project_formset.is_valid():
            try:
                with transaction.atomic():
                    # 1. Save Member initial data (commit=False to attach generated fields)
                    member = form.save(commit=False)

                    # 2. Generate Credentials
                    member_id = generate_member_id(member.roll_no)
                    username = generate_username(member_id)
                    plaintext_password = generate_password(length=8)

                    member.member_id = member_id
                    member.username = username
                    
                    # Create corresponding Django User
                    user = User.objects.create_user(
                        username=username,
                        email=member.email,
                        password=plaintext_password,
                        first_name=member.name.split()[0] if member.name else '',
                        last_name=' '.join(member.name.split()[1:]) if len(member.name.split()) > 1 else ''
                    )
                    member.user = user
                    member.save()

                    # 3. Save Selected Skills
                    selected_skills = form.cleaned_data.get('skills', [])
                    for skill in selected_skills:
                        MemberSkill.objects.create(member=member, skill=skill)

                    # 4. Save Projects
                    projects = project_formset.save(commit=False)
                    for project in projects:
                        if project.project_name and project.project_name.strip():
                            project.member = member
                            project.save()

                    # 5. Generate QR Code
                    qr_file, verify_url = generate_member_qr(member, plaintext_password)
                    member.qr_code.save(qr_file.name, qr_file, save=False)

                    # 6. Generate A4 PDF
                    pdf_file = generate_proforma_pdf(member, plaintext_password)
                    member.pdf_file.save(pdf_file.name, pdf_file, save=False)

                    member.save()

                    # 7. Store one-time credentials in session for success page display
                    request.session['credentials_success'] = {
                        'member_id': member.member_id,
                        'name': member.name,
                        'username': username,
                        'password': plaintext_password,
                        'secure_token': str(member.secure_token),
                    }

                    logger.info(f"Successfully generated proforma for member {member.member_id} ({member.roll_no})")
                    return redirect('members:success')

            except Exception as e:
                logger.error(f"Error saving member proforma: {e}", exc_info=True)
                messages.error(request, f"An unexpected error occurred while processing your proforma: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = MemberProformaForm()
        project_formset = ProjectFormSet()

    context = {
        'form': form,
        'project_formset': project_formset,
        'skills_by_sig_json': skills_by_sig,
        'sig_choices': SIG_CHOICES,
    }
    return render(request, 'members/form.html', context)


def success_view(request):
    """
    Success Page displaying member credentials & PDF download button.
    """
    cred = request.session.get('credentials_success')
    if not cred:
        # If page refreshed or accessed directly without session
        return redirect('members:form')

    context = {
        'cred': cred,
    }
    return render(request, 'members/success.html', context)


def pdf_download_view(request, token):
    """
    Protected PDF download view using secure token.
    Always regenerates latest PDF version on download request.
    """
    member = get_object_or_404(Member, secure_token=token)
    pdf_file = generate_proforma_pdf(member, "[Stored Securely]")
    member.pdf_file.save(pdf_file.name, pdf_file, save=True)

    try:
        response = FileResponse(
            open(member.pdf_file.path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="proforma_{member.member_id}.pdf"'
        return response
    except Exception as e:
        logger.error(f"Error serving PDF for {member.member_id}: {e}")
        raise Http404("PDF file not found.")


def member_token_view(request, token):
    """
    Public QR token verification page.
    """
    member = get_object_or_404(Member, secure_token=token)
    skills = [ms.skill.name for ms in member.member_skills.select_related('skill').all()]
    projects = member.projects.all()

    context = {
        'member': member,
        'skills': skills,
        'projects': projects,
    }
    return render(request, 'members/member_detail.html', context)


@staff_member_required
def dashboard_view(request):
    """
    Staff/Admin Dashboard View.
    """
    query = request.GET.get('q', '').strip()
    sig_filter = request.GET.get('sig', '').strip()
    prev_core = request.GET.get('previous_core', '').strip()
    y26_core = request.GET.get('y26_core', '').strip()

    members = Member.objects.all().prefetch_related('member_skills__skill', 'projects')

    if query:
        members = members.filter(name__icontains=query) | members.filter(roll_no__icontains=query) | members.filter(member_id__icontains=query)

    if sig_filter:
        members = members.filter(sig=sig_filter)

    if prev_core in ('true', '1', 'yes'):
        members = members.filter(previous_core=True)
    elif prev_core in ('false', '0', 'no'):
        members = members.filter(previous_core=False)

    if y26_core in ('true', '1', 'yes'):
        members = members.filter(y26_core=True)
    elif y26_core in ('false', '0', 'no'):
        members = members.filter(y26_core=False)

    total_count = Member.objects.count()
    sig_counts = {sig: Member.objects.filter(sig=sig).count() for sig, _ in SIG_CHOICES}

    context = {
        'members': members,
        'total_count': total_count,
        'sig_counts': sig_counts,
        'sig_choices': SIG_CHOICES,
        'query': query,
        'sig_filter': sig_filter,
        'prev_core': prev_core,
        'y26_core': y26_core,
    }
    return render(request, 'members/dashboard.html', context)


@staff_member_required
def regenerate_pdf_view(request, member_id):
    """
    Staff action: Regenerate member PDF.
    """
    member = get_object_or_404(Member, member_id=member_id)
    try:
        pdf_file = generate_proforma_pdf(member, "[Regenerated by Admin]")
        member.pdf_file.save(pdf_file.name, pdf_file, save=True)
        messages.success(request, f"Successfully regenerated PDF for {member.name} ({member.member_id}).")
    except Exception as e:
        messages.error(request, f"Failed to regenerate PDF: {e}")
    return redirect('members:dashboard')


@staff_member_required
def export_csv_view(request):
    """
    Staff action: Export member data as CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="robotech_members_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Member ID', 'Roll No', 'Full Name', 'Branch', 'DOB', 'Phone', 'Email',
        'SIG', 'Previous Core', 'Y26 Core', 'LinkedIn', 'Instagram',
        'Skills', 'Projects Count', 'Username', 'Created At'
    ])

    members = Member.objects.all().prefetch_related('member_skills__skill', 'projects')
    for m in members:
        skills_str = ", ".join([ms.skill.name for ms in m.member_skills.all()])
        writer.writerow([
            m.member_id, m.roll_no, m.name, m.branch, m.dob.strftime('%Y-%m-%d'), m.phone, m.email,
            m.sig, 'Yes' if m.previous_core else 'No', 'Yes' if m.y26_core else 'No',
            m.linkedin or '', m.instagram or '',
            skills_str, m.projects.count(), m.username, m.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response


@staff_member_required
def export_bulk_pdfs_zip_view(request):
    """
    Staff action: Export all generated PDFs as a single ZIP package.
    """
    members = Member.objects.exclude(pdf_file='')

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for m in members:
            if m.pdf_file and os.path.exists(m.pdf_file.path):
                filename = f"proforma_{m.member_id}.pdf"
                zip_file.write(m.pdf_file.path, arcname=filename)

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="robotech_member_proformas.zip"'
    return response
