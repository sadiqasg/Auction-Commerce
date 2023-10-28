from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.category

class Listings(models.Model):
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=300)
    image_url = models.CharField(max_length=300)
    bid_price = models.IntegerField()
    current_highest_bid = models.IntegerField(default=0, blank=True, null=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listed_by")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="listings_category")
    is_active = models.BooleanField(default=True)
    watchers = models.ManyToManyField(User, through='Watchlist', related_name="watchlist_items")

    def __str__(self):
        return self.title
    

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="user_bid_listing")
    bid_amount = models.IntegerField()

    def __str__(self):
        return str(self.bid_amount)


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user.username}'s Watchlist"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="user_comment_listing")
    message = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.author.username}'s comment"
    
