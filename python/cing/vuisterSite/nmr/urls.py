from __future__ import unicode_literals, print_function, absolute_import, division

from django.conf.urls import url
from django.views.generic.base import TemplateView



urlpatterns = [
    url(r'^$|(?i)index\.html{0,1}', TemplateView.as_view(template_name='nmr/index.html'),
    name='index'),
]

