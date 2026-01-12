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

@admin.action(description="Send Active Template to FILTERED users")
def send_update_email(modeladmin, request, queryset):
    # 1. Fetch the active template from the database
    email_update = EmailUpdate.objects.filter(is_active=True).first()

    if not email_update:
        messages.error(request, "Error: You must create an 'Email Update' and check 'Is Active' first.")
        return

    # Import the helper function we wrote in models.py
    from .models import send_custom_template_email

    sent_count = 0
    for user in queryset:
        # Only send to verified users with email addresses
        if user.email and user.is_verified:
            # We call the helper function here!
            success = send_custom_template_email(user, email_update)
            if success:
                sent_count += 1

    messages.success(request, f"Successfully sent '{email_update.title}' to {sent_count} users.")

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
        count = 0
    # Loop through and call save() to trigger the send_verification_email logic
        for user in queryset.filter(is_staff=False, is_superuser=False, is_verified=False):
            user.is_verified = True
            user.save() # This triggers the save() method in models.py
            count += 1
        self.message_user(request, f"{count} members verified and notified via email.")
        
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