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
