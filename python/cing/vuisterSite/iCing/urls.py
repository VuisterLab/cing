from __future__ import unicode_literals, print_function, absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.UploadView.as_view(), name='upload'),
    # url(r'^index$', views.index, name='iCing_index'),
    url(r'^upload$', views.UploadView.as_view(), name='upload'),
    url(r'^options/(?P<pk>\w{6})/$', views.OptionsView.as_view(), name='options'),
    url(r'^run/(?P<pk>\w{6})$', views.Run.as_view(), name='run'),
    url(r'^view/(?P<pk>\w{6})$', views.view, name='view'),

    url(r'^logTextView/(?P<pk>\w{6})$', views.logTextView, name='logTextView'),
    url(r'^runFinishedView/(?P<pk>\w{6})$', views.runFinishedView, name='runFinishedView'),

    url(r'^icing/serv/iCingServlet', views.ccpnSubmit, name='ccpnSubmit'),
]

