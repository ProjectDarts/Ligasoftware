from django.contrib import admin
from .models import Season, LeagueTier, League, LeaguePlayer
from .forms import LeaguePlayerAdminForm


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")


@admin.register(LeagueTier)
class LeagueTierAdmin(admin.ModelAdmin):
    list_display = ("name", "order")


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "season", "tier", "max_players", "is_public")


@admin.register(LeaguePlayer)
class LeaguePlayerAdmin(admin.ModelAdmin):
    form = LeaguePlayerAdminForm
    list_display = ("player", "league")
    list_filter = ("league__season", "league__tier", "league")
    search_fields = (
        "player__display_name",
        "player__first_name",
        "player__last_name",
        "league__name",
    )