from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_usertaste_options_remove_user_favorite_genres_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="latitude",
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text="Current latitude coordinate",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="longitude",
            field=models.DecimalField(
                max_digits=9,
                decimal_places=6,
                null=True,
                blank=True,
                help_text="Current longitude coordinate",
            ),
        ),
    ]
