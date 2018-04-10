"""Module for working comments from redis backend.
"""

import datetime
import doctest
import time
import re
import json
import logging
import zipfile
import base64

import requests

import redis

from eyap.core import comments, yap_exceptions

class RedisCommentThread(comments.CommentThread):
    """Class to represent a thread of redis comments.
    """

    def __init__(self, *args, ltrim=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ltrim = ltrim
        self.redis = redis.Redis()

    def lookup_thread_id(self):
        return 'eyap:%s:%s' % (self.realm, self.topic)

    def add_comment(self, body, allow_create=False, allow_hashes=False,
                    summary=None):
        thread_id = self.lookup_thread_id()
        if not allow_create and not self.redis.exists(thread_id):
            raise ValueError('Tried to add comment to non-exist thread %s' % (
                thread_id))

        comment = comments.SingleComment(
            self.user, datetime.datetime.now(datetime.timezone.utc), body, 
            summary=summary)
        lpush = self.redis.lpush(thread_id, comment.to_json())
        logging.debug('Pushing comment to redis returned %s', str(lpush))
        if self.ltrim:
            ltrim = self.redis.ltrim(thread_id, 0, self.ltrim)
            logging.debug('Redis ltrim returend %s', str(ltrim))
        else:
            ltrim = None

        return {'status': 'OK', 'lpush': lpush, 'ltrim': ltrim}

    def create_thread(self, body):
        return self.add_comment(body, allow_create=True)
        
    def lookup_comments(self, reverse=False):
        thread_id = self.lookup_thread_id()
        data = self.redis.lrange(thread_id, 0, -1)
        clist = []
        for jitem in data:
            citem = json.loads(jitem.decode('utf8'))
            clist.append(comments.SingleComment(**citem))
        if reverse:
            clist = list(reversed(clist))

        return comments.CommentSection(clist)

    @staticmethod
    def _regr_test():
        """
>>> from eyap.core import redis_comments
>>> rc = redis_comments.RedisCommentThread(
...     'test-owner', 'test-realm', 'test-topic', 'test-owner')
>>> rc.delete_thread(really=True)
>>> rc.add_comment('test_comment', allow_create=True)
>>> sec = rc.lookup_comments('test-topic')
>>> print(sec.show())
FIXME
        """
    

if __name__ == '__main__':
    doctest.testmod()
    print('Finished tests')
