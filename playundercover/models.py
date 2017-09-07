from django.db import models


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


class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50)

    class Meta:
        app_label = 'playundercover'


class UserPair(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    pair = models.ForeignKey(Pair)

    class Meta:
        app_label = 'playundercover'


class Namelist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=14)

    class Meta:
        app_label = 'playundercover'