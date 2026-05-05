from django.core.exceptions import ValidationError
from django.db import models


class Matchday(models.Model):
    league = models.ForeignKey(
        "leagues.League",
        on_delete=models.CASCADE,
        related_name="matchdays"
    )
    number = models.PositiveIntegerField()
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["league", "number"]
        unique_together = ["league", "number"]

    def __str__(self):
        return f"{self.league} - Spieltag {self.number}"


class Match(models.Model):
    matchday = models.ForeignKey(
        Matchday,
        on_delete=models.CASCADE,
        related_name="matches"
    )
    player1 = models.ForeignKey(
        "players.Player",
        on_delete=models.PROTECT,
        related_name="matches_as_player1"
    )
    player2 = models.ForeignKey(
        "players.Player",
        on_delete=models.PROTECT,
        related_name="matches_as_player2"
    )
    player1_legs = models.PositiveIntegerField(default=0)
    player2_legs = models.PositiveIntegerField(default=0)
    winner = models.ForeignKey(
        "players.Player",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_matches"
    )
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ["matchday", "id"]
        verbose_name = "Spiel"
        verbose_name_plural = "Spiele"

    def __str__(self):
        return f"{self.player1} vs. {self.player2}"

    def clean(self):
        if self.player1 == self.player2:
            raise ValidationError("Ein Spieler kann nicht gegen sich selbst spielen.")

        league = self.matchday.league

        player1_exists = league.league_players.filter(player=self.player1).exists()
        player2_exists = league.league_players.filter(player=self.player2).exists()

        if not player1_exists:
            raise ValidationError("Spieler 1 ist nicht in dieser Liga registriert.")

        if not player2_exists:
            raise ValidationError("Spieler 2 ist nicht in dieser Liga registriert.")

        if self.winner and self.winner not in [self.player1, self.player2]:
            raise ValidationError("Der Gewinner muss Spieler 1 oder Spieler 2 sein.")

        # 🔴 NEU: gesperrte Spieler dürfen nicht spielen
        if self.player1 and self.player1.is_blocked:
            raise ValidationError("Spieler 1 ist gesperrt und kann nicht eingesetzt werden.")

        if self.player2 and self.player2.is_blocked:
            raise ValidationError("Spieler 2 ist gesperrt und kann nicht eingesetzt werden.")

        # Ein Spieler darf pro Spieltag nur einmal spielen
        existing_matches = Match.objects.filter(matchday=self.matchday).exclude(pk=self.pk)

        used_player_ids = set()
        for existing_match in existing_matches:
            used_player_ids.add(existing_match.player1_id)
            used_player_ids.add(existing_match.player2_id)

        if self.player1_id in used_player_ids:
            raise ValidationError("Spieler 1 hat an diesem Spieltag bereits ein Spiel.")

        if self.player2_id in used_player_ids:
            raise ValidationError("Spieler 2 hat an diesem Spieltag bereits ein Spiel.")

    def save(self, *args, **kwargs):
        # Gewinner automatisch setzen
        if self.player1_legs > self.player2_legs:
            self.winner = self.player1
        elif self.player2_legs > self.player1_legs:
            self.winner = self.player2
        else:
            self.winner = None

        # Match als beendet markieren, sobald Legs eingetragen sind
        self.is_finished = (self.player1_legs + self.player2_legs) > 0

        # Validierung ausführen
        self.full_clean()

        super().save(*args, **kwargs)


class MatchPlayerStat(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="player_stats"
    )
    player = models.ForeignKey(
        "players.Player",
        on_delete=models.CASCADE,
        related_name="match_stats"
    )
    avg_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="AVG gesamt"
    )
    avg_first9 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="First 9 AVG"
    )
    avg_to_170 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="AVG to 170"
    )
    checkout_percent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Checkquote %"
    )
    throws_60_plus = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="60+"
    )
    throws_100_plus = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="100+"
    )
    throws_140_plus = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="140+"
    )
    throws_170_plus = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="170+"
    )
    throws_180 = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="180"
    )

    class Meta:
        ordering = ["match", "player__display_name"]
        unique_together = ["match", "player"]
        verbose_name = "Spieler-Statistik"
        verbose_name_plural = "Spieler-Statistiken"

    def __str__(self):
        return f"{self.match} - {self.player}"

    def clean(self):
        if self.match_id and self.player_id:
            if self.player not in [self.match.player1, self.match.player2]:
                raise ValidationError("Der Spieler muss an diesem Match beteiligt sein.")


class MatchSpecial(models.Model):
    class SpecialType(models.TextChoices):
        MAX_180 = "180", "180"
        HIGHFINISH = "highfinish", "Highfinish"

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="specials"
    )
    player = models.ForeignKey(
        "players.Player",
        on_delete=models.CASCADE,
        related_name="match_specials"
    )
    special_type = models.CharField(
        max_length=20,
        choices=SpecialType.choices
    )
    value = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["match", "id"]

    def __str__(self):
        return f"{self.player} - {self.special_type} - {self.value}"

    def clean(self):
        if self.player not in [self.match.player1, self.match.player2]:
            raise ValidationError("Der Spieler muss an diesem Match beteiligt sein.")

        # 🔴 Optional (sehr sinnvoll): gesperrte Spieler auch hier blockieren
        if self.player and self.player.is_blocked:
            raise ValidationError("Gesperrte Spieler können keine Specials eintragen.")

        if self.special_type == self.SpecialType.MAX_180 and self.value < 1:
            raise ValidationError("Für den Typ 180 muss die Anzahl mindestens 1 sein.")

        if self.special_type == self.SpecialType.HIGHFINISH and self.value < 2:
            raise ValidationError("Highfinish muss größer als 1 sein.")