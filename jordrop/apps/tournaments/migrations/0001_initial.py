import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField()),
                ('format', models.CharField(choices=[('single_elimination', 'Single Elimination'), ('double_elimination', 'Double Elimination'), ('round_robin', 'Round Robin')], default='single_elimination', max_length=25)),
                ('prize_pool', models.CharField(blank=True, max_length=50)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('upcoming', 'Upcoming'), ('ongoing', 'Ongoing'), ('finished', 'Finished')], default='upcoming', max_length=10)),
                ('description', models.TextField(blank=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournaments', to='games.game')),
            ],
            options={'ordering': ['-start_date'], 'abstract': False},
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('round_number', models.PositiveSmallIntegerField()),
                ('match_number', models.PositiveSmallIntegerField()),
                ('round_label', models.CharField(blank=True, max_length=50)),
                ('score_a', models.PositiveSmallIntegerField(default=0)),
                ('score_b', models.PositiveSmallIntegerField(default=0)),
                ('played_at', models.DateTimeField(blank=True, null=True)),
                ('is_finished', models.BooleanField(default=False)),
                ('next_match', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeder_matches', to='tournaments.match')),
                ('team_a', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='home_matches', to='games.team')),
                ('team_b', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='away_matches', to='games.team')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='tournaments.tournament')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='won_matches', to='games.team')),
            ],
            options={'ordering': ['round_number', 'match_number'], 'unique_together': {('tournament', 'round_number', 'match_number')}, 'abstract': False},
        ),
    ]
