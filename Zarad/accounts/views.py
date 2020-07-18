from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from PIL import Image
from django.conf import settings
import io
import info

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
                return render(request, 'signup.html', {'emailExists': True, 'adminLogin': adminLogin, 'isloggedin': isloggedin, 'accountType': accountType})
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
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])
        if acType == 'customer':
            cartTableHTML = generateCartTableHTML(request)
            orderTableHTML = generateOrderTableHTML(request)
            purchaseOrderHTML = orderTableHTML[0]
            returnOrderHTML = orderTableHTML[1]
            walletTableHTML = generateWalletTableHTML(request)
            reviewTableHTML = genrateReviewTableHTML(request)
            accountBalance = 12000
            return render(request, 'customerAccount.html', {'isloggedin': isloggedin, 'accountType': acType, 'cartTableHTML': cartTableHTML, 'purchaseOrderHTML': purchaseOrderHTML, 'returnOrderHTML': returnOrderHTML, 'walletTableHTML': walletTableHTML, 'reviewTableHTML': reviewTableHTML})
        elif acType == 'seller':
            productTableHTML = generateProductTableHTML(request)
            offerTableHTML = generateOfferTableHTML(request)
            advertTableHTML = generateAdvertTableHTML(request)
            walletTableHTML = generateWalletTableHTML(request)
            accountBalance = 12000
            return render(request, 'sellerAccount.html', {'isloggedin': isloggedin, 'accountType': acType, 'productTableHTML': productTableHTML, 'offerTableHTML': offerTableHTML, 'advertTableHTML': advertTableHTML, 'walletTableHTML': walletTableHTML, 'accountBalance': accountBalance})
        elif acType == 'deliveryGuy':
            return render(request, 'deliveryGuy.html', {'isloggedin': isloggedin, 'accountType': acType})
        elif acType == 'customerCare':
            return render(request, 'customerCare.html', {'isloggedin': isloggedin, 'accountType': acType})
        elif acType == 'admin':
            # Work To Be Done
            return HttpResponseRedirect(reverse('home_page'))
    else:
        return HttpResponseRedirect(reverse('home_page'))

def generateProductTableHTML(request):
    sellerID = 1
    products = [ [123451234512345, '3 in 1 Electric Trimmer For Men', 'Men\'s Fashion', 12, 100],
                 [123451234512345, '3 in 1 Electric Trimmer For Men', 'Men\'s Fashion', 12, 100],
                 [123451234512345, '3 in 1 Electric Trimmer For Men', 'Men\'s Fashion', 12, 100],
                 [123451234512345, '3 in 1 Electric Trimmer For Men', 'Men\'s Fashion', 12, 100] ]

    result = ""
    if( len(products)==0 ):
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
        for i in range( len(products) ):
            productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], products[i][0], sellerID)
            editButton = """<a href={}>
                                <button type="button" class="btn btn-link">Edit</button>
                            </a>
                         """.format(productURL)
            result += """<tr>
                            <th scope="row"><a href={}>{}</a></th>
                            <td >{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>
                     """.format( productURL, products[i][0], products[i][1], products[i][2], products[i][3], products[i][4], editButton)
    return result

def generateOfferTableHTML(request):
    sellerID = 1
    offers = [ [123451234512345, 'Sept 31 2019', 'Oct 03 2019', 12, 0, 0, 1],
               [123451234512345, 'Oct 03 2019', 'Dec 03 2019', 32, 10, 100, 2] ]
    result = ""
    if( len(offers)==0 ):
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
        for i in range( len(offers) ):
            productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], offers[i][0], sellerID)
            endOfferButton = "<button type='button' class='btn btn-danger'>Force End</button>"
            result += """<tr>
                            <th scope="row"><a href={}>{}</a></th>
                            <td >{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>
                     """.format( productURL, offers[i][0], offers[i][1], offers[i][2], offers[i][3], offers[i][4], offers[i][5], endOfferButton)
    return result

