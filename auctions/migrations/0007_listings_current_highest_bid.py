# Generated by Django 4.2.6 on 2023-10-27 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_comment_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='current_highest_bid',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
