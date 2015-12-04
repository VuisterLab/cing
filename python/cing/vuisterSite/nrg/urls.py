from __future__ import unicode_literals, print_function, absolute_import, division

from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import RevisionedTemplateView, fakeDataTableServer

urlpatterns = [
    url(r'^$|(?i)index\.html{0,1}', RevisionedTemplateView.as_view(template_name='nrg/index.html'),
    name='home'),
    url(r'^(?i)about', TemplateView.as_view(template_name='nrg/about.html'),
    name='about'),
    url(r'^(?i)credits', TemplateView.as_view(template_name='nrg/credits.html'),
    name='credits'),
    url(r'^(?i)download', TemplateView.as_view(template_name='nrg/download.html'),
    name='download'),
    url(r'^(?i)help', TemplateView.as_view(template_name='nrg/help.html'),
    name='help'),
    url(r'^(?i)cinghelp', TemplateView.as_view(template_name='nrg/cingHelp.html'),
    name='cing_help'),
    url(r'^(?i)glossary', TemplateView.as_view(template_name='nrg/glossary.html'),
    name='glossary'),
    url(r'^(?i)tutorials', TemplateView.as_view(template_name='nrg/tutorials.html'),
    name='tutorials'),

    url(r'^fdts$', fakeDataTableServer, name='fdts'),
]

