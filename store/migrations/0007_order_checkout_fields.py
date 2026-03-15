from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0006_customer_preferred_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_address",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="order",
            name="notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="stripe_session_id",
            field=models.CharField(blank=True, db_index=True, default="", max_length=200),
        ),
    ]
