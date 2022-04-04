# Generated by Django 3.0.5 on 2022-04-02 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_appointment_patientid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='age',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='gender',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='height',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='weight',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
    ]