def generateAdvertTableHTML(request):
    sellerID = 1
    adverts = [ [123451234512345, 'Aug 31 2019', '31 Jan 2019', 2000, 1, 'picBlob'],
                [123451234512345, 'Aug 31 2019', '31 Jan 2019', 2000, 1, 'picBlob'] ]
    result = ""
    if( len(adverts)==0 ):
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
        for i in range( len(adverts) ):
            productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], adverts[i][0], sellerID)
            endOfferButton = "<button type='button' class='btn btn-danger'>Force End</button>"
            result += """<tr>
                            <th scope="row"><a href={}>{}</a></th>
                            <td >{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>
                     """.format( productURL, adverts[i][0], adverts[i][1], adverts[i][2], adverts[i][3], adverts[i][4], adverts[i][5], endOfferButton)
    return result

def generateWalletTableHTML(request):
    sellerID = 1
    scp = info.serviceChargePercentage
    transactions = [ [123451234512345, 'Aug 31 2019', 'Recharge', 2000, scp*2000],
                [123451234512345, 'Aug 31 2019', 'Recharge', 1000, scp*1000] ]
    result = ""
    if( len(transactions)==0 ):
        result = """<tr>
                        <th scope="row"></th>
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
    cartItems = [ [1, 2, 'Trimmer', 'Gilette', 2, 1000, 0.05],
                  [1, 2, 'Trimmer', 'Gilette', 2, 1000, 0.05] ]
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
            totalPrice = cartItems[i][5]*cartItems[i][4] * (1-cartItems[i][6])
            orderButton = """<a href={}>
                                <button type="button" class="btn btn-success" style="margin: 5px">Order</button>
                            </a>
                         """.format(productURL)
            deleteButton = """<a href={}>
                                <button type="button" class="btn btn-danger" style="margin: 5px">Delete</button>
                            </a>
                         """.format(productURL)
            result += """<tr>
                            <th scope="row"><a href={}>{}</a></th>
                            <td >{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{} {}</td>
                        </tr>
                     """.format( productURL, cartItems[i][2], cartItems[i][3], cartItems[i][5], cartItems[i][4], cartItems[i][6], totalPrice, orderButton, deleteButton)
    return result

def generateOrderTableHTML(request):
    pHTML = rHTML = ""
    purchaseOrder = [ ['123451234512345', 'Aug 31 2019', 'Wallet', 'Delivered', 'Sept 10 2019', '9 Sept 2019', '01722345467'],
                      ['123451234512345', 'Aug 31 2019', 'Wallet', 'Not Delivered', 'Sept 10 2019', '', '01722345467'], ]
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
            orderAlterButton = '<button type="button" class="btn btn-danger">{}</button>'
            if( purchaseOrder[i][3] == 'Delivered' ):
                orderAlterButton = orderAlterButton.format("Return")
            elif( purchaseOrder[i][3] == 'Not Delivered' ):
                orderAlterButton = orderAlterButton.format("Cancel")
            pHTML += """<tr>
                            <th scope="row"><a href={}>{}</a></th>
                            <td >{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>
                     """.format( orderURL, purchaseOrder[i][0], purchaseOrder[i][1], purchaseOrder[i][2], purchaseOrder[i][3], purchaseOrder[i][4], purchaseOrder[i][5], purchaseOrder[i][6], orderAlterButton)


    returnOrder = [ ['123451234512345', 'Aug 31 2019', 'Does not Work', 'Wallet', 'Approved', 'Oct 31 2019', '01844375468'],
                    ['123451234512345', 'Aug 31 2019', 'Does not Work', 'Wallet', 'Not Approved', '', '01844375468'],]
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
            orderAlterButton = '<button type="button" class="btn btn-danger" style="display: {}">Cancel</button>'
            if( returnOrder[i][4] == 'Approved' ):
                orderAlterButton = orderAlterButton.format('none')
            else:
                orderAlterButton = orderAlterButton.format('block')
            rHTML += """<tr>
                            <th scope="row"><a href={}>{}</a></th>
                            <td >{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>
                     """.format( orderURL, returnOrder[i][0], returnOrder[i][1], returnOrder[i][2], returnOrder[i][3], returnOrder[i][4], returnOrder[i][5], returnOrder[i][6], orderAlterButton)


    return [pHTML, rHTML]

def generateWalletTableHTML(request):
    pass

def genrateReviewTableHTML(request):
    pass
