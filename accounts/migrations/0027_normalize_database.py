from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_alter_role_options_alter_role_name_and_more'),  # Adjust to your last migration
    ]

    operations = [
        # Add database indexes for faster queries
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['membership_tier', 'is_verified'], name='user_tier_verified_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='user_email_idx'),
        ),
        migrations.AddIndex(
            model_name='announcement',
            index=models.Index(fields=['-date_posted', 'is_published'], name='announcement_date_pub_idx'),
        ),
        migrations.AddIndex(
            model_name='announcement',
            index=models.Index(fields=['featured', '-date_posted'], name='announcement_featured_idx'),
        ),
        migrations.AddIndex(
            model_name='cpdrecord',
            index=models.Index(fields=['user', '-date_completed', 'is_verified'], name='cpd_user_date_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read', '-created_at'], name='notif_user_read_idx'),
        ),
        migrations.AddIndex(
            model_name='committeereport',
            index=models.Index(fields=['committee', '-uploaded_at'], name='report_comm_date_idx'),
        ),
        migrations.AddIndex(
            model_name='committeeannouncement',
            index=models.Index(fields=['committee', '-date_posted'], name='commann_comm_date_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['status', 'is_public', '-created_at'], name='article_status_idx'),
        ),
        
        # Make Role.name unique to prevent duplicates
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=50, unique=True, db_index=True),
        ),
        
        # Make EmailUpdate.title unique
        migrations.AlterField(
            model_name='emailupdate',
            name='title',
            field=models.CharField(max_length=200, unique=True, help_text="Internal name for admins"),
        ),
    ]