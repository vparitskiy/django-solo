from __future__ import absolute_import, division, unicode_literals

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from solo.models import DEFAULT_SINGLETON_INSTANCE_ID


class SingletonModelAdmin(admin.ModelAdmin):
    object_history_template = "admin/solo/object_history.html"
    change_form_template = "admin/solo/change_form.html"

    def __init__(self, *args, **kwargs):
        super(SingletonModelAdmin, self).__init__(*args, **kwargs)
        self.model._meta.verbose_name_plural = self.model._meta.verbose_name

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        kwargs = {'object_id': str(self.singleton_instance_id)}
        url_prefix = '{}_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
        urls = [
            url(
                r'^history/$', self.admin_site.admin_view(self.history_view), kwargs,
                name='{}_history'.format(url_prefix)
            ),
            url(r'^$', self.admin_site.admin_view(self.change_view), kwargs, name='{}_change'.format(url_prefix)),
        ]
        return urls + super(SingletonModelAdmin, self).get_urls()

    def response_change(self, request, obj):
        msg = _('{} was changed successfully.').format(force_unicode(obj))
        if '_continue' in request.POST:
            self.message_user(request, '{} {}'.format(msg, _('You may edit it again below.')))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            return redirect('admin:index')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if object_id == str(self.singleton_instance_id):
            self.model.objects.get_or_create(pk=self.singleton_instance_id)
        return super(SingletonModelAdmin, self).change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    @property
    def singleton_instance_id(self):
        return getattr(self.model, 'singleton_instance_id', DEFAULT_SINGLETON_INSTANCE_ID)
