from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='pandascore_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
