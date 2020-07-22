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

def make_16_9(img):
    width, height = img.size
    if width > height*1.78:
        newwidth = width
        newheight = int(width * 9/16)
        new_img = Image.new('RGB', (newwidth, newheight), (255, 255, 255))
        new_img.paste(img, (int((newwidth - width) / 2), int((newheight - height) / 2)))
        return new_img
    else:
        newwidth = int(height*(16/9))
        newheight = height
        new_img = Image.new('RGB', (newwidth, newheight), (255, 255, 255))
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

def accountBalance(email, type):
    with connections['oracle'].cursor() as cursor:
        if type == 'customer':
            cursor.execute("SELECT WALLET_BALANCE(CUSTOMER_ID , 'CUSTOMER') FROM CUSTOMER WHERE EMAIL_ID = :email", {'email':email})
            balance = cursor.fetchall()[0][0]
            if balance == None:
                return 0
        elif type == 'seller':
            cursor.execute("SELECT WALLET_BALANCE(SELLER_ID , 'SELLER') FROM SELLER WHERE EMAIL_ID = :email", {'email': email})
            balance = cursor.fetchall()[0][0]
            if balance == None:
                return 0

def myaccount(request):
    isloggedin = False
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])

        if acType == 'customer':
            # TO DO extract the basic info details
            if request.method == 'POST':
                formIdentity = request.POST.get('formIdentity')
                if formIdentity == 'reviewForm':
                    productID = request.POST.get('delRevBtn').split('+')[0]
                    sellerID = request.POST.get('delRevBtn').split('+')[1]
                    # TODO nawmi delete review
                    return HttpResponseRedirect(reverse('accounts:myaccount'))

            cartTableHTML = generateCartTableHTML(request)
            orderTableHTML = generateOrderTableHTML(request)
            purchaseOrderHTML = orderTableHTML[0]
            returnOrderHTML = orderTableHTML[1]
            walletTableHTML = generateWalletTableHTMLCustomer(request)
            reviewTableHTML = genrateReviewTableHTML(request)
            acBal = accountBalance(request.session['useremail'], acType)

            data = {'isloggedin': isloggedin, 'accountType': acType, 'cartTableHTML': cartTableHTML,
                    'purchaseOrderHTML': purchaseOrderHTML, 'returnOrderHTML': returnOrderHTML,
                    'walletTableHTML': walletTableHTML, 'reviewTableHTML': reviewTableHTML,
                    'accountBalance': acBal}

            return render(request, 'customerAccount.html', data)

        elif acType == 'seller':
            # TO DO extract the basic info details
            if request.method == 'POST':
                formIdentity = request.POST.get('formIdentity')
                if formIdentity == 'addOfferForm':
                    # TODO nawmi
                    # check if product id is valid
                    productID = int(request.POST.get('productID'))
                    startDate = request.POST.get('startDate')
                    endDate = request.POST.get('endDate')
                    discount = request.POST.get('discount')
                    minQuan = request.POST.get('minQuan')

                elif formIdentity == 'addAdvertForm':
                    productID = int(request.POST.get('productID'))

                    blob = io.BytesIO()
                    if 'advertImage' in request.FILES:
                        imgFile = request.FILES['advertImage']
                        img = Image.open(imgFile)
                        img = make_16_9(img)
                        img.save(blob, 'jpeg')
                        blob.seek(0)

                return HttpResponseRedirect(reverse('accounts:myaccount'))
            productTableHTML = generateProductTableHTML(request)
            offerTableHTML = generateOfferTableHTML(request)
            advertTableHTML = generateAdvertTableHTML(request)
            walletTableHTML = generateWalletTableHTML(request)
            acBal = accountBalance(request.session['useremail'], acType)
            advertCost = info.advertCost

            data = {'isloggedin': isloggedin, 'accountType': acType, 'productTableHTML': productTableHTML,
                    'offerTableHTML': offerTableHTML, 'advertTableHTML': advertTableHTML,
                    'walletTableHTML': walletTableHTML, 'accountBalance': acBal, 'advertCost': advertCost,
                    'buyAdvert': acBal>=advertCost}

            return render(request, 'sellerAccount.html', data)

        elif acType == 'deliveryGuy':
            # TO DO extract the basic info details
            deliveredItemHTML = generateDeliveredItemHTML(request)
            pendingDeliveryItemHTML = generatePendingDeliveryHTML(request)
            return render(request, 'deliveryGuy.html', {'isloggedin': isloggedin, 'accountType': acType, 'deliveredItemHTML': deliveredItemHTML, 'pendingDeliveryItemHTML': pendingDeliveryItemHTML})

        elif acType == 'customerCare':
            # TO DO extract the basic info details
            managedComplaintsHTML = generateManagedComplaintsHTML(request)
            pendingComplaintsHTML = generatePendingComplaintsHTML(request)
            return render(request, 'customerCare.html', {'isloggedin': isloggedin, 'accountType': acType, 'managedComplaintsHTML': managedComplaintsHTML, 'pendingComplaintsHTML': pendingComplaintsHTML})
        elif acType == 'admin':
            # Work To Be Done
            return HttpResponseRedirect(reverse('home_page'))
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
                    ON(P.PRODUCT_ID = S.PRODUCT_ID AND S.STATUS = 'Sold')
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
    with connections['oracle'].cursor() as cursor:
        query = """SELECT PRODUCT_ID, START_DATE, END_DATE, PERCENTAGE_DISCOUNT DISCOUNT, MINIMUM_QUANTITY_PURCHASED MINIMUM_QUANTITY FROM OFFER
                   WHERE SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email)"""
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
                            <th scope="row"></th>
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
                            </tr>
                         """.format( productURL, offers[i][0], offers[i][1], offers[i][2], offers[i][3], offers[i][4], endOfferButton)
        return result

def generateAdvertTableHTML(request):
    with connections['oracle'].cursor() as cursor:
        query = """SELECT PRODUCT_ID, START_DATE, END_DATE, COST_FOR_SELLER COST, PICTURE FROM ADVERTISEMENT
                   WHERE SELLER_ID = (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        adverts = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            adverts.append(temp)

        cursor.execute("SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email", {'email':request.session['useremail']})
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
                productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], adverts[i][0], sellerID)
                endOfferButton = "<button type='button' class='btn btn-danger'>Force End</button>"
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                         """.format( productURL, adverts[i][0], adverts[i][1], adverts[i][2], adverts[i][3], adverts[i][4], endOfferButton)
        return result

def generateWalletTableHTML(request):
    # TODO transaction id date type amount service charge
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
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT Q.PRODUCT_ID, Q.SELLER_ID, P.NAME P_NAME, S.NAME S_NAME, QUANTITY, P.PRICE, DISCOUNT  FROM
                    ( SELECT X.PRODUCT_ID, X.SELLER_ID, QUANTITY, MAX(PERCENTAGE_DISCOUNT) DISCOUNT FROM
                    ( SELECT PRODUCT_ID, SELLER_ID, QUANTITY FROM CART_ITEM
                    WHERE CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email) ) X
                    LEFT OUTER JOIN
                    (SELECT PRODUCT_ID, SELLER_ID, PERCENTAGE_DISCOUNT, MINIMUM_QUANTITY_PURCHASED FROM OFFER) Y
                    ON (X.PRODUCT_ID=Y.PRODUCT_ID AND X.SELLER_ID=Y.SELLER_ID)
                    WHERE ( QUANTITY>=MINIMUM_QUANTITY_PURCHASED OR MINIMUM_QUANTITY_PURCHASED IS NULL )
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
            if temp[i][6] == None:
                temp[i][6] = 0
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
                totalPrice = cartItems[i][5]*cartItems[i][4] * (1-cartItems[i][6]/100)
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
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, ORDER_DATE, PAYMENT_METHOD, DELIVERY_STATUS, MAX(ORDER_DATE+EXPECTED_TIME_TO_DELIVER)
                    EXPECTED_DELIVERY_DATE, DELIVERED_DATE, PHONE_NUMBER DELIVERY_GUY_NUMBER FROM
                    CUSTOMER_ORDER JOIN PURCHASE_ORDER P USING(ORDER_ID)
                    JOIN (SELECT PHONE_NUMBER, EMPLOYEE_ID FROM EMPLOYEE ) PH ON (PH.EMPLOYEE_ID = P.DELIVERY_EMPLOYEE_ID)
                    JOIN (SELECT ORDER_ID, PRODUCT_ID, SELLER_ID FROM ORDERED_ITEMS) USING(ORDER_ID) JOIN
                    (SELECT PRODUCT_ID, SELLER_ID, EXPECTED_TIME_TO_DELIVER FROM PRODUCT) USING(PRODUCT_ID, SELLER_ID)
                    WHERE CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email)
                    GROUP BY ORDER_ID, ORDER_DATE, PAYMENT_METHOD, DELIVERY_STATUS, DELIVERED_DATE, PHONE_NUMBER"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        purchaseOrder = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            if temp[i][5] == None:
                temp[i][5] = ''
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

        query =  """SELECT ORDER_ID, ORDER_DATE,COMPLAINT_DES, PAYMENT_METHOD, APPROVAL_STATUS, RETURN_DATE,
                    PHONE_NUMBER CUSTOMER_CARE_NUMBER FROM CUSTOMER_ORDER JOIN RETURN_ORDER P USING(ORDER_ID)
                    JOIN (SELECT PHONE_NUMBER, EMPLOYEE_ID FROM EMPLOYEE ) PH ON
                    (PH.EMPLOYEE_ID = P.CUSTOMER_CARE_EMPLOYEE_ID)
                    WHERE CUSTOMER_ID = (SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID = :email)"""
        cursor.execute(query, {'email':request.session['useremail']})
        table = cursor.fetchall()
        returnOrder = []
        for i in range(len(table)):
            temp= []
            for j in range(len(table[i])):
                temp.append(table[i][j])
            if table[i][5] == None:
                table[i][5] = 0
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

def generateWalletTableHTMLCustomer(request):
    scp = info.serviceChargePercentage
    transactions = [ [123451234512345, 'Aug 31 2019', 'Recharge', 2000, scp*2000],
                     [123451234512345, 'Aug 31 2019', 'Payment', -1000, 0] ]
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

def genrateReviewTableHTML(request):
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
                deleteReview = """<button name="delRevBtn" value="{}" type="submit" class="btn btn-danger">
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
                    MAX(ORDER_DATE+EXPECTED_TIME_TO_DELIVER) EXPECTED_DELIVERY_DATE , DELIVERED_DATE, PAYMENT_METHOD,
                    ORDER_TOTAL(ORDER_ID) TOTAL_PAYMENT FROM (SELECT * FROM PURCHASE_ORDER JOIN CUSTOMER_ORDER USING(ORDER_ID)
                    WHERE DELIVERY_EMPLOYEE_ID = (SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :email)
                    AND DELIVERY_STATUS = 'Delivered' ) JOIN (SELECT (FIRST_NAME||' '||LAST_NAME)
                    CUSTOMER_NAME, PHONE_NUMBER "CUSTOMER PHONE",('Apartment : '|| APARTMENT_NUMBER||', Building : '
                    ||BUILDING_NUMBER||', Road : '||ROAD||' , '||AREA||' , '||CITY) "CUSTOMER ADDRESS",
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
        orderedItems = [ [123451234512345, 'Fatima Nawmi', '01722345467', 'BUET Chattri Hall', 'Oct 04 2020', 'Oct 09 2020', 'Cash', 5000] ]
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
                orderURL = "http://{}".format(request.META['HTTP_HOST'])
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                         """.format( orderURL, orderedItems[i][0], orderedItems[i][1], orderedItems[i][2], orderedItems[i][3], orderedItems[i][4], orderedItems[i][5], orderedItems[i][6], orderedItems[i][7])
        return result

def generatePendingDeliveryHTML(request):
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, CUSTOMER_NAME, "CUSTOMER PHONE", "CUSTOMER ADDRESS",
                    MAX(ORDER_DATE+EXPECTED_TIME_TO_DELIVER) EXPECTED_DELIVERY_DATE, PAYMENT_METHOD,
                    ORDER_TOTAL(ORDER_ID) TOTAL_PAYMENT FROM (SELECT * FROM PURCHASE_ORDER JOIN CUSTOMER_ORDER USING(ORDER_ID)
                    WHERE DELIVERY_EMPLOYEE_ID = (SELECT EMPLOYEE_ID FROM EMPLOYEE WHERE EMAIL_ID = :email)
                    AND DELIVERY_STATUS = 'Not Delivered' ) JOIN (SELECT (FIRST_NAME||' '||LAST_NAME)
                    CUSTOMER_NAME, PHONE_NUMBER "CUSTOMER PHONE",('Apartment : '|| APARTMENT_NUMBER||', Building : '
                    ||BUILDING_NUMBER||', Road : '||ROAD||' , '||AREA||' , '||CITY) "CUSTOMER ADDRESS",
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
        orderedItems = [ [123451234512345, 'Fatima Nawmi', '01722345467', 'BUET Chattri Hall', 'Oct 04 2020', 'Cash', 5000] ]
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
                markDelivered = '<button type="button" class="btn btn-info">Delivered</button>'
                orderURL = "http://{}".format(request.META['HTTP_HOST'])
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                         """.format( orderURL, orderedItems[i][0], orderedItems[i][1], orderedItems[i][2], orderedItems[i][3], orderedItems[i][4], orderedItems[i][5], orderedItems[i][6], markDelivered)
        return result

def generateManagedComplaintsHTML(request):
    # TODO order id date customer name number complaint payment method amount status returned date
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, ORDER_DATE, "CUSTOMER NAME","CUSTOMER PHONE",COMPLAINT_DES "COMPLAINT",
                    PAYMENT_METHOD, "TOTAL AMOUNT", STATUS,"MANAGED DATE" FROM
                    (SELECT ORDER_ID, COMPLAINT_DES,ORDER_TOTAL(ORDER_ID)"TOTAL AMOUNT",APPROVAL_STATUS STATUS,
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
        complaints = [ [123451234512345, 'Oct 04 2020', 'Fatima Nawmi', '01722345467', 'Does Not Work', 'Cash', 5000, 'Approved', 'Oct 15 2019'],
                       [123451234512345, 'Oct 04 2020', 'Fatima Nawmi', '01722345467', 'Does Not Work', 'Cash', 5000, 'Rejected', 'Oct 15 2019'] ]
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
                            <td></td>
                        </tr>
                     """
        else:
            for i in range( len(complaints) ):
                orderURL = "http://{}".format(request.META['HTTP_HOST'])
                color = ""
                if( complaints[i][7] == 'Approved' ):
                    color = '#5cb85c'
                elif( complaints[i][7] == 'Rejected' ):
                    color = "#d9534f"
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td style="font-weight: bold; color: {}">{}</td>
                                <td>{}</td>
                            </tr>
                         """.format( orderURL, complaints[i][0], complaints[i][1], complaints[i][2], complaints[i][3], complaints[i][4], complaints[i][5], complaints[i][6], color, complaints[i][7], complaints[i][8])
        return result

def generatePendingComplaintsHTML(request):
    # TODO order id date customer name number complaint payment method amount
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT ORDER_ID, ORDER_DATE, "CUSTOMER NAME","CUSTOMER PHONE",COMPLAINT_DES "COMPLAINT", PAYMENT_METHOD,
                    "TOTAL AMOUNT", STATUS,"MANAGED DATE" FROM
                    (SELECT ORDER_ID, COMPLAINT_DES,ORDER_TOTAL(ORDER_ID)"TOTAL AMOUNT",APPROVAL_STATUS STATUS,
                    RETURN_DATE "MANAGED DATE" FROM RETURN_ORDER WHERE CUSTOMER_CARE_EMPLOYEE_ID = (SELECT EMPLOYEE_ID
                    FROM EMPLOYEE WHERE EMAIL_ID = :email)AND APPROVAL_STATUS = 'Not Approved') JOIN CUSTOMER_ORDER USING(ORDER_ID) JOIN
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
        complaints = [ [123451234512345, 'Oct 04 2020', 'Fatima Nawmi', '01722345467', 'Does Not Work', 'Cash', 5000] ]
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
                approve = """<a href={}>
                                <i style="color: #5cb85c; margin-right: 10px; margin-left: 5px" class="fa fa-check-square fa-2x" aria-hidden="true"></i>
                             </a>""".format(orderURL)
                reject = """<a href={}>
                                <i style="color: #d9534f" class="fa fa-window-close fa-2x" aria-hidden="true"></i>
                            </a>""".format(orderURL)
                result += """<tr>
                                <th scope="row"><a href={}>{}</a></th>
                                <td >{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{}</td>
                                <td>{} {}</td>
                            </tr>
                         """.format( orderURL, complaints[i][0], complaints[i][1], complaints[i][2], complaints[i][3], complaints[i][4], complaints[i][5], complaints[i][6], approve, reject)
        return result
