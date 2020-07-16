from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from PIL import Image
from django.conf import settings
import io

# Create your views here.
def email_taken(email):
    with connections['oracle'].cursor() as cursor:
        cursor.execute("SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email", {"email": email})
        results = cursor.fetchall()
        if(len(results) == 0):
            cursor.execute("SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :email", {"email": email})
            results = cursor.fetchall()
            if(len(results) == 0):
                cursor.execute("SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email", {"email": email})
                results = cursor.fetchall()
            if(len(results)== 0):
                return False
            else:
                return True

        if(len(results)== 0):
            return False
        else:
            return True

def email_pass_match(email , password):
    with connections['oracle'].cursor() as cursor:
        cursor.execute("SELECT PASSWORD FROM SELLER WHERE EMAIL_ID ="+ email)
        results = cursor.fetchall()
        if(len(results) == 0):
            cursor.execute("SELECT PASSWORD FROM CUSTOMER WHERE EMAIL_ID ="+ email)
            results = cursor.fetchall()
            if(len(results) == 0):
                cursor.execute("SELECT PASSWORD FROM EMPLOYEE WHERE EMAIL_ID ="+ email)
                results = cursor.fetchall()
                if( len(result) == 0 ):
                    return False
                else:
                    if( results[0] == password ):
                        return True
                    else:
                        return False
            else:
                if( results[0] == password):
                    return True
                else:
                    return False
        else:
            if( results[0] == password ):
                return True
            else:
                return False

def accountType(email):
    with connections['oracle'].cursor() as cursor:
        cursor.execute("SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID ="+ email)
        results = cursor.fetchall()
        if(len(results) == 0):
            cursor.execute("SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID ="+ email)
            results = cursor.fetchall()
            if(len(results) == 0):
                cursor.execute("SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID ="+ email)
                empID = cursor.fetchall()[0]
                cursor.execute("SELECT EMPLOYEE_ID FROM DELIVERY_GUY WHERE EMPLOYEE_ID ="+ empID)
                results = cursor.fetchall()
                if(len(results) == 0):
                     cursor.execute("SELECT EMPLOYEE_ID FROM CUSTOMER_CARE_EMPLOYEE WHERE EMPLOYEE_ID ="+ empID)
                     results = cursor.fetchall()
                     if(len(results) == 0):
                         cursor.execute("SELECT EMPLOYEE_ID FROM ADMIN WHERE EMPLOYEE_ID ="+ empID)
                         results = cursor.fetchall()
                         if(len(results) != 0):
                             return 'admin'
                     else :
                         return 'customerCare'
                else:
                    return 'deliveryGuy'
            else:
                    return 'customer'
        else:
            return 'seller'

