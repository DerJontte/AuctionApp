from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class UserSettings(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    currency = models.CharField(max_length=3, null=True, blank=True)


class Auction(models.Model):
    seller_id = models.IntegerField()
    seller_name = models.CharField(max_length=20)
    seller_email = models.EmailField()
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    starting_price = models.FloatField()
    current_price = models.FloatField()
    current_winner_id = models.IntegerField(null=True, blank=True)
    current_winner_name = models.CharField(max_length=20, default='No bids yet.')
    time_posted = models.DateTimeField()
    time_closing = models.DateTimeField()
    active = models.BooleanField(default=True)
    banned = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def get(self, instance):
        return self.serializable_value(instance)

    def __str__(self):
        return self.title


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user_id = models.IntegerField(unique=False)
    name = models.CharField(max_length=20)
    email = models.EmailField()
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __get__(self, instance, owner):
        return self.serializable_value(instance)

    def __str__(self):
        return self.timestamp.strftime('%X') + ' User ' + str(self.name) + ' on auction ' + str(self.auction) + ' (' + str(self.price) + ')'


class ExchangeRate(models.Model):
     code = models.CharField(primary_key=True, max_length=3)
     rate = models.FloatField()
     last_updated = models.DateTimeField(auto_now=True)
