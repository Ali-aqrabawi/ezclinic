#coding: utf-8

from django.conf import settings
from django.conf.urls import url ,include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponse

from simple_forms.apps.core import views
from simple_forms.apps.core import forms

urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^$', views.calendar, name='home'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^patients/$', views.patients, name='patients'),
    url(r'^add/$', views.add_person, name='add_person'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^password_reset/$', auth_views.password_reset,
        {'template_name': "core/password_reset.html",
         'from_email': 'Password_reset@ezclinic16.appspotmail.com',
         'password_reset_form': forms.AppEnginePasswordResetForm},
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done,
        {'template_name': "core/password_reset_done.html"}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'set_password_form': forms.SetPasswordForm,
        'template_name': "core/password_reset_confirm.html"},  name='password_reset_confirm' ),
    url(r'^reset/done/$', auth_views.password_reset_complete,
        {'template_name': "core/password_reset_complete.html"},
        name='password_reset_complete'),
    url(r'^(?P<person_id>\d+)/delete/$', views.delete_person, name='delete_person'),
    url(r'^(?P<person_id>\d+)/image/(?P<image_id>\d+)/delete/$', views.delete_person_image, name='delete_person_image'),
    url(r'^(?P<person_id>\d+)/diagcode/(?P<diagcode_id>\d+)/delete/$', views.delete_person_diagcode, name='delete_person_diagcode'),
    url(r'^(?P<person_id>\d+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<person_id>\d+)/view/$', views.view, name='view'),
    url(r'^(?P<person_id>\d+)/foto/$', views.foto, name='foto'),
    url(r'^(?P<person_id>\d+)/appointment/$',
        views.AppointmentView.as_view(),
        name='appointment'),
    url(r'^(?P<person_id>\d+)/receipt/$',
        views.ReceiptView.as_view(),
        name='receipt'),
    url(r'^search/$', views.search, name='search'),
	url(r'^_ah/', include('djangae.urls')),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^google323523d1a2bbb38c\.html$', lambda r: HttpResponse("google-site-verification: google323523d1a2bbb38c.html", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

