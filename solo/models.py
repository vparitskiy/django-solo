from __future__ import absolute_import, division, unicode_literals

from django.conf import settings
from django.core.cache import caches
from django.db import models

from solo import settings as solo_settings

DEFAULT_SINGLETON_INSTANCE_ID = 1


class SingletonModel(models.Model):
    singleton_instance_id = DEFAULT_SINGLETON_INSTANCE_ID

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = self.singleton_instance_id
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_to_cache()

    def delete(self, *args, **kwargs):
        self.clear_cache()
        super(SingletonModel, self).delete(*args, **kwargs)

    def clear_cache(self):
        cache_name = self.get_cache_name()
        if cache_name:
            cache = caches[cache_name]
            cache_key = self.get_cache_key()
            cache.delete(cache_key)

    def set_to_cache(self):
        cache_name = self.get_cache_name()
        if not cache_name:
            return None
        cache = caches[cache_name]
        cache_key = self.get_cache_key()
        cache_timeout = getattr(settings, 'SOLO_CACHE_TIMEOUT', solo_settings.SOLO_CACHE_TIMEOUT)
        cache.set(cache_key, self, cache_timeout)

    @classmethod
    def get_cache_key(cls):
        prefix = getattr(settings, 'SOLO_CACHE_PREFIX', solo_settings.SOLO_CACHE_PREFIX)
        return '%s:%s' % (prefix, cls.__name__.lower())

    @classmethod
    def get_cache_name(cls):
        return getattr(settings, 'SOLO_CACHE', solo_settings.SOLO_CACHE)

    @classmethod
    def get_solo(cls):
        cache_name = cls.get_cache_name()
        if not cache_name:
            obj, created = cls.objects.get_or_create(pk=cls.singleton_instance_id)
            return obj
        cache = caches[cache_name]
        cache_key = cls.get_cache_key()
        obj = cache.get(cache_key)
        if not obj:
            obj, created = cls.objects.get_or_create(pk=cls.singleton_instance_id)
            obj.set_to_cache()
        return obj
