from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("ligen/", views.league_list, name="league_list"),
    path("ligen/<int:league_id>/", views.league_detail, name="league_detail"),
    path("ligen/<int:league_id>/specials/", views.league_specials, name="league_specials"),
    path("spiele/<int:match_id>/", views.match_detail, name="match_detail"),
    path("spieler/<int:player_id>/", views.player_detail, name="player_detail"),
]
