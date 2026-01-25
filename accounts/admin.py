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
    Notification,
    Role,
    Committee,
    CommitteeReport,     
    CommitteeAnnouncement
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
    search_fields = ('title', 'subject', 'message')

@admin.register(User)
class NAAUserAdmin(BaseUserAdmin):
    model = User
    
    readonly_fields = ('date_verified', 'last_login',)

    # ================= LIST VIEW =================
    list_display = (
        'username',
        'email',
        'membership_tier',
        'is_verified',
        'last_login',
        'date_verified',
        'is_staff',
    )

    list_filter = (
        'membership_tier',
        'is_verified',
        'last_login',
        'is_staff',
    )

    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

    # ================= EDIT USER =================
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            'NAA Professional Info',
            {
                'fields': (
                    'membership_tier',
                    'roles',
                    'phone_number',
                    'is_verified',
                    'date_verified',
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
    actions = ['verify_members', 'unverify_members', send_update_email, 'send_dashboard_notification']

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
        
    @admin.action(description="Notify selected members on their Dashboards")
    def send_dashboard_notification(self, request, queryset):
        # Fetch the Active template
        email_template = EmailUpdate.objects.filter(is_active=True).first()

        if not email_template:
            self.message_user(request, "No active Email Template found.", level=messages.ERROR)
            return

        for user in queryset:
            # 1. Clean the message and ensure replacement works
            msg = email_template.message
            # Replace common variations of the placeholder
            msg = msg.replace('{{username}}', user.username).replace('{{ username }}', user.username)

            # 2. Create the notification
            Notification.objects.create(
                user=user,
                title=email_template.subject,
                message=msg,
                is_read=False # Ensure it shows as NEW to the user
             )

        self.message_user(request, f"Sent to {queryset.count()} members.", level=messages.SUCCESS)

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

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'featured',
        'author',
        'date_posted',
        'updated_at',
    )
    list_filter = ('is_published', 'featured', 'date_posted')
    search_fields = ('title', 'summary', 'content')
    list_editable = ('is_published', 'featured')
    ordering = ('-featured', '-date_posted')

# ================= RESOURCE ADMIN =================
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'access_level', 'is_verified_only', 'uploaded_at')
    list_filter = ('category', 'access_level', 'is_verified_only')
    search_fields = ('title', 'description')
    list_editable = ('access_level', 'is_verified_only') # Quick edits from the list view
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Simplified list view for the NAA Portal
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'user__membership_tier') #
    search_fields = ('user__username', 'title', 'message') #
    
    # REMOVE fieldsets for now to avoid "Add Page" errors. 
    # This makes the form simple top-to-bottom.
    fields = ('user', 'title', 'message', 'is_read')
    readonly_fields = ('created_at',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'permissions_level')

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'director')
    filter_horizontal = ('members',)
    
@admin.register(CommitteeReport)
class CommitteeReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'committee', 'submitted_by', 'uploaded_at')
    list_filter = ('committee', 'uploaded_at')

@admin.register(CommitteeAnnouncement)
class CommitteeAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'committee', 'author', 'date_posted')
    list_filter = ('committee', 'date_posted')
    search_fields = ('title', 'content')

# ================= OTHER MODELS =================
admin.site.register(Leader)
admin.site.register(AboutPage)
admin.site.register(StudentProfile)
admin.site.register(StudentAnnouncement)