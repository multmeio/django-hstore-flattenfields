'''
Created on 13/10/2012

@author: iuri
'''

from django.template import Context, loader
from hstoredyn.models import Something
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from hstoredyn.models import SomethingForm

def index(request):
    somethings = Something.objects.all()
    t = loader.get_template('something/index.html')
    c = Context({
        'somethings_list': somethings,
    })
    return HttpResponse(t.render(c))

def detail(request, some_id):
    return HttpResponse("You're looking at something %s." % some_id)

def add(request):
    if request.method == 'POST': # If the form has been submitted...
        form = SomethingForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = SomethingForm() # An unbound form

    return render(request, 'something/add.html', {
        'form': form,
    })
