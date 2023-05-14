# Generated by Django 4.2.1 on 2023-05-13 17:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='code',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_code', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='code',
            constraint=models.UniqueConstraint(fields=('code', 'user'), name='code_user_unique'),
        ),
    ]
