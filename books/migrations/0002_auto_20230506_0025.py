# Generated by Django 3.2.18 on 2023-05-05 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30, null=True)),
                ('file', models.FileField(upload_to='files/')),
            ],
        ),
        migrations.AlterField(
            model_name='books',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
