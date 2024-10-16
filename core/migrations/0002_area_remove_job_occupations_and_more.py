# Generated by Django 4.2 on 2024-09-16 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='Номер территориальной зоны')),
            ],
        ),
        migrations.RemoveField(
            model_name='job',
            name='occupations',
        ),
        migrations.RemoveField(
            model_name='worker',
            name='objects_photos',
        ),
        migrations.RemoveField(
            model_name='worker',
            name='occupations',
        ),
        migrations.AddField(
            model_name='job',
            name='permanent_work',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='worker',
            name='permanent_work',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='min_salary',
            field=models.PositiveIntegerField(default=0, verbose_name='Зарплата (от) ₪'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='min_salary',
            field=models.PositiveIntegerField(default=0, verbose_name='Зарплата (от) ₪'),
        ),
        migrations.DeleteModel(
            name='ObjectPhoto',
        ),
        migrations.DeleteModel(
            name='Occupation',
        ),
        migrations.AddField(
            model_name='job',
            name='areas',
            field=models.ManyToManyField(blank=True, related_name='jobs', to='core.area', verbose_name='зоны'),
        ),
        migrations.AddField(
            model_name='worker',
            name='areas',
            field=models.ManyToManyField(blank=True, related_name='workers', to='core.area', verbose_name='зоны'),
        ),
    ]
