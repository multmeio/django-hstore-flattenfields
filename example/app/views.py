'''
Created on 13/10/2012

@author: iuri
'''

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect

from models import Something
from forms import SomethingForm

def index(request):
    data = {
        'somethings': Something.objects.all()
    }
    return render_to_response('something/index.html', data,
        context_instance=RequestContext(request))

def detail(request, something_pk):
    data = {
        'something': Something.objects.get(pk=something_pk)
    }
    return render_to_response('something/detail.html', data,
        context_instance=RequestContext(request))

def add(request):
    form = SomethingForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('index')

    data = {
        'form': form
    }
    return render_to_response('something/add.html', data,
        context_instance=RequestContext(request))
