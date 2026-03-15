from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_product_code_product_grade_product_pack_quantity_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="preferred_address",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
