from django.db import models
from django.contrib.auth.models import User

class Station(models.Model):
    """
    A Pandora station, automatically created from calls to our Pandora service

    Currently stubbed out, and just has a name. Will add more data to flesh
    this out once the backend service in pypandora is further along.
    """

    name = models.CharField(max_length=256)
    pandora_id = models.CharField(max_length=256)
    current = models.BooleanField(default=False)
    account = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.name

class Song(models.Model):
    """
    A Pandora song tied to a Station, automatically created from calls to our Pandora service

    Currently stubbed out, and just has a name and station. Will add more data to flesh
    this out once the backend service in pypandora is further along.
    """

    title = models.CharField(max_length=256)
    station = models.ForeignKey(Station)
    album = models.CharField(max_length=512)
    artist = models.CharField(max_length=256)
    pandora_id = models.CharField(max_length=128)

    def __unicode__(self):
        return u'%s - %s' % (self.title, self.station)

class Vote(models.Model):
    """
    A user's voting result. Votes are tallied for specific songs on 
    specific station. 
    """

    class Meta:
        unique_together = (('user', 'song', 'station'))

    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    station = models.ForeignKey(Station)
    value = models.IntegerField()

    def __unicode__(self):
        return u'%s vote on %s in %s' % (self.user, self.song, self.station)