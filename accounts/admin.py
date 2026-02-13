from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from .models import (
    User,
    Announcement,
    Executive,
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
    CommitteeAnnouncement,
    Article,
)
from .services import NotificationService, EmailService

admin.site.site_header = "NAA Portal Management"
admin.site.site_title = "NAA Admin Portal"
admin.site.index_title = "Welcome to the Academy Management System"


@admin.action(description="Send Active Template to FILTERED users")
def send_update_email(modeladmin, request, queryset):
    # 1. Fetch the active template from the database
    email_update = EmailUpdate.objects.filter(is_active=True).first()

    if not email_update:
        messages.error(
            request,
            "Error: You must create an 'Email Update' and check 'Is Active' first.",
        )
        return

    # Import the helper function we wrote in models.py
    from .models import send_custom_template_email

    sent_count = 0
    for user in queryset:
        # Only send to verified users with email addresses
        if user.email and user.is_verified:
            exec_profile = Executive.objects.filter(user=user).first()
            context = {
                "position": exec_profile.position if exec_profile else "Member",
            }
            # We call the helper function here!
            success = send_custom_template_email(user, email_update, context=context)
            if success:
                sent_count += 1

    messages.success(
        request, f"Successfully sent '{email_update.title}' to {sent_count} users."
    )


@admin.register(EmailUpdate)
class EmailUpdateAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "created_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "subject", "message")
    list_editable = ("is_active",)


@admin.register(User)
class NAAUserAdmin(BaseUserAdmin):
    model = User

    readonly_fields = (
        "date_verified",
        "last_login",
    )

    # ================= LIST VIEW =================
    list_display = (
        "username",
        "email",
        "membership_tier",
        "is_verified",
        "last_login",
        "date_verified",
        "is_staff",
    )

    list_filter = (
        "membership_tier",
        "is_verified",
        "last_login",
        "is_staff",
    )

    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)

    actions = ["send_dashboard_notification", "send_email_to_selected"]

    # ================= EDIT USER =================
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "NAA Professional Info",
            {
                "fields": (
                    "membership_tier",
                    "roles",
                    "phone_number",
                    "is_verified",
                    "date_verified",
                )
            },
        ),
    )

    # ================= ADD USER =================
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "membership_tier",
                    "phone_number",
                    "is_verified",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    # ================= ACTIONS =================
    actions = [
        "verify_members",
        "unverify_members",
        send_update_email,
        "send_dashboard_notification",
    ]

    @admin.action(description="Verify selected members")
    def verify_members(self, request, queryset):
        count = 0
        # Loop through and call save() to trigger the send_verification_email logic
        for user in queryset.filter(
            is_staff=False, is_superuser=False, is_verified=False
        ):
            user.is_verified = True
            user.save()  # This triggers the save() method in models.py
            count += 1
        self.message_user(request, f"{count} members verified and notified via email.")

    @admin.action(description="Unverify selected members")
    def unverify_members(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, "Selected members verification revoked.")

    @admin.action(description="Notify selected members on their Dashboards")
    def send_dashboard_notification(self, request, queryset):
        email_template = EmailUpdate.objects.filter(is_active=True).first()

        if not email_template:
            self.message_user(
                request, "No active Email Template found.", level=messages.ERROR
            )
            return

        for user in queryset:
            msg = EmailService.render_text(email_template.message, {"username": user.username})
            NotificationService.create(user, email_template.subject, msg, send_email=False)

        self.message_user(
            request, f"Sent to {queryset.count()} members.", level=messages.SUCCESS
        )

    @admin.action(description="Send email to selected members")
    def send_email_to_selected(self, request, queryset):
        email_template = EmailUpdate.objects.filter(is_active=True).first()
        if not email_template:
            self.message_user(request, "No active Email Template found.", level=messages.ERROR)
            return
        sent = 0
        failed = 0
        for user in queryset:
            ok = EmailService.send_custom_template_email(user, email_template)
            if ok:
                sent += 1
            else:
                failed += 1
        if failed == 0:
            self.message_user(request, f"Emails sent to {sent} members.", level=messages.SUCCESS)
        else:
            self.message_user(request, f"Emails sent: {sent}, failed: {failed}.", level=messages.WARNING)

# ================= CPD RECORD ADMIN =================
@admin.register(CPDRecord)
class CPDRecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "activity_name",
        "points",
        "date_completed",
        "is_verified",
    )

    list_filter = (
        "is_verified",
        "date_completed",
    )

    search_fields = (
        "user__username",
        "activity_name",
    )

    actions = ["verify_records"]

    @admin.action(description="Mark selected activities as Verified")
    def verify_records(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, "Selected CPD records have been verified.")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_published",
        "featured",
        "author",
        "date_posted",
        "updated_at",
    )
    list_filter = ("is_published", "featured", "date_posted")
    search_fields = ("title", "summary", "content")
    list_editable = ("is_published", "featured")
    ordering = ("-featured", "-date_posted")


# ================= RESOURCE ADMIN =================
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "access_level",
        "is_verified_only",
        "uploaded_at",
    )
    list_filter = ("category", "access_level", "is_verified_only")
    search_fields = ("title", "description")
    list_editable = (
        "access_level",
        "is_verified_only",
    )  # Quick edits from the list view


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Simplified list view for the NAA Portal
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at", "user__membership_tier")  #
    search_fields = ("user__username", "title", "message")  #

    # REMOVE fieldsets for now to avoid "Add Page" errors.
    # This makes the form simple top-to-bottom.
    fields = ("user", "title", "message", "is_read")
    readonly_fields = ("created_at",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "permissions_level")


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ("name", "director")
    filter_horizontal = ("members",)


@admin.register(CommitteeReport)
class CommitteeReportAdmin(admin.ModelAdmin):
    list_display = ("title", "committee", "submitted_by", "uploaded_at")
    list_filter = ("committee", "uploaded_at")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "is_public")
    prepopulated_fields = {"slug": ("title",)}  # Automatically creates URLs from titles


@admin.register(Executive)
class ExecutiveAdmin(admin.ModelAdmin):
    list_display = ("position", "user", "rank", "is_active")
    list_filter = ("is_active", "term_start_date")
    search_fields = ("position", "user__username", "bio")
    list_editable = ("rank", "is_active")


@admin.register(StudentAnnouncement)
class StudentAnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "target_university",
        "author",
        "is_published",
        "date_posted",
    )
    list_filter = ("target_university", "is_published", "date_posted")
    search_fields = ("title", "content")
    list_editable = ("is_published",)

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(CommitteeAnnouncement)
class CommitteeAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "committee", "author", "is_published", "date_posted")
    list_filter = ("committee", "is_published", "date_posted")
    search_fields = ("title", "content")
    list_editable = ("is_published",)


# ================= OTHER MODELS =================
admin.site.register(AboutPage)
admin.site.register(StudentProfile)
