from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from random import randrange
from django.core.mail import send_mail
from RTA.settings import EMAIL_HOST_USER
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from .genetic.genetic import getAllCoordinates as safest
from .genetic.distance_genetic import getAllCoordinates as shortest
from .genetic.hamiltonian import getHamiltonian as hamiltonian
from .genetic.geo_dist import weather,latlong
import simplejson

def index(request):
    context={ 'message':'Enter Atleast 1 Destination'}
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

    #Getting radio button Info
    radio = str(request.POST.get('type'))
    op=[]
    #CHeck import to see names of the functions
    if radio=='safe':
        pathType= 'Safest'
        op=safest(waypoint)
    elif radio=='short':
        pathType= 'Shortest'
        op=shortest(waypoint)
    elif radio=='hamilton':
        pathType='Hamiltonian'
        op=hamiltonian(waypoint)
    else :
        pathType= 'Shortest'
        op=shortest(waypoint)

    for i in range(len(op)):
        op[i]=list(op[i])
        # weather Part
    weathe=[]
    for x in waypoint:
        weathe.append(weather(str(x)))
    for i in range(len(waypoint)):
        try:
            weathe[i]=str(waypoint[i])+"→"+weathe[i]
        except Exception as e:
            weathe[i]=str(waypoint[i])+"→"+"Not Available"
    #op is ouyput of all polyline coordinates
    op=simplejson.dumps(op)
    #storing coordinates of all waypoints in waycoord
    waycoord=[]
    for z in waypoint:
        waycoord.append(latlong(str(z)))
    waycoord=simplejson.dumps(waycoord)

    message= 'Enter Atleast 1 Destination'

    context={'coord':op, 'waypoint':waypoint,'weather':weathe,'waycoord':waycoord,'pathType':pathType, 'message':message}
    return render(request, 'output.html' , context)


#  AUAPP VIEWS


def user_signup(request):

    if request.method == "POST":
        un = request.POST.get("un")
        em = request.POST.get("em")
        try:
            usr = User.objects.get(username=un)
            return render(request, "user_signup.html", {'msg': "Username Already Exists"})
        except User.DoesNotExist:
            try:
                usr = User.objects.get(email=em)
                return render(request, "user_signup.html", {"msg": "Email Already Exists"})
            except User.DoesNotExist:
                pw = ""
                text = "1234567890"
                for i in range(6):
                    pw = pw + text[randrange(len(text))]
                print(pw)
                msg = "Your Password is "+pw
                send_mail("Welcome to RTA ", msg, EMAIL_HOST_USER, [str(em)])
                usr = User.objects.create_user(
                    username=un, password=pw, email=em)
                usr.save()
                return redirect("user_login")
    else:
        return render(request, "user_signup.html")


def user_login(request):
    if request.method == "POST":
        un = request.POST.get("un")
        pw = request.POST.get("pw")
        usr = authenticate(username=un, password=pw)
        if usr is None:
            return render(request, "user_login.html", {"msg": "Access Denied"})
        else:
            login(request, usr)
            request.session['name'] = un
            return redirect("home")
    else:
        return render(request, "user_login.html")


def user_logout(request):
    logout(request)
    request.session.flush()
    request.session.clear_expired()
    return redirect("user_login")


def user_rp(request):
    if request.method == "POST":
        un = request.POST.get("un")
        em = request.POST.get("em")
        try:
            usr = User.objects.get(username=un) and User.objects.get(email=em)
            pw = ""
            text = "1234567890"
            for i in range(6):
                pw = pw + text[randrange(len(text))]
            print(pw)
            msg = "Your Password has been resetted, New Password is "+pw
            send_mail("Welcome to RTA", msg, EMAIL_HOST_USER, [str(em)])
            usr.set_password(pw)
            usr.save()
            return redirect("user_login")
        except User.DoesNotExist:
            return render(request, "user_rp.html", {"msg": "Invalid Info"})
    else:
        return render(request, "user_rp.html")


def user_cp(request):
    if request.method == "POST" and request.user.is_authenticated:
        un = request.user.username
        pw1 = request.POST.get("pw1")
        pw2 = request.POST.get("pw2")
        if pw1 == pw2:
            usr = User.objects.get(username=un)
            print(usr)
            usr.set_password(pw1)
            usr.save()
            return redirect("user_login")
        else:
            return render(request, "user_cp.html", {"msg":"Password did not match"})
    elif request.method == "GET" and request.user.is_authenticated:
        return render(request, "user_cp.html")
    else:
        return redirect("user_login")


# HOME
def home(request):
    return render(request,"home.html")
