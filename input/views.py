from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from .genetic.genetic import *

def index(request):
    return render(request,'index.html')

def error (request):
    context={ 'message':'Enter Atleast 1 Destination'}
    return render(request,'index.html',context )

def input_form (request,count):
    global waypoint
    waypoint=[]
    waypoint.append(request.POST.get('source'))
    for i in range(1,count+1):
        try:
            waypoint.append(request.POST[str(i)])
        except MultiValueDictKeyError:
            waypoint.append(None)
            
    op=getAllCoordinates(waypoint)

    return HttpResponse(op)
