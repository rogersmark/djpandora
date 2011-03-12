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
    	response = self.client.get(reverse('djpandora_vote'))
    	self.assertEquals(response.status_code, 200)

    	response = self.client.post(reverse('djpandora_vote'), {})
    	self.assertEquals(response.status_code, 200)

    	post = {
    		u'station': [u'1'], u'value': [u'1'], u'song': [u'1']
    	}
    	response = self.client.post(reverse('djpandora_vote'), post)
    	self.assertEquals(response.status_code, 302)
