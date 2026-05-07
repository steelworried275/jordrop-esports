import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('accent_color', models.CharField(default='#00e5ff', max_length=7)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='games/')),
                ('description', models.TextField(blank=True)),
            ],
            options={'ordering': ['name'], 'abstract': False},
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField()),
                ('logo', models.ImageField(blank=True, null=True, upload_to='teams/')),
                ('country', models.CharField(blank=True, max_length=100)),
                ('founded', models.IntegerField(blank=True, null=True)),
                ('bio', models.TextField(blank=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='games.game')),
            ],
            options={'ordering': ['name'], 'unique_together': {('game', 'slug')}, 'abstract': False},
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ign', models.CharField(max_length=100, verbose_name='In-game name')),
                ('real_name', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('role', models.CharField(blank=True, max_length=50)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='players/')),
                ('bio', models.TextField(blank=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='games.game')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='players', to='games.team')),
            ],
            options={'ordering': ['ign'], 'abstract': False},
        ),
    ]
