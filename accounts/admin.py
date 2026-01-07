from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    Announcement,
    Leader,
    AboutPage,
    Resource,
    StudentProfile,
    StudentAnnouncement,
    CPDRecord
)


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
    actions = ['verify_members', 'unverify_members']

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