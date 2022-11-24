from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category, Bid


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, id):
    listing_ = Listing.objects.filter(id=id).first()
    if request.method == "POST":
        bid = Bid(listing=listing_, user=request.user, amount=request.POST["amount"])
        print(bid)
        bid.save()
    bids = Bid.objects.filter(listing=listing_)
    user_bid = Bid(listing=listing_, user=request.user)
    total_bids = len(bids)
    highest_bid = None
    if total_bids != 0:
        highest_bid = bids[0]
    return render(request, "auctions/listing.html", {
        "listing": listing_,
        "highest_bid": highest_bid,
        "user_bid": user_bid,
        "total_bids": total_bids
    })

def categories(request):
    pass

def watchlist(request):
    pass

@login_required
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        url = request.POST["url"]
        category = Category.objects.filter(title=request.POST["category"]).first()
        description = request.POST["description"]
        price = request.POST["price"]
        listing = Listing(user=request.user, title=title, image=url, category=category, description=description, price=price)
        listing.save()
        return HttpResponseRedirect(reverse("listing", kwargs={"id": listing.id}))
    categories = Category.objects.all()
    return render(request, "auctions/create.html", {
        "categories": categories
    })