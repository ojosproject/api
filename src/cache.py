# cache.py
# Ojos Project
# 
# Caching.
import time
import threading
from collections import namedtuple

def start_updating_cache():
    # called in main to periodically update the cache in the background
    while True:
        time.sleep(60)
        global_cache.update_cache()


class Cache():
    Tokenlog = namedtuple("token", ["times_logged", "time_last_logged"])

    def __init__(self):
        # cache is a dictionary with tokens as keys and a tuple as a value.
        # the tuple contains how many calls the token has made and the time that
        # the last call was made.
        self.cache: dict[str, namedtuple] = {}
        self.lock = threading.Lock()

    def contains_max(self, token: str) -> bool:
        with self.lock:
            if self.cache_contains(token):
                return self.cache[token].times_logged == 10
            return False

    def add_to_cache(self, token: str):
        with self.lock:
            if self.cache_contains(token):
                self.cache[token] = self.Tokenlog(
                    self.cache[token].times_logged + 1, time.time())
            else:
                self.cache[token] = self.Tokenlog(1, time.time())

    def cache_contains(self, token: str) -> bool:
        with self.lock:
            return token in self.cache

    def update_cache(self):
        # this function must be periodically called to reset the cache
        with self.lock:
            self.cache = {
                token: token_log for token, token_log in self.cache.items() if (
                    token_log.time_last_logged + 60) > time.time()
            }


global_cache = Cache()
# todo: put the Cache class in a separate .py file for interface purposes
