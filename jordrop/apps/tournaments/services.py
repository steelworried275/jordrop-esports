import math
from .models import Match, Tournament


def generate_single_elimination(tournament: Tournament, teams: list):
    """
    Generate a full single-elimination bracket and persist it to the database.

    Args:
        tournament: Tournament instance (must be saved already).
        teams: List of Team instances. Length need not be a power of 2 —
               odd teams get a bye (team_b=None) in round 1.

    Returns:
        List of all created Match instances.
    """
    if not teams:
        raise ValueError('At least 2 teams are required.')

    n = len(teams)
    total_rounds = math.ceil(math.log2(max(n, 2)))

    # Delete any existing matches for this tournament to avoid duplicates
    tournament.matches.all().delete()

    all_matches = []

    # Round 1: seed teams
    round_1_matches = []
    for i in range(0, n, 2):
        m = Match.objects.create(
            tournament=tournament,
            round_number=1,
            match_number=(i // 2) + 1,
            round_label=_round_label(1, total_rounds),
            team_a=teams[i],
            team_b=teams[i + 1] if i + 1 < n else None,
        )
        round_1_matches.append(m)
        all_matches.append(m)

    # Generate subsequent rounds and wire next_match pointers
    prev_round = round_1_matches
    for r in range(2, total_rounds + 1):
        current_round = []
        pairs = list(zip(prev_round[::2], prev_round[1::2]))
        for j, (m1, m2) in enumerate(pairs):
            nxt = Match.objects.create(
                tournament=tournament,
                round_number=r,
                match_number=j + 1,
                round_label=_round_label(r, total_rounds),
            )
            m1.next_match = nxt
            m1.save(update_fields=['next_match'])
            m2.next_match = nxt
            m2.save(update_fields=['next_match'])
            current_round.append(nxt)
            all_matches.append(nxt)
        prev_round = current_round

    return all_matches


def _round_label(round_number: int, total_rounds: int) -> str:
    """Return a human-readable round name based on distance from the final."""
    distance_from_final = total_rounds - round_number
    labels = {0: 'Final', 1: 'Semi-final', 2: 'Quarter-final'}
    return labels.get(distance_from_final, f'Round {round_number}')
