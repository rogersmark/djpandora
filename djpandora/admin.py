from django.contrib import admin

import models

admin.site.register(models.Song)
admin.site.register(models.Station)
admin.site.register(models.Vote)
admin.site.register(models.StationPoll)
admin.site.register(models.StationVote)