from django.db import models
from django.contrib.auth.models import User

class Station(models.Model):

    name = models.CharField(max_length=256)

    def __unicode__(self):
        return u'%s' % self.name

class Song(models.Model):

    name = models.CharField(max_length=256)

    def __unicode__(self):
        return u'%s' % self.name

class Vote(models.Model):

    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    station = models.ForeignKey(Station)
    value = models.IntegerField()

    def __unicode__(self):
        return u'%s vote on %s in %s' % (self.user, self.song, self.station)