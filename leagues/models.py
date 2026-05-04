from django.core.exceptions import ValidationError
from django.db import models


class Season(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


class LeagueTier(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class League(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="leagues"
    )
    tier = models.ForeignKey(
        LeagueTier,
        on_delete=models.PROTECT,
        related_name="leagues"
    )
    name = models.CharField(max_length=100)
    max_players = models.PositiveIntegerField(default=12)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["tier__order", "name"]
        unique_together = ["season", "name"]

    def __str__(self):
        return f"{self.name} ({self.season})"


class LeaguePlayer(models.Model):
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="league_players"
    )
    player = models.ForeignKey(
        "players.Player",
        on_delete=models.CASCADE,
        related_name="league_entries"
    )

    class Meta:
        ordering = ["league", "player"]
        constraints = [
            models.UniqueConstraint(fields=["player"], name="unique_player_one_league"),
        ]

    def __str__(self):
        return f"{self.player} in {self.league}"

    def clean(self):
        if self.player and self.player.is_blocked:
            raise ValidationError("Gesperrte Spieler können keiner Liga zugewiesen werden.")