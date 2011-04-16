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
    s = utils.get_pandora_rpc_conn()
    if request.GET.get('vote') == 'like':
        vote = 1
        s.play_sound('upvote')
    else:
        vote = -1
        s.play_sound('downvote')
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
    Calls the Pandora service, forms a JSON object and returns it. This function
    should only be called via AJAX calls.
    """
    song_result = utils.get_song(request.user)
    print song_result
    vote_result = utils.song_voting(request.user, song_result['song'])
    poll_results = utils.station_election(request.user)
    json_data = {
        'title': song_result['song_info']['title'],
        'station': song_result['station_name'],
        'artist': song_result['song_info']['artist'],
        'album_art': song_result['song'].album_art,
        'time': song_result['song_info']['time'],
        'album': song_result['song_info']['album'],        
        'progress': song_result['song_info']['progress'],
        'length': song_result['song_info']['length'],
        'volume': song_result['volume'],
        'upcoming': song_result['playlist'],
        'recents': song_result['recents'],
        'voting': vote_result,
        'station_voting': poll_results,
        'status': 'success',
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
        s = utils.get_pandora_rpc_conn()
        s.play_sound('station')
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

@login_required
def volume_control(request):
    volume = request.GET.get('volume', 0)
    s = utils.get_pandora_rpc_conn()
    if volume == 0:
        s.set_volume(0)
    else:
        level = float(volume) / 100.0
        s.set_volume(level)
    json_data = {'status': 'success'}
    return HttpResponse(json.dumps(json_data), mimetype='application/json')

@login_required
def control_player(request):
    control_type = request.GET.get('control_type', False)
    if not control_type:
        return HttpResponseNotFound()

    s = utils.get_pandora_rpc_conn()
    station = models.Station.objects.get(current=True)
    json_data = {'status': 'success', 'control_type': control_type}

    if control_type == 'play':
        if station.paused:
            s.pause_song(False)
        else:
            s.play_station(station.pandora_id)
    elif control_type == 'pause':
        s.pause_song(True)
        station.paused = True
        station.save()
    elif control_type == 'stop':
        s.stop_song()
    else:
        json_data['status'] = 'failure'
        json_data['error'] = 'Invalid control type'
    return HttpResponse(json.dumps(json_data), mimetype='application/json')
