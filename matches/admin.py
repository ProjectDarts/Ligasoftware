from django.contrib import admin
from .forms import MatchAdminForm
from .models import Matchday, Match, MatchSpecial


@admin.register(Matchday)
class MatchdayAdmin(admin.ModelAdmin):
    list_display = ("league", "number", "date")
    list_filter = ("league__season", "league__tier", "league")
    search_fields = ("league__name",)


class MatchSpecialInline(admin.TabularInline):
    model = MatchSpecial
    extra = 0


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "matchday",
        "player1",
        "player2",
        "player1_legs",
        "player2_legs",
        "winner",
        "is_finished",
    )
    list_filter = (
        "matchday__league__season",
        "matchday__league__tier",
        "matchday__league",
    )
    search_fields = (
        "player1__display_name",
        "player2__display_name",
        "matchday__league__name",
    )
    inlines = [MatchSpecialInline]

    class Media:
        js = ("admin/js/match_admin.js",)

    def get_form(self, request, obj=None, **kwargs):
        base_form = MatchAdminForm

        class RequestAwareMatchAdminForm(base_form):
            def __init__(self2, *args, **inner_kwargs):
                inner_kwargs["request"] = request
                super().__init__(*args, **inner_kwargs)

        kwargs["form"] = RequestAwareMatchAdminForm
        return super().get_form(request, obj, **kwargs)


@admin.register(MatchSpecial)
class MatchSpecialAdmin(admin.ModelAdmin):
    list_display = ("match", "player", "special_type", "value")
    list_filter = ("special_type", "match__matchday__league")
    search_fields = (
        "player__display_name",
        "match__player1__display_name",
        "match__player2__display_name",
    )