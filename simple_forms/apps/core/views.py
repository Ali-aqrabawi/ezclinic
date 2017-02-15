# coding: utf-8

import datetime
import logging


from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.cache  import never_cache
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from simple_forms.apps.core.models import Person, Picture, Diagcode, PersonForm, UserForm, User, EventForm, AppointmentForm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

@login_required
def add_person(request):
    form = PersonForm(request.POST or None,
                        request.FILES or None, instance=Person())
    #form = PersonForm(request.POST or None,request.FILES )
    print 'invalid'
    if form.is_valid():
        print 'valid'
        persons = form.save(commit=False)

        persons.user = request.user
        # to captilized the first litter so we have consistancy when
        # quering , this is a workarround since __iexact is not working
        persons.name = persons.name.title()
        persons.last_name = persons.last_name.title()

        persons.save()
        files = request.FILES.getlist('pictures')
        if files:
            for f in files:
                Picture.objects.create(person=persons, picture=f)

        diagcodes = request.POST.getlist('diagcode')
        if diagcodes:
            for diagcode in diagcodes:
                Diagcode.objects.create(person=persons, diagcode=diagcode)

        return redirect(reverse('view', args=(persons.id,)))
    context = {
        "form": form,
    }

    return render(request, 'core/add_person.html', context)


@login_required
def patients(request):
    persons = Person.objects.filter(user=request.user)

    page = request.GET.get('page', 1)

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

"""
def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save()
            return redirect('home')
    else:
        form = PersonForm()
    return render(request, 'core/add_person.html', { 'form': form })
"""
#===========delete a prson==================


@login_required
def delete_person(request, person_id):
    if request.method == "GET":

        c = get_object_or_404(Person, pk=person_id)
        c.delete()
        return redirect(reverse('home'))
    else:
        return redirect(reverse('home'))
'''
    if request.method == "POST":

        c = get_object_or_404(Person, pk=person_id)
        c.delete()

        return redirect('home')
    else:
        return redirect('home')
'''


@login_required
def delete_person_image(request, person_id, image_id):
    if request.method == "GET":
        image = get_object_or_404(Picture, pk=image_id)
        image.delete()
        return redirect("%s?tab=tab3" % reverse('view', args=(person_id,)))
    else:
        return redirect(reverse('view', args=(person_id,)))


@login_required
def delete_person_diagcode(request, person_id, diagcode_id):
    if request.method == "GET":
        diagcode = get_object_or_404(Diagcode, pk=diagcode_id)
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
    form = UserForm(request.POST or None)
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
    i = get_object_or_404(Person, pk=person_id)
    tab = request.GET.get('tab')

    if request.method == "POST":
        form = PersonForm(request.POST, request.FILES or None, instance=i)

        if form.is_valid():
          # update main BL
            form.save()

            files = request.FILES.getlist('pictures')
            if files:
                for f in files:
                    Picture.objects.create(person=i, picture=f)

            diagcodes = request.POST.getlist('diagcode')
            if diagcodes:
                for diagcode in diagcodes:
                    if not Diagcode.objects.filter(person=i, diagcode=diagcode):
                        Diagcode.objects.create(person=i, diagcode=diagcode)
                    else:
                        pass

        url = reverse('view', args=(i.id,))
        if tab:
            url = "{}?tab={}".format(url, tab)
        return redirect(url)
    else:
        form = PersonForm(instance=i)

    return render(request, 'core/edit.html', {'i': i, 'form': form, 'mode': 'edit', 'person': i, 'tab': tab})
#=======================


#======================= view

@login_required
def view(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
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

    print pictures_tuple, last_picture

    appointment_form = AppointmentForm(request.POST)
    if appointment_form.is_valid():
        person.date = appointment_form.cleaned_data["date"]
        person.time = appointment_form.cleaned_data["time"]
        person.save()

    return render(request, 'core/view.html', {'person': person, 'pictures_tuple': pictures_tuple,
                                              'last_picture': last_picture, 'tab': tab,
                                              'appointment_form': appointment_form})

    #====================================


def foto(request, person_id):
    persons = get_object_or_404(Person, pk=person_id)

    return render(request, 'core/home3.html', {'persons': persons})

@never_cache
@login_required
def calendar(request):
    persons = None

    try:
        logging.info(request.GET.get("appointment", "").strip())
        date = datetime.datetime.strptime(request.GET.get("appointment", "").strip(), "%Y-%m-%d").date()
    except ValueError as e:
        date = datetime.date.today()

    event_form = EventForm(request.POST)
    if event_form.is_valid():
        event = event_form.save(commit=False)
        event.user = request.user
        event.save()
        # Redirect after POST
        return redirect(request.get_full_path())

    # Simulate ORDER BY with NULLS LAST
    persons = list(request.user.person_set.filter(date=date))
    persons.sort(key=lambda p: p.time or datetime.time(23, 59, 59))

    events = request.user.event_set.filter(date=date)

    return render(request, 'core/calendar.html',
            {'persons': persons,
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
        persons = Person.objects.filter(Q(name=q) & Q(last_name=q1))
    elif q:
        persons = Person.objects.filter(Q(name=q))
    elif q1:
        persons = Person.objects.filter(Q(last_name=q1))

    return render(request, 'core/search.html', {'persons': persons})

