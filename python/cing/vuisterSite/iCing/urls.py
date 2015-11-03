from __future__ import unicode_literals, print_function, absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.UploadView.as_view(), name='upload'),
    # url(r'^index$', views.index, name='iCing_index'),
    url(r'^upload$', views.UploadView.as_view(), name='upload'),
    url(r'^options/(?P<submission_code>\w{6})/$', views.OptionsView.as_view(), name='options'),
    url(r'^run/(?P<submission_code>\w{6})$', views.run, name='run'),
    url(r'^report/(?P<submission_code>\w{6})$', views.report, name='report'),

    url(r'^icing/serv/iCingServlet', views.ccpnSubmit, name='ccpnSubmit'),
]

