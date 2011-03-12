import json

from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import list_detail
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail

import models, forms

@login_required
def djpandora_index(request):
    song = models.Song.objects.get(id=1)
    upboat_avail = True
    downboat_avail = True
    user_vote = song.vote_set.filter(user=request.user)
    if user_vote:
        user_vote = user_vote[0]
        if user_vote.value == 1:
            upboat_avail = False
        elif user_vote.value == -1:
            downboat_avail = False

    return render_to_response('djpandora/index.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def djpandora_vote(request, song_id):
    song = get_object_or_404(models.Song, id=song_id)
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