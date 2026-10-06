from django.contrib import admin
from members.models import Member, Skill, MemberSkill, Project

class MemberSkillInline(admin.TabularInline):
    model = MemberSkill
    extra = 1

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'roll_no', 'name', 'sig', 'previous_core', 'y26_core', 'created_at')
    list_filter = ('sig', 'previous_core', 'y26_core', 'created_at')
    search_fields = ('member_id', 'roll_no', 'name', 'email', 'phone')
    readonly_fields = ('member_id', 'secure_token', 'username', 'created_at', 'updated_at')
    inlines = [MemberSkillInline, ProjectInline]
    
    fieldsets = (
        ('Identification & Auth', {
            'fields': ('member_id', 'secure_token', 'username', 'user')
        }),
        ('Personal Details', {
            'fields': ('name', 'roll_no', 'branch', 'dob', 'phone', 'email', 'photo')
        }),
        ('Social Links', {
            'fields': ('linkedin', 'instagram')
        }),
        ('Club Status', {
            'fields': ('sig', 'previous_core', 'y26_core')
        }),
        ('Reflection', {
            'fields': ('learning_review', 'changes_review')
        }),
        ('Generated Files', {
            'fields': ('qr_code', 'pdf_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'sig', 'active')
    list_filter = ('sig', 'active')
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'member', 'created_at')
    search_fields = ('project_name', 'member__name', 'member__roll_no')
