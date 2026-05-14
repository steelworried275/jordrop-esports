from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='image_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='pandascore_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='image_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='team',
            name='pandascore_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
