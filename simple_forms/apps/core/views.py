# coding: utf-8

from itertools import groupby, takewhile, dropwhile
from calendar import monthrange
import datetime
import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache  import never_cache
from django.views import View

from . import models as m
from . import forms as f
from . import charts_data

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

@login_required
def add_person(request):
    form = f.PersonForm(request.POST or None, request.FILES or None)
    print 'invalid'
    if form.is_valid():
        print 'valid'
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

        appointment_form = f.AppointmentForm(request.POST)
        if appointment_form.is_valid():
            appointment = appointment_form.save(commit=False)
            appointment.user = request.user
            appointment.person = person
            appointment.save()

        return redirect(reverse('view', args=(person.id,)))
    context = {
        "form": form,
    }

    return render(request, 'core/add_person.html', context)


@login_required
def patients(request):
    page = request.GET.get('page', 1)
    persons = request.user.person_set.all()
    paginator = Paginator(persons, 6)
    # to avoid unsppuorted query by datastore
    if not persons:
        return render(request, 'core/home.html', {'persons': persons})

    try:
        persons = paginator.page(page)
    except PageNotAnInteger:

        persons = paginator.page(1)
    except EmptyPage:

        persons = paginator.page(paginator.num_pages)

    return render(request, 'core/home.html', {'persons': persons})


#===========delete a prson==================
@login_required
def delete_person(request, person_id):
    if request.method == "GET":
        c = get_object_or_404(m.Person, pk=person_id)
        c.delete()
        return redirect(reverse('home'))
    else:
        return redirect(reverse('home'))


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
    person = get_object_or_404(m.Person, pk=person_id)
    tab = request.GET.get('tab')

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

            diagcodes = request.POST.getlist('diagcode')
            if diagcodes:
                for diagcode in diagcodes:
                    if not m.Diagcode.objects.filter(person=person,
                                                     diagcode=diagcode):
                        m.Diagcode.objects.create(person=person,
                                                  diagcode=diagcode)
                    else:
                        pass

            appointment_form = f.AppointmentForm(request.POST)
            if appointment_form.is_valid():
                appointment = appointment_form.save(commit=False)
                appointment.user = request.user
                appointment.person = person
                appointment.save()

        url = reverse('view', args=(person.id,))
        if tab:
            url = "{}?tab={}".format(url, tab)
        return redirect(url)
    else:
        form = f.PersonForm(instance=person)

    return render(request, 'core/edit.html',
                  {'form': form, 'mode': 'edit', 'person': person, 'tab': tab})


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
        date = datetime.datetime.strptime(request.GET.get("appointment", "").strip(), "%Y-%m-%d").date()
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
    # persons = list(request.user.person_set.filter(date=date))
    # persons.sort(key=lambda p: p.time or datetime.time(23, 59, 59))
    appointments = list(m.Appointment.objects
                        .filter(date=date, user=request.user)
                        .prefetch_related())
    appointments.sort(key=lambda p: p.time or datetime.time(23, 59, 59))

    events = request.user.event_set.filter(date=date)

    return render(request, 'core/calendar.html',
            {'appointments': appointments,
             'events': events,
             'date': date,
             'today': date == datetime.date.today(),
             'event_form': event_form,})


# search by name or last name
@login_required
def search(request):
    q = request.GET.get("q", None).title()

    q1 = request.GET.get("q1", None).title()
    if not q and not q1:
        return redirect("home")
    if q and q1:
        persons = m.Person.objects.filter(name=q, last_name=q1)
    elif q:
        persons = m.Person.objects.filter(name=q)
    elif q1:
        persons = m.Person.objects.filter(last_name=q1)

    return render(request, 'core/search.html', {'persons': persons})


