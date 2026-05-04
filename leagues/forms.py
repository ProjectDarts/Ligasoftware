from django import forms
from django.core.exceptions import ValidationError

from players.models import Player
from .models import LeaguePlayer


class LeaguePlayerAdminForm(forms.ModelForm):
    class Meta:
        model = LeaguePlayer
        fields = ["league", "player"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assigned_player_ids = LeaguePlayer.objects.values_list("player_id", flat=True)

        # Neuer Eintrag:
        # nur Spieler, die noch in keiner Liga sind UND nicht gesperrt sind
        if not self.instance.pk:
            self.fields["player"].queryset = Player.objects.exclude(
                id__in=assigned_player_ids
            ).filter(
                is_blocked=False
            ).order_by("display_name")

        # Bestehenden Eintrag bearbeiten:
        # aktueller Spieler bleibt auswählbar, aber nur wenn er nicht gesperrt ist
        else:
            self.fields["player"].queryset = (
                Player.objects.exclude(
                    id__in=assigned_player_ids
                ).filter(
                    is_blocked=False
                )
                |
                Player.objects.filter(
                    id=self.instance.player_id,
                    is_blocked=False
                )
            ).order_by("display_name")

    def clean_player(self):
        player = self.cleaned_data["player"]

        if player.is_blocked:
            raise ValidationError("Gesperrte Spieler können keiner Liga zugewiesen werden.")

        return player