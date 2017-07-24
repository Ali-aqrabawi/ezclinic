# coding: utf-8

from itertools import groupby, takewhile, dropwhile
from calendar import monthrange
import datetime
import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.cache import never_cache

from djangae.contrib.consistency.signals import connect_signals
from djangae.contrib.consistency.consistency import improve_queryset_consistency
from djangae.utils import get_in_batches

from . import models as m
from . import forms as f
from . import charts_data

connect_signals()

# Appengine Datastore magic limit
CHUNK_SIZE = 30

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


@login_required
def add_person(request):
    form = f.PersonForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        person = form.save(commit=False)

        person.user = request.user
        # Capitilize first letter so we have consistancy when
        # quering , this is a workarround since __iexact is not working
        person.name = person.name.title()
        person.last_name = person.last_name.title()

        person.save()
        files = request.FILES.getlist('pictures')
        if files:
            for picture in files:
                m.Picture.objects.create(person=person, picture=picture)

        diagcodes = request.POST.getlist('diagcode')
        if diagcodes:
            for diagcode in diagcodes:
                m.Diagcode.objects.create(person=person, diagcode=diagcode)

        return redirect(reverse('view', args=(person.id,)))
    context = {
        "form": form,
    }

    return render(request, 'core/add_person.html', context)


@login_required
def patients(request):
    page = request.GET.get('page', 1)
    persons = improve_queryset_consistency(
        request.user.person_set.order_by("pk"))  # Default ordering
    paginator = Paginator(persons, 6)
    # to avoid unsppuorted query by datastore
    if not persons:
        return render(request, 'core/patients.html', {'persons': persons})

    try:
        persons = paginator.page(page)
    except PageNotAnInteger:

        persons = paginator.page(1)
    except EmptyPage:

        persons = paginator.page(paginator.num_pages)

    return render(request, 'core/patients.html', {'persons': persons})


#===========delete a prson==================
@login_required
def delete_person(request, person_id):
    if request.method == "GET" or request.method == 'POST':
        c = get_object_or_404(m.Person, pk=person_id, user=request.user)
        c.delete()
        if request.GET.get('next', None) == 'calendar':
            return redirect('home')
        return redirect(reverse('patients'))
    else:
        return redirect(reverse('view', args=(person_id,)))


@login_required
def hide_person(request, person_id):
    person = get_object_or_404(m.Person, pk=person_id, user=request.user)
    person.is_archived = True
    person.save()
    return JsonResponse({'hide': 'success'}, safe=True)


@login_required
def delete_person_image(request, person_id, image_id):
    if request.method == "GET":
        image = get_object_or_404(m.Picture, pk=image_id)
        image.delete()
        return redirect("%s?tab=tab3" % reverse('view', args=(person_id,)))
    else:
        return redirect(reverse('view', args=(person_id,)))


@login_required
def delete_person_diagcode(request, person_id, diagcode_id):
    if request.method == "GET":
        diagcode = get_object_or_404(m.Diagcode, pk=diagcode_id)
        diagcode.delete()
        return redirect("%s?tab=tab2" % reverse('view', args=(person_id,)))
    else:
        return redirect(reverse('view', args=(person_id,)))


def logout_user(request):
    logout(request)
    return redirect(reverse("login_user"))

#=====================doctor login======================


def login_user(request):
    form = AuthenticationForm(request.POST)
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("home")
            else:
                return render(request, 'core/login.html', {'error_message': 'Your account has been disabled', 'form': form})
        else:
            return render(request, 'core/login.html', {'error_message': 'Invalid login', 'form': form})
    return render(request, 'core/login.html', {'form': form})

#=================regetser a doctor======================


def register(request):
    form = f.UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']

        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()

        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect(reverse('home'))

    context = {"form": form}
    return render(request, 'core/register.html', context)

#======================edit the patient details


@login_required
def edit(request, person_id):
    person = get_object_or_404(
        m.Person.objects.prefetch_related('diagcodes'), pk=person_id)
    tab = request.GET.get('tab')
    diagcodes = ''

    if request.method == "POST":
        form = f.PersonForm(request.POST,
                            request.FILES or None, instance=person)

        if form.is_valid():
          # update main BL
            form.save()

            files = request.FILES.getlist('pictures')
            if files:
                for picture in files:
                    m.Picture.objects.create(person=person, picture=picture)

            person.diagcodes.all().delete()
            diagcodes = request.POST.getlist('diagcode')
            if diagcodes:
                for diagcode in diagcodes:
                    if not m.Diagcode.objects.filter(person=person,
                                                     diagcode=diagcode):
                        m.Diagcode.objects.create(person=person,
                                                  diagcode=diagcode)
                    else:
                        pass

            url = reverse('view', args=(person.id,))
            if tab:
                url = "{}?tab={}".format(url, tab)
            return redirect(url)
    else:
        form = f.PersonForm(instance=person)
        diagcodes = ','.join(
            [diagcode.diagcode for diagcode in person.diagcodes.all()])

    return render(request, 'core/edit.html',
                  {'form': form, 'mode': 'edit', 'person': person, 'diagcodes': diagcodes, 'tab': tab})


