# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import memcache
import os
import pickle
from tempfile import gettempdir
from watson.stdlib.imports import get_qualified_name


class BaseStorage(object):
    config = None

    def __init__(self, config=None):
        self.config = config or {}

    def __setitem__(self, key, value, timeout=0):
        raise NotImplementedError('__setitem__ must be implemented')

    def __getitem__(self, key, default=None):
        raise NotImplementedError('__getitem__ must be implemented')

    def __delitem__(self, key):
        raise NotImplementedError('__delitem__ must be implemented')

    def __contains__(self, key):
        raise NotImplementedError('__contains__ must be implemented')

    def flush(self):
        raise NotImplementedError('flush must be implemented')

    def expired(self, key):
        raise NotImplementedError('expired must be implemented')

    def __repr__(self):
        return '<{0}>'.format(get_qualified_name(self))

    # Convenience methods

    def set(self, key, value, timeout=0):
        self.__setitem__(key, value, timeout)

    def get(self, key, default=None):
        return self.__getitem__(key, default)


class Memory(BaseStorage):
    def __init__(self):
        self._cache = {}

    def __setitem__(self, key, value, timeout=0):
        expires = datetime.now() + timedelta(seconds=int(timeout)) if timeout else None
        self._cache.__setitem__(key, (value, expires))

    def __getitem__(self, key, default=None):
        if self.expired(key):
            return default
        else:
            value, expires = self._stored(key, default)
            return value

    def __delitem__(self, key):
        self._cache.__delitem__(key)

    def flush(self):
        self._cache.clear()
        return True

    def expired(self, key):
        value, expires = self._stored(key)
        if expires is not None and expires < datetime.now():
            return True
        return False

    def __contains__(self, key):
        return self._cache.__contains__(key)

    def _stored(self, key, default=None):
        (value, expires) = self._cache.get(key, (default, None))
        return value, expires


class File(BaseStorage):
    def __init__(self, config=None):
        settings = {'dir': gettempdir(), 'prefix': 'cache'}
        if not config:
            config = {}
        settings.update(config)
        self.config = settings

    def __setitem__(self, key, value, timeout=0):
        expires = datetime.now() + timedelta(seconds=int(timeout)) if timeout else None
        with open(self.__file_path(key), 'wb') as file:
            try:
                pickle.dump((value, expires), file, pickle.HIGHEST_PROTOCOL)
            except:
                pass

    def __getitem__(self, key, default=None):
        if self.expired(key):
            return default
        else:
            value, expires = self._stored(key, default)
            return value

    def __delitem__(self, key):
        try:
            os.unlink(self.__file_path(key))
        except OSError:
            pass

    def expired(self, key):
        value, expires = self._stored(key)
        if expires is not None and expires < datetime.now():
            return True
        return False

    def __contains__(self, key):
        return os.path.exists(self.__file_path(key))

    def flush(self):
        storage_dir = self.config['dir']
        index = len(self.config['prefix']) + 1
        files = [f for f in os.listdir(storage_dir) if self.__is_cache_file(f)]
        for file in files:
            del self[file[index:]]
        return True

    def _stored(self, key, default=None):
        value, expires = default, None
        try:
            with open(self.__file_path(key), 'rb') as file:
                try:
                    (value, expires) = pickle.load(file)
                except:
                    pass
        except:
            pass
        return value, expires

    def __cache_file(self, file):
        storage_dir = self.config['dir']
        return os.path.abspath(os.path.join(storage_dir, file))

    def __is_cache_file(self, file):
        if not file.startswith(self.config['prefix']):
            return False
        return os.path.isfile(self.__cache_file(file))

    def __file_path(self, key):
        return os.path.join(self.config['dir'], '{0}-{1}'.format(self.config['prefix'], key))

    def __repr__(self):
        return '<{0} dir:{1}>'.format(get_qualified_name(self), self.config['dir'])


class Memcached(BaseStorage):
    def __init__(self, config=None):
        settings = {'servers': ['127.0.0.1:11211']}
        if not config:
            config = {}
        settings.update(config)
        self.config = settings
        self.client = memcache.Client(self.config['servers'])

    def __setitem__(self, key, value, timeout=0):
        self.client.set(key, value, timeout)

    def __getitem__(self, key, default=None):
        value = self.client.get(key)
        if not value:
            return default
        return value

    def __delitem__(self, key):
        return self.client.delete(key)

    def flush(self):
        self.client.flush_all()
        return True

    def close(self):
        self.client.disconnect_all()
        return True

    def __contains__(self, key):
        return True if self.get(key) else False

    def expired(self, key):
        return not key in self

    def __repr__(self):
        return '<{0} servers:{1}>'.format(get_qualified_name(self),
                                          len(self.config['servers']))