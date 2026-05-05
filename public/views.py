from django.shortcuts import get_object_or_404, render
from leagues.models import League
from players.models import Player
from matches.models import Match, Matchday


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
            "matches__player_stats__player",
        )
        .order_by("number")
    )

    table = {}

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

            match.specials_highfinish = [
                special for special in specials if special.special_type == "highfinish"
            ]
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

            for stat in match.player_stats.all():
                if stat.player_id not in table:
                    continue

                table[stat.player_id]["count_180"] += stat.throws_180 or 0

            for special in specials:
                if special.player_id not in table:
                    continue

                if special.special_type == "highfinish":
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
            "matches__player_stats__player",
        )
        .order_by("number")
    )

    specials_180 = []
    highfinishes = []

    for matchday in matchdays:
        for match in matchday.matches.all():
            for stat in match.player_stats.all():
                if stat.throws_180 and stat.throws_180 > 0:
                    specials_180.append({
                        "matchday": matchday,
                        "match": match,
                        "player": stat.player,
                        "value": stat.throws_180,
                    })

            for special in match.specials.all():
                if special.special_type == "highfinish":
                    highfinishes.append({
                        "matchday": matchday,
                        "match": match,
                        "player": special.player,
                        "value": special.value,
                    })

    highfinishes.sort(key=lambda item: -item["value"])

    context = {
        "league": league,
        "specials_180": specials_180,
        "highfinishes": highfinishes,
    }
    return render(request, "public/league_specials.html", context)


def match_detail(request, match_id):
    match = get_object_or_404(
        Match.objects.select_related(
            "matchday__league__season",
            "matchday__league__tier",
            "player1",
            "player2",
            "winner",
        ).prefetch_related(
            "player_stats__player",
            "specials__player",
        ),
        id=match_id,
    )

    stats_by_player_id = {
        stat.player_id: stat
        for stat in match.player_stats.all()
    }

    player_rows = []
    for player in [match.player1, match.player2]:
        player_rows.append({
            "player": player,
            "stat": stats_by_player_id.get(player.id),
        })

    context = {
        "match": match,
        "league": match.matchday.league,
        "player_rows": player_rows,
        "specials": match.specials.all(),
    }
    return render(request, "public/match_detail.html", context)


def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    stats = (
        player.match_stats
        .select_related(
            "match__matchday__league",
            "match__player1",
            "match__player2",
        )
        .order_by("match__matchday__number", "match__id")
    )

    stat_list = list(stats)

    def average(field_name):
        values = [
            getattr(stat, field_name)
            for stat in stat_list
            if getattr(stat, field_name) is not None
        ]
        if not values:
            return None
        return sum(values) / len(values)

    def total(field_name):
        return sum(
            getattr(stat, field_name) or 0
            for stat in stat_list
        )

    summary = {
        "avg_total": average("avg_total"),
        "avg_first9": average("avg_first9"),
        "avg_to_170": average("avg_to_170"),
        "checkout_percent": average("checkout_percent"),
        "throws_60_plus": total("throws_60_plus"),
        "throws_100_plus": total("throws_100_plus"),
        "throws_140_plus": total("throws_140_plus"),
        "throws_170_plus": total("throws_170_plus"),
        "throws_180": total("throws_180"),
    }

    avg_chart_points = []

    for stat in stat_list:
        if stat.avg_total is not None:
            avg_chart_points.append({
                "matchday": stat.match.matchday.number,
                "avg_total": float(stat.avg_total),
                "avg_first9": float(stat.avg_first9) if stat.avg_first9 else 0,
                "avg_to_170": float(stat.avg_to_170) if stat.avg_to_170 else 0,
            })

    context = {
        "player": player,
        "stats": stat_list,
        "summary": summary,
        "avg_chart_points": avg_chart_points,
    }
    return render(request, "public/player_detail.html", context)