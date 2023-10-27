from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from .models import User, Listings, Category, Comment, Bid


def index(request):
    active_listings = Listings.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        # Get the form data
        title = request.POST["title"]
        desc = request.POST["description"]
        image_url = request.POST["image_url"]
        bid_price = request.POST["bid_price"]
        category = request.POST["category"]

        # Get actual category data that matches the value we selected
        cat = Category.objects.get(category=category)

        # Get the current signed in user (authenticated user can be gotten from the request body)
        user = request.user

        new_listing = Listings(
            title=title, 
            desc=desc, 
            image_url=image_url, 
            bid_price=bid_price, 
            category=cat, 
            listed_by=user
        )
        new_listing.save()
        
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })
    

def listing_view(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing=listing)

    if request.user.is_authenticated:
        bids = Bid.objects.filter(pk=listing_id)
        total_bids = bids.count()
        current_user = request.user
        is_owner = current_user.username == listing.listed_by.username
        user_bids = Bid.objects.filter(user=current_user)
        user_max_bid = user_bids.aggregate(Max('bid_amount'))['bid_amount__max']
        is_highest_bidder = user_max_bid == listing.current_highest_bid

        print(f"user_max_bid: {user_max_bid}, listing.current_highest_bid: {listing.current_highest_bid}")

        
        if request.method == "POST":
            current_user = request.user
            listing = Listings.objects.get(pk=listing_id)
            new_bid_amount = int(request.POST["bid_amount"])

            if new_bid_amount > listing.bid_price and new_bid_amount > listing.current_highest_bid:
                listing.current_highest_bid = new_bid_amount
                listing.save()

                bid = Bid(user=current_user, listing=listing, bid_amount=new_bid_amount)
                bid.save()

                return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comments": comments,
                    "total_bids": total_bids,
                    "is_owner": is_owner,
                    "is_highest_bidder": is_highest_bidder,
                    "message": "Amount must be higher than the starting bid and highest bid",
                })
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "total_bids": total_bids,
                "is_owner": is_owner,
                "is_highest_bidder": is_highest_bidder,
            })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
        })


def categories_view(request):
    all_categories = Category.objects.all()

    if request.method == "POST":
        selected_category = request.POST["category"]
        category = Category.objects.get(category=selected_category)
        active_listings = Listings.objects.filter(is_active=True, category=category)

        return render(request, "auctions/categories.html", {
            "category": selected_category,
            "categories": all_categories,
            "listings": active_listings
        })
    
    else:
        return render(request, "auctions/categories.html", {
            "categories": all_categories,
        })

def watchlist_view(request):
    current_user = request.user
    listings_watched = current_user.watchlist_items.all() # using the related_name yay!
    return render(request, "auctions/watchlist.html", {
        "listings": listings_watched
    })


def add_watch(request, listing_id):
    current_listing = Listings.objects.get(pk=listing_id)
    current_user = request.user
    current_listing.watchers.add(current_user)

    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id, )))


def remove_watch(request, listing_id):
    current_listing = Listings.objects.get(pk=listing_id)
    current_user = request.user
    current_listing.watchers.remove(current_user)

    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id, )))

def comment(request, listing_id):
    if request.method == "POST":
        current_user = request.user
        listing = Listings.objects.get(pk=listing_id)
        comment = request.POST["comment"]

        new_comment = Comment(
            author=current_user,
            listing=listing,
            message=comment
        )

        new_comment.save()
        return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))
    
        

def close_listing(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    current_user = request.user
    comments = Comment.objects.filter(listing=listing)
    bids = Bid.objects.filter(pk=listing_id)
    total_bids = bids.count()
    is_owner = current_user.username == listing.listed_by.username
    user_bids = Bid.objects.filter(user=current_user)
    user_max_bid = user_bids.aggregate(Max('bid_amount'))['bid_amount__max']
    is_highest_bidder = user_max_bid == listing.current_highest_bid

    if current_user.username == listing.listed_by.username:
        listing.is_active = False
        listing.save()

        return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id, )))

        # return render(request, "auctions/listing.html", {
        #     "listing": listing,
        #     "comments": comments,
        #     "total_bids": total_bids,
        #     "is_owner": is_owner,
        #     "is_highest_bidder": is_highest_bidder,
        # })