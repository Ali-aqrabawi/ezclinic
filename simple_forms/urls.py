#coding: utf-8

from django.conf.urls import url ,include
from django.contrib import admin
from simple_forms.apps.core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^$', views.calendar, name='home'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^add/$', views.add_person, name='add_person'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^(?P<person_id>\d+)/delete/$', views.delete_person, name='delete_person'),
    url(r'^(?P<person_id>\d+)/image/(?P<image_id>\d+)/delete/$', views.delete_person_image, name='delete_person_image'),
    url(r'^(?P<person_id>\d+)/diagcode/(?P<diagcode_id>\d+)/delete/$', views.delete_person_diagcode, name='delete_person_diagcode'),
    url(r'^(?P<person_id>\d+)/edit/$', views.edit, name='edit'),
	url(r'^(?P<person_id>\d+)/view/$', views.view, name='view'),
    url(r'^(?P<person_id>\d+)/foto/$', views.foto, name='foto'),
    url(r'^search/$', views.search, name='search'),
	url(r'^_ah/', include('djangae.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

