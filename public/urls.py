from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("ligen/", views.league_list, name="league_list"),
    path("ligen/<int:league_id>/", views.league_detail, name="league_detail"),
    path("ligen/<int:league_id>/specials/", views.league_specials, name="league_specials"),
]