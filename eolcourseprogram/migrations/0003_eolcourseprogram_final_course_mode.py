# Generated by Django 2.2.16 on 2021-01-21 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eolcourseprogram', '0002_auto_20201203_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='eolcourseprogram',
            name='final_course_mode',
            field=models.CharField(choices=[('credit', 'Credit'), ('audit', 'Audit'), ('verified', 'Verified'), ('no-id-professional', 'No-Id-Professional'), ('masters', "Master's"), ('honor', 'Honor'), ('professional', 'Professional')], default='honor', max_length=100),
            preserve_default=False,
        ),
    ]