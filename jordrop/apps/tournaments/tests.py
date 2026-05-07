from django.test import TestCase
from apps.games.models import Game, Team
from apps.tournaments.models import Tournament, Match
from apps.tournaments.services import generate_single_elimination


class BracketGenerationTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(name='CS2', slug='cs2-t')
        self.tournament = Tournament.objects.create(
            game=self.game, name='Test Cup', slug='test-cup',
        )
        self.teams = [
            Team.objects.create(game=self.game, name=f'Team {i}', slug=f'team-{i}')
            for i in range(1, 9)  # 8 teams → 3 rounds
        ]

    def test_generates_correct_number_of_matches(self):
        matches = generate_single_elimination(self.tournament, self.teams)
        # 8 teams → 4 QF + 2 SF + 1 F = 7 matches
        self.assertEqual(len(matches), 7)

    def test_round_1_has_four_matches(self):
        generate_single_elimination(self.tournament, self.teams)
        r1 = Match.objects.filter(tournament=self.tournament, round_number=1)
        self.assertEqual(r1.count(), 4)

    def test_final_has_correct_label(self):
        generate_single_elimination(self.tournament, self.teams)
        final = Match.objects.get(tournament=self.tournament, round_number=3)
        self.assertEqual(final.round_label, 'Final')

    def test_semifinal_label(self):
        generate_single_elimination(self.tournament, self.teams)
        sf = Match.objects.filter(tournament=self.tournament, round_number=2)
        self.assertTrue(all(m.round_label == 'Semi-final' for m in sf))

    def test_next_match_pointers_are_set(self):
        generate_single_elimination(self.tournament, self.teams)
        qf_matches = Match.objects.filter(tournament=self.tournament, round_number=1)
        for m in qf_matches:
            self.assertIsNotNone(m.next_match)

    def test_winner_advances_to_next_match(self):
        generate_single_elimination(self.tournament, self.teams)
        qf = Match.objects.filter(tournament=self.tournament, round_number=1).first()
        qf.winner = qf.team_a
        qf.is_finished = True
        qf.save()
        qf.next_match.refresh_from_db()
        self.assertEqual(qf.next_match.team_a, qf.team_a)
