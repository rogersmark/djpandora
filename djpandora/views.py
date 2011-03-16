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
    form = forms.Vote(post, instance=instance)
    json_status = {'status': 'success'}
    if form.is_valid():
        try:
            form.save()
        except Exception, e:
            ## Unique Error
            vote_obj = models.Vote.objects.get(user=request.user,
                song=song, station=song.station
            )
            if int(vote) == int(vote_obj.value):
                json_status['status'] = 'failed'
            else:
                vote_obj.value = vote
                vote_obj.save()

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
    except Exception, e:
        ## Likely a refusal of connection
        print e
        time_left = 0
        station_name = 'null'
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
        if diff.seconds > 300:
            s = utils.get_pandora_rpc_conn()
            s.play_station(poll.station.pandora_id)
            poll.active = False
            station_vote = True
            poll.save()
            ## TODO: If proper value, we switch stations
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
    json_data = {}
    stations = models.Station.objects.filter(account=settings.PANDORA_USER)
    html = '<ul>'
    for x in stations:
        if x.stationpoll_set.filter(active=True):
            poll = x.stationpoll_set.filter(active=True)[0]
            vote_total = 0
            for vote in poll.stationvote_set.all():
                vote_total += vote.value
            html += '<li style="color: red;">\
                <a style="color: red;" href="#" onclick="javascript: return \
                station_poll(%s);">%s</a>  <a href="#" id="station-up" \
                onclick="javascript: return station_vote(%s, 1);">+</a>  \
                <a href="#" id="station-down" \
                onclick="javascript: return station_vote(%s, -1);">-</a>  \
                (<span style="color: black;" \
                id="station-vote-total">%s</span>)</li>' % (
                x.id, x.name, x.id, x.id, vote_total
            )
        else:
            html += '<li><a href="#" onclick="javascript: return station_poll(%s);">%s</a></li>' % (
                x.id, x.name
            )
    html += '</ul>'
    json_data['html'] = html
    json_data['status'] = 'success'
    return HttpResponse(json.dumps(json_data), mimetype='application/json')

@login_required
def start_station_vote(request):
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

    return HttpResponse(json.dumps(json_data), mimetype='application/json')

@login_required
def station_vote(request):
    json_data = {'status': 'success'}
    station = get_object_or_404(models.Station, id=request.GET.get('station_id'))
    value = int(request.GET.get('value'))
    station_poll = models.StationPoll.objects.get(active=True)
    print station_poll.station
    print station
    if station_poll.station.id is not station.id:
        json_data['status'] = 'failed'
        print "failed"
        return HttpResponse(json.dumps(json_data), mimetype='application/json')

    vote, created = models.StationVote.objects.get_or_create(poll=station_poll,
        user=request.user
    )
    vote.value = value
    vote.save()
    print vote
    return HttpResponse(json.dumps(json_data), mimetype='application/json')