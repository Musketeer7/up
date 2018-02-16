import json

from django.test import TestCase, Client


class SmsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_browse(self):
        response = self.client.get('/browse/')
        self.assertEqual(response.status_code, 200)

    def test_sms(self):
        data = {
            'method': 'send_sms',
            'id':1,
            'params': ['9137866088', 'text for test'],
        }
        response = self.client.post('/json/', json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content.decode('UTF-8'))
        self.assertIs(response_content['error'], None)
