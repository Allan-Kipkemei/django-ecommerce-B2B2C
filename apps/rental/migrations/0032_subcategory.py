# Generated by Django 3.2.4 on 2022-04-26 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0031_item_rooms'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(max_length=255)),
                ('image', models.ImageField(null=True, upload_to='images/')),
            ],
        ),
    ]
