from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_pandascore_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='image_url',
            field=models.URLField(blank=True),
        ),
    ]
