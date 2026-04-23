from django import forms

from players.models import Player
from .models import LeaguePlayer


class LeaguePlayerAdminForm(forms.ModelForm):
    class Meta:
        model = LeaguePlayer
        fields = ["league", "player"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assigned_player_ids = LeaguePlayer.objects.values_list("player_id", flat=True)

        # Neuer Eintrag: nur Spieler, die noch in keiner Liga sind
        if not self.instance.pk:
            self.fields["player"].queryset = Player.objects.exclude(
                id__in=assigned_player_ids
            ).order_by("display_name")

        # Bestehenden Eintrag bearbeiten:
        # aktueller Spieler bleibt auswählbar, alle anderen bereits zugewiesenen nicht
        else:
            self.fields["player"].queryset = Player.objects.exclude(
                id__in=assigned_player_ids
            ).union(
                Player.objects.filter(id=self.instance.player_id)
            ).order_by("display_name")