from django.contrib import admin
from django import forms
from .forms import MatchAdminForm
from .models import Matchday, Match, MatchSpecial, MatchPlayerStat


@admin.register(Matchday)
class MatchdayAdmin(admin.ModelAdmin):
    list_display = ("league", "number", "date")
    list_filter = ("league__season", "league__tier", "league")
    search_fields = ("league__name",)


class MatchPlayerStatInline(admin.TabularInline):
    model = MatchPlayerStat
    extra = 2
    max_num = 2
    can_delete = False

    fields = (
        "stat_player_label",
        "player",
        "avg_total",
        "avg_first9",
        "avg_to_170",
        "checkout_percent",
        "throws_60_plus",
        "throws_100_plus",
        "throws_140_plus",
        "throws_170_plus",
        "throws_180",
    )

    readonly_fields = ("stat_player_label",)

    verbose_name = "Spiel-Wert"
    verbose_name_plural = "Spiel-Werte aus Screenshot"

    def stat_player_label(self, obj):
        if obj and obj.player_id:
            return obj.player.display_name
        return "wird automatisch gesetzt"

    stat_player_label.short_description = "Spieler"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "player":
            kwargs["widget"] = forms.HiddenInput

        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "player":
            field.required = False

        return field


class MatchSpecialInline(admin.TabularInline):
    model = MatchSpecial
    extra = 0

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "special_type":
            kwargs["choices"] = (
                ("highfinish", "Highfinish"),
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)


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
    inlines = [MatchPlayerStatInline, MatchSpecialInline]

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

    def save_formset(self, request, form, formset, change):
        if formset.model == MatchPlayerStat:
            match = form.instance
            players = [match.player1, match.player2]

            instances = formset.save(commit=False)

            for index, instance in enumerate(instances):
                if index < len(players):
                    instance.player = players[index]

                instance.match = match
                instance.save()

            for deleted_object in formset.deleted_objects:
                deleted_object.delete()

            formset.save_m2m()
            return

        super().save_formset(request, form, formset, change)


@admin.register(MatchSpecial)
class MatchSpecialAdmin(admin.ModelAdmin):
    list_display = ("match", "player", "special_type", "value")
    list_filter = ("special_type", "match__matchday__league")
    search_fields = (
        "player__display_name",
        "match__player1__display_name",
        "match__player2__display_name",
    )

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "special_type":
            kwargs["choices"] = (
                ("highfinish", "Highfinish"),
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(MatchPlayerStat)
class MatchPlayerStatAdmin(admin.ModelAdmin):
    list_display = (
        "match",
        "player",
        "avg_total",
        "avg_first9",
        "avg_to_170",
        "checkout_percent",
        "throws_60_plus",
        "throws_100_plus",
        "throws_140_plus",
        "throws_170_plus",
        "throws_180",
    )
    list_filter = ("match__matchday__league",)
    search_fields = (
        "player__display_name",
        "player__discord_name",
        "player__autodarts_name",
        "match__player1__display_name",
        "match__player2__display_name",
    )