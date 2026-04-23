from django import forms
from django.core.exceptions import ValidationError

from leagues.models import League
from players.models import Player
from .models import Match, Matchday


class MatchAdminForm(forms.ModelForm):
    league = forms.ModelChoiceField(
        queryset=League.objects.all().order_by("name"),
        required=False,
        label="Liga",
    )

    class Meta:
        model = Match
        fields = [
            "league",
            "matchday",
            "player1",
            "player2",
            "player1_legs",
            "player2_legs",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["matchday"].queryset = Matchday.objects.none()
        self.fields["player1"].queryset = Player.objects.none()
        self.fields["player2"].queryset = Player.objects.none()

        league = None
        matchday = None

        # Beim Bearbeiten bestehender Spiele
        if self.instance and self.instance.pk:
            if self.instance.matchday_id:
                matchday = self.instance.matchday
                league = matchday.league
                self.fields["league"].initial = league

        # Liga aus POST
        elif self.data.get("league"):
            try:
                league = League.objects.get(pk=int(self.data.get("league")))
            except (ValueError, TypeError, League.DoesNotExist):
                league = None

        # Liga aus URL
        elif self.request and self.request.GET.get("league"):
            try:
                league = League.objects.get(pk=int(self.request.GET.get("league")))
                self.fields["league"].initial = league
            except (ValueError, TypeError, League.DoesNotExist):
                league = None

        # Matchday aus POST
        if self.data.get("matchday"):
            try:
                matchday = Matchday.objects.get(pk=int(self.data.get("matchday")))
            except (ValueError, TypeError, Matchday.DoesNotExist):
                matchday = None
        elif self.request and self.request.GET.get("matchday"):
            try:
                matchday = Matchday.objects.get(pk=int(self.request.GET.get("matchday")))
            except (ValueError, TypeError, Matchday.DoesNotExist):
                matchday = None

        if league:
            self.fields["matchday"].queryset = Matchday.objects.filter(
                league=league
            ).order_by("number")

            player_ids = set(
                league.league_players.values_list("player_id", flat=True)
            )

            # Wenn ein Spieltag gewählt ist:
            # alle Spieler rausfiltern, die dort schon gespielt haben
            if matchday:
                used_player_ids = set()

                existing_matches = Match.objects.filter(matchday=matchday)
                if self.instance and self.instance.pk:
                    existing_matches = existing_matches.exclude(pk=self.instance.pk)

                for existing_match in existing_matches:
                    used_player_ids.add(existing_match.player1_id)
                    used_player_ids.add(existing_match.player2_id)

                player_ids = player_ids - used_player_ids

                # Beim Bearbeiten aktuelles Spielerpaar trotzdem wieder erlauben
                if self.instance and self.instance.pk:
                    player_ids.add(self.instance.player1_id)
                    player_ids.add(self.instance.player2_id)

            player_qs = Player.objects.filter(id__in=player_ids).order_by("display_name")

            self.fields["player1"].queryset = player_qs
            self.fields["player2"].queryset = player_qs

    def clean(self):
        cleaned_data = super().clean()

        league = cleaned_data.get("league")
        matchday = cleaned_data.get("matchday")
        player1 = cleaned_data.get("player1")
        player2 = cleaned_data.get("player2")

        if not league:
            raise ValidationError("Bitte zuerst eine Liga auswählen.")

        if not matchday:
            raise ValidationError("Bitte einen Spieltag auswählen.")

        if matchday.league_id != league.id:
            raise ValidationError("Der Spieltag gehört nicht zur gewählten Liga.")

        if player1 and player2 and player1 == player2:
            raise ValidationError("Ein Spieler kann nicht gegen sich selbst spielen.")

        allowed_player_ids = set(
            league.league_players.values_list("player_id", flat=True)
        )

        if player1 and player1.id not in allowed_player_ids:
            raise ValidationError("Spieler 1 gehört nicht zur gewählten Liga.")

        if player2 and player2.id not in allowed_player_ids:
            raise ValidationError("Spieler 2 gehört nicht zur gewählten Liga.")

        # Prüfung: an diesem Spieltag darf kein Spieler zweimal spielen
        existing_matches = Match.objects.filter(matchday=matchday)
        if self.instance and self.instance.pk:
            existing_matches = existing_matches.exclude(pk=self.instance.pk)

        used_player_ids = set()
        for existing_match in existing_matches:
            used_player_ids.add(existing_match.player1_id)
            used_player_ids.add(existing_match.player2_id)

        if player1 and player1.id in used_player_ids:
            raise ValidationError("Spieler 1 hat an diesem Spieltag bereits ein Spiel.")

        if player2 and player2.id in used_player_ids:
            raise ValidationError("Spieler 2 hat an diesem Spieltag bereits ein Spiel.")

        return cleaned_data