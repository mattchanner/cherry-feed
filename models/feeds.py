"""
  The MIT License (MIT)
  Copyright 2015 Matt Channer (mchanner at gmail dot com)

  Permission is hereby granted, free of charge, to any person obtaining a
  copy of this software and associated documentation files (the "Software"),
  to deal in the Software without restriction, including without limitation
  the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the
  Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
"""
import feedparser
import datetime
import time
import uuid
import logging


logger = logging.getLogger("feeds")

# 1 hour cache duration for each feed
CACHE_DURATION = 60 * 60


class FeedNotFoundError(Exception):
    pass


class FeedStore(object):
    """ The Feed Model. """

    def __init__(self, feed_json):
        """
        Initializes a new instance of the feed store.
        @param feed_json: The parsed JSON data containing the feeds to load
        """
        self._cache = {}
        logger.debug(
            "FeedStore called with the following JSON: {}".format(
                str(feed_json)))

        for feed_data in feed_json["feeds"]:
            id = self._uuid()
            parsed_data = self._load_feed(feed_data)
            self._cache[id] = parsed_data

    def _uuid(self):
        """Helper used for creating a unique identifier for a feed."""
        return str(uuid.uuid4()).replace('-', '')

    def _load_feed(self, feed):
        """Creates the feed data by parsing a feed url"""
        try:

            logger.info("Loading feed {}".format(feed['title']))

            url = feed["url"]
            feed_data = feedparser.parse(url)
            cached = {
                'source': feed,
                'title': feed['title'],
                'url': url,
                'cache_time': time.time(),
                'feed': feed_data
            }
            return cached
        except Exception, e:
            logger.error(
                "Error caught loading feed with URL {}: {}".format(url, e))
            return {}

    def cache_is_ok(self, feed_data):
        """Returns True if the cached item is not stale."""
        current = time.time()
        elapsed = current - feed_data["cache_time"]
        elapsed_secs = datetime.timedelta(seconds=int(elapsed)).total_seconds()
        is_valid = elapsed_secs < CACHE_DURATION
        if is_valid:
            logger.info("Cache hit for {}", feed_data['title'])
        else:
            logger.info("Cache MISS for {}, elapsed = {}",
                        feed_data['title'], elapsed)
        return is_valid

    def feeds(self):
        """Retuns an array of top level feed items."""
        data = []
        for k, v in self._cache.iteritems():
            data.append(dict(id=k, title=v['title'], url=v['url']))
        return data

    def feed_by_id(self, feed_id):
        """Returns a cached feed item.
           If the feed item is stale, the item is refetched."""
        def get_cached_item():
            if feed_id in self._cache:
                cached = self._cache[feed_id]
                if not self.cache_is_ok(cached):
                    self._cache[feed_id] = self._load_feed(cached['source'])
                return self._cache[feed_id]["feed"]
            else:
                raise FeedNotFoundError()

        logger.info("Fetching feed data for feed with id {}".format(feed_id))

        cached_item = get_cached_item()
        items = []
        for i, item in enumerate(cached_item['items']):
            items.append({
                'index': i,
                'href': item['link'],
                'url': "/feeds/{}/{}".format(feed_id, i),
                'title': item['title'],
                'summary': item['summary']
            })

        feed = cached_item['feed']
        return {
            'data': {
                'items': items
            },
            'id': feed_id,
            'title': feed['title']
        }
