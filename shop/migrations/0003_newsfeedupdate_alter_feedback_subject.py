# Generated by Django 5.1.3 on 2024-12-21 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_product_special_offer_alter_category_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsFeedUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='newsfeed/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='feedback',
            name='subject',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
