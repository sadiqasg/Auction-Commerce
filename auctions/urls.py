from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("categories", views.categories_view, name="categories"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("close/<int:listing_id>", views.close_listing, name="close"),
    path("add_watch/<int:listing_id>", views.add_watch, name="add_watch"),
    path("remove_watch/<int:listing_id>", views.remove_watch, name="remove_watch"),
]
