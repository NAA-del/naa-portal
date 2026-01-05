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
)


@admin.register(User)
class NAAUserAdmin(BaseUserAdmin):
    model = User

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

    actions = ['verify_members', 'unverify_members']

    @admin.action(description='Verify selected members')
    def verify_members(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, "Selected members have been verified.")

    @admin.action(description='Unverify selected members')
    def unverify_members(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, "Selected members verification revoked.")


# Other models
admin.site.register(Announcement)
admin.site.register(Leader)
admin.site.register(AboutPage)
admin.site.register(Resource)
admin.site.register(StudentProfile)
admin.site.register(StudentAnnouncement)
