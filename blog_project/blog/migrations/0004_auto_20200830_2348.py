# Generated by Django 3.1 on 2020-08-30 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20200830_2222'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogcomment',
            options={'ordering': ['-timeStamp']},
        ),
    ]