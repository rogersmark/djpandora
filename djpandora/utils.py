import datetime
import xmlrpclib
import json

from django.conf import settings
from django.core import serializers

import models

def get_pandora_rpc_conn():
    try:
        host = settings.PANDORA_RPC_HOST
    except AttributeError:
        host = 'localhost'
    try:
        port = settings.PANDORA_RPC_PORT
    except AttributeError:
        port = '8123'
    s = xmlrpclib.ServerProxy('http://%s:%s' % (host, port))
    return s

def get_song(user):
    result = {
        'song_info': {
            'album': 'null',
            'artist': 'null',
            'id': 'null',
            'length': 50,
            'progress': 0,
            'title': 'null',
            'time': 50,
            'album_art': None,
        },
        'status': 'Stopped',
        'volume': 0,
        'station_name': None,
        'time_left': 0,
        'playlist': [],
        'song': None,
        'recents': []
    }
    try:
        s = get_pandora_rpc_conn()
        station = models.Station.objects.get(current=True)
        result['station_name'] = station.name
        result['playlist'] = s.get_playlist(station.pandora_id)
        song_info = s.current_song()
        song, created = models.Song.objects.get_or_create(
            title=song_info['title'],
            album=song_info['album'],
            pandora_id=song_info['id'],
            artist=song_info['artist'],
            station=station,
            album_art=song_info['art']
        )
        song.played = datetime.datetime.now()
        if not song.is_playing:
            song.is_playing = True
            old_song = models.Song.objects.filter(is_playing=True)
            if old_song:
                old_song = old_song[0]
                old_song.is_playing = False
                old_song.save()
        
        song.save()

        result['song'] = song
        if song_info['progress'] is 0:
            song_info['time'] = 0
        else:
            song_info['time'] = int(float(song_info['progress']) / float(song_info['length']) * 100.0)

        if song_info['length'] is 0:
            song_info['length'] = 100
        remaining_time = song_info['length'] - song_info['progress']
        song_info['album_art'] = song.album_art

        if remaining_time < 30:
            ## If greater than 0, and not liked previously
            if song.vote_total > 0 and not song.liked:
                song.liked = True
                song.save()
                s.like_song()

            ## If less than 0 and not disliked previously
            elif song.vote_total < 0 and song.liked:
                song.liked = False
                song.save()
                s.dislike_song()

        result['song_info'] = song_info
        result['volume'] = s.get_volume()
        result['status'] = station.get_status_display()

        ## Get recents
        recent_songs = station.song_set.all().order_by('-played')[1:6]
        recents = []
        for rs in recent_songs:
            voting = song_voting(user, rs)
            rs_dict = {'title': rs.title, 'artist': rs.artist}
            rs_dict.update(voting)
            recents.append(rs_dict)

        result['recents'] = recents
    except Exception, e:
        ## Likely a refusal of connection
        print e
    
    return result

def song_voting(user, song=None):
    upboat_avail = True
    downboat_avail = True
    vote_total = 0
    song_id = None
    if song:
        song_id = song.id
        for vote in song.vote_set.all():
            vote_total += vote.value
        user_vote = song.vote_set.filter(user=user)
        if user_vote:
            user_vote = user_vote[0]
            if user_vote.value == 1:
                upboat_avail = False
            elif user_vote.value == -1:
                downboat_avail = False

    ## Grab 10 most recent votes
    votes = models.Vote.objects.all().order_by('-modified')[:10]
    recent_votes = []
    for vote in votes:
        rv = {'user': vote.user.username, 'song': vote.song.title, 
            'value': vote.value}
        recent_votes.append(rv)
    return {'vote_total': vote_total,
        'upboat_avail': upboat_avail, 'downboat_avail': downboat_avail,
        'song_id': song_id, 'recents': recent_votes
    }

def station_election(user):
    station_polls = models.StationPoll.objects.filter(active=True)
    station = models.Station.objects.get(current=True)
    station_vote = False
    station_upboat_avail = True
    station_downboat_avail = True
    for poll in station_polls:
        now = datetime.datetime.now()
        diff = now - poll.time_started
        station_votes = models.StationVote.objects.filter(poll=poll,
            user=user
        )
        if station_votes:
            user_vote = station_votes[0]
            if user_vote.value == 1:
                station_upboat_avail = False
                station_downboat_avail = True
            else:
                station_upboat_avail = True
                station_downboat_avail = False
        if diff.seconds > 300:
            s = get_pandora_rpc_conn()
            s.play_station(poll.station.pandora_id)
            poll.active = False
            station_vote = True
            if station:
                station.current = False
                station.save()
            poll.station.current = True
            poll.station.save()
            poll.save()
        else:
            station_vote = True
    return {
        'station_vote': station_vote, 
        'station_upboat_avail': station_upboat_avail,
        'station_downboat_avail': station_downboat_avail
    }
