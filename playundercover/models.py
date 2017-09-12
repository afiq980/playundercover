from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

class Season(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    from_date = models.DateField()
    to_date = models.DateField()

    class Meta:
        app_label = 'playundercover'


class Pair(models.Model):
    id = models.AutoField(primary_key=True)
    word1 = models.CharField(max_length=40)
    word2 = models.CharField(max_length=40)
    level = models.IntegerField(default=0)
    season = models.ForeignKey(Season, blank=True, null=True, default=None)

    class Meta:
        app_label = 'playundercover'


class CustomUser(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name="user")

    class Meta:
        app_label = 'playundercover'


class UserPair(models.Model):
    id = models.AutoField(primary_key=True)
    custom_user = models.ForeignKey(CustomUser)
    pair = models.ForeignKey(Pair)

    class Meta:
        app_label = 'playundercover'


class Namelist(models.Model):
    id = models.AutoField(primary_key=True)
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=14)

    class Meta:
        app_label = 'playundercover'


class PairFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    pair = models.ForeignKey(Pair)
    feedback = models.BooleanField()
    models.DateField(default=datetime.datetime.now())

    class Meta:
        app_label = 'playundercover'


def create_custom_user(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        custom_user = CustomUser(user=user)
        custom_user.save()

post_save.connect(create_custom_user, sender=User)