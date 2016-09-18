from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^new/$', views.new, name='new'),
    url(r'^show/(?P<scrape_id>[0-9]+)/$', views.show, name='show'),
]