# Generated by Django 2.2.13 on 2020-07-03 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peeringdb_server', '0040_auto_20200703_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='ixfmemberdata',
            name='reason',
            field=models.CharField(default='', max_length=255),
        ),
    ]
