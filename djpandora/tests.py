import json

from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.core.urlresolvers import reverse

import models

class PandoraTests(TestCase):

    fixtures = ['testdata.json',]

    def setUp(self):
        self.client = Client()

    def test_index(self):
        ## Not logged in
        response = self.client.get(reverse('djpandora_index'))
        self.assertEquals(response.status_code, 302)

        ## Logged in
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('djpandora_index'))
        self.assertEquals(response.status_code, 200)

    def test_vote(self):
        ## Bit of boiler plate
        self.client.login(username='tester', password='tester')
        url = reverse('djpandora_vote')

        ## 404
        response = self.client.get('%s?song_id=11111112&vote=like' % url)
        self.assertEquals(response.status_code, 404)

        ## Received a JSON Response
        response = self.client.get('%s?song_id=1&vote=like' % url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data.get('status'), 'success')

        ## Make sure we created an object
        vote = models.Vote.objects.get(id=1)
        self.assertEquals(vote.value, -1)

        ## Post again, handle a unique error
        response = self.client.get('%s?song_id=1&vote=like' % url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data.get('status'), 'success')

    def test_pandora_status(self):
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('djpandora_status'))
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data.get('status'), 'success')

    def test_pandora_stations(self):
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('djpandora_stations'))
        self.assertEquals(response.status_code, 200)

    def test_station_poll(self):
        self.client.login(username='tester', password='tester')
        url = '%s?station_id=1' % reverse('start_station_vote')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_station_vote(self):
        self.client.login(username='tester', password='tester')
        url = '%s?station_id=1&value=1' % reverse('station_vote')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)