from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
import os
from Zarad import settings

# Create your views here.
def signup_page(request):
    adminLogin = False
    if request.session.has_key('useremail'):
        if request.user['useremail'] == 'nazmultakbir98@gmail.com' or request.user['useremail'] == 'fatimanawmi@gmail.com':
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
            apart = request.POST.get("customerApartment","")
            area = request.POST.get("customerArea","empty")
            building = request.POST.get("customerBuilding","")
            road = request.POST.get("customerRoad","")
            city = request.POST.get("customerCity","empty")

            if 'customerImage' in request.FILES:
                img = request.FILES['customerImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            # if User.objects.filter(email=email).exists():
            #     return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin})
            # else:
            #     pass
                # user = User.objects.create_user(username=email, email=email, password=password)
                # user.save()
                query = "INSERT INTO CUSTOMER(CUSTOMER_ID, FIRST_NAME ,LAST_NAME ,APARTMENT_NUMBER , BUILDING_NUMBER , ROAD, AREA , CITY , PHONE_NUMBER , DOB, EMAIL_ID , PASSWORD, LOCATION) VALUES(CUSTOMER_ID_SEQ.NEXTVAL, fname, lname , apart, building, road, area, city, phno,TO_DATE(dob , 'DD-MM-YYYY'), email , password ,'23.726627, 90.388727')"
                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query)

                # return HttpResponseRedirect(reverse('accounts:login'))

        elif request.POST.get("radioButton", "empty") == 'Employee':
            email = request.POST.get("employeeEmail","empty")
            password = request.POST.get("employeePassword","empty")
            fname = request.POST.get("employeeFirstName","empty")
            lname = request.POST.get("employeeLastName","empty")
            dob = request.POST.get("employeeDOB","empty")
            phno = request.POST.get("employeePhNo","empty")
            apart = request.POST.get("employeeApartment","")
            area = request.POST.get("employeeArea","empty")
            building = request.POST.get("employeeBuilding","")
            road = request.POST.get("employeeRoad","")
            city = request.POST.get("employeeCity","empty")
            type = request.POST.get("employeeType","empty")
            salary = request.POST.get("employeeSalary","empty")

            if 'employeeImage' in request.FILES:
                img = request.FILES['employeeImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            # if User.objects.filter(email=email).exists():
            #     return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin})
            # else:
            #     pass
                # user = User.objects.create_user(username=email, email=email, password=password)
                # user.save()
                query = "INSERT INTO EMPLOYEE(EMPLOYEE_ID, FIRST_NAME ,LAST_NAME ,APARTMENT_NUMBER , BUILDING_NUMBER ,ROAD, AREA , CITY , PHONE_NUMBER , DOB, EMAIL_ID , PASSWORD, SALARY) VALUES(CUSTOMER_ID_SEQ.NEXTVAL, fname, lname , apart, building, road, area, city, phno,TO_DATE(dob , 'DD-MM-YYYY'), email , password,TO_NUMBER(salary) )"
                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query)
                # return HttpResponseRedirect(reverse('login'))

        elif request.POST.get("radioButton", "empty") == 'Seller':
            email = request.POST.get("sellerEmail","empty")
            password = request.POST.get("sellerPassword","empty")
            name = request.POST.get("sellerName","empty")
            website = request.POST.get("sellerWebsite","empty")
            phno = request.POST.get("sellerPhNo","empty")
            area = request.POST.get("sellerArea","empty")
            building = request.POST.get("sellerBuilding","")
            road = request.POST.get("sellerRoad","")
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
                query = "INSERT INTO SELLER(SELLER_ID, NAME , BUILDING_NUMBER , ROAD, AREA , CITY , EMAIL_ID , PASSWORD, WEBSITE, LOCATION ) VALUES(SELLER_ID_SEQ.NEXTVAL, name, building, road, area, city, email , password,website , '23.726627, 90.388727' )"
                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query)
                for i in range(len(phno)):
                    query = "INSERT INTO SELLER_PHONE_NUMBER VALUES((SELECT MAX(SELLER_ID) FROM SELLER), phno[i] )"
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query)
                # return HttpResponseRedirect(reverse('login'))

    return render(request, 'signup.html', {'emailExists': False, 'adminLogin': adminLogin})

def login_page(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'error': False})
    elif request.method == 'POST':
        email = request.POST.get("Email", "empty")
        password = request.POST.get("Password", "empty")
        request.session['useremail'] = email
        # user = authenticate(username=email, password=password)
        # if user is not None:
        #     login(request, user)
        #     return HttpResponseRedirect(reverse('home_page'))
        # else:
        #     return render(request, 'login.html', {'error': True})
        return HttpResponseRedirect(reverse('home_page'))

def logout_page(request):
    if request.session.has_key('useremail'):
        del request.session['useremail']
        return HttpResponseRedirect(reverse('home_page'))
    else:
        return HttpResponseRedirect(reverse('home_page'))

def myaccount(request):
    accountType = 'customerCare'
    if accountType == 'customer':
        return render(request, 'customerAccount.html')
    elif accountType == 'seller':
        return render(request, 'sellerAccount.html')
    elif accountType == 'deliveryGuy':
        return render(request, 'deliveryGuy.html')
    elif accountType == 'customerCare':
        return render(request, 'customerCare.html')
    elif accountType == 'admin':
        pass
