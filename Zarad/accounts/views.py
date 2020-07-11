from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse

# Create your views here.
def signup_page(request):
    adminLogin = False
    isloggedin = False
    accountType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        if request.session['useremail'] == 'nazmultakbir98@gmail.com' or request.session['useremail'] == 'fatimanawmi@gmail.com':
            adminLogin = True
            accountType = 'admin'
        else:
            return HttpResponseRedirect(reverse('home_page'))

    if request.method == 'POST':
        if request.POST.get("radioButton", "empty") == 'Customer':
            email = request.POST.get("customerEmail","empty")
            password = request.POST.get("customerPassword","empty")
            fname = request.POST.get("customerFirstName","empty")
            lname = request.POST.get("customerLastName","empty")
            dob = request.POST.get("customerDOB","empty")
            dob = dob[8:10]+'-'+dob[5:7]+'-'+dob[0:4]
            phno = request.POST.get("customerPhNo","empty")
            apart = request.POST.get("customerApartment","")
            area = request.POST.get("customerArea","empty")
            building = request.POST.get("customerBuilding","")
            road = request.POST.get("customerRoad","")
            city = request.POST.get("customerCity","empty")
            latitude = request.POST.get("customerLatitude","empty")
            longitude = request.POST.get("customerLongitude","empty")

            if 'customerImage' in request.FILES:
                img = request.FILES['customerImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if 'check if email is already taken':
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
            else:
                query = """INSERT INTO CUSTOMER(CUSTOMER_ID, FIRST_NAME ,LAST_NAME ,APARTMENT_NUMBER ,
                           BUILDING_NUMBER , ROAD, AREA , CITY , PHONE_NUMBER , DOB, EMAIL_ID , PASSWORD,
                           LOCATION) VALUES(CUSTOMER_ID_SEQ.NEXTVAL, fname, lname , apart, building, road,
                           area, city, phno,TO_DATE(dob , 'DD-MM-YYYY'), email , password ,'23.726627,
                           90.388727')"""
                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query)
                return HttpResponseRedirect(reverse('accounts:login'))

        elif request.POST.get("radioButton", "empty") == 'Employee':
            email = request.POST.get("employeeEmail","empty")
            password = request.POST.get("employeePassword","empty")
            fname = request.POST.get("employeeFirstName","empty")
            lname = request.POST.get("employeeLastName","empty")
            dob = request.POST.get("employeeDOB","empty")
            dob = dob[8:10]+'-'+dob[5:7]+'-'+dob[0:4]
            phno = request.POST.get("employeePhNo","empty")
            apart = request.POST.get("employeeApartment","")
            area = request.POST.get("employeeArea","empty")
            building = request.POST.get("employeeBuilding","")
            road = request.POST.get("employeeRoad","")
            city = request.POST.get("employeeCity","empty")
            type = request.POST.get("employeeType","empty")
            salary = request.POST.get("employeeSalary","empty")
            latitude = request.POST.get("employeeLatitude","empty")
            longitude = request.POST.get("employeeLongitude","empty")
            
            if 'employeeImage' in request.FILES:
                img = request.FILES['employeeImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if 'check if email is already taken':
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
            else:
                query = """INSERT INTO EMPLOYEE(EMPLOYEE_ID, FIRST_NAME ,LAST_NAME ,APARTMENT_NUMBER ,
                           BUILDING_NUMBER ,ROAD, AREA , CITY , PHONE_NUMBER , DOB, EMAIL_ID , PASSWORD,
                           SALARY) VALUES(EMPLOYEE_ID_SEQ.NEXTVAL, fname, lname , apart, building, road, area,
                           city, phno,TO_DATE(dob , 'DD-MM-YYYY'), email , password,TO_NUMBER(salary) )"""
                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query)
                return HttpResponseRedirect(reverse('login'))

        elif request.POST.get("radioButton", "empty") == 'Seller':
            email = request.POST.get("sellerEmail","")
            password = request.POST.get("sellerPassword","")
            name = request.POST.get("sellerName","")
            website = request.POST.get("sellerWebsite","")
            phno1 = request.POST.get("sellerPhNo","")
            phno2 = request.POST.get("sellerPhNo2","")
            phno3 = request.POST.get("sellerPhNo3","")
            phno4 = request.POST.get("sellerPhNo4","")
            area = request.POST.get("sellerArea","")
            building = request.POST.get("sellerBuilding","")
            road = request.POST.get("sellerRoad","")
            city = request.POST.get("sellerCity","")
            latitude = request.POST.get("sellerLatitude","empty")
            longitude = request.POST.get("sellerLongitude","empty")

            phno = [phno1]
            if phno2 != "":
                phno.append(phno2)
            if phno3 != "":
                phno.append(phno3)
            if phno4 != "":
                phno.append(phno4)

            if 'sellerImage' in request.FILES:
                img = request.FILES['sellerImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if 'check if email is already taken':
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
            else:
                query = """INSERT INTO SELLER(SELLER_ID, NAME , BUILDING_NUMBER , ROAD, AREA , CITY , EMAIL_ID ,
                           PASSWORD, WEBSITE, LOCATION ) VALUES(SELLER_ID_SEQ.NEXTVAL, name, building, road,
                           area, city, email , password,website , '23.726627, 90.388727' )"""
                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query)
                for i in range(len(phno)):
                    query = """INSERT INTO SELLER_PHONE_NUMBER VALUES((SELECT MAX(SELLER_ID) FROM SELLER),
                               phno[i] )"""
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query)
                return HttpResponseRedirect(reverse('login'))

    return render(request, 'signup.html', {'emailExists': False, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})

def login_page(request):
    isloggedin = False
    accountType = 'none'
    if request.session.has_key('useremail'):
        return HttpResponseRedirect(reverse('home_page'))
    if request.method == 'GET':
        return render(request, 'login.html', {'error': False, 'isloggedin': isloggedin, 'accountType': accountType})
    elif request.method == 'POST':
        email = request.POST.get("Email", "empty")
        password = request.POST.get("Password", "empty")

        if 'check if email and password match':
            request.session['useremail'] = email
            return HttpResponseRedirect(reverse('home_page'))
        else:
            return render(request, 'login.html', {'error': True, 'isloggedin': isloggedin, 'accountType': accountType})

def logout_page(request):
    if request.session.has_key('useremail'):
        del request.session['useremail']
        return HttpResponseRedirect(reverse('home_page'))
    else:
        return HttpResponseRedirect(reverse('home_page'))

def myaccount(request):
    isloggedin = False
    accountType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        if request.session['useremail'] == 'nazmultakbir98@gmail.com' or request.session['useremail'] == 'fatimanawmi@gmail.com':
            ### accountType = 'admin'
            accountType = 'customer'
        else:
            " check accountType from database using request.session['useremail'] "
            accountType = 'customer'
        if accountType == 'customer':
            return render(request, 'customerAccount.html', {'isloggedin': isloggedin, 'accountType': accountType})
        elif accountType == 'seller':
            return render(request, 'sellerAccount.html', {'isloggedin': isloggedin, 'accountType': accountType})
        elif accountType == 'deliveryGuy':
            return render(request, 'deliveryGuy.html', {'isloggedin': isloggedin, 'accountType': accountType})
        elif accountType == 'customerCare':
            return render(request, 'customerCare.html', {'isloggedin': isloggedin, 'accountType': accountType})
        elif accountType == 'admin':
            pass
    else:
        return HttpResponseRedirect(reverse('home_page'))
