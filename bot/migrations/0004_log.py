# Generated by Django 2.0 on 2017-12-07 21:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20171208_0008'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_log', models.CharField(blank=True, max_length=250, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('date_in', models.DateTimeField(auto_now_add=True, null=True)),
                ('bot_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot.BotUser')),
            ],
            options={
                'verbose_name_plural': 'Логи',
            },
        ),
    ]
