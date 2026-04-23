from django.shortcuts import get_object_or_404, render
from leagues.models import League
from matches.models import Matchday


def home(request):
    leagues = League.objects.all().select_related("season", "tier")
    return render(request, "public/home.html", {"leagues": leagues})


def league_list(request):
    leagues = League.objects.all().select_related("season", "tier")
    return render(request, "public/league_list.html", {"leagues": leagues})


def league_detail(request, league_id):
    league = get_object_or_404(
        League.objects.select_related("season", "tier"),
        id=league_id,
    )

    league_players = list(
        league.league_players
        .select_related("player")
        .order_by("player__display_name")
    )

    matchdays = (
        Matchday.objects.filter(league=league)
        .prefetch_related(
            "matches__player1",
            "matches__player2",
            "matches__winner",
            "matches__specials__player",
        )
        .order_by("number")
    )

    table = {}

    # entry_order bleibt in Reihenfolge der Liga-Eintragung erhalten
    league_entries_for_ranking = list(
        league.league_players.select_related("player").all()
    )

    for entry_index, entry in enumerate(league_entries_for_ranking, start=1):
        player = entry.player
        table[player.id] = {
            "player": player,
            "matches": 0,
            "wins": 0,
            "losses": 0,
            "points": 0,
            "legs_for": 0,
            "legs_against": 0,
            "leg_diff": 0,
            "match_diff": 0,
            "count_180": 0,
            "best_highfinish": 0,
            "entry_order": entry_index,
        }

    for matchday in matchdays:
        matches = list(matchday.matches.all())

        for match in matches:
            specials = list(match.specials.all())

            match.specials_180 = [
                special for special in specials if special.special_type == "180"
            ]
            match.specials_highfinish = [
                special for special in specials if special.special_type == "highfinish"
            ]
            match.has_180 = len(match.specials_180) > 0
            match.has_highfinish = len(match.specials_highfinish) > 0

            if not match.is_finished:
                continue

            player1 = match.player1
            player2 = match.player2

            if player1.id not in table or player2.id not in table:
                continue

            table[player1.id]["matches"] += 1
            table[player2.id]["matches"] += 1

            table[player1.id]["legs_for"] += match.player1_legs
            table[player1.id]["legs_against"] += match.player2_legs

            table[player2.id]["legs_for"] += match.player2_legs
            table[player2.id]["legs_against"] += match.player1_legs

            if match.winner_id == player1.id:
                table[player1.id]["wins"] += 1
                table[player1.id]["points"] += 3
                table[player2.id]["losses"] += 1

            elif match.winner_id == player2.id:
                table[player2.id]["wins"] += 1
                table[player2.id]["points"] += 3
                table[player1.id]["losses"] += 1

            for special in specials:
                if special.player_id not in table:
                    continue

                if special.special_type == "180":
                    table[special.player_id]["count_180"] += special.value

                elif special.special_type == "highfinish":
                    if special.value > table[special.player_id]["best_highfinish"]:
                        table[special.player_id]["best_highfinish"] = special.value

    for row in table.values():
        row["leg_diff"] = row["legs_for"] - row["legs_against"]
        row["match_diff"] = row["wins"] - row["losses"]

    ranking = sorted(
        table.values(),
        key=lambda row: (
            -row["points"],
            -row["leg_diff"],
            row["entry_order"],
        )
    )

    for index, row in enumerate(ranking, start=1):
        row["position"] = index

    context = {
        "league": league,
        "league_players": league_players,
        "matchdays": matchdays,
        "ranking": ranking,
    }
    return render(request, "public/league_detail.html", context)


def league_specials(request, league_id):
    league = get_object_or_404(
        League.objects.select_related("season", "tier"),
        id=league_id,
    )

    matchdays = (
        Matchday.objects.filter(league=league)
        .prefetch_related(
            "matches__player1",
            "matches__player2",
            "matches__specials__player",
        )
        .order_by("number")
    )

    specials_180 = []
    highfinishes = []

    for matchday in matchdays:
        for match in matchday.matches.all():
            for special in match.specials.all():
                entry = {
                    "matchday": matchday,
                    "match": match,
                    "player": special.player,
                    "value": special.value,
                }

                if special.special_type == "180":
                    specials_180.append(entry)

                elif special.special_type == "highfinish":
                    highfinishes.append(entry)

    highfinishes.sort(key=lambda item: -item["value"])

    context = {
        "league": league,
        "specials_180": specials_180,
        "highfinishes": highfinishes,
    }
    return render(request, "public/league_specials.html", context)