# Generated by Django 3.2.4 on 2022-04-22 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0015_auto_20220422_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceprovider',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
