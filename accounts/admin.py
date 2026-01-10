from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from .models import (
    User,
    Announcement,
    Leader,
    AboutPage,
    Resource,
    StudentProfile,
    StudentAnnouncement,
    CPDRecord,
    EmailUpdate,
)


admin.site.site_header = "NAA Portal Management"
admin.site.site_title = "NAA Admin Portal"
admin.site.index_title = "Welcome to the Academy Management System"

@admin.action(description="Send selected email update to verified users")
def send_update_email(modeladmin, request, queryset):
    email_update = EmailUpdate.objects.filter(is_active=True).first()

    if not email_update:
        messages.error(request, "No active email update found.")
        return

    sent = 0
    for user in queryset:
        if user.is_verified and user.email:
            send_mail(
                subject=email_update.subject,
                message=email_update.message.replace(
                    "{{name}}", user.first_name or user.username
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            sent += 1

    messages.success(request, f"{sent} emails sent successfully.")

@admin.register(EmailUpdate)
class EmailUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subject')

@admin.register(User)
class NAAUserAdmin(BaseUserAdmin):
    model = User

    # ================= LIST VIEW =================
    list_display = (
        'username',
        'email',
        'membership_tier',
        'is_verified',
        'is_staff',
    )

    list_filter = (
        'membership_tier',
        'is_verified',
        'is_staff',
    )

    search_fields = ('username', 'email')
    ordering = ('username',)

    # ================= EDIT USER =================
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            'NAA Professional Info',
            {
                'fields': (
                    'membership_tier',
                    'phone_number',
                    'is_verified',
                )
            },
        ),
    )

    # ================= ADD USER =================
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'membership_tier',
                'phone_number',
                'is_verified',
                'is_staff',
                'is_active',
            ),
        }),
    )

    # ================= ACTIONS =================
    actions = ['verify_members', 'unverify_members', send_update_email]

    @admin.action(description='Verify selected members')
    def verify_members(self, request, queryset):
        queryset.filter(
            is_staff=False,
            is_superuser=False
        ).update(is_verified=True)
        self.message_user(request, "Selected members have been verified.")

    @admin.action(description='Unverify selected members')
    def unverify_members(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, "Selected members verification revoked.")


# ================= CPD RECORD ADMIN =================
@admin.register(CPDRecord)
class CPDRecordAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'activity_name',
        'points',
        'date_completed',
        'is_verified',
    )

    list_filter = (
        'is_verified',
        'date_completed',
    )

    search_fields = (
        'user__username',
        'activity_name',
    )

    actions = ['verify_records']

    @admin.action(description="Mark selected activities as Verified")
    def verify_records(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, "Selected CPD records have been verified.")


# ================= RESOURCE ADMIN =================
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'access_level', 'is_verified_only', 'uploaded_at')
    list_filter = ('category', 'access_level', 'is_verified_only')
    search_fields = ('title', 'description')
    list_editable = ('access_level', 'is_verified_only') # Quick edits from the list view


# ================= OTHER MODELS =================
admin.site.register(Announcement)
admin.site.register(Leader)
admin.site.register(AboutPage)
admin.site.register(StudentProfile)
admin.site.register(StudentAnnouncement)