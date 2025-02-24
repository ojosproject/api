# cache.py
# Ojos Project
#
# Caching.
import time
import threading
from collections import namedtuple

global_cache: list[dict[str:str, str:int]] = []

def add_to_cache(token, timestamp):
    global_cache.append({"token":token, "timestamp":timestamp})


def start_threading(testing=False):
    if not any(t.name == "CacheUpdater" for t in threading.enumerate()):
        thread = threading.Thread(target=start_updating_cache, args=(testing,), name="CacheUpdater", daemon=True)
        thread.start()


def start_updating_cache(testing=False):
    # called to periodically update the cache in the background
    start = time.time()
    while True:
        time.sleep(2)
        # global_cache.update_cache()
        if testing and (time.time() - start) > 6:
            break


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
                    time.time() - token_log.time_last_logged) < 60
            }

# todo: put the Cache class in a separate .py file for interface purposes