@login_required
def view(request, person_id):
    person = get_object_or_404(m.Person, pk=person_id)
    tab = request.GET.get('tab')
    pictures = person.pictures.all()
    pictures_length = len(pictures)
    if pictures_length % 2 == 0:
        it = iter(pictures)
        pictures_tuple = zip(it, it)
        last_picture = None
    else:
        it = iter(pictures)
        pictures_tuple = zip(it, it)
        last_picture = pictures.last()

    return render(request, 'core/view.html',
                  {'person': person, 'pictures_tuple': pictures_tuple,
                   'last_picture': last_picture, 'tab': tab,
                   'appointment_form': f.AppointmentForm(),
                   'receipt_form': f.ReceiptForm()})

    #====================================


def foto(request, person_id):
    persons = get_object_or_404(m.Person, pk=person_id)

    return render(request, 'core/home3.html', {'persons': persons})


@never_cache
@login_required
def calendar(request):
    try:
        date = datetime.datetime.strptime(request.GET.get(
            "appointment", "").strip(), "%Y-%m-%d").date()
    except ValueError as e:
        date = datetime.date.today()

    event_form = f.EventForm(request.POST)
    if event_form.is_valid():
        event = event_form.save(commit=False)
        event.user = request.user
        event.save()
        # Redirect after POST
        return redirect(request.get_full_path())

    # Simulate ORDER BY with NULLS LAST
    persons = list(request.user.person_set.filter(date=date, is_archived=False))
    persons.sort(key=lambda p: p.time or datetime.time(23, 59, 59))
    print(persons)

    events = request.user.event_set.filter(date=date)

    return render(request, 'core/calendar.html',
                  {'persons': persons,
                   'events': events,
                   'date': date,
                   'today': date == datetime.date.today(),
                   'event_form': event_form, })


# search by name or last name
@login_required
def search(request):
    q = request.GET.get("q", None).title()

    q1 = request.GET.get("q1", None).title()
    if not q and not q1:
        return redirect("home")
    if q and q1:
        persons = m.Person.objects.filter(
            name=q, last_name=q1, user=request.user)
    elif q:
        persons = m.Person.objects.filter(name=q, user=request.user)
    elif q1:
        persons = m.Person.objects.filter(last_name=q1, user=request.user)

    return render(request, 'core/search.html', {'persons': persons})


@login_required
def dashboard(request):
    # You can use it for preseeding database with users

    # import random
    # for i in range(100):
    #     p = m.Person.objects.create(
    #         name="test_{}".format(i),
    #         last_name="test_{}".format(i),
    #         amount_paid=0,
    #         age=random.randint(8, 88))
    #     p.created_at = datetime.datetime(2016, random.randint(1, 12), random.randint(1, 20))
    #     p.save()
    #     for j in range(random.randint(3, 20)):
    #         r = m.Receipt.objects.create(
    #             user=request.user,
    #             person=p,
    #             amount=random.randint(20, 600))
    #         r.created_at=datetime.datetime(2016, random.randint(1, 12), random.randint(1, 20))
    #         r.save()

    persons = list(get_in_batches(request.user.person_set.all(), CHUNK_SIZE))

    # Pseudomigration
    for patient in persons:
        if patient.created_at is None:
            patient.created_at = datetime.datetime.utcnow()
            patient.save()

    data = {}
    data["count"] = len(persons)

    data["ages"] = charts_data.ages([p.age for p in persons])

    p_ids = list(person.pk for person in persons)
    dental_charts_records = []
    for i in range(0, len(persons), CHUNK_SIZE):
        dental_charts_records.extend(
            m.DentalChart.objects
            .filter(person__in=p_ids[i: i + CHUNK_SIZE])
            .values_list("extraction", "filling", "rct"))
    data["dental_charts"] = charts_data.dental_charts(dental_charts_records)

    year_ago, end_of_month = charts_data.year_range()

    patients_records = [patient.created_at for patient in persons]
    patients_records.sort()
    data["patients"] = charts_data.patients(patients_records,
                                            year_ago, end_of_month)

    today = datetime.date.today()
    next_sat = (today + datetime.timedelta(days=(5 - today.weekday()) % 7))
    next_sat2 = next_sat + datetime.timedelta(weeks=1)
    next_sat3 = next_sat + datetime.timedelta(weeks=2)
    next_appointments = [person.date for person in persons
                         if next_sat <= person.date < next_sat3]
    next_appointments.sort()
    data["appointment_next_week"] = len([d for d in next_appointments
                                         if next_sat <= d < next_sat2])
    data["appointment_next_week2"] = len([d for d in next_appointments
                                          if next_sat2 <= d < next_sat3])

    receipts_records = request.user.receipt_set.values("amount", "created_at")
    receipts_records = list(get_in_batches(receipts_records, CHUNK_SIZE))
    receipts_records.sort()
    data["revenue"] = charts_data.revenue(receipts_records,
                                          year_ago, end_of_month)

    return render(request, 'core/dashboard.html', data)


class AppointmentView(View):

    def post(self, request, person_id):
        person = get_object_or_404(m.Person, pk=person_id)
        appointment_form = f.AppointmentForm(request.POST or None)
        if appointment_form.is_valid():
            person.date = appointment_form.cleaned_data["date"]
            person.time = appointment_form.cleaned_data["time"]
            person.save()
        return redirect(reverse('view', args=(person.id,)))


class ReceiptView(View):

    def post(self, request, person_id):
        person = get_object_or_404(m.Person, pk=person_id)
        receipt_form = f.ReceiptForm(request.POST or None)
        if receipt_form.is_valid():
            # Receipt will be create automatically
            person.amount_paid += receipt_form.cleaned_data["amount"]
            person.save()
        return redirect(reverse('view', args=(person.id,)))
