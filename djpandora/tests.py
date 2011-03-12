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
        response = self.client.get(reverse('djpandora_index'))
        self.assertEquals(response.status_code, 302)

        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('djpandora_index'))
        self.assertEquals(response.status_code, 200)

    def test_vote(self):
        self.client.login(username='tester', password='tester')
        valid_url = reverse('djpandora_vote', kwargs={'song_id': 1})
        invalid_url = reverse('djpandora_vote', kwargs={'song_id': 2})
        response = self.client.get(invalid_url)
        self.assertEquals(response.status_code, 404)

        response = self.client.get('%s?vote=like' % valid_url)
        self.assertEquals(response.status_code, 302)

        vote = models.Vote.objects.get(id=1)
        self.assertEquals(vote.value, 1)
