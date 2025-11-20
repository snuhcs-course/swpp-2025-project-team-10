from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_initial_taste',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='UserTaste',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorite_genres', models.JSONField(default=list, help_text='List of favorite book genres')),
                ('reading_frequency', models.CharField(choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly'), ('RARELY', 'Rarely')], default='RARELY', max_length=20)),
                ('preferred_language', models.CharField(choices=[('KOREAN', 'Korean'), ('ENGLISH', 'English'), ('BOTH', 'Both')], default='KOREAN', max_length=20)),
                ('reading_style', models.CharField(choices=[('DEEP', 'Deep and thorough'), ('QUICK', 'Quick and efficient'), ('BOTH', 'Depends on the book')], default='BOTH', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='taste', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
