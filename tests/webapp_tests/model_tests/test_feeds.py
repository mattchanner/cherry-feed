import unittest
import time
from webapp.models import feeds


class FeedStoreTests(unittest.TestCase):

    def setUp(self):
        self.parse_requests = []
        self.store = feeds.FeedStore({
            'feeds': [
                {'title': 'test title', 'url': 'http://feed.com'},
                {'title': 'test title2', 'url': 'http://feed2.com'}
            ]},
            self.fake_parser)

    def fake_parser(self, url):
        self.parse_requests.append(url)
        return {
            'feed': {
                'title': 'feed title'
            },
            'url': url,
            'items': [
                {
                    'link': 'http://example.com',
                    'title': 'title text',
                    'summary': 'summary text'
                }
            ]
        }

    def test_store_fetches_feeds_when_initialized(self):
        assert 'http://feed.com' in self.parse_requests
        assert 'http://feed2.com' in self.parse_requests

    def test_store_caches_parsed_feed(self):
        assert len(self.store._cache) == 2

    def test_store_returns_feed_array(self):
        def finder(feeds, url):
            return filter(lambda x: x['url'] == url, feeds)

        feeds = self.store.feeds()
        assert len(feeds) == 2
        assert finder(feeds, 'http://feed.com')
        assert finder(feeds, 'http://feed2.com')

    def test_cache_is_ok_when_timestamp_is_within_cache_threshold(self):
        # 30 seconds ago
        cache_time = time.time() - 30
        assert self.store.cache_is_ok(
            dict(cache_time=cache_time, title='test'))

    def test_cache_is_not_ok_when_timestamp_is_outside_cache_threshold(self):
        # 30 seconds ago
        cache_time = time.time() - (feeds.CACHE_DURATION + 10)
        assert not self.store.cache_is_ok(
            dict(cache_time=cache_time, title='test'))

    @unittest.expectedFailure
    def test_feed_by_id_raises_feed_not_found_error_when_not_in_cache(self):
        self.store.feed_by_id('does not exist')

    def test_feed_returns_data_when_id_is_present_in_cache(self):
        feed_id = self.store.feeds()[0]['id']
        feed = self.store.feed_by_id(feed_id)
        self.assertEqual(feed['id'], feed_id)
        self.assertEqual(feed['title'], 'feed title')

    def test_feed_item_is_mapped(self):
        feed_id = self.store.feeds()[0]['id']
        feed = self.store.feed_by_id(feed_id)
        items = feed['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['index'], 0)
        self.assertEqual(items[0]['href'], 'http://example.com')
        self.assertEqual(items[0]['url'], '/feeds/{}/0'.format(feed_id))
        self.assertEqual(items[0]['title'], 'title text')
        self.assertEqual(items[0]['summary'], 'summary text')

if __name__ == '__main__':
    unittest.main()
