import json
import datetime

from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import list_detail
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.core import serializers

import models, forms, utils

@login_required
def djpandora_index(request):
    """
    Main entry point.

    Check to see if the user has voted on this song/station already. If so,
    we give them the option of reversing their vote.
    """


    return render_to_response('djpandora/index.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def djpandora_vote(request):
    """
    Receives a vote, returns JSON status

    Creates a vote object and applies it to a song. If it's a duplicate we check
    to see if our value reverses our vote, and applies that to the existing
    vote object. This prevents a user from repeatedly voting on a song.
    """
    song = get_object_or_404(models.Song, id=request.GET.get('song_id'))
    if request.GET.get('vote') == 'like':
        vote = 1
    else:
        vote = -1
    instance = models.Vote(user=request.user)
    post = {
        u'station': song.station_id, u'value': vote, 
        u'song': song.id
    }
    vote_obj, created = models.Vote.objects.get_or_create(user=request.user,
        station=song.station, song=song
    )
    vote_obj.value = vote
    vote_obj.save()
    form = forms.Vote(post, instance=instance)
    json_status = {'status': 'success'}
    return HttpResponse(json.dumps(json_status), 
                mimetype='application/json'
    )

@login_required
def djpandora_status(request):
    """
    TODO: Actually call to our Pandora service

    Calls the Pandora service, forms a JSON object and returns it. This function
    should only be called via AJAX calls.
    """
    try:
        s = utils.get_pandora_rpc_conn()
        station = models.Station.objects.get(current=True)
        station_name = station.name
        playlist = s.get_playlist(station.pandora_id)
        song_info = s.current_song()
        song, created = models.Song.objects.get_or_create(
            title=song_info['title'],
            album=song_info['album'],
            pandora_id=song_info['id'],
            artist=song_info['artist'],
            station=station
        )
        song_info['time'] = int(float(song_info['progress']) / float(song_info['length']) * 100.0)
        remaining_time = song_info['length'] - song_info['progress']
        if remaining_time < 30:
            if song.vote_total > 0:
                s.like_song()
            elif song.vote_total < 0:
                s.dislike_song()
    except Exception, e:
        ## Likely a refusal of connection
        print e
        time_left = 0
        station_name = 'null'
        station = None
        playlist = []
        song = None
        song_info = {
            'album': 'null',
            'artist': 'null',
            'id': 'null',
            'length': 50,
            'progress': 0,
            'title': 'null',
            'time': 50,
        }

    playlist_html = '<ul>'
    for x in playlist:
        playlist_html += '<li>%s by %s</li>' % (x['title'], x['artist'])

    playlist_html += '</ul></li></ul>'
    upboat_avail = True
    downboat_avail = True
    vote_total = 0
    if song:
        for vote in song.vote_set.all():
            vote_total += vote.value
        user_vote = song.vote_set.filter(user=request.user)
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

    station_polls = models.StationPoll.objects.filter(active=True)
    station_vote = False
    station_upboat_avail = True
    station_downboat_avail = True
    for poll in station_polls:
        now = datetime.datetime.now()
        diff = now - poll.time_started
        station_votes = models.StationVote.objects.filter(poll=poll,
            user=request.user
        )
        if station_votes:
            user_vote = station_votes[0]
            if user_vote.value == 1:
                station_upboat_avail = False
                station_downboat_avail = True
            else:
                station_upboat_avail = True
                station_downboat_avail = False
        if diff.seconds > 30000:
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

    json_data = {
        'title': song_info['title'],
        'station': station_name,
        'artist': song_info['artist'],
        'votes': vote_total,
        'vote-html': vote_html,
        'time': song_info['time'],
        'album': song_info['album'],
        'upcoming': playlist_html,
        'status': 'success',
        'progress': song_info['progress'],
        'length': song_info['length'],
        'station_vote': station_vote,
        'station_up': station_upboat_avail,
        'station_down': station_downboat_avail
    }
    return HttpResponse(json.dumps(json_data), mimetype='application/json')

@login_required
def djpandora_stations(request):
    """
    Gets all the stations for the currently in use Pandora account, and displays
    them. If a vote is in progress, the station being voted on will be shown 
    as such.
    """
    json_serializer = serializers.get_serializer("json")()
    stations = models.Station.objects.filter(account=settings.PANDORA_USER)
    station_data = json_serializer.serialize(stations, ensure_ascii=False)
    station_data = json.loads(station_data)
    polling = False
    for x in station_data:
        station = models.Station.objects.get(id=x['pk'])
        x['fields']['polling'] = station.polling
        if station.polling:
            polling = True
            poll = models.StationPoll.objects.get(active=True)
            x['fields']['vote_total'] = poll.vote_total

    json_data = {'status': 'success', 'poll': polling, 'items': station_data}
    return HttpResponse(json.dumps(json_data), mimetype="application/json")

@login_required
def start_station_vote(request):
    """
    Starts a station voting poll. If one is already in progress, we fail out.
    Only one poll can be going on at a time.
    """
    json_data = {
        'status': 'success'
    }
    station = get_object_or_404(models.Station, id=request.GET.get('station_id'))
    station_polls = models.StationPoll.objects.filter(active=True)
    if station_polls:
        json_data['status'] = 'failed'
    else:
        poll = models.StationPoll(station=station, active=True)
        poll.save()
        json_data['vote_total'] = poll.vote_total
    
    json_data['pk'] = station.id
    json_data['name'] = station.name
    return HttpResponse(json.dumps(json_data), mimetype='application/json')

@login_required
def station_vote(request):
    """
    Capture a vote from a user, and apply it. Only allows a user to vote
    exactly one time in a poll.
    """
    json_data = {'status': 'success'}
    station = get_object_or_404(models.Station, id=request.GET.get('station_id'))
    value = int(request.GET.get('value'))
    station_poll = models.StationPoll.objects.get(active=True)
    if station_poll.station.id is not station.id:
        json_data['status'] = 'failed'
        return HttpResponse(json.dumps(json_data), mimetype='application/json')

    vote, created = models.StationVote.objects.get_or_create(poll=station_poll,
        user=request.user
    )
    vote.value = value
    vote.save()
    return HttpResponse(json.dumps(json_data), mimetype='application/json')