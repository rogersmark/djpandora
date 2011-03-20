import xmlrpclib

from django.conf import settings

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

def get_song():
    result = {
        'song_info': {
            'album': 'null',
            'artist': 'null',
            'id': 'null',
            'length': 50,
            'progress': 0,
            'title': 'null',
            'time': 50,
        },
        'station_name': None,
        'time_left': 0,
        'playlist': [],
        'song': None
    }
    try:
        s = get_pandora_rpc_conn()
        station = models.Station.objects.get(current=True)
        result['station_name'] = station.name
        result['playlist'] = s.get_playlist(station.pandora_id)
        song_info = s.current_song()
        song, created = models.Song.objects.get_or_create(
            title=result['song_info']['title'],
            album=result['song_info']['album'],
            pandora_id=result['song_info']['id'],
            artist=result['song_info']['artist'],
            station=station
        )
        result['song'] = song
        song_info['time'] = int(float(song_info['progress']) / float(song_info['length']) * 100.0)
        remaining_time = song_info['length'] - song_info['progress']
        if remaining_time < 30:
            if song.vote_total > 0:
                s.like_song()
            elif song.vote_total < 0:
                s.dislike_song()

        result['song_info'] = song_info
    except Exception, e:
        ## Likely a refusal of connection
        print e
    
    return result

def song_voting(user, song=None):
    upboat_avail = True
    downboat_avail = True
    vote_total = 0
    if song:
        for vote in song.vote_set.all():
            vote_total += vote.value
        user_vote = song.vote_set.filter(user=user)
        if user_vote:
            user_vote = user_vote[0]
            if user_vote.value == 1:
                upboat_avail = False
            elif user_vote.value == -1:
                downboat_avail = False
        if upboat_avail and downboat_avail:
            vote_html = """<a href="#" onclick="javascript:return ajax_vote(%s, 'like');">Like</a> - <a href="#" onclick="javascript:return ajax_vote(%s, 'dislike');">Dislike</a>""" % (song.id, song.id)
        elif upboat_avail and not downboat_avail:
            vote_html = """<a href="#" onclick="javascript:return ajax_vote(%s, 'like');">Like</a>""" % (song.id)
        else:
            vote_html = """<a href="#" onclick="javascript:return ajax_vote(%s, 'dislike');">Dislike</a>""" % (song.id)
    else:
        vote_html = ''
    return {'vote_html': vote_html, 'vote_total': vote_total,
        'upboat_avail': upboat_avail, 'downboat_avail': downboat_avail
    }

def station_election(user):
    station_polls = models.StationPoll.objects.filter(active=True)
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
            s = utils.get_pandora_rpc_conn()
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