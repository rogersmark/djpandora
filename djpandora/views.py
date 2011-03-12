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
    print request.user.id
    form = forms.Vote(post, instance=instance)
    if form.is_valid():
        form.save()
    return HttpResponseRedirect(reverse('djpandora_index'))