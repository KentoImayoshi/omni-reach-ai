from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("analytics", "0004_insight_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="insight",
            name="confidence_score",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
