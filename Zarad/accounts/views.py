from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from Zarad import settings

def signup_page(request):
    adminLogin = False
    if request.user.is_authenticated:
        if request.user.email == 'nazmultakbir98@gmail.com':
            adminLogin = True
        else:
            return HttpResponseRedirect(reverse('home_page'))


    if request.method == 'POST':
        if request.POST.get("radioButton", "empty") == 'Customer':
            email = request.POST.get("customerEmail","empty")
            password = request.POST.get("customerPassword","empty")
            fname = request.POST.get("customerFirstName","empty")
            lname = request.POST.get("customerLastName","empty")
            dob = request.POST.get("customerDOB","empty")
            phno = request.POST.get("customerPhNo","empty")
            apart = request.POST.get("customerApartment","empty")
            area = request.POST.get("customerArea","empty")
            building = request.POST.get("customerBuilding","empty")
            road = request.POST.get("customerRoad","empty")
            city = request.POST.get("customerCity","empty")

            if 'customerImage' in request.FILES:
                img = request.FILES['customerImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if User.objects.filter(email=email).exists():
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin})
            else:
                pass
                # user = User.objects.create_user(username=email, email=email, password=password)
                # user.save()
                # return HttpResponseRedirect(reverse('accounts:login'))

        elif request.POST.get("radioButton", "empty") == 'Employee':
            email = request.POST.get("employeeEmail","empty")
            password = request.POST.get("employeePassword","empty")
            fname = request.POST.get("employeeFirstName","empty")
            lname = request.POST.get("employeeLastName","empty")
            dob = request.POST.get("employeeDOB","empty")
            phno = request.POST.get("employeePhNo","empty")
            apart = request.POST.get("employeeApartment","empty")
            area = request.POST.get("employeeArea","empty")
            building = request.POST.get("employeeBuilding","empty")
            road = request.POST.get("employeeRoad","empty")
            city = request.POST.get("employeeCity","empty")
            type = request.POST.get("employeeType","empty")
            salary = request.POST.get("employeeSalary","empty")

            if 'employeeImage' in request.FILES:
                img = request.FILES['employeeImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if User.objects.filter(email=email).exists():
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin})
            else:
                pass
                # user = User.objects.create_user(username=email, email=email, password=password)
                # user.save()
                # return HttpResponseRedirect(reverse('login'))

        elif request.POST.get("radioButton", "empty") == 'Seller':
            email = request.POST.get("sellerEmail","empty")
            password = request.POST.get("sellerPassword","empty")
            name = request.POST.get("sellerName","empty")
            website = request.POST.get("sellerWebsite","empty")
            phno = request.POST.get("sellerPhNo","empty")
            area = request.POST.get("sellerArea","empty")
            building = request.POST.get("sellerBuilding","empty")
            road = request.POST.get("sellerRoad","empty")
            city = request.POST.get("sellerCity","empty")

            if 'sellerImage' in request.FILES:
                img = request.FILES['sellerImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if User.objects.filter(email=email).exists():
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin})
            else:
                pass
                # user = User.objects.create_user(username=email, email=email, password=password)
                # user.save()
                # return HttpResponseRedirect(reverse('login'))

    return render(request, 'signup.html', {'emailExists': False, 'adminLogin': adminLogin})

def login_page(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'error': False})
    elif request.method == 'POST':
        email = request.POST.get("Email", "empty")
        password = request.POST.get("Password", "empty")
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('home_page'))
        else:
            return render(request, 'login.html', {'error': True})

@login_required
def logout_page(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('home_page'))
