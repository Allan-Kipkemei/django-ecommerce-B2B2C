# Generated by Django 3.2.4 on 2022-03-29 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0015_item_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='phone',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
