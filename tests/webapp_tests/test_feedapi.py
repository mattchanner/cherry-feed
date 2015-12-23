import unittest
import json

from webapp import feedapi


class FakeModel(object):

    def feeds(self):
        return [{'title': 'test title', 'url': 'http://feed.com'},
                {'title': 'test title2', 'url': 'http://feed2.com'}]

    def feed_by_id(self, feed_id):
        self.requested_feed_id = feed_id
        return {
            'data': {'items': [{'url': 'url1', 'summary': '<p>summary</p>'}]}
        }


class FeedApiTests(unittest.TestCase):

    def setUp(self):
        self.fake_model = FakeModel()
        self.feed_api = feedapi.FeedApi(self.fake_model)

    def test_get_with_no_params_returns_feed_array_as_json(self):
        json_string = self.feed_api.GET()
        json_data = json.loads(json_string)
        self.assertEqual(len(json_data), 2)
        self.assertEqual(json_data[0]['title'], 'test title')
        self.assertEqual(json_data[1]['title'], 'test title2')

    def test_get_with_id_returns_feed_data_as_json(self):
        json_string = self.feed_api.GET('feed_id')
        json_data = json.loads(json_string)
        self.assertEqual(self.fake_model.requested_feed_id, 'feed_id')
        self.assertEqual(len(json_data['data']['items']), 1)
        self.assertEqual(json_data['data']['items'][0]['url'], 'url1')

    def test_get_with_id_and_index_returns_feed_html(self):
        html_string = self.feed_api.GET('feed_id', '0')
        self.assertTrue('<p>summary</p>' in html_string)
