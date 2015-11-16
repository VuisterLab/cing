from __future__ import unicode_literals, print_function, absolute_import, division

from django.conf.urls import url
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    url(r'^$|(?i)index\.html{0,1}', TemplateView.as_view(template_name='nrg/index.html'),
    name='nrg_home'),
    url(r'^(?i)about', TemplateView.as_view(template_name='nrg/about.html'),
    name='nrg_about'),
    url(r'^(?i)credits', TemplateView.as_view(template_name='nrg/credits.html'),
    name='nrg_credits'),
    url(r'^(?i)download', TemplateView.as_view(template_name='nrg/download.html'),
    name='nrg_download'),
    url(r'^(?i)help', TemplateView.as_view(template_name='nrg/help.html'),
    name='nrg_help'),
    url(r'^(?i)cinghelp', TemplateView.as_view(template_name='nrg/cingHelp.html'),
    name='cing_help'),
    url(r'^(?i)glossary', TemplateView.as_view(template_name='nrg/glossary.html'),
    name='nrg_glossary'),
    url(r'^(?i)tutorials', TemplateView.as_view(template_name='nrg/tutorials.html'),
    name='nrg_tutorials'),

    url(r'^fdts$', views.fakeDataTableServer, name='fdts'),
]