def make_image_square(img):
    width, height = img.size
    size = max(width, height)
    new_img = Image.new('RGB', (size, size), (255, 255, 255))
    new_img.paste(img, (int((size - width) / 2), int((size - height) / 2)))
    return new_img

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
            email = request.POST.get("customerEmail")
            password = request.POST.get("customerPassword")
            fname = request.POST.get("customerFirstName")
            lname = request.POST.get("customerLastName")
            dob = request.POST.get("customerDOB")
            dob = dob[0:4] + "-" + dob[-5:-3] + "-" + dob[-2:]
            phno = request.POST.get("customerPhNo")
            apart = request.POST.get("customerApartment")
            area = request.POST.get("customerArea")
            building = request.POST.get("customerBuilding")
            road = request.POST.get("customerRoad")
            city = request.POST.get("customerCity","NULL")
            latitude = request.POST.get("customerLatitude")
            longitude = request.POST.get("customerLongitude")
            location = latitude+ ','+ longitude

            if email_taken(email) == True :
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
            else:
                if 'customerImage' in request.FILES:
                    imgFile = request.FILES['customerImage']
                    img = Image.open(imgFile)
                    squareImg = make_image_square(img)
                    blob = io.BytesIO()
                    squareImg.save(blob, 'jpeg')
                    blob.seek(0)

                    query = """INSERT INTO CUSTOMER(CUSTOMER_ID, FIRST_NAME, LAST_NAME, APARTMENT_NUMBER,
                                BUILDING_NUMBER, ROAD, AREA, CITY, PHONE_NUMBER, DOB, EMAIL_ID , PASSWORD,
                                LOCATION, PICTURE) VALUES(CUSTOMER_ID_SEQ.NEXTVAL, :fname, :lname, :apart,
                                :building, :road, :area, :city, :phno, TO_DATE(:dob, 'yyyy-mm-dd'), :email, :password, :location,
                                :picture)"""
                    with connections['oracle'].cursor() as cursor:
                        data = { 'email': email, 'password': password, 'fname': fname, 'lname': lname, 'dob': dob,
                                 'phno': phno, 'apart': apart, 'area': area, 'building': building, 'road': road,
                                 'city': city, 'location': location, 'picture': blob.getvalue() }
                        cursor.execute(query, data)
                        cursor.execute("commit")
                else:
                    query ="""INSERT INTO CUSTOMER(CUSTOMER_ID, FIRST_NAME ,LAST_NAME ,APARTMENT_NUMBER ,
                               BUILDING_NUMBER , ROAD, AREA , CITY , PHONE_NUMBER , DOB, EMAIL_ID , PASSWORD,
                               LOCATION ) VALUES(CUSTOMER_ID_SEQ.NEXTVAL,""" + fname + """,
                                """+lname+ """, """+  apart+ """, """+ building+ """, """+  road+ """,
                               """+area+ """, """+ city+ """, """+  phno+ """, """+ """TO_DATE("""+ dob +""", 'DD-MM-YYYY'),
                                """+email+ """, """+  password + """, """+ location+ """)"""
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
            employeeType = request.POST.get("employeeType","empty") # customerCare # deliveryGuy
            salary = request.POST.get("employeeSalary","empty")
            latitude = request.POST.get("employeeLatitude","empty")
            longitude = request.POST.get("employeeLongitude","empty")
            location = latitude+ ','+ longitude

            if 'employeeImage' in request.FILES:
                img = request.FILES['employeeImage']
                imgBLOB = img.read()
                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if email_taken(email) == True :
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
            else:
                query = """INSERT INTO EMPLOYEE(EMPLOYEE_ID, FIRST_NAME ,LAST_NAME ,APARTMENT_NUMBER ,
                           BUILDING_NUMBER ,ROAD, AREA , CITY , PHONE_NUMBER , DOB, EMAIL_ID , PASSWORD,
                           SALARY, PICTURE) VALUES(EMPLOYEE_ID_SEQ.NEXTVAL,"""+ fname +""","""+ lname +"""
                            ,"""+apart+""","""+ building+""","""+ road+""","""+ area+""","""+ city+""",
                            """+ phno+""", TO_DATE("""+ dob+""" , 'DD-MM-YYYY'),"""+ email +""",
                            """+password+""","""+ """TO_NUMBER( """+ salary +"""),"""+ imgBLOB+""" )"""
                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query)
                if employeeType == 'customerCare':
                    query = """INSERT INTO CUSTOMER_CARE_EMPLOYEE VALUES(( SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID ="""+ email+ """))"""
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query)
                elif employeeType == 'deliveryGuy':
                     query = """INSERT INTO DELIVERY_GUY VALUES(( SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID ="""+ email+ """),"""+ location+""" )"""
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
            location = latitude+ ','+ longitude

            phno = [phno1]
            if phno2 != "":
                phno.append(phno2)
            if phno3 != "":
                phno.append(phno3)
            if phno4 != "":
                phno.append(phno4)

                # https://cx-oracle.readthedocs.io/en/latest/user_guide/lob_data.html

            if email_taken(email) == True :
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
            else:
                if 'sellerImage' in request.FILES:
                    img = request.FILES['sellerImage']
                    imgBLOB = img.read()
                    query = """INSERT INTO SELLER(SELLER_ID, NAME , BUILDING_NUMBER , ROAD, AREA , CITY , EMAIL_ID ,
                               PASSWORD, WEBSITE, LOCATION, PICTURE ) VALUES( SELLER_ID_SEQ.NEXTVAL, """+ name+"""
                               building+""","""+ road+""","""+ area+""","""+ city+""","""+ email +""","""+
                               ,"""+password+""","""+website +""","""+ location +""","""+ imgBLOB+""")"""
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query)
                    for i in range(len(phno)):
                        query = """INSERT INTO SELLER_PHONE_NUMBER VALUES((SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID =
                        """+ email+ """),"""+ phno[i]+""" )"""
                        with connections['oracle'].cursor() as cursor:
                            cursor.execute(query)
                else:
                    query = """INSERT INTO SELLER(SELLER_ID, NAME , BUILDING_NUMBER , ROAD, AREA , CITY , EMAIL_ID ,
                               PASSWORD, WEBSITE, LOCATION ) VALUES(SELLER_ID_SEQ.NEXTVAL,"""+  name + """,""" + building + ""","""+ road + """
                               ,"""+area+ ""","""+ city+ ""","""+ email + ""","""+ password + ""","""+ website+ ""","""+ location +""")"""
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query)
                    for i in range(len(phno)):
                        query = """INSERT INTO SELLER_PHONE_NUMBER VALUES((SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = """+ email +""")
                                   ,"""+phno[i] + """)"""
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

        if email_pass_match(email , password) == True:
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
            accountType = accountType(request.session['useremail'])
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
