# Generated by Django 5.1.7 on 2025-04-07 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorados', '0002_agendareunioes'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorado',
            name='token',
            field=models.CharField(default=123, max_length=16),
            preserve_default=False,
        ),
    ]
