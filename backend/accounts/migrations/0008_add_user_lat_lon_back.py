from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Restore latitude/longitude fields on User for proximity features.
    """

    dependencies = [
        ("accounts", "0007_remove_user_latitude_remove_user_longitude_and_more"),
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
