from django.db import models

# Create your models here.
class NewsListing(models.Model):
    queryId = models.CharField(max_length=20, unique=True)
    query   = models.CharField(max_length=100)
    sources = models.CharField(max_length=200)
    secrecy = models.PositiveIntegerField()
    lastuser= models.CharField(max_length=200)
    
    def __str__(self):
        return "{}".format(self.queryId)
    
class UserXtraAuth(models.Model):
    username = models.CharField(max_length=200)
    secrecy  = models.PositiveIntegerField()
    tokenkey = models.CharField(max_length=20)