from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from PIL import Image
from django.conf import settings
import io
import info
import random
import datetime
from django.http import JsonResponse
import json

def deliveryEmployeeSelection(orderID):
    orderID = int(orderID)
    query = """SELECT HAVERSINE(ORDER_ID) FROM CUSTOMER_ORDER WHERE ORDER_ID = (:orderID)"""
    with connections['oracle'].cursor() as cursor:
        cursor.execute(query, {'orderID':orderID});
        id = cursor.fetchall()[0][0]
    return id

def getAdverts(request):
    query = """SELECT PRODUCT_ID, SELLER_ID, ADVERTISEMENT_NUMBER, PICTURE FROM ADVERTISEMENT
               WHERE END_DATE>SYSDATE"""
    with connections['oracle'].cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        imagePaths = []
        for result in results:
            imagePath = "http://{}/static/images/productImages/advert{}_{}_{}.jpg".format(request.META['HTTP_HOST'], result[0], result[1], result[2])
            imageFile = open(settings.BASE_DIR+"\\static\\images\\productImages\\advert{}_{}_{}.jpg".format(result[0], result[1], result[2]),'wb')
            imageFile.write( result[3].read() )
            imageFile.close()
            imagePaths.append(imagePath)
        if len(imagePaths)<4:
            placeHolder = "http://{}/static/images/productImages/{}".format(request.META['HTTP_HOST'], 'advertisementPlaceholder.jpg')
            imagePaths.append(placeHolder)
        adverts = []
        for i in range(8):
            index = random.randrange(0, len(imagePaths))
            adverts.append(imagePaths[index])
        return adverts

def check_productID(product_id, seller_id):
    with connections['oracle'].cursor() as cursor:
        query = "SELECT PRODUCT_ID FROM PRODUCT WHERE ( PRODUCT_ID = :product_id AND SELLER_ID = :seller_id )"
        cursor.execute(query, {'product_id' :product_id, 'seller_id': seller_id})
        result = cursor.fetchall()
        if(len(result) == 0):
            return False
        else:
            return True

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
        cursor.execute("SELECT PASSWORD FROM SELLER WHERE EMAIL_ID = :email", {"email": email})
        results = cursor.fetchall()
        if(len(results) == 0):
            cursor.execute("SELECT PASSWORD FROM CUSTOMER WHERE EMAIL_ID = :email", {"email": email})
            results = cursor.fetchall()
            if(len(results) == 0):
                cursor.execute("SELECT PASSWORD FROM EMPLOYEE WHERE EMAIL_ID = :email", {"email": email})
                results = cursor.fetchall()
                if( len(results) == 0 ):
                    return False
                else:
                    if( results[0][0] == password ):
                        return True
                    else:
                        return False
            else:
                if( results[0][0]  == password):
                    return True
                else:
                    return False
        else:
            if( results[0][0]  == password ):
                return True
            else:
                return False

def accountType(email):
    with connections['oracle'].cursor() as cursor:
        cursor.execute("SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID =:email", {"email": email})
        results = cursor.fetchall()
        if(len(results) == 0):
            cursor.execute("SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID =:email", {"email": email})
            results = cursor.fetchall()
            if(len(results) == 0):
                cursor.execute("SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID =:email", {"email": email})
                emID = cursor.fetchall()[0][0]
                cursor.execute("SELECT EMPLOYEE_ID FROM DELIVERY_GUY WHERE EMPLOYEE_ID =:emID", {"emID" : emID})
                results = cursor.fetchall()
                if(len(results) == 0):
                     cursor.execute("SELECT EMPLOYEE_ID FROM CUSTOMER_CARE_EMPLOYEE WHERE EMPLOYEE_ID =:emID", {"emID" : emID})
                     results = cursor.fetchall()
                     if(len(results) == 0):
                         cursor.execute("SELECT EMPLOYEE_ID FROM ADMIN WHERE EMPLOYEE_ID =:emID", {"emID" : emID})
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

def make_9_2(img):
    width, height = img.size
    if width > height*4.5:
        newwidth = width
        newheight = int(width * 2/9)
        new_img = Image.new('RGB', (newwidth, newheight), (242, 247, 228))
        new_img.paste(img, (int((newwidth - width) / 2), int((newheight - height) / 2)))
        return new_img
    else:
        newwidth = int(height*(9/2))
        newheight = height
        new_img = Image.new('RGB', (newwidth, newheight), (242, 247, 228))
        new_img.paste(img, (int((newwidth - width) / 2), int((newheight - height) / 2)))
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

    adverts = getAdverts(request)

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
                data = {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin,
                        'accountType': accountType,'advert1': adverts[0], 'advert2': adverts[1],
                        'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4],
                        'advert6': adverts[5], 'advert7': adverts[6], 'advert8': adverts[7]}
                return render(request, 'signup.html', data)
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
                                :building, :road, :area, :city, :phno, TO_DATE(:dob, 'YYYY-MM-DD'), :email, :password, :location,
                                :picture)"""
                    with connections['oracle'].cursor() as cursor:
                        data = { 'email': email, 'password': password, 'fname': fname, 'lname': lname, 'dob': dob,
                                 'phno': phno, 'apart': apart, 'area': area, 'building': building, 'road': road,
                                 'city': city, 'location': location, 'picture': blob.getvalue() }
                        cursor.execute(query, data)
                        cursor.execute("COMMIT")
                else:
                    query = """INSERT INTO CUSTOMER(CUSTOMER_ID, FIRST_NAME, LAST_NAME, APARTMENT_NUMBER,
                               BUILDING_NUMBER, ROAD, AREA, CITY, PHONE_NUMBER, DOB, EMAIL_ID , PASSWORD,
                               LOCATION) VALUES(CUSTOMER_ID_SEQ.NEXTVAL, :fname, :lname, :apart,
                               :building, :road, :area, :city, :phno, TO_DATE(:dob, 'YYYY-MM-DD'), :email, :password, :location)"""
                    with connections['oracle'].cursor() as cursor:
                        data = { 'email': email, 'password': password, 'fname': fname, 'lname': lname, 'dob': dob,
                                 'phno': phno, 'apart': apart, 'area': area, 'building': building, 'road': road,
                                 'city': city, 'location': location}
                        cursor.execute(query, data)
                        cursor.execute("COMMIT")
                return HttpResponseRedirect(reverse('accounts:login'))

        elif request.POST.get("radioButton", "empty") == 'Employee':
            email = request.POST.get("employeeEmail")
            password = request.POST.get("employeePassword")
            fname = request.POST.get("employeeFirstName")
            lname = request.POST.get("employeeLastName")
            dob = request.POST.get("employeeDOB")
            dob = dob[0:4] + "-" + dob[-5:-3] + "-" + dob[-2:]
            phno = request.POST.get("employeePhNo")
            apart = request.POST.get("employeeApartment")
            area = request.POST.get("employeeArea")
            building = request.POST.get("employeeBuilding")
            road = request.POST.get("employeeRoad")
            city = request.POST.get("employeeCity")
            employeeType = request.POST.get("employeeType")
            salary = request.POST.get("employeeSalary")
            latitude = request.POST.get("employeeLatitude")
            longitude = request.POST.get("employeeLongitude")
            location = latitude+ ','+ longitude

            blob = io.BytesIO()
            if 'employeeImage' in request.FILES:
                imgFile = request.FILES['employeeImage']
                img = Image.open(imgFile)
                squareImg = make_image_square(img)
                squareImg.save(blob, 'jpeg')
                blob.seek(0)

            if email_taken(email) == True :
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
            else:
                query = """INSERT INTO EMPLOYEE(EMPLOYEE_ID, FIRST_NAME ,LAST_NAME ,APARTMENT_NUMBER ,
                           BUILDING_NUMBER ,ROAD, AREA , CITY , PHONE_NUMBER , DOB, EMAIL_ID , PASSWORD,
                           SALARY, PICTURE) VALUES(EMPLOYEE_ID_SEQ.NEXTVAL, :fname, :lname ,:apart, :building, :road, :area, :city ,:phno,
                           TO_DATE(:dob, 'YYYY-MM-DD'), :email ,:password ,TO_NUMBER(:salary), :picture )"""

                with connections['oracle'].cursor() as cursor:
                    data = {'fname' : fname, 'lname': lname, 'apart': apart, 'building':building ,'road' : road , 'area' :area , 'city':city,
                            'phno' :phno , 'email' :email , 'password':password , 'dob' :dob, 'salary':salary, 'picture':blob.getvalue()}
                    cursor.execute(query, data)
                    cursor.execute("COMMIT")
                if employeeType == 'customerCare':
                    query = """INSERT INTO CUSTOMER_CARE_EMPLOYEE VALUES(( SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :email))"""
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query, {'email':email})
                        cursor.execute("COMMIT")
                elif employeeType == 'deliveryGuy':
                     query = """INSERT INTO DELIVERY_GUY VALUES(( SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :email) , :location)"""
                     with connections['oracle'].cursor() as cursor:
                         cursor.execute(query, {'email': email, 'location':location})
                         cursor.execute("COMMIT")
                return HttpResponseRedirect(reverse('accounts:login'))

        elif request.POST.get("radioButton", "empty") == 'Seller':
            email = request.POST.get("sellerEmail")
            password = request.POST.get("sellerPassword")
            name = request.POST.get("sellerName")
            website = request.POST.get("sellerWebsite")
            phno1 = request.POST.get("sellerPhNo")
            phno2 = request.POST.get("sellerPhNo2")
            phno3 = request.POST.get("sellerPhNo3")
            phno4 = request.POST.get("sellerPhNo4")
            area = request.POST.get("sellerArea")
            building = request.POST.get("sellerBuilding")
            road = request.POST.get("sellerRoad")
            city = request.POST.get("sellerCity")
            latitude = request.POST.get("sellerLatitude")
            longitude = request.POST.get("sellerLongitude")
            location = latitude+ ','+ longitude

            phno = [phno1]
            if phno2 != "":
                phno.append(phno2)
            if phno3 != "":
                phno.append(phno3)
            if phno4 != "":
                phno.append(phno4)

            if email_taken(email) == True :
                data = {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin,
                        'accountType': accountType,'advert1': adverts[0], 'advert2': adverts[1],
                        'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4],
                        'advert6': adverts[5], 'advert7': adverts[6], 'advert8': adverts[7]}
                return render(request, 'signup.html', data)
            else:
                if 'sellerImage' in request.FILES:
                    imgFile = request.FILES['sellerImage']
                    img = Image.open(imgFile)
                    squareImg = make_image_square(img)
                    blob = io.BytesIO()
                    squareImg.save(blob, 'jpeg')
                    blob.seek(0)

                    query = """INSERT INTO SELLER(SELLER_ID, NAME , BUILDING_NUMBER , ROAD, AREA , CITY , EMAIL_ID ,
                               PASSWORD, WEBSITE, LOCATION, LOGO ) VALUES( SELLER_ID_SEQ.NEXTVAL, :name, :building,
                               :road, :area, :city, :email, :password, :website , :location , :imgBLOB)"""
                    with connections['oracle'].cursor() as cursor:
                        data = {'name' : name, 'building':building ,'road' : road , 'area' :area , 'city':city,
                        'email' :email , 'password':password ,'imgBLOB':blob.getvalue(), 'location' :location , 'website':website}
                        cursor.execute(query, data)
                        cursor.execute("COMMIT")
                    for i in range(len(phno)):
                        query = """INSERT INTO SELLER_PHONE_NUMBER VALUES((SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email),:phno)"""
                        with connections['oracle'].cursor() as cursor:
                            cursor.execute(query, {'email':email, 'phno':phno[i]})
                            cursor.execute("COMMIT")
                else:
                    query = """INSERT INTO SELLER(SELLER_ID, NAME , BUILDING_NUMBER , ROAD, AREA , CITY , EMAIL_ID ,
                               PASSWORD, WEBSITE, LOCATION ) VALUES(SELLER_ID_SEQ.NEXTVAL, :name, :building,
                               :road, :area, :city, :email, :password, :website , :location )"""
                    with connections['oracle'].cursor() as cursor:
                        data = {'name' : name, 'building':building ,'road' : road , 'area' :area , 'city':city,
                        'email' :email , 'password':password, 'location' :location , 'website':website}
                        cursor.execute(query, data)
                        cursor.execute("COMMIT")
                    for i in range(len(phno)):
                        query = """INSERT INTO SELLER_PHONE_NUMBER VALUES((SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email),:phno)"""
                        with connections['oracle'].cursor() as cursor:
                            cursor.execute(query, {'email':email, 'phno':phno[i]})
                            cursor.execute("COMMIT")
                return HttpResponseRedirect(reverse('accounts:login'))

    data = {'emailExists': False, 'adminLogin': adminLogin, 'isloggedin': isloggedin,
            'accountType': accountType,'advert1': adverts[0], 'advert2': adverts[1], 'advert3': adverts[2],
            'advert4': adverts[3], 'advert5': adverts[4], 'advert6': adverts[5], 'advert7': adverts[6],
            'advert8': adverts[7]}
    return render(request, 'signup.html', data)

def login_page(request):
    isloggedin = False
    accountType = 'none'
    if request.session.has_key('useremail'):
        return HttpResponseRedirect(reverse('home_page'))

    adverts = getAdverts(request)

    if request.method == 'GET':
        data = {'error': False, 'isloggedin': isloggedin, 'accountType': accountType, 'advert1': adverts[0],
                'advert2': adverts[1], 'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4],
                'advert6': adverts[5], 'advert7': adverts[6], 'advert8': adverts[7]}
        return render(request, 'login.html', data)
    elif request.method == 'POST':
        email = request.POST.get("Email", "empty")
        password = request.POST.get("Password", "empty")

        if email_pass_match(email , password) == True:
            request.session['useremail'] = email
            return HttpResponseRedirect(reverse('home_page'))
        else:
            data = {'error': True, 'isloggedin': isloggedin, 'accountType': accountType, 'advert1': adverts[0],
                    'advert2': adverts[1], 'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4],
                    'advert6': adverts[5], 'advert7': adverts[6], 'advert8': adverts[7]}
            return render(request, 'login.html', data)

def logout_page(request):
    if request.session.has_key('useremail'):
        del request.session['useremail']
        return HttpResponseRedirect(reverse('home_page'))
    else:
        return HttpResponseRedirect(reverse('home_page'))

def accountBalance(email, type):
    with connections['oracle'].cursor() as cursor:
        if type == 'customer':
            cursor.execute("SELECT WALLET_BALANCE(CUSTOMER_ID , 'CUSTOMER') FROM CUSTOMER WHERE EMAIL_ID = :email", {'email':email})
            balance = cursor.fetchall()[0][0]
            if balance == None:
                return 0
            else:
                return float(balance)
        elif type == 'seller':
            cursor.execute("SELECT WALLET_BALANCE(SELLER_ID , 'SELLER') FROM SELLER WHERE EMAIL_ID = :email", {'email': email})
            balance = cursor.fetchall()[0][0]
            if balance == None:
                return 0
            else:
                return float(balance)

def acoountBalance_id(id, type):
    with connections['oracle'].cursor() as cursor:
        if type == 'customer':
            cursor.execute("SELECT WALLET_BALANCE(CUSTOMER_ID , 'CUSTOMER') FROM CUSTOMER WHERE CUSTOMER_ID = :id", {'id':id})
            balance = cursor.fetchall()[0][0]
            if balance == None:
                return 0
            else:
                return float(balance)
        elif type == 'seller':
            cursor.execute("SELECT WALLET_BALANCE(SELLER_ID , 'SELLER') FROM SELLER WHERE SELLER_ID =:id", {'id':id})
            balance = cursor.fetchall()[0][0]
            if balance == None:
                return 0
            else:
                return float(balance)

def myaccount(request, firstPage):
    isloggedin = False
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])

        adverts = getAdverts(request)

        if acType == 'customer':

            with connections['oracle'].cursor() as cursor:
                query = "SELECT EMAIL_ID, FIRST_NAME, LAST_NAME, PHONE_NUMBER, APARTMENT_NUMBER, BUILDING_NUMBER, ROAD, AREA, CITY, DOB, PASSWORD, CUSTOMER_ID  FROM CUSTOMER WHERE EMAIL_ID = :emailID;"
                cursor.execute(query, {'emailID' :request.session['useremail']});
                result = cursor.fetchall()
                emailID = result[0][0]
                firstName = result[0][1]
                lastName = result[0][2]
                phoneNumber = result[0][3]
                apartmentNumber = result[0][4] if result[0][4] else ''
                buildingNumber = result[0][5] if result[0][5] else ''
                road = result[0][6] if result[0][6] else ''
                area = result[0][7] if result[0][7] else ''
                city = result[0][8] if result[0][8] else ''
                dob = str(result[0][9].date())
                current_password = result[0][10]
                customerID = result[0][11]

                basic_info = {'email': emailID, 'firstName': firstName, 'lastName': lastName,
                              'phoneNumber': phoneNumber, 'apartmentNumber': apartmentNumber,
                              'buildingNumber': buildingNumber, 'road': road, 'area': area,
                              'city': city, 'dob': dob}

            if request.is_ajax():
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                orderID = body['orderID']

                with connections['oracle'].cursor() as cursor:
                    query = """SELECT PRODUCT_ID, O.SELLER_ID, P.NAME PRODUCT_NAME, ORDER_TOTAL(ORDER_ID)
                               TOTAL_PRICE, S.NAME SELLER_NAME, COUNT(*) QUANTITY FROM CUSTOMER_ORDER O
                               JOIN SELLER S ON(S.SELLER_ID=O.SELLER_ID) JOIN ORDERED_ITEMS I USING(ORDER_ID)
                               JOIN PRODUCT P USING(PRODUCT_ID) WHERE ORDER_ID = :oid GROUP BY PRODUCT_ID, O.SELLER_ID,
                               P.NAME, ORDER_TOTAL(ORDER_ID), S.NAME;"""
                    cursor.execute(query, {'oid': orderID})
                    orderDetails = cursor.fetchall()[0]

                    productURL = 'http://'+request.META['HTTP_HOST']+'/product/item/{}/{}'.format(orderDetails[0], orderDetails[1])
                    data = {'productName': orderDetails[2], 'totalPrice': orderDetails[3],
                            'sellerName': orderDetails[4], 'quantity': orderDetails[5],
                            'productURL': productURL}

                return JsonResponse(data, status=200)

            elif request.method == 'POST':
                formIdentity = request.POST.get('formIdentity')
                if formIdentity == 'changeBasicInfoForm':
                    newPassword = request.POST.get('customerNewPassword')
                    newFirstName = request.POST.get('customerFirstName')
                    newLastName = request.POST.get('customerLastName')
                    newPhoneNumber = request.POST.get('customerPhNo')
                    newApartmentNumber = request.POST.get('customerApartment')
                    newBuildingNumber = request.POST.get('customerBuilding')
                    newRoad = request.POST.get('customerRoad')
                    newArea = request.POST.get('customerArea')
                    newCity = request.POST.get('customerCity')
                    newdob = request.POST.get('customerDOB')

                    with connections['oracle'].cursor() as cursor:
                        if len(newPassword) > 0:
                            query = """UPDATE CUSTOMER SET
                                       FIRST_NAME = :fn,
                                       LAST_NAME = :ln,
                                       APARTMENT_NUMBER = :an,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       PHONE_NUMBER = :pn,
                                       PASSWORD = :ps,
                                       DOB = :dob
                                       WHERE CUSTOMER_ID = :cid"""
                            data = {'fn': newFirstName, 'ln': newLastName, 'an': newApartmentNumber,
                                    'pn': newPhoneNumber, 'bn': newBuildingNumber, 'ps': newPassword,
                                    'r': newRoad, 'a': newArea, 'c': newCity, 'dob': newdob,
                                    'cid': customerID}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")
                        else:
                            query = """UPDATE CUSTOMER SET
                                       FIRST_NAME = :fn,
                                       LAST_NAME = :ln,
                                       APARTMENT_NUMBER = :an,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       PHONE_NUMBER = :pn,
                                       DOB = :dob
                                       WHERE CUSTOMER_ID = :cid"""
                            data = {'fn': newFirstName, 'ln': newLastName, 'an': newApartmentNumber,
                                    'pn': newPhoneNumber, 'bn': newBuildingNumber, 'r': newRoad,
                                    'a': newArea, 'c': newCity, 'dob': newdob, 'cid': customerID}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")


                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/basic'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'reviewForm':
                    productID = request.POST.get('delRevBtn').split('+')[0]
                    sellerID = request.POST.get('delRevBtn').split('+')[1]

                    with connections['oracle'].cursor() as cursor:
                        query = """DELETE FROM REVIEW WHERE (PRODUCT_ID = :product_id AND SELLER_ID = :seller_id AND CUSTOMER_ID =
                                  (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email) )"""
                        data = {'product_id' :productID,'seller_id':sellerID, 'email':request.session['useremail']}
                        cursor.execute(query, data)
                        cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/reviews'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'cartForm':
                    action = request.POST.get('CartBtn').split('+')[0]
                    productID = request.POST.get('CartBtn').split('+')[1]
                    sellerID = request.POST.get('CartBtn').split('+')[2]
                    if action == 'ORDER':
                        pass
                    elif action == 'DEL':
                        with connections['oracle'].cursor() as cursor:
                            query = """DELETE FROM CART_ITEM WHERE (PRODUCT_ID = :product_id AND SELLER_ID = :seller_id AND CUSTOMER_ID =
                                      (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email) )"""
                            data = {'product_id' :productID,'seller_id':sellerID, 'email':request.session['useremail']}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/cart'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'orderForm':
                    productID = request.POST.get('productID')
                    sellerID = request.POST.get('sellerID')
                    quantity = request.POST.get('quantity')
                    paymentMethod = request.POST.get('paymentMethod')

                    query = """SELECT ITEM_NUMBER FROM PRODUCT_UNIT WHERE PRODUCT_ID = TO_NUMBER(:pid)
                               AND SELLER_ID = TO_NUMBER(:sid) AND LOWER(STATUS) = 'not sold'"""
                    data = {'pid': productID, 'sid': sellerID}

                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query, data)
                        itemNumbers = cursor.fetchall()
                        if( len(itemNumbers) >= int(quantity) ):
                            for i in range( int(quantity) ):
                                inum = itemNumbers[i][0]
                                query = """UPDATE PRODUCT_UNIT SET STATUS = 'Sold' WHERE
                                           PRODUCT_ID = TO_NUMBER(:pid) AND SELLER_ID = TO_NUMBER(:sid)
                                           AND ITEM_NUMBER = TO_NUMBER(:inum)"""
                                data = {'pid': productID, 'sid': sellerID, 'inum': inum}
                                cursor.execute(query, data)

                            query = "SELECT ORDER_ID_SEQ.NEXTVAL FROM DUAL"
                            cursor.execute(query)
                            orderID = cursor.fetchall()[0][0]

                            query = """INSERT INTO CUSTOMER_ORDER VALUES(TO_NUMBER(:oid),
                                       (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email),
                                       SYSDATE, TO_NUMBER(:sid) )"""
                            data = { 'oid': orderID, 'sid': sellerID,
                                     'email': request.session['useremail'] }
                            cursor.execute(query, data)


                            query = """INSERT INTO PURCHASE_ORDER VALUES(TO_NUMBER(:oid),
                                      TO_NUMBER(:empID), NULL, 'Not Delivered', :pm)"""
                            data = { 'oid': orderID, 'empID': deliveryEmployeeSelection(orderID),
                                     'pm': paymentMethod }
                            cursor.execute(query, data)

                            for i in range( int(quantity) ):
                                inum = itemNumbers[i][0]
                                query = """INSERT INTO ORDERED_ITEMS VALUES(TO_NUMBER(:pid),
                                           TO_NUMBER(:sid), TO_NUMBER(:oid), TO_NUMBER(:inum)) """
                                data = {'pid': productID, 'sid': sellerID, 'oid': orderID,
                                        'inum': inum}
                                cursor.execute(query, data)
                            query = """DELETE FROM CART_ITEM WHERE (PRODUCT_ID = :product_id AND
                                       SELLER_ID = :seller_id AND CUSTOMER_ID = (SELECT CUSTOMER_ID
                                       FROM CUSTOMER WHERE EMAIL_ID = :email) )"""
                            data = { 'product_id' :productID, 'seller_id':sellerID,
                                     'email':request.session['useremail'] }
                            cursor.execute(query, data)

                            cursor.execute("commit")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/orders'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'alterPurchaseOrder':
                    orderID = request.POST.get('alterPurchaseOrderButton').split('_')[0]
                    action = request.POST.get('alterPurchaseOrderButton').split('_')[1]

                    if action == 'cancel':
                        with connections['oracle'].cursor() as cursor:
                            try:
                                query = "SELECT PRODUCT_ID, SELLER_ID FROM ORDERED_ITEMS WHERE ORDER_ID = :oid"
                                cursor.execute(query, {'oid': int(orderID)})
                                result = cursor.fetchall()
                                productID, sellerID = int(result[0][0]), int(result[0][1])

                                query = """UPDATE PRODUCT_UNIT
                                           SET STATUS = 'Not Sold'
                                           WHERE PRODUCT_ID = :pid AND SELLER_ID = :sid AND
                                           ITEM_NUMBER IN (SELECT ITEM_NUMBER FROM ORDERED_ITEMS WHERE ORDER_ID = :orderID)"""
                                cursor.execute(query, {'pid': productID, 'sid': sellerID, 'orderID': int(orderID)});

                                query = """UPDATE PURCHASE_ORDER
                                           SET DELIVERY_STATUS = 'Cancelled'
                                           WHERE ORDER_ID = :orderID"""
                                cursor.execute(query, {'orderID': orderID});

                            except Exception as e:
                                print(e)
                                cursor.execute("ROLLBACK")
                            else:
                                cursor.execute("COMMIT")

                    elif action == 'return':
                        complaint = request.POST.get('complaint'+str(orderID))

                        with connections['oracle'].cursor() as cursor:
                            try:
                                query = """SELECT EMPLOYEE_ID, COUNT(ORDER_ID) NO_TASKS FROM CUSTOMER_CARE_EMPLOYEE
                                           LEFT OUTER JOIN RETURN_ORDER ON(CUSTOMER_CARE_EMPLOYEE_ID=EMPLOYEE_ID
                                           AND LOWER(APPROVAL_STATUS)='Not Approved') GROUP BY EMPLOYEE_ID ORDER BY NO_TASKS ASC"""
                                cursor.execute(query);
                                empID = int(cursor.fetchall()[0][0])
                                query = """INSERT INTO RETURN_ORDER VALUES( TO_NUMBER(:orderID), :complaint,
                                           TO_NUMBER(:empID), SYSDATE, 'Not Approved')"""
                                cursor.execute(query, {'orderID': orderID, 'complaint': complaint, 'empID' : empID});
                                query = "UPDATE PURCHASE_ORDER SET DELIVERY_STATUS = 'Returned' WHERE ORDER_ID = :orderID"
                                cursor.execute(query, {'orderID': orderID});
                            except Exception as e:
                                print(e)
                                cursor.execute("ROLLBACK")
                            else:
                                cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/orders'
                    return HttpResponseRedirect(reverseStr)

                reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/basic'
                return HttpResponseRedirect(reverseStr)

            cartTableHTML = generateCartTableHTML(request)
            orderTableHTML = generateOrderTableHTML(request)
            purchaseOrderHTML = orderTableHTML[0]
            returnOrderHTML = orderTableHTML[1]
            walletTableHTML = generateWalletTableHTMLCustomer(request)
            reviewTableHTML = generateReviewTableHTML(request)
            acBal = accountBalance(request.session['useremail'], acType)

            data = {'isloggedin': isloggedin, 'accountType': acType, 'cartTableHTML': cartTableHTML,
                    'purchaseOrderHTML': purchaseOrderHTML, 'returnOrderHTML': returnOrderHTML,
                    'walletTableHTML': walletTableHTML, 'reviewTableHTML': reviewTableHTML,
                    'accountBalance': acBal, 'advert1': adverts[0], 'advert2': adverts[1],
                    'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4],
                    'advert6': adverts[5], 'advert7': adverts[6], 'advert8': adverts[7],
                    'firstPage': firstPage, 'deliveryCharge': info.serviceChargePercentage}
            data = {**data, **basic_info}

            return render(request, 'customerAccount.html', data)

        elif acType == 'seller':
            with connections['oracle'].cursor() as cursor:
                query = "SELECT EMAIL_ID, NAME, BUILDING_NUMBER, ROAD, AREA, CITY, WEBSITE, SELLER_ID FROM SELLER WHERE EMAIL_ID = :emailID"
                cursor.execute(query, {'emailID' :request.session['useremail'] });
                result = cursor.fetchall()
                emailID = result[0][0]
                name = result[0][1]
                buildingNumber = result[0][2]
                road =  result[0][3]
                area =  result[0][4]
                city =  result[0][5]
                website = result[0][6]

                sellerID = int(result[0][7])
                query = "SELECT PHONE_NUMBER FROM SELLER_PHONE_NUMBER WHERE SELLER_ID = :sellerID"
                cursor.execute(query, {'sellerID' : sellerID });
                result = cursor.fetchall()
                phoneNumber = []
                for i in range(len(result)) :
                    phoneNumber.append(result[i][0])

                for i in range(4-len(phoneNumber)):
                    phoneNumber.append('')

                basicInfo = {'emailID': emailID, 'companyName': name, 'buildingNumber': buildingNumber,
                             'road': road, 'area': area, 'city': city, 'website': website,
                             'phoneNumber1': phoneNumber[0], 'phoneNumber2': phoneNumber[1],
                             'phoneNumber3': phoneNumber[2], 'phoneNumber4': phoneNumber[3]}

            if request.method == 'POST':
                formIdentity = request.POST.get('formIdentity')
                if formIdentity == 'changeBasicInfoForm':
                    newPassword = request.POST.get('sellerNewPassword')
                    companyName = request.POST.get('companyName')
                    sellerPhoneNumber1 = request.POST.get('sellerPhoneNumber1')
                    sellerPhoneNumber2 = request.POST.get('sellerPhoneNumber2')
                    sellerPhoneNumber3 = request.POST.get('sellerPhoneNumber3')
                    sellerPhoneNumber4 = request.POST.get('sellerPhoneNumber4')
                    website = request.POST.get('website')
                    sellerBuilding = request.POST.get('sellerBuilding')
                    sellerRoad = request.POST.get('sellerRoad')
                    sellerCity = request.POST.get('sellerCity')
                    sellerArea = request.POST.get('sellerArea')

                    with connections['oracle'].cursor() as cursor:
                        query = "DELETE FROM SELLER_PHONE_NUMBER WHERE SELLER_ID = :sid"
                        cursor.execute(query, {'sid': sellerID})
                        for pn in [sellerPhoneNumber1, sellerPhoneNumber2, sellerPhoneNumber3, sellerPhoneNumber4]:
                            if len(pn) > 0:
                                query = "INSERT INTO SELLER_PHONE_NUMBER VALUES(:sid, :pn)"
                                cursor.execute(query, {'sid': sellerID, 'pn': pn})

                    with connections['oracle'].cursor() as cursor:
                        if len(newPassword) > 0:
                            query = """UPDATE SELLER SET
                                       NAME = :cn,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       PASSWORD = :ps,
                                       WEBSITE = :w
                                       WHERE SELLER_ID = :sid"""
                            data = {'cn': companyName, 'bn': sellerBuilding, 'ps': newPassword,
                                    'r': sellerRoad, 'a': sellerArea, 'c': sellerCity, 'sid': sellerID,
                                    'w': website}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")
                        else:
                            query = """UPDATE SELLER SET
                                       NAME = :cn,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       WEBSITE = :w
                                       WHERE SELLER_ID = :sid"""
                            data = {'cn': companyName, 'bn': sellerBuilding, 'r': sellerRoad, 'a': sellerArea,
                                    'c': sellerCity, 'sid': sellerID, 'w': website}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")

                elif formIdentity == 'addOfferForm':
                    productID = int(request.POST.get('productID'))
                    startDate = request.POST.get('startDate')
                    endDate = request.POST.get('endDate')
                    discount = request.POST.get('discount')
                    minQuan = request.POST.get('minQuan')

                    sellerID = -1
                    with connections['oracle'].cursor() as cursor:
                        query = "SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email"
                        cursor.execute(query , {'email':request.session['useremail']})
                        result = cursor.fetchall()
                        sellerID = result[0][0]

                    if(check_productID(productID, sellerID)):
                        with connections['oracle'].cursor() as cursor:
                            query = "SELECT MAX(OFFER_NUMBER) FROM OFFER WHERE PRODUCT_ID = :productID AND SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email)"
                            cursor.execute(query , {'productID': productID , 'email':request.session['useremail']})
                            result = cursor.fetchall()
                            offer_number = 1

                            if (result[0][0] is not None ) :
                                offer_number = int(result[0][0]) + 1

                            query = """INSERT INTO OFFER VALUES(TO_NUMBER(:productID),  (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email), TO_NUMBER(:offer_number),
                                       TO_DATE(:startDate,'YYYY-MM-DD'),TO_DATE(:endDate,'YYYY-MM-DD'), TO_NUMBER(:discount), TO_NUMBER(:minQuan) )"""
                            data = {'productID' : productID,  'email':request.session['useremail'] , 'offer_number' :offer_number,
                                    'startDate':startDate , 'endDate':endDate ,'minQuan':minQuan,'discount':discount }
                            cursor.execute(query,data)
                            cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/offers'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'addAdvertForm':
                    productID = int(request.POST.get('productID'))

                    blob = io.BytesIO()
                    if 'advertImage' in request.FILES:
                        imgFile = request.FILES['advertImage']
                        img = Image.open(imgFile)
                        img = make_9_2(img)
                        img.save(blob, 'jpeg')
                        blob.seek(0)

                    sellerID = -1
                    with connections['oracle'].cursor() as cursor:
                        query = "SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email"
                        cursor.execute(query , {'email':request.session['useremail']})
                        result = cursor.fetchall()
                        sellerID = result[0][0]

                    if(check_productID(productID, sellerID)):
                        with connections['oracle'].cursor() as cursor:
                            query = "SELECT MAX(ADVERTISEMENT_NUMBER) FROM ADVERTISEMENT WHERE PRODUCT_ID = :productID AND SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email)"
                            cursor.execute(query , {'productID': productID , 'email':request.session['useremail']})
                            result = cursor.fetchall()
                            add_number = 1
                            if result[0][0] is not None :
                                add_number = int(result[0][0]) + 1
                            query = """INSERT INTO ADVERTISEMENT VALUES(TO_NUMBER(:productID),(SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email), TO_NUMBER(:add_number),
                                       SYSDATE ,SYSDATE + 30, TO_NUMBER(:cost), :picture )"""
                            data = {'productID' : productID,'email':request.session['useremail'] , 'add_number' :add_number, 'picture':blob.getvalue(),'cost': info.advertCost}
                            cursor.execute(query,data)
                            cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/advertisements'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'delOfferForm':
                    product_id = request.POST.get('delOfferBtn').split('+')[0]
                    seller_id = request.POST.get('delOfferBtn').split('+')[1]
                    offerNumber = request.POST.get('delOfferBtn').split('+')[2]
                    query = "UPDATE OFFER SET END_DATE = SYSDATE WHERE PRODUCT_ID = :pID AND SELLER_ID = :sID AND OFFER_NUMBER = :offnum "
                    data = {'pID' : product_id , 'sID':seller_id , 'offnum':offerNumber}
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query, data)
                        cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/offers'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'delAdvertForm':
                    product_id = request.POST.get('delAdvertButton').split('+')[0]
                    seller_id = request.POST.get('delAdvertButton').split('+')[1]
                    advertNumber = request.POST.get('delAdvertButton').split('+')[2]
                    query = "UPDATE ADVERTISEMENT SET END_DATE = SYSDATE WHERE PRODUCT_ID = :pID AND SELLER_ID = :sID AND ADVERTISEMENT_NUMBER = :addnum "
                    data = {'pID' : product_id , 'sID':seller_id , 'addnum':advertNumber}
                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query, data)
                        cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/advertisements'
                    return HttpResponseRedirect(reverseStr)

                reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/basic'
                return HttpResponseRedirect(reverseStr)

            productTableHTML = generateProductTableHTML(request)
            offerTableHTML = generateOfferTableHTML(request)
            advertTableHTML = generateAdvertTableHTML(request)
            walletTableHTML = generateWalletTableHTML(request)
            acBal = accountBalance(request.session['useremail'], acType)
            advertCost = info.advertCost

            data = {'isloggedin': isloggedin, 'accountType': acType, 'productTableHTML': productTableHTML,
                    'offerTableHTML': offerTableHTML, 'advertTableHTML': advertTableHTML,
                    'walletTableHTML': walletTableHTML, 'accountBalance': acBal, 'advertCost': advertCost,
                    'buyAdvert': acBal>=advertCost, 'advert1': adverts[0], 'advert2': adverts[1],
                    'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4],
                    'advert6': adverts[5], 'advert7': adverts[6], 'advert8': adverts[7], 'firstPage': firstPage}
            data = {**data, **basicInfo}

            return render(request, 'sellerAccount.html', data)

        elif acType == 'deliveryGuy':
            with connections['oracle'].cursor() as cursor:
                query = """SELECT EMAIL_ID, FIRST_NAME, LAST_NAME, PHONE_NUMBER, APARTMENT_NUMBER,
                           BUILDING_NUMBER, ROAD, AREA, CITY, DOB, EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :emailID;"""
                cursor.execute(query, {'emailID' :request.session['useremail'] });
                result = cursor.fetchall()
                emailID = result[0][0]
                firstName = result[0][1]
                lastName = result[0][2]
                phoneNumber = result[0][3]
                apartment = result[0][4] if result[0][4] else ''
                building = result[0][5] if result[0][5] else ''
                road =  result[0][6] if result[0][6] else ''
                area =  result[0][7] if result[0][7] else ''
                city =  result[0][8] if result[0][8] else ''
                dob = str(result[0][9].date())
                employeeID = result[0][10]

                basicInfo = {'email': emailID, 'firstName': firstName, 'lastName': lastName,
                             'phoneNumber': phoneNumber, 'apartment': apartment,
                             'building': building, 'road': road, 'area': area,
                             'city': city, 'dob': dob}


            if request.method == 'POST':
                formIdentity = request.POST.get('formIdentity')
                if formIdentity == 'changeBasicInfoForm':
                    newPassword = request.POST.get('newPassword')
                    firstName = request.POST.get('firstName')
                    lastName = request.POST.get('lastName')
                    phoneNumber = request.POST.get('phoneNumber')
                    building = request.POST.get('building')
                    road = request.POST.get('road')
                    city = request.POST.get('city')
                    area = request.POST.get('area')
                    apartment = request.POST.get('apartment')
                    dob = request.POST.get('dob')

                    with connections['oracle'].cursor() as cursor:
                        if len(newPassword) > 0:
                            query = """UPDATE EMPLOYEE SET
                                       FIRST_NAME = :fn,
                                       LAST_NAME = :ln,
                                       APARTMENT_NUMBER = :an,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       PHONE_NUMBER = :pn,
                                       PASSWORD = :ps,
                                       DOB = :dob
                                       WHERE EMPLOYEE_ID = :eid"""
                            data = {'fn': firstName, 'ln': lastName, 'an': apartment,
                                    'pn': phoneNumber, 'bn': building, 'ps': newPassword,
                                    'r': road, 'a': area, 'c': city, 'dob': dob,
                                    'eid': employeeID}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")
                        else:
                            query = """UPDATE EMPLOYEE SET
                                       FIRST_NAME = :fn,
                                       LAST_NAME = :ln,
                                       APARTMENT_NUMBER = :an,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       PHONE_NUMBER = :pn,
                                       DOB = :dob
                                       WHERE EMPLOYEE_ID = :eid"""
                            data = {'fn': firstName, 'ln': lastName, 'an': apartment,
                                    'pn': phoneNumber, 'bn': building, 'r': road, 'a': area,
                                    'c': city, 'dob': dob, 'eid': employeeID}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")

                elif formIdentity == 'pendingDeliveriesForm':
                    orderID = request.POST.get('deliveredButton')
                    with connections['oracle'].cursor() as cursor:
                        try:
                            query = """SELECT PAYMENT_METHOD FROM PURCHASE_ORDER WHERE
                                       ORDER_ID = TO_NUMBER(:oid)"""
                            cursor.execute(query, {'oid': orderID})
                            paymentMethod = cursor.fetchall()[0][0]

                            if paymentMethod.lower() == 'cash':
                                query = "SELECT TRANSACTION_ID_SEQ.NEXTVAL FROM DUAL"
                                cursor.execute(query)
                                tranID = cursor.fetchall()[0][0]

                                query = """INSERT INTO TRANSACTIONS VALUES(:tranID, SYSDATE,
                                           ORDER_TOTAL(TO_NUMBER(:oid)), TO_NUMBER(:scp))"""
                                data = { 'tranID': tranID, 'oid': orderID,
                                         'scp': info.serviceChargePercentage*100 }
                                cursor.execute(query, data)

                                query = """INSERT INTO CUSTOMER_CASH_TRANSACTION VALUES(TO_NUMBER(:tranID),
                                           TO_NUMBER(:oid))"""
                                cursor.execute(query, {'tranID': tranID, 'oid': orderID})

                            query = """UPDATE PURCHASE_ORDER SET DELIVERED_DATE = SYSDATE,
                                       DELIVERY_STATUS = 'Delivered' WHERE ORDER_ID = TO_NUMBER(:oid)"""
                            cursor.execute(query, {'oid': orderID})

                        except Exception as e:
                            print(e)
                            cursor.execute("ROLLBACK")
                        else:
                            cursor.execute("COMMIT")

                        reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/pending'
                        return HttpResponseRedirect(reverseStr)

                reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/basic'
                return HttpResponseRedirect(reverseStr)

            deliveredItemHTML = generateDeliveredItemHTML(request)
            pendingDeliveryItemHTML = generatePendingDeliveryHTML(request)

            data = {'isloggedin': isloggedin, 'accountType': acType,
                    'deliveredItemHTML': deliveredItemHTML,
                    'pendingDeliveryItemHTML': pendingDeliveryItemHTML, 'advert1': adverts[0],
                    'advert2': adverts[1], 'advert3': adverts[2], 'advert4': adverts[3],
                    'advert5': adverts[4], 'advert6': adverts[5], 'advert7': adverts[6],
                    'advert8': adverts[7], 'firstPage': firstPage}
            data = {**data, **basicInfo}

            return render(request, 'deliveryGuy.html', data)

        elif acType == 'customerCare':
            with connections['oracle'].cursor() as cursor:
                query = "SELECT EMAIL_ID, FIRST_NAME, LAST_NAME, PHONE_NUMBER, APARTMENT_NUMBER, BUILDING_NUMBER, ROAD, AREA, CITY, DOB, EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :emailID;"
                cursor.execute(query, {'emailID' :request.session['useremail'] });
                result = cursor.fetchall()
                emailID = result[0][0]
                firstName = result[0][1]
                lastName = result[0][2]
                phoneNumber = result[0][3]
                apartment = result[0][4] if result[0][4] else ''
                building = result[0][5] if result[0][5] else ''
                road =  result[0][6] if result[0][6] else ''
                area =  result[0][7] if result[0][7] else ''
                city =  result[0][8]
                dob = str(result[0][9].date())
                employeeID = result[0][10]

                basicInfo = {'firstName': firstName, 'lastName': lastName, 'phoneNumber': phoneNumber,
                             'apartment': apartment, 'building': building, 'road': road,
                             'area': area, 'city': city, 'dob': dob, 'email': emailID}

            managedComplaintsHTML = generateManagedComplaintsHTML(request)
            pendingComplaintsHTML = generatePendingComplaintsHTML(request)

            if request.method == 'POST':
                formIdentity = request.POST.get('formIdentity')
                if formIdentity == 'changeBasicInfoForm':
                    newPassword = request.POST.get('newPassword')
                    firstName = request.POST.get('firstName')
                    lastName = request.POST.get('lastName')
                    phoneNumber = request.POST.get('phoneNumber')
                    building = request.POST.get('building')
                    road = request.POST.get('road')
                    city = request.POST.get('city')
                    area = request.POST.get('area')
                    apartment = request.POST.get('apartment')
                    dob = request.POST.get('dob')

                    with connections['oracle'].cursor() as cursor:
                        if len(newPassword) > 0:
                            query = """UPDATE EMPLOYEE SET
                                       FIRST_NAME = :fn,
                                       LAST_NAME = :ln,
                                       APARTMENT_NUMBER = :an,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       PHONE_NUMBER = :pn,
                                       PASSWORD = :ps,
                                       DOB = :dob
                                       WHERE EMPLOYEE_ID = :eid"""
                            data = {'fn': firstName, 'ln': lastName, 'an': apartment,
                                    'pn': phoneNumber, 'bn': building, 'ps': newPassword,
                                    'r': road, 'a': area, 'c': city, 'dob': dob,
                                    'eid': employeeID}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")
                        else:
                            query = """UPDATE EMPLOYEE SET
                                       FIRST_NAME = :fn,
                                       LAST_NAME = :ln,
                                       APARTMENT_NUMBER = :an,
                                       BUILDING_NUMBER = :bn,
                                       ROAD = :r,
                                       AREA = :a,
                                       CITY = :c,
                                       PHONE_NUMBER = :pn,
                                       DOB = :dob
                                       WHERE EMPLOYEE_ID = :eid"""
                            data = {'fn': firstName, 'ln': lastName, 'an': apartment,
                                    'pn': phoneNumber, 'bn': building, 'r': road, 'a': area,
                                    'c': city, 'dob': dob, 'eid': employeeID}
                            cursor.execute(query, data)
                            cursor.execute("COMMIT")

                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/basic'
                    return HttpResponseRedirect(reverseStr)

                elif formIdentity == 'decisionForm':
                    reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/pending'
                    return HttpResponseRedirect(reverseStr)

            data = {'isloggedin': isloggedin, 'accountType': acType,
                    'managedComplaintsHTML': managedComplaintsHTML,
                    'pendingComplaintsHTML': pendingComplaintsHTML, 'advert1': adverts[0],
                    'advert2': adverts[1], 'advert3': adverts[2], 'advert4': adverts[3],
                    'advert5': adverts[4], 'advert6': adverts[5], 'advert7': adverts[6],
                    'advert8': adverts[7], 'firstPage': firstPage}
            data = {**data, **basicInfo}

            return render(request, 'customerCare.html', data)

        elif acType == 'admin':
            if request.method == 'POST':
                formIdentity = request.POST.get('formIdentity')
                if formIdentity == 'rechargeForm':
                    acType = request.POST.get('acType')
                    accountID = request.POST.get('accountID')
                    rechargeAmount = int(request.POST.get('rechargeAmount'))

                    if acType == 'customer':
                        query = "SELECT CUSTOMER_ID FROM CUSTOMER WHERE CUSTOMER_ID = :ID"
                        with connections['oracle'].cursor() as cursor:
                            cursor.execute(query, {'ID': accountID})
                            result = cursor.fetchall()
                            if( len(result)==1 ):
                                query = "SELECT TRANSACTION_ID_SEQ.NEXTVAL FROM DUAL"
                                cursor.execute(query)
                                tranID = cursor.fetchall()[0][0]

                                query = """INSERT INTO TRANSACTIONS VALUES(TO_NUMBER(:id),SYSDATE,:amount , :charge )"""
                                data = {'id':tranID, 'amount': rechargeAmount - rechargeAmount * info.serviceChargePercentage , 'charge': 100 * info.serviceChargePercentage}
                                cursor.execute(query, data)

                                query = """INSERT INTO CUSTOMER_WALLET_RECHARGE VALUES(TO_NUMBER(:ID), TO_NUMBER(:ID2))"""
                                data = {'ID':tranID, 'ID2':accountID}
                                cursor.execute(query, data)
                                cursor.execute("COMMIT")

                    elif acType == 'seller':
                        query = "SELECT SELLER_ID FROM SELLER WHERE SELLER_ID = :ID"
                        with connections['oracle'].cursor() as cursor:
                            cursor.execute(query, {'ID': accountID})
                            result = cursor.fetchall()
                            if( len(result)==1 ):
                                query = "SELECT TRANSACTION_ID_SEQ.NEXTVAL FROM DUAL"
                                cursor.execute(query)
                                tranID = cursor.fetchall()[0][0]

                                query = """INSERT INTO TRANSACTIONS VALUES(TO_NUMBER(:id),SYSDATE,:amount , :charge )"""
                                data = {'id':tranID, 'amount': rechargeAmount - rechargeAmount * info.serviceChargePercentage , 'charge': 100 * info.serviceChargePercentage}
                                cursor.execute(query, data)

                                query = """INSERT INTO SELLER_TRANSACTION VALUES(TO_NUMBER(:ID), TO_NUMBER(:ID2))"""
                                data = {'ID':tranID, 'ID2':accountID}
                                cursor.execute(query, data)
                                cursor.execute("COMMIT")

                elif formIdentity == 'withdrawForm':
                    accountID = request.POST.get('accountID')
                    withdrawAmount = int(request.POST.get('withdrawAmount'))

                    query = "SELECT SELLER_ID FROM SELLER WHERE SELLER_ID = :accountID"

                    with connections['oracle'].cursor() as cursor:
                        cursor.execute(query, {'accountID': int(accountID)})
                        result = cursor.fetchall()

                        if( len(result)==1 ):
                            acBal = acoountBalance_id(accountID, 'seller')
                            if float(acBal >= withdrawAmount):
                                query = "SELECT TRANSACTION_ID_SEQ.NEXTVAL FROM DUAL"
                                cursor.execute(query)
                                tranID = cursor.fetchall()[0][0]

                                query = """INSERT INTO TRANSACTIONS VALUES(TO_NUMBER(:id),SYSDATE,:amount , :charge )"""
                                data = {'id':tranID, 'amount':(-1)* withdrawAmount  , 'charge': 100 * info.serviceChargePercentage}
                                cursor.execute(query, data)

                                query = """INSERT INTO SELLER_TRANSACTION VALUES(TO_NUMBER(:ID), TO_NUMBER(:ID2))"""
                                data = {'ID':tranID, 'ID2':accountID}
                                cursor.execute(query, data)
                                cursor.execute("COMMIT")

                reverseStr = 'http://'+request.META['HTTP_HOST']+'/accounts/myaccount/basic'
                return HttpResponseRedirect(reverseStr)

            data = {'isloggedin': isloggedin, 'accountType': acType, 'advert1': adverts[0],
                    'advert2': adverts[1], 'advert3': adverts[2], 'advert4': adverts[3],
                    'advert5': adverts[4], 'advert6': adverts[5], 'advert7': adverts[6],
                    'advert8': adverts[7]}

            return render(request, 'adminAccount.html', data)
    else:
        return HttpResponseRedirect(reverse('home_page'))

def generateProductTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        query = """SELECT PRODUCT_ID, NAME, CATEGORY_NAME,IN_STOCK,SOLD_AMOUNT FROM
                    (SELECT Q.PRODUCT_ID, Q.NAME, CATEGORY_NAME ,COUNT(T.PRODUCT_ID)IN_STOCK
                    FROM (SELECT PRODUCT_ID, NAME, CATEGORY_ID FROM PRODUCT
                    WHERE SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email))Q
                    JOIN CATEGORY USING(CATEGORY_ID)
                    LEFT OUTER JOIN
                    (SELECT PRODUCT_ID, STATUS FROM PRODUCT_UNIT)T
                    ON(T.PRODUCT_ID = Q.PRODUCT_ID AND T.STATUS ='Not Sold' )
                    GROUP BY  Q.PRODUCT_ID, Q.NAME, CATEGORY_NAME ) JOIN
                    (SELECT P.PRODUCT_ID ,COUNT(S.PRODUCT_ID)SOLD_AMOUNT
                    FROM (SELECT PRODUCT_ID FROM PRODUCT WHERE SELLER_ID = (SELECT SELLER_ID FROM SELLER
                    WHERE EMAIL_ID = :email))P
                    LEFT OUTER JOIN (SELECT PRODUCT_ID, STATUS FROM PRODUCT_UNIT)S
                    ON(P.PRODUCT_ID = S.PRODUCT_ID AND LOWER(S.STATUS) = 'sold')
                    GROUP BY P.PRODUCT_ID)
                    USING(PRODUCT_ID);"""

        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()

        products = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            products.append(temp)

        cursor.execute("SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email", {'email':request.session['useremail']})
        sellerID = cursor.fetchall()[0][0]

        result = ""
        if( len(products)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                        </tr>
                     """
        else:
            for i in range( len(products) ):
                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], products[i][0], sellerID)
                editURL = "http://{}/product/editproduct/{}/{}/".format(request.META['HTTP_HOST'], products[i][0], sellerID)
                editButton = """<a href={}>
                                    <button type="button" class="btn btn-link">Edit</button>
                                </a>
                             """.format(editURL)
                result += """<tr>
                                <th style="background-color: #f2f8f8" scope="row"><a href={}>{}</a></th>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="text-align: center; background-color: #f2f8f8">{}</td>
                            </tr>
                         """.format( productURL, products[i][0], products[i][1], products[i][2], products[i][3], products[i][4], editButton)
        return result

def generateOfferTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        query = """SELECT PRODUCT_ID, START_DATE, END_DATE, PERCENTAGE_DISCOUNT DISCOUNT,
                   MINIMUM_QUANTITY_PURCHASED MINIMUM_QUANTITY, OFFER_NUMBER FROM OFFER
                   WHERE SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email) """
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        offers = []
        for i in range(len(table)):
            temp = []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            offers.append(temp)

        cursor.execute("SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email", {'email':request.session['useremail']})
        sellerID = cursor.fetchall()[0][0]

        result = ""
        if( len(offers)==0 ):
            result = """<tr>
                            <th style="background-color: #f2f8f8" scope="row"></th>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                            <td style="background-color: #f2f8f8"></td>
                        </tr>
                     """
        else:
            for i in range( len(offers) ):
                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], offers[i][0], sellerID)
                if offers[i][2] > datetime.datetime.now():
                    endOfferButton = """<button name="delOfferBtn" type="submit" value="{}" class="btn customDanger" style="margin: 5px">
                                        Delete
                                        </button>""".format(str(offers[i][0])+"+"+str(sellerID)+"+"+str(offers[i][5]))
                else:
                    endOfferButton = ''
                result += """<tr>
                                <th style="background-color: #f2f8f8" scope="row"><a href={}>{}</a></th>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="text-align: center; background-color: #f2f8f8">{}</td>
                            </tr>
                         """.format( productURL, offers[i][0], offers[i][1], offers[i][2], offers[i][3], offers[i][4], endOfferButton)
        return result

def generateAdvertTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        query = """SELECT PRODUCT_ID, START_DATE, END_DATE, COST_FOR_SELLER COST, PICTURE, SELLER_ID, ADVERTISEMENT_NUMBER FROM ADVERTISEMENT
                   WHERE SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        adverts = []
        for i in range(len(table)):
            temp = []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            adverts.append(temp)

        cursor.execute('SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email', {'email':request.session['useremail']})
        sellerID = cursor.fetchall()[0][0]

        result = ""
        if( len(adverts)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(adverts) ):
                imagePath = "http://{}/static/images/productImages/advert{}_{}_{}.jpg".format(request.META['HTTP_HOST'], adverts[i][0], adverts[i][5], adverts[i][6])
                imageFile = open(settings.BASE_DIR+"\\static\\images\\productImages\\advert{}_{}_{}.jpg".format(adverts[i][0], adverts[i][5], adverts[i][6]),'wb')
                imageFile.write( adverts[i][4].read() )
                imageFile.close()

                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], adverts[i][0], sellerID)
                if adverts[i][2] > datetime.datetime.now():
                    endAdvertButton = """<button name="delAdvertButton" type="submit" value="{}" class="btn customDanger" style="margin: 5px">
                                        Delete
                                        </button>""".format(str(adverts[i][0])+"+"+str(adverts[i][5])+"+"+str(adverts[i][6]))
                else:
                    endAdvertButton = ''
                result += """<tr>
                                <th style="background-color: #f2f8f8" scope="row"><a href={}>{}</a></th>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8">{}</td>
                                <td style="background-color: #f2f8f8"><img src="{}" alt="Advertisement Picture" style="width:100%; height:auto"></td>
                                <td style="text-align: center; vertical-align: middle; background-color: #f2f8f8">{}</td>
                            </tr>
                         """.format( productURL, adverts[i][0], adverts[i][1], adverts[i][2], adverts[i][3], imagePath, endAdvertButton)
        return result

def generateWalletTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        transactions = []
        query = """SELECT TRANSACTIONS_DATE, AMOUNT, AMOUNT / ( 1 -SERVICE_CHARGE_PERCENTAGE *1/100 ) - AMOUNT,
                    AMOUNT / ( 1 -SERVICE_CHARGE_PERCENTAGE *1/100 ) TOTAL FROM TRANSACTIONS
                   JOIN SELLER_TRANSACTION USING (TRANSACTION_ID) WHERE
                   SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email) AND
                   AMOUNT >= 0"""

        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Wallet Recharge']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            transactions.append(temp)

        query = """SELECT TRANSACTIONS_DATE, -AMOUNT, (-AMOUNT) * SERVICE_CHARGE_PERCENTAGE *1/100,
                   (-AMOUNT -(-AMOUNT)* SERVICE_CHARGE_PERCENTAGE*1/100) TOTAL FROM TRANSACTIONS
                   JOIN SELLER_TRANSACTION USING(TRANSACTION_ID) WHERE
                   SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email)
                   AND AMOUNT < 0"""
        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Withdraw From Wallet']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            transactions.append(temp)

        query = """SELECT ORDER_DATE, ORDER_TOTAL(ORDER_ID) TOTAL FROM CUSTOMER_ORDER A JOIN
                   PURCHASE_ORDER B USING(ORDER_ID) WHERE LOWER(PAYMENT_METHOD) = 'wallet'
                   AND SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email);"""
        cursor.execute(query, {'email':request.session['useremail']})
        result = cursor.fetchall()
        for i in range(len(result)):
            temp = ['Revenue From Sales']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            temp = temp + [0, temp[2]]
            transactions.append(temp)

        query = """SELECT DELIVERED_DATE, ORDER_TOTAL(ORDER_ID) TOTAL FROM CUSTOMER_ORDER A JOIN
                   PURCHASE_ORDER B USING(ORDER_ID) WHERE LOWER(PAYMENT_METHOD) = 'cash'
                   AND LOWER(DELIVERY_STATUS) = 'delivered' AND
                   SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email);"""
        cursor.execute(query, {'email':request.session['useremail']})
        result = cursor.fetchall()
        for i in range(len(result)):
            temp = ['Revenue From Sales']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            temp = temp + [0, temp[2]]
            transactions.append(temp)

        query = """SELECT RETURN_DATE, ORDER_TOTAL(ORDER_ID) FROM RETURN_ORDER A JOIN
                   CUSTOMER_ORDER B USING(ORDER_ID)  WHERE LOWER(APPROVAL_STATUS) =  'approved'
                   AND SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email);"""
        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Loss From Returned Items']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            temp = temp + [0, temp[2]]
            transactions.append(temp)

        query = """SELECT START_DATE, COST_FOR_SELLER FROM ADVERTISEMENT WHERE
                   SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Payment For Advertisement']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            temp = temp + [0, temp[2]]
            transactions.append(temp)

        query = "SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email"
        cursor.execute(query, {'email':request.session['useremail']})
        sellerID = cursor.fetchall()[0][0]

        result = ""
        if( len(transactions)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(transactions) ):
                result += """<tr>
                                <th scope="row">{}</th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                         """.format( transactions[i][0], transactions[i][1], transactions[i][2], transactions[i][3], transactions[i][4])
        return result

def generateCartTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT Q.PRODUCT_ID, Q.SELLER_ID, P.NAME P_NAME, S.NAME S_NAME, QUANTITY, P.PRICE, DISCOUNT  FROM
                    ( SELECT X.PRODUCT_ID, X.SELLER_ID, QUANTITY, MAX(PERCENTAGE_DISCOUNT) DISCOUNT FROM
                    ( SELECT PRODUCT_ID, SELLER_ID, QUANTITY FROM CART_ITEM
                    WHERE CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email) ) X
                    LEFT OUTER JOIN
                    (SELECT PRODUCT_ID, SELLER_ID, PERCENTAGE_DISCOUNT, MINIMUM_QUANTITY_PURCHASED,
                    END_DATE FROM OFFER) Y
                    ON (X.PRODUCT_ID=Y.PRODUCT_ID AND X.SELLER_ID=Y.SELLER_ID)
                    WHERE ( QUANTITY>=MINIMUM_QUANTITY_PURCHASED AND END_DATE>SYSDATE ) OR
                    ( MINIMUM_QUANTITY_PURCHASED IS NULL AND END_DATE IS NULL )
                    GROUP BY X.PRODUCT_ID, X.SELLER_ID, QUANTITY ) Q
                    JOIN PRODUCT P ON ( P.PRODUCT_ID=Q.PRODUCT_ID AND P.SELLER_ID=Q.SELLER_ID )
                    JOIN SELLER S ON ( S.SELLER_ID=Q.SELLER_ID );"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        cartItems = []
        for i in range(len(table)):
            temp = []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            if temp[6] is None:
                temp[6] = 0
            cartItems.append(temp)

        result = ""
        if( len(cartItems)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(cartItems) ):
                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], cartItems[i][0], cartItems[i][1])
                totalPrice = int(float(cartItems[i][5])*float(cartItems[i][4]) * (1-float(cartItems[i][6])/100))
                orderButton = """<button value="{}" onClick="displayOrder(event);" name="CartBtn" type="button" data-toggle="modal" data-target="#orderModal" class="btn customSuccess" style="margin: 5px;">
                                    Order
                                  </button>""".format("ORDER+"+str(cartItems[i][0])+"+"+str(cartItems[i][1]))
                deleteButton = """<button name="CartBtn" type="submit" value="{}" class="btn customDanger" style="margin: 5px">
                                    Delete
                                  </button>""".format("DEL+"+str(cartItems[i][0])+"+"+str(cartItems[i][1]))
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td style="vertical-align: middle; text-align: center">{} {}</td>
                            </tr>
                         """.format( productURL, cartItems[i][2], cartItems[i][3], cartItems[i][5], cartItems[i][4], cartItems[i][6], totalPrice, orderButton, deleteButton)
        return result

def generateOrderTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, ORDER_DATE, PAYMENT_METHOD, DELIVERY_STATUS, TO_CHAR(MAX(ORDER_DATE+EXPECTED_TIME_TO_DELIVER), 'MONTH DD, YYYY')
                    EXPECTED_DELIVERY_DATE, DELIVERED_DATE, PHONE_NUMBER DELIVERY_GUY_NUMBER FROM CUSTOMER_ORDER C JOIN
                    PURCHASE_ORDER P USING(ORDER_ID) JOIN EMPLOYEE E ON ( E.EMPLOYEE_ID = P.DELIVERY_EMPLOYEE_ID )
                    JOIN ORDERED_ITEMS OI USING(ORDER_ID) JOIN PRODUCT PR ON ( PR.PRODUCT_ID = OI.PRODUCT_ID AND
                    PR.SELLER_ID = OI.SELLER_ID ) WHERE CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email) AND
                    (LOWER(P.DELIVERY_STATUS) != 'cancelled' OR LOWER(P.DELIVERY_STATUS) != 'returned' )GROUP BY ORDER_ID, ORDER_DATE, PAYMENT_METHOD, DELIVERY_STATUS,
                    DELIVERED_DATE, PHONE_NUMBER"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        purchaseOrder = []
        for i in range(len(table)):
            temp = []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            if temp[5] == None:
                temp[5] = ''
            purchaseOrder.append(temp)
        pHTML = rHTML = ""

        if( len(purchaseOrder)==0 ):
            pHTML = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(purchaseOrder) ):

                orderURL = "http://{}".format(request.META['HTTP_HOST'])

                orderAlterButton = '<button type="submit" name="alterPurchaseOrderButton" class="btn customDanger" value="{}">{}</button>'
                orderDetailsButtonStyle = "background: none!important; border: none; padding: 0!important; font-family: arial, sans-serif; color: #007BFF; text-decoration: underline; font-weight: bold; cursor: pointer;"
                if( purchaseOrder[i][3].lower() == 'delivered' ):
                    orderAlterButton = orderAlterButton.format(str(purchaseOrder[i][0])+'_return', "Return")
                    displayType = 'block'
                elif( purchaseOrder[i][3].lower() == 'not delivered' ):
                    orderAlterButton = orderAlterButton.format(str(purchaseOrder[i][0])+'_cancel', "Cancel")
                    displayType = 'none'
                elif( purchaseOrder[i][3].lower() == 'returned' or purchaseOrder[i][3].lower() == 'cancelled' ):
                    orderAlterButton = ''
                    displayType = 'none'

                pHTML += """<tr>
                                <th scope="row"><button value='{}' onclick="fetchProductDetails(this)" type='button' style='{}' data-toggle="modal" data-target="#orderDetailsModal">{}</button></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td style="text-align: center; vertical-align: middle">
                                    {}
                                    <input type="text" name="complaint{}" placeholder="Complaint" class="form-control" style="margin-top: 5px; display: {}" onfocus="this.placeholder = '';" onfocusout="this.placeholder='Complaint'" >
                                </td>
                            </tr>
                         """.format(str(purchaseOrder[i][0]), orderDetailsButtonStyle, purchaseOrder[i][0], purchaseOrder[i][1], purchaseOrder[i][2], purchaseOrder[i][3], purchaseOrder[i][4], purchaseOrder[i][5], purchaseOrder[i][6], orderAlterButton, purchaseOrder[i][0], displayType)

        query =  """SELECT ORDER_ID, ORDER_DATE, COMPLAINT_DES, APPROVAL_STATUS, RETURN_DATE,
                    PHONE_NUMBER CUSTOMER_CARE_NUMBER FROM CUSTOMER_ORDER JOIN RETURN_ORDER P
                    USING(ORDER_ID) JOIN (SELECT PHONE_NUMBER, EMPLOYEE_ID FROM EMPLOYEE ) PH ON
                    (PH.EMPLOYEE_ID = P.CUSTOMER_CARE_EMPLOYEE_ID) WHERE
                    CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        returnOrder = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            if table[i][4] == None:
                table[i][4] = ''
            returnOrder.append(temp)

        if( len(returnOrder)==0 ):
            rHTML = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(returnOrder) ):
                orderURL = "http://{}".format(request.META['HTTP_HOST'])
                orderAlterButton = '<button type="button" class="btn customDanger" style="display: {}">Cancel</button>'
                orderDetailsButtonStyle = "background: none!important; border: none; padding: 0!important; font-family: arial, sans-serif; color: #007BFF; text-decoration: underline; font-weight: bold; cursor: pointer;"
                if( returnOrder[i][4] == 'Approved' ):
                    orderAlterButton = orderAlterButton.format('none')
                else:
                    orderAlterButton = orderAlterButton.format('block')
                rHTML += """<tr>
                                <th scope="row"><button type='button' style='{}' data-toggle="modal" data-target="#orderDetailsModal">{}</button></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                         """.format( orderDetailsButtonStyle, returnOrder[i][0], returnOrder[i][1], returnOrder[i][2], 'Wallet', returnOrder[i][3], returnOrder[i][4], returnOrder[i][5], orderAlterButton)


        return [pHTML, rHTML]

