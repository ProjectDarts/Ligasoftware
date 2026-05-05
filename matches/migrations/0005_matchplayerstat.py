# Generated manually for Autodarts match/player statistics

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0005_alter_player_autodarts_name_and_more"),
        ("matches", "0004_alter_match_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="MatchPlayerStat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("avg_total", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name="AVG gesamt")),
                ("avg_first9", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name="First 9 AVG")),
                ("avg_to_170", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name="AVG to 170")),
                ("checkout_percent", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name="Checkquote %")),
                ("match", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="player_stats", to="matches.match")),
                ("player", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="match_stats", to="players.player")),
            ],
            options={
                "verbose_name": "Spieler-Statistik",
                "verbose_name_plural": "Spieler-Statistiken",
                "ordering": ["match", "player__display_name"],
                "unique_together": {("match", "player")},
            },
        ),
    ]
