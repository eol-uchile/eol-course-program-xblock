# Generated by Django 2.2.16 on 2021-01-21 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eolcourseprogram', '0004_auto_20210121_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eolcourseprogram',
            name='final_course_mode',
            field=models.CharField(blank=True, choices=[('verified', 'Verified'), ('masters', "Master's"), ('honor', 'Honor'), ('professional', 'Professional'), ('no-id-professional', 'No-Id-Professional'), ('credit', 'Credit'), ('audit', 'Audit')], max_length=100, null=True),
        ),
    ]