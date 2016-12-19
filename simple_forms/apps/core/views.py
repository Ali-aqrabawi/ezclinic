# coding: utf-8
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
import logging
from django.http import HttpResponse

from simple_forms.apps.core.models import Person, Picture, PersonForm,UserForm,User

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

"""
def home(request):
    persons = Person.objects.all()
    return render(request, 'core/home.html', { 'persons': persons })



def home(request):
    if not request.user.is_authenticated():
        return render(request, 'core/login.html')
    else:
        persons = Person.objects.filter(user=request.user)



    return render(request, 'core/home.html', {'persons': persons})


"""


def add_person(request):
    if not request.user.is_authenticated():
        return render(request, 'core/login.html')
    else: 
        form = PersonForm(request.POST or None,request.FILES or None,instance=Person())
		#form = PersonForm(request.POST or None,request.FILES )

        if form.is_valid():
            print 'valid'
            persons = form.save()
            
            persons.user = request.user
			#to captilized the first litter so we have consistancy when quering , this is a workarround since __iexact is not working
            persons.name=persons.name.title()
            persons.last_name=persons.last_name.title()
            
          
            persons.save()
            files = request.FILES.getlist('pictures')
            if files:
                for f in files:
                    Picture.objects.create(person=persons, picture=f)

            return redirect('home')
        context = {
            "form": form,
        }
        
        return render(request, 'core/add_person.html', context)


def home(request):
    
    if not request.user.is_authenticated():
	
        return render(request, 'core/login.html')
    else:
		
        
        persons = Person.objects.filter(user=request.user)
            
        
        

			
        page = request.GET.get('page', 1)
        
        paginator = Paginator(persons, 6)
        #to avoid unsppuorted query by datastore
        if not persons :
            return render(request, 'core/home.html', {'persons': persons})
			
        try:
            persons = paginator.page(page)
        except PageNotAnInteger:
            
            persons= paginator.page(1)
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
def delete_person(request, person_id):
    if not request.user.is_authenticated():
	
        return render(request, 'core/login.html')
		
    if request.method == "GET":
        
        c = get_object_or_404(Person, pk=person_id)
        c.delete()
        return redirect('home')
    else :
        return redirect('home')
'''
    if request.method == "POST":

        c = get_object_or_404(Person, pk=person_id)
        c.delete()

        return redirect('home')
    else:
        return redirect('home')
'''

def delete_person_image(request, person_id, image_id):
    if not request.user.is_authenticated():

        return render(request, 'core/login.html')
        
    if request.method == "GET":
        image = get_object_or_404(Picture, pk=image_id)
        image.delete()
        return redirect(reverse('view', args=(person_id,)))
    else :
        return redirect(reverse('view', args=(person_id,)))


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'core/login.html', context)

#=====================doctor login======================
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                
                login(request, user)
                albums = Person.objects.filter(user=request.user)
                #return render(request, 'core/home.html', {'persons': albums})
                return redirect("home")
            else:
                return render(request, 'core/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'core/login.html', {'error_message': 'Invalid login'})
    return render(request, 'core/login.html')

#=================regetser a doctor======================
def register(request):
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    	
    if form.is_valid():
        
        user = form.save(commit=False)
        username = form.cleaned_data['username']       
        
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Person.objects.filter(user=request.user)
                return render(request, 'core/home.html', {'albums': albums})
				
    else :
        error = str(form.errors.as_data())
        if error :
            
            if 'is already in use' in error and 'Username' in error:
                erro = "Username is already in use"
                logging.info('here')
                return render(request, 'core/register.html', {'error_message':erro})
    
    return render(request, 'core/register.html', context )

#======================edit the patient details 
def edit(request, person_id):

    if not request.user.is_authenticated():	
        return render(request, 'core/login.html')
		
    i = get_object_or_404(Person, pk=person_id)


    if request.method == "POST":
        form = PersonForm(request.POST, request.FILES or None,instance=i)

        if form.is_valid():
          # update main BL
            form.save()


            i.save()
            files = request.FILES.getlist('pictures')
            if files:
                for f in files:
                    Picture.objects.create(person=i, picture=f)

        return redirect("home")
    else:
        form = PersonForm(instance=i)

    return render(request, 'core/edit.html', {'i': i, 'form': form, 'mode': 'edit'})
#=======================



#======================= view

def view(request, person_id):

    if not request.user.is_authenticated():	
        return render(request, 'core/login.html')
		
    person = get_object_or_404(Person, pk=person_id)
    pictures = person.pictures.all()
    pictures_length = len(pictures)
    if pictures_length%2 == 0:
        it = iter(pictures)
        pictures_tuple = zip(it, it)
        last_picture = None
    else:
        it = iter(pictures)
        pictures_tuple = zip(it, it)
        last_picture = pictures.last()

    print pictures_tuple, last_picture
    
    return render(request, 'core/view.html', {'person': person,'pictures_tuple':pictures_tuple, 'last_picture':last_picture })
	
	#====================================

def foto(request, person_id):
    persons= get_object_or_404(Person, pk=person_id)


    return render(request, 'core/home3.html', {'persons':persons})


def calender(request):
	if not request.user.is_authenticated():
		
		return render(request, 'core/login.html')
		
	else :
		return render(request,'core/calender.html')

##search by name or last name
def search(request):

    if not request.user.is_authenticated():
	
        return render(request, 'core/login.html')

    q = request.GET.get("q", None).title()

    q1 = request.GET.get("q1", None).title()
    if not q and not q1 :
        return redirect("home")
    if q and q1 :
        persons = Person.objects.filter(Q(name=q) & Q(last_name=q1))	
    elif q :
        persons = Person.objects.filter(Q(name=q))
    elif q1 :
        persons = Person.objects.filter(Q(last_name=q1))
	
	
	
    return render(request, 'core/home.html', {'persons':persons})


def date(request):

    if not request.user.is_authenticated():
	
        return render(request, 'core/login.html')

    if ('appointement' in request.GET) and request.GET['appointement'].strip():
        date = request.GET['appointement']
        
        persons = Person.objects.filter(Q(date=date) & Q(user=request.user))


    return render(request, 'core/home1.html', {'persons':persons})