def generateWalletTableHTMLCustomer(request):
    with connections['oracle'].cursor() as cursor:
        transactions = []
        query = """SELECT TRANSACTIONS_DATE, AMOUNT, AMOUNT / ( 1 -SERVICE_CHARGE_PERCENTAGE *1/100 ) - AMOUNT,
                   AMOUNT / ( 1 -SERVICE_CHARGE_PERCENTAGE *1/100 ) TOTAL FROM TRANSACTIONS
                   JOIN CUSTOMER_WALLET_RECHARGE USING(TRANSACTION_ID) WHERE
                   CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Wallet Recharge']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            transactions.append(temp)

        query = """SELECT ORDER_DATE, ORDER_TOTAL(ORDER_ID) AMOUNT FROM CUSTOMER_ORDER JOIN
                   PURCHASE_ORDER USING(ORDER_ID) WHERE LOWER(PAYMENT_METHOD) = 'wallet' AND
                   CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID =:email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Purchase Order using Wallet']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            temp = temp + [0, temp[2]]
            transactions.append(temp)

        query = """SELECT DELIVERED_DATE, ORDER_TOTAL(ORDER_ID) AMOUNT FROM
                   CUSTOMER_ORDER JOIN PURCHASE_ORDER USING(ORDER_ID) WHERE
                   LOWER(PAYMENT_METHOD) = 'cash' AND LOWER(DELIVERY_STATUS) = 'delivered' AND
                   CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID =:email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Purchase Order using Cash']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            temp = temp + [0, temp[2]]
            transactions.append(temp)

        query = """SELECT RETURN_DATE,ORDER_TOTAL(ORDER_ID) AMOUNT FROM CUSTOMER_ORDER JOIN
                   RETURN_ORDER USING (ORDER_ID) WHERE LOWER(APPROVAL_STATUS) = 'approved' AND
                   CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        result =  cursor.fetchall()
        for i in range(len(result)):
            temp = ['Return Order using Wallet']
            for j in range(len(result[i])):
                temp.append(result[i][j])
            temp = temp + [0, temp[2]]
            transactions.append(temp)

    result = ""
    if( len(transactions)==0 ):
        result = """<tr>
                        <th scope="row"></th>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                 """
    else:
        for i in range( len(transactions) ):
            result += """<tr>
                            <th scope="row">{}</th>
                            <td >{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>
                     """.format( transactions[i][0], transactions[i][1], transactions[i][2], transactions[i][3], transactions[i][4])
    return result

def generateReviewTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT PRODUCT_ID, SELLER_ID, P.NAME PRODUCT_NAME, S.NAME SELLER_NAME, REVIEW_DATE, RATING,
                    DESCRIPTION FROM REVIEW JOIN (SELECT PRODUCT_ID, SELLER_ID, NAME FROM PRODUCT) P
                    USING (PRODUCT_ID, SELLER_ID) JOIN (SELECT SELLER_ID, NAME FROM SELLER) S USING (SELLER_ID)
                    WHERE CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        reviews = []
        for i in range(len(table)):
            temp = []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            if temp[6] == None:
                temp[6] = ''
            reviews.append(temp)

        result = ""
        if( len(reviews)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(reviews) ):
                deleteReview = """<button name="delRevBtn" value="{}" type="submit" class="btn customDanger">
                                    Delete
                                  </button>""".format( str(reviews[i][0])+"+"+str(reviews[i][1]) )
                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], reviews[i][0], reviews[i][1])
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td style="vertical-align: middle; text-align: center">{}</td>
                            </tr>
                         """.format( productURL, reviews[i][2], reviews[i][3], reviews[i][4], reviews[i][5], reviews[i][6], deleteReview)
        return result

def generateDeliveredItemHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, CUSTOMER_NAME, "CUSTOMER PHONE", "CUSTOMER ADDRESS",
                    TO_CHAR(MAX(ORDER_DATE+EXPECTED_TIME_TO_DELIVER), 'MONTH DD, YYYY') EXPECTED_DELIVERY_DATE , DELIVERED_DATE, PAYMENT_METHOD,
                    ORDER_TOTAL(ORDER_ID) TOTAL_PAYMENT FROM (SELECT * FROM PURCHASE_ORDER JOIN CUSTOMER_ORDER USING(ORDER_ID)
                    WHERE DELIVERY_EMPLOYEE_ID = (SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :email)
                    AND LOWER(DELIVERY_STATUS) = 'delivered' ) JOIN (SELECT (FIRST_NAME||' '||LAST_NAME)
                    CUSTOMER_NAME, PHONE_NUMBER "CUSTOMER PHONE",('Apartment : '|| APARTMENT_NUMBER||', Building : '
                    ||BUILDING_NUMBER||', Road : '||ROAD||', '||AREA||', '||CITY) "CUSTOMER ADDRESS",
                    CUSTOMER_ID FROM CUSTOMER) USING (CUSTOMER_ID) JOIN (SELECT ORDER_ID, PRODUCT_ID FROM ORDERED_ITEMS)
                    USING(ORDER_ID) JOIN (SELECT PRODUCT_ID, EXPECTED_TIME_TO_DELIVER FROM PRODUCT) USING(PRODUCT_ID)
                    GROUP BY ORDER_ID, CUSTOMER_NAME, "CUSTOMER PHONE", "CUSTOMER ADDRESS", DELIVERED_DATE, PAYMENT_METHOD"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        orderedItems = []
        for i in range(len(table)):
            temp = []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            orderedItems.append(temp)
        result = ""
        if( len(orderedItems)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(orderedItems) ):
                query = """SELECT PRODUCT_ID, SELLER_ID, NAME, ITEM_NUMBER FROM ORDERED_ITEMS JOIN
                           PRODUCT USING(PRODUCT_ID, SELLER_ID) WHERE ORDER_ID = TO_NUMBER(:order_id)"""
                cursor.execute(query, {'order_id':orderedItems[i][0]})
                orderDetails = cursor.fetchall()
                productID = orderDetails[0][0]
                sellerID = orderDetails[0][1]
                name = orderDetails[0][2]
                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], productID, sellerID)
                numbers = ''
                for j in range( len(orderDetails) ):
                    numbers += str(orderDetails[j][3]) + '+'
                numbers = numbers[:-1]

                totalPrice = orderedItems[i][7]
                deliveryCharge = 0
                if orderedItems[i][6].lower() == 'cash':
                    orderedItems[i][7] = int(float(orderedItems[i][7]) * (1+info.serviceChargePercentage))
                    deliveryCharge = float(totalPrice)*info.serviceChargePercentage

                result += """<tr>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <th scope="row">
                                    <a href="#" data-toggle="modal" data-target="#orderedItemsModal" onclick="return fetchData(event)">
                                        {}
                                    </a>
                                </th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                         """.format(totalPrice, deliveryCharge, orderedItems[i][0], productURL, productID, sellerID, name, numbers, orderedItems[i][0], orderedItems[i][1], orderedItems[i][2], orderedItems[i][3], orderedItems[i][4], orderedItems[i][5], orderedItems[i][6], orderedItems[i][7])
        return result

def generatePendingDeliveryHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, CUSTOMER_NAME, "CUSTOMER PHONE", "CUSTOMER ADDRESS",
                    TO_CHAR(MAX(ORDER_DATE+EXPECTED_TIME_TO_DELIVER), 'MONTH DD, YYYY') EXPECTED_DELIVERY_DATE, PAYMENT_METHOD,
                    ORDER_TOTAL(ORDER_ID) TOTAL_PAYMENT FROM (SELECT * FROM PURCHASE_ORDER JOIN CUSTOMER_ORDER USING(ORDER_ID)
                    WHERE DELIVERY_EMPLOYEE_ID = (SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :email)
                    AND LOWER(DELIVERY_STATUS) = 'not delivered' ) JOIN (SELECT (FIRST_NAME||' '||LAST_NAME)
                    CUSTOMER_NAME, PHONE_NUMBER "CUSTOMER PHONE",('Apartment : '|| APARTMENT_NUMBER||', Building : '
                    ||BUILDING_NUMBER||', Road : '||ROAD||', '||AREA||', '||CITY) "CUSTOMER ADDRESS",
                    CUSTOMER_ID FROM CUSTOMER) USING (CUSTOMER_ID) JOIN (SELECT ORDER_ID, PRODUCT_ID FROM ORDERED_ITEMS)
                    USING(ORDER_ID) JOIN (SELECT PRODUCT_ID, EXPECTED_TIME_TO_DELIVER FROM PRODUCT) USING(PRODUCT_ID)
                    GROUP BY ORDER_ID, CUSTOMER_NAME, "CUSTOMER PHONE", "CUSTOMER ADDRESS", DELIVERED_DATE, PAYMENT_METHOD"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        orderedItems = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            orderedItems.append(temp)

        result = ""
        if( len(orderedItems)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(orderedItems) ):
                query = """SELECT PRODUCT_ID, SELLER_ID, NAME, ITEM_NUMBER FROM ORDERED_ITEMS JOIN
                           PRODUCT USING(PRODUCT_ID, SELLER_ID) WHERE ORDER_ID = TO_NUMBER(:order_id)"""
                cursor.execute(query, {'order_id':orderedItems[i][0]})
                orderDetails = cursor.fetchall()
                productID = orderDetails[0][0]
                sellerID = orderDetails[0][1]
                name = orderDetails[0][2]
                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], productID, sellerID)
                numbers = ''
                for j in range( len(orderDetails) ):
                    numbers += str(orderDetails[j][3]) + '+'
                numbers = numbers[:-1]

                totalPrice = orderedItems[i][6]
                deliveryCharge = 0
                if orderedItems[i][5].lower() == 'cash':
                    orderedItems[i][6] = int(float(orderedItems[i][6]) * (1+info.serviceChargePercentage))
                    deliveryCharge = float(totalPrice)*info.serviceChargePercentage

                markDelivered = """<button value="{}" name="deliveredButton" type="submit" class="btn customSuccess">
                                      Delivered
                                   </button>""".format(orderedItems[i][0])
                result += """<tr>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <td style="display:none">{}</td>
                                <th scope="row">
                                    <a href="#" data-toggle="modal" data-target="#orderedItemsModal" onclick="return fetchData(event)">
                                        {}
                                    </a>
                                </th>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td style="text-align: center; vertical-align: middle">{}</td>
                            </tr>
                         """.format(totalPrice, deliveryCharge, orderedItems[i][0], productURL, productID, sellerID, name, numbers, orderedItems[i][0], orderedItems[i][1], orderedItems[i][2], orderedItems[i][3], orderedItems[i][4], orderedItems[i][5], orderedItems[i][6], markDelivered)
        return result

def generateManagedComplaintsHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, ORDER_DATE, "CUSTOMER NAME","CUSTOMER PHONE",COMPLAINT_DES "COMPLAINT",
                    "TOTAL AMOUNT", STATUS, "MANAGED DATE" FROM
                    (SELECT ORDER_ID, COMPLAINT_DES, ORDER_TOTAL(ORDER_ID) "TOTAL AMOUNT", APPROVAL_STATUS STATUS,
                    RETURN_DATE "MANAGED DATE" FROM RETURN_ORDER WHERE CUSTOMER_CARE_EMPLOYEE_ID = (SELECT EMPLOYEE_ID
                    FROM EMPLOYEE WHERE EMAIL_ID = :email)) JOIN CUSTOMER_ORDER
                    USING(ORDER_ID) JOIN (SELECT (FIRST_NAME||' '||LAST_NAME)"CUSTOMER NAME",PHONE_NUMBER
                    "CUSTOMER PHONE",CUSTOMER_ID FROM CUSTOMER ) USING (CUSTOMER_ID)"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        complaints = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            complaints.append(temp)

        result = ""
        if( len(complaints)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(complaints) ):
                orderURL = "http://{}".format(request.META['HTTP_HOST'])
                color = ""
                if( complaints[i][6].lower() == 'approved' ):
                    color = '#21c2ae'
                elif( complaints[i][6].lower() == 'rejected' ):
                    color = "#ff5f40"
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td style="font-weight: bold; color: {}">{}</td>
                                <td>{}</td>
                            </tr>
                         """.format( orderURL, complaints[i][0], complaints[i][1], complaints[i][2], complaints[i][3], complaints[i][4], complaints[i][5], color, complaints[i][6], complaints[i][7])
        return result

def generatePendingComplaintsHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, ORDER_DATE, "CUSTOMER NAME","CUSTOMER PHONE",COMPLAINT_DES "COMPLAINT",
                    "TOTAL AMOUNT", STATUS,"MANAGED DATE" FROM
                    (SELECT ORDER_ID, COMPLAINT_DES,ORDER_TOTAL(ORDER_ID)"TOTAL AMOUNT",APPROVAL_STATUS STATUS,
                    RETURN_DATE "MANAGED DATE" FROM RETURN_ORDER WHERE CUSTOMER_CARE_EMPLOYEE_ID = (SELECT EMPLOYEE_ID
                    FROM EMPLOYEE WHERE EMAIL_ID = :email) AND LOWER(APPROVAL_STATUS) = 'not approved') JOIN CUSTOMER_ORDER USING(ORDER_ID) JOIN
                    (SELECT (FIRST_NAME||' '||LAST_NAME)"CUSTOMER NAME",PHONE_NUMBER "CUSTOMER PHONE",
                    CUSTOMER_ID FROM CUSTOMER ) USING (CUSTOMER_ID);"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        complaints = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            complaints.append(temp)

        result = ""
        if( len(complaints)==0 ):
            result = """<tr>
                            <th scope="row"></th>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(complaints) ):
                orderURL = "http://{}".format(request.META['HTTP_HOST'])
                approve = """<a href={}>
                                <i style="color: #21c2ae; margin-right: 10px; margin-left: 5px" class="fa fa-check-square fa-2x" aria-hidden="true"></i>
                             </a>""".format(orderURL)
                reject = """<a href={}>
                                <i style="color: #ff5f40" class="fa fa-window-close fa-2x" aria-hidden="true"></i>
                            </a>""".format(orderURL)
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td style="text-align: center; vertical-align: middle">{} {}</td>
                            </tr>
                         """.format( orderURL, complaints[i][0], complaints[i][1], complaints[i][2], complaints[i][3], complaints[i][4], complaints[i][5], approve, reject)
        return result
