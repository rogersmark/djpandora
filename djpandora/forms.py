from django import forms

import models

class Vote(forms.ModelForm):

    class Meta:
        model = models.Vote
        exclude = ('user',)