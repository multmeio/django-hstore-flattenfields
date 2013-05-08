'''
Created on 13/10/2012

@author: iuri
'''

from django.shortcuts import render_to_response
from django.template import RequestContext
from app.models import Something
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from models import SomethingForm

def index(request):
    data = {
        'something': Something.objects.all()
    }
    return render_to_response('something/index.html', data,
        context_instance=RequestContext(request))

def detail(request, some_id):
    return HttpResponse("You're looking at something %s." % some_id)

def add(request):
    form = SomethingForm(request.POST or None) # A form bound to the POST data

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/thanks/') # Redirect after POST

    data = {
        'form': form
    }
    return render_to_response('something/add.html', data,
        context_instance=RequestContext(request))
