# Generated by Django 3.2.4 on 2022-07-14 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newProduct', '0030_adjacentcolorproduct_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='have_adjacent_color',
            field=models.BooleanField(default=False),
        ),
    ]