@login_required
def dashboard(request):
    data = {}
    persons = list(request.user.person_set.all())
    p_ids = list(person.id for person in persons)
    data["count"] = len(persons)

    ages = [0] * 5
    for key, group in groupby(sorted(person.age for person in persons),
                              lambda age: age // 10):
        if key > 4:
            ages[4] += len(list(group))
        else:
            ages[key] = len(list(group))
    data["ages"] = json.dumps({
        "chart": {
            "plotBackgroundColor": None,
            "plotBorderWidth": None,
            "plotShadow": False, "type": "pie",
            },
        "title": {
            "text": "Patients Ages Chart"
            },
        "tooltip": {
            "pointFormat": "{series.name}: <b>{point.y} — {point.percentage:.1f}%</b>"
            },
        "plotOptions": {
            "pie": {
                "allowPointSelect": True,
                "cursor": "pointer",
                "dataLabels": {"enabled": False},
                "showInLegend": True
                }},
            "series": [{
                "name": "Ages",
                "colorByPoint": True,
                "data": [{"name": name, "y": count}
                    for name, count in
                    zip(["<10", "10—19", "20—29", "30—40", "40"], ages)]
                }]}, indent=4)


    d_c = {"extraction": 0, "filling": 0, "rct": 0}
    dental_charts = (m.DentalChart.objects
                     .filter(person__in=p_ids)
                     .values_list("extraction", "filling", "rct"))

    for extraction, filling, rct in dental_charts:
        d_c["extraction"] += extraction
        d_c["filling"] += filling
        d_c["rct"] += rct

    data["dental_charts"] = json.dumps({
        "chart": {
            "plotBackgroundColor": None,
            "plotBorderWidth": None,
            "plotShadow": False,
            "type": "pie",
            },
         "title": {
             "text": "Dental charts"
         },
         "tooltip": {
             "pointFormat": "{series.name}: <b>{point.y} — {point.percentage:.1f}%</b>"
             },
         "plotOptions": {
             "pie": {
                 "allowPointSelect": True,
                 "cursor": "pointer",
                 "dataLabels": {"enabled": False},
                 "showInLegend": True
                 }},
         "series": [{
             "name": "Dental charts",
             "colorByPoint": True,
             "data": [
                 {"name": "extraction", "y": d_c["extraction"], "color": "#4D6790"},
                 {"name": "filling", "y": d_c["filling"], "color": "#FF8400"},
                 {"name": "rct", "y": d_c["rct"], "color": "#91CEB0" }]
             }]}, indent=4)

    year_ago, end_of_month = charts_data.year_range()
    appointment_records = (request.user.appointment_set
                           .filter(date__gte=year_ago, date__lte=end_of_month)
                           .order_by("date")
                           .values_list("date", flat=True))

    data["appointments"] = charts_data.appointments(appointment_records,
                                                    year_ago, end_of_month)


    today = datetime.date.today()
    next_sat = (today + datetime.timedelta(days=(5 - today.weekday()) % 7))
    next_sat2 = next_sat + datetime.timedelta(weeks=1)
    next_sat3 = next_sat + datetime.timedelta(weeks=2)
    next_appointments = (request.user.appointment_set
                         .filter(date__gte=next_sat, date__lte=next_sat3)
                         .order_by("date")
                         .values_list("date", flat=True))
    data["appointment_next_week"] = len([d for d in next_appointments
                                         if next_sat <= d < next_sat2])
    data["appointment_next_week2"] = len([d for d in next_appointments
                                          if next_sat2 <= d < next_sat3])

    receipts_records = (request.user.receipt_set
                        .filter(created_at__gte=year_ago,
                                created_at__lte=end_of_month)
                        .order_by("created_at"))
    data["revenue"] = charts_data.revenue(receipts_records,
                                          year_ago, end_of_month)

    return render(request, 'core/dashboard.html', data)


class AppointmentView(View):
    def post(self, request, person_id):
        person = get_object_or_404(m.Person, pk=person_id)
        appointment_form = f.AppointmentForm(request.POST or None)
        if appointment_form.is_valid():
            logging.info(request.POST)
            logging.info(appointment_form.cleaned_data)
            appointment = appointment_form.save(commit=False)
            appointment.user = request.user
            appointment.person = person
            appointment.save()
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
