import unittest
import models


class FeedStoreTests(unittest.TestCase):

    def __init__(self):
        self.parse_requests = []

    def fake_parser(self, url):
        self.parse_requests.append(url)
        return {'url': url}

    def test_store_fetches_feeds_when_initialized(self):

        models.feeds.FeedStore({
            'feeds': [
                {'title': 'test title', 'url': 'http://feed.com'},
                {'title': 'test title2', 'url': 'http://feed2.com'}
            ]},
            self.fake_parser)

        assert 'http://feed.com' in self.parse_requests
        assert 'http://feed2.com' in self.parse_requests


if __name__ == '__main__':
    unittest.main()
