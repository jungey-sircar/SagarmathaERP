from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0011_holiday_holidaysettings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.CharField(max_length=13),
        ),
    ]
