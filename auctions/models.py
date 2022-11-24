from unicodedata import category
from click import pass_context
from django.contrib.auth.models import AbstractUser
from django.db import models
from platformdirs import user_cache_dir


class User(AbstractUser):
    pass

class Category(models.Model):
    title = models.CharField(max_length=64)

class Listing(models.Model):
    title = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    image = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=256)
    price = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=False)
    comment = models.CharField(max_length=1024)

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def save(self, *args, **kwargs):
        latest_bid = Bid.objects.filter(listing=self.listing).first()
        if latest_bid is None:
            if self.amount < Listing.objects.filter(id=self.listing.id).first().price:
                return
            else:
                super().save(*args, **kwargs)
        else:
            if self.amount < latest_bid.amount:
                return
            else:
                super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.listing} - {self.user}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=False)
