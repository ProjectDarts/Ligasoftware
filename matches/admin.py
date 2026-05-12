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
            valid_player_ids = {player.id for player in players if player}

            # Wichtig:
            # formset.save(commit=False) liefert nur neue/geänderte Inline-Zeilen.
            # Bei einem bestehenden Match mit bereits einer gespeicherten Statistik
            # wurde eine neu nachgetragene zweite Statistik vorher wieder Spieler 1
            # zugeordnet. Das führte bei (match, player) zu einem Unique-Constraint-Fehler
            # und damit zu HTTP 500 im Admin.
            instances = formset.save(commit=False)

            instance_pks = [instance.pk for instance in instances if instance.pk]
            existing_player_by_pk = dict(
                MatchPlayerStat.objects
                .filter(match=match)
                .values_list("pk", "player_id")
            )

            used_player_ids = set(
                MatchPlayerStat.objects
                .filter(match=match)
                .exclude(pk__in=instance_pks)
                .values_list("player_id", flat=True)
            )

            for instance in instances:
                instance.match = match

                # Bestehende Statistikzeilen behalten ihren Spieler.
                # Das Hidden-Feld kann beim Nachbearbeiten leer/instabil sein;
                # die DB ist hier die zuverlässige Quelle.
                if instance.pk and instance.pk in existing_player_by_pk:
                    instance.player_id = existing_player_by_pk[instance.pk]

                # Neue oder ungültig zugeordnete Zeilen bekommen den noch fehlenden
                # Spieler dieses Matches. So kann man Statistiken auch nachträglich
                # einzeln ergänzen, ohne Duplikate zu erzeugen.
                if not instance.player_id or instance.player_id not in valid_player_ids or instance.player_id in used_player_ids:
                    missing_players = [
                        player for player in players
                        if player and player.id not in used_player_ids
                    ]
                    if missing_players:
                        instance.player = missing_players[0]

                instance.save()
                if instance.player_id:
                    used_player_ids.add(instance.player_id)

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