"""
URL configuration for naa_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts import views
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import MemberListAPI

urlpatterns = [
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('announcement/<int:pk>/',views.announcement,name='announcement'),
    path('download-constitution/', views.download_constitution, name='download_constitution'),
    path('cpd-tracker/', views.cpd_tracker, name='cpd_tracker'),
    path('resources/', views.resource_library, name='resource_library'),
    path('student-hub/', views.student_hub, name='student_hub'),
    path('member-id/', views.member_id, name='member_id'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('notification/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/members/', MemberListAPI.as_view(), name='member_api'),
    path('committee-dashboard/', views.committee_dashboard, name='committee_dashboard'),
    path('api/exco/all-reports/', views.ExcoReportFetchAPI.as_view(), name='exco_reports_api'),
    path('exco/master-dashboard/', views.exco_master_dashboard, name='exco_master_dashboard'),
    path('exco/verify/<int:user_id>/', views.exco_verify_member, name='exco_verify_member'),
    path('exco/post-national/', views.post_national_announcement, name='post_national_announcement'),
    path('articles/', views.home, name='article_list'), 
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('submit-article/', views.submit_article, name='submit_article'),
    path('exco/export-members/', views.export_members_csv, name='export_members_csv'),
    path('committee/export/<int:committee_id>/', views.export_members_csv, name='export_committee_members_csv'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# This line is the "magic" that makes images show up on your computer
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
