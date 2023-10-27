from django.contrib import admin
from .models import User, Category, Listings, Watchlist, Comment, Bid

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listings)
admin.site.register(Watchlist)
admin.site.register(Comment)
admin.site.register(Bid)