# Generated by Django 2.1.7 on 2019-04-12 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0002_auto_20190411_1735'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionquestion',
            name='session',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, related_name='questions', related_query_name='question', to='session.Session'),
            preserve_default=False,
        ),
    ]
