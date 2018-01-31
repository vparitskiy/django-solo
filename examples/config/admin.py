from __future__ import absolute_import, division, unicode_literals

from django.contrib import admin

from solo.admin import SingletonModelAdmin
from .models import SiteConfiguration

admin.site.register(SiteConfiguration, SingletonModelAdmin)
