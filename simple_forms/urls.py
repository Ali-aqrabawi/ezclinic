#coding: utf-8

from django.conf.urls import url ,include
from django.contrib import admin
from simple_forms.apps.core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^calender/$', views.calender, name='calender'),
    url(r'^add/$', views.add_person, name='add_person'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^(?P<person_id>\d+)/delete/$', views.delete_person, name='delete_person'),
    url(r'^(?P<person_id>\d+)/edit/$', views.edit, name='edit'),
	url(r'^(?P<person_id>\d+)/view/$', views.view, name='view'),
    url(r'^(?P<person_id>\d+)/foto/$', views.foto, name='foto'),
    url(r'^search/$', views.search, name='search'),
    url(r'^date/$', views.date, name='date'),
	url(r'^_ah/', include('djangae.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

