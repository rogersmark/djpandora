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

    def _get_polling(self):
        if self.stationpoll_set.filter(active=True):
            return True
        else:
            return False

    polling = property(_get_polling)

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
    played = models.DateTimeField(blank=True, null=True)
    is_playing = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.title, self.station)

    def _get_votes(self):
        votes = self.vote_set.all()
        vote_total = 0
        for vote in votes:
            vote_total += vote.value
        return vote_total

    vote_total = property(_get_votes)

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
    value = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s vote on %s in %s' % (self.user, self.song, self.station)


class StationPoll(models.Model):

    station = models.ForeignKey(Station)
    time_started = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Poll: %s, Active=%s' % (self.station, self.active)

    def _get_votes(self):
        votes = self.stationvote_set.all()
        vote_total = 0
        for vote in votes:
            vote_total += vote.value
        return vote_total

    vote_total = property(_get_votes)

class StationVote(models.Model):

    class Meta:
        unique_together = (('user', 'poll'))

    user = models.ForeignKey(User)
    poll = models.ForeignKey(StationPoll)
    value = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s vote on %s' % (self.user.username, self.poll)