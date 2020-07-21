from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.conf import settings
import threading
import math
import io

def ratingUtility(num):
    if num<=0:
        return 0
    elif num>=1:
        return 1
    else:
        return num

def make_image_square(img):
    width, height = img.size
    size = max(width, height)
    new_img = Image.new('RGB', (size, size), (255, 255, 255))
    new_img.paste(img, (int((size - width) / 2), int((size - height) / 2)))
    return new_img

def check_productID(id):
    with connections['oracle'].cursor() as cursor:
        cursor.execute("SELECT PRODUCT_ID FROM PRODUCT WHERE PRODUCT_ID = :id", {'id' :id})
        if(len(cursor.fetchall()) != 0):
            if(cursor.fetchall()[0][0] == id):
                return True
        else :
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

def item_page(request, product_id, seller_id):

    isloggedin = False
    acType = 'none'
    iscustomerlogin = False
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])
        if acType == 'customer':
            iscustomerlogin = True
    # TODO FOR NAWMI
    if request.method == 'POST' and iscustomerlogin:
        rating = request.POST.get("starRating")
        reviewDescription = request.POST.get("reviewDescription")
        with connections['oracle'].cursor() as cursor:
            query = """INSERT INTO REVIEW VALUES (TO_NUMBER(:product_id), TO_NUMBER(:seller_id), (SELECT CUSTOMER_ID FROM CUSTOMER
                       WHERE EMAIL_ID = :email),SYSDATE ,TO_NUMBER(:rating), :description)"""
            data = {'product_id' :product_id,'seller_id':seller_id, 'email':request.session['useremail'], 'rating':rating, 'description':reviewDescription}
            cursor.execute(query, data)
            cursor.execute("COMMIT")
    with connections['oracle'].cursor() as cursor:
        query =  """SELECT P.NAME PRODUCT_NAME, P.DESCRIPTION, C.CATEGORY_NAME, P.EXPECTED_TIME_TO_DELIVER,S.NAME SELLER_NAME ,COUNT(PU.ITEM_NUMBER) IN_STOCK, AVG(R.RATING) RATING FROM
                    PRODUCT P JOIN CATEGORY C USING(CATEGORY_ID) JOIN SELLER S USING(SELLER_ID) JOIN PRODUCT_UNIT PU USING(PRODUCT_ID,SELLER_ID) LEFT OUTER JOIN REVIEW R USING(PRODUCT_ID,SELLER_ID)
                    WHERE (PRODUCT_ID = :product_id AND SELLER_ID = :seller_id AND PU.STATUS = 'Not Sold')
                    GROUP BY P.NAME, P.DESCRIPTION, CATEGORY_NAME, EXPECTED_TIME_TO_DELIVER,S.NAME"""
        data = {'product_id' :product_id,'seller_id':seller_id}
        cursor.execute(query, data)
        result = cursor.fetchall()
        productName = result[0][0]
        productDescription = result[0][1]
        productCategory = result[0][2]
        rating = result[0][6]
        sellerName = result[0][4]
        inStock = result[0][5]
        deliveryTime = result[0][3]
        query = """SELECT FEATURE_DESCRIPTION FROM PRODUCT_FEATURE WHERE PRODUCT_ID = :product_id AND SELLER_ID = :seller_id"""
        cursor.execute(query, data)
        result = cursor.fetchall()
        features = []

        for i in range(len(result)):
            features.append(result[i][0])

        query = """SELECT PERCENTAGE_DISCOUNT, END_DATE, MINIMUM_QUANTITY_PURCHASED FROM OFFER WHERE
                   (PRODUCT_ID = :product_id AND SELLER_ID = :seller_id AND START_DATE<= SYSDATE AND SYSDATE <= END_DATE)"""
        cursor.execute(query, data)
        result = cursor.fetchall()
        offers = []
        for i in range(len(result)):
            temp = []
            for j in range(len(result[i])):
                temp.append(result[i][j])
            offers.append(temp)

        query = """SELECT NAME, RATING, DESCRIPTION, TO_CHAR(REVIEW_DATE,'DD MON YYYY') FROM REVIEW JOIN (SELECT (FIRST_NAME||' '||LAST_NAME)NAME,
                   CUSTOMER_ID FROM CUSTOMER) USING (CUSTOMER_ID) WHERE (PRODUCT_ID = :product_id AND SELLER_ID = :seller_id )"""
        cursor.execute(query, data)
        result = cursor.fetchall()
        reviews = []
        for i in range(len(result)):
            temp = []
            for j in range(len(result[i])):
                temp.append(result[i][j])
            reviews.append(temp)
        query = """SELECT PICTURE FROM PRODUCT_PICTURE WHERE (PRODUCT_ID = :product_id AND SELLER_ID = :seller_id )"""
        cursor.execute(query, data)
        result = cursor.fetchall()
        pictures = []
        # for i in range(len(result)):
        #     pictures.append(result[i][0])
    #features = ['sth', 'hoiun ew', 'iyu98ornu98wer 8 sdji f f oi']
    #offers = [ [3, "31 Oct 2020", 2], [15, "31 Oct 2020", 10] ]

    #reviews = [ ['Fatima Nawmi', 4, 'Battery Does Not Last Long Enough', 'Sept 30 2020'],
    #            ['Nazmul Takbir', 5, 'Perfect. Changed my life', 'Aug 30 2020'] ]
        pictures = ['https://image.freepik.com/free-vector/coffee-advertisement-realistic-composition_1284-26172.jpg',
                    'https://www.designyourway.net/blog/wp-content/uploads/2010/11/Nike-Print-Ads-10.jpg',
                    'https://videohive.img.customer.envatousercontent.com/files/62074379/previewImage.jpg?auto=compress%2Cformat&fit=crop&crop=top&max-h=8000&max-w=590&s=386c05c2a5bf67524b74e2b7a5d8ada9',
                    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAASFBMVEX///8AAADCwsLy8vJ7e3tSUlJZWVk3Nzf4+PiioqLW1tb8/PwEBATa2trz8/NPT09FRUWoqKjQ0NAoKCg8PDwyMjK9vb1ycnIbkZltAAABjElEQVR4nO3dW27UQBRFURsS8nAHJ4Ek858pIhLim6PyKYteawDl2rqy5b+7LAAAAAAAAAAAtG2zL3C4ExaOvdL2fd/320FGnLQ/vw4NXLav69m8jw1czlf4ZWjhonCCaygc+zG9nsLL1Krfj/9zg8NmODnx7/OPm+Hdt5n242e4vgw99189rUfPcF0fpv6jvlYKZ3pUGFPYojCnsEVhTmGLwpzCFoU5hS0KcwpbFOYUtijMKWxRmFPYojCnsEVhTmGLwpzCFoU5hS0KcwpbFOYUtijMKWxRmFPYojCnsEVhTmGLwpzCFoU5hS0KcwpbFOYUtijMKWxRmFPYojCnsEVhTmGLwpzCFoU5hS0KcwpbFOYUtijMKWxRmFPYojCnsEVhTmGLwpzCFoU5hS0KcwpbFOYUtijMKWxRmLuewsv6stzPszVm+OPn3URvh28HvEzf8Hj8/sOzUKhQ4XxjdzpvJ9yt/v8Xjt0ev2z3Nyfz8TS4cOxbPcLYK32edrbIs90HAAAAAAAAAGD5BeMzNfuZXsmPAAAAAElFTkSuQmCC']

        ratingHTML = "<span style='color: #d9534f'><strong> -- UNRATED</strong></span>"
        if rating is None:
            rating = 0
        rating = float(rating)
        if rating > 0 :
            r1 = ratingUtility(rating)
            r2 = ratingUtility(rating-1)
            r3 = ratingUtility(rating-2)
            r4 = ratingUtility(rating-3)
            r5 = ratingUtility(rating-4)
            ratingHTML = """<h1>
                                <span style='color: rgba(249, 146, 69, {})'>★ </span>
                                <span style='color: rgba(249, 146, 69, {})'>★ </span>
                                <span style='color: rgba(249, 146, 69, {})'>★ </span>
                                <span style='color: rgba(249, 146, 69, {})'>★ </span>
                                <span style='color: rgba(249, 146, 69, {})'>★ </span>
                            </h1>
                            <h6> {} out of 5 </h6>""".format(r1, r2, r3, r4, r5, rating)
        featureListHTML = ""
        for feature in features:
            featureListHTML += "<li>"
            featureListHTML += feature
            featureListHTML += "</li>"

        offerListHTML = ""
        offerDisplay = 'block'
        if len(offers) == 0:
            offerDisplay = 'none'
        else:
            for offer in offers:
                offerListHTML += "<li style='margin-bottom:8px'>"
                offerListHTML += """<span style='color: #0275d8; font-size: 20px;'><strong>{}% discount till {}.</strong></span>
                                    <br />
                                    Conditions: <br />
                                    -- {} or more units bought""".format(offer[0], offer[1], offer[2])
                offerListHTML += "</li>"

        inStockHTML = '<h4 style="color: {}"><strong>{}</strong></h4>'
        if int(inStock) > 0:
            inStockHTML = '<h4 style="color: {}"><strong>{}</strong></h4>'.format('#5cb85c', inStock)
        else:
            inStockHTML = '<h4 style="color: {}"><strong>{}</strong></h4>'.format('#d9534f', inStock)

        reviewsHTML = ""
        if len(reviews) == 0:
            reviewsHTML = "<h4>Be the first one to review !!!</h4>"
        else:
            for review in reviews:
                starHTML = ""
                for j in range(1, int(review[1])+1):
                    starHTML += '<li class="fa fa-star" style="color: #ffb300;"></li>'
                for j in range(int(review[1])+1, 6):
                    starHTML += ' <li class="fa fa-star" style="color: rgb(100, 0, 0);"></li>'
                reviewsHTML += """<li class="list-group-item">
                                    <h6 class="card-title" style="color: #0275d8">{}</h6>
                                    <p class="card-text" style="margin-bottom: 2px;">{}</p>
                                    <ul class="rating" style="padding-left: 0;">
                                        {}
                                    </ul>
                                    <small class="text-muted">{}</small>
                                  </li>""".format(review[0], review[2], starHTML, review[3])

        productImageHTML = ""
        productImageHTML2 = ""
        for i in range(0, len(pictures)):
            if i == 0:
                productImageHTML += """<div class="carousel-item active">
                                            <img class="w-100 d-block" style="width: 100%; height: auto" src="{}" alt="Slide Image" style="width: auto; height: 350px">
                                       </div>""".format(pictures[i])
                productImageHTML2 += '<li data-target="#carousel-1" data-slide-to="{}" class="active"></li>'.format(i)
            else:
                productImageHTML += """<div class="carousel-item">
                                            <img class="w-100 d-block" style="width: 100%; height: auto" src="{}" alt="Slide Image" style="width: auto; height: 350px">
                                       </div>""".format(pictures[i])
                productImageHTML2 += '<li data-target="#carousel-1" data-slide-to="{}"></li>'.format(i)

        data = {'iscustomerlogin': iscustomerlogin, 'isloggedin': isloggedin, 'accountType': acType, 'productName': productName,
                'productDescription': productDescription, 'productCategory': productCategory,
                'featureListHTML': featureListHTML, 'offerListHTML': offerListHTML, 'ratingHTML': ratingHTML,
                'sellerName': sellerName, 'inStockHTML': inStockHTML, 'deliveryTime': deliveryTime,
                'offerDisplay': offerDisplay, 'reviewsHTML': reviewsHTML, 'productImageHTML': productImageHTML,
                'productImageHTML2': productImageHTML2}

        return render(request, 'item.html', data)

def add_item_page(request):
    isloggedin = False
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])
        if acType != 'seller':
            return HttpResponseRedirect(reverse('home_page'))
    else:
        return HttpResponseRedirect(reverse('home_page'))

    if request.method == 'POST':
        id = request.POST.get("productID")
        name = request.POST.get("productName")
        price = request.POST.get("productPrice")
        deliveryTime = request.POST.get("deliveryTime")
        category = request.POST.get("chosenCategory")
        description = request.POST.get("description")
        quantityInStock = request.POST.get("quantityInStock")
        feature1 = request.POST.get("feature1")
        feature2 = request.POST.get("feature2")
        feature3 = request.POST.get("feature3")
        feature4 = request.POST.get("feature4")
        feature5 = request.POST.get("feature5")
        feature6 = request.POST.get("feature6")
        features = [feature1, feature2, feature3, feature4, feature5, feature6]

        if(check_productID(id) == False):
            with connections['oracle'].cursor() as cursor:
                cursor.execute("SELECT PRODUCT_ID_SEQ.NEXTVAL FROM DUAL")
                result = cursor.fetchall()
                id = result[0][0]

        query = """INSERT INTO PRODUCT VALUES (TO_NUMBER(:id) , (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email) , :name ,
                (SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME = :category), :description , :deliveryTime, TO_NUMBER(:price))"""
        with connections['oracle'].cursor() as cursor:
            data = {'name' : name,  'email' :request.session['useremail'] ,'id': id , 'category' : category , 'description' : description,
                    'deliveryTime' :deliveryTime, 'price' : price}
            cursor.execute(query, data)
            cursor.execute("COMMIT")

        num = 0
        for i in range(len(features)):
            if(features[i] != ""):
                num = num + 1
                query = """INSERT INTO PRODUCT_FEATURE VALUES(TO_NUMBER(:id) , (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email),
                        TO_NUMBER(:num), :des)"""
                with connections['oracle'].cursor() as cursor:
                    data = {'email' :request.session['useremail'] , 'des' :features[i],'id': id, 'num' : num}
                    cursor.execute(query, data)
                    cursor.execute("COMMIT")
        pics = []
        if 'productImage' in request.FILES:
            for pic in request.FILES.getlist('productImage'):
                img = Image.open(pic)
                squareImg = make_image_square(img)
                blob = io.BytesIO()
                squareImg.save(blob, 'jpeg')
                blob.seek(0)
                pics.append(blob)

            if len(pics)>4:
                pics = pics[:4]

            for i in range(len(pics)):
                query = """INSERT INTO PRODUCT_PICTURE VALUES(TO_NUMBER(:id), (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email),
                        TO_NUMBER(:num) , :pic)"""
                with connections['oracle'].cursor() as cursor:
                    data = {'email' :request.session['useremail'] ,'id': id, 'num' : i+1, 'pic' : pics[i].getvalue()}
                    cursor.execute(query, data)
                    cursor.execute("COMMIT")

        quantityInStock = int(quantityInStock)
        if quantityInStock > 0:
            quantityInStock = min(quantityInStock, 1000000)
            for i in range(int(quantityInStock)):
                query = """INSERT INTO PRODUCT_UNIT VALUES(TO_NUMBER(:id), (SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID = :email),
                           TO_NUMBER(:num),:status )"""

                with connections['oracle'].cursor() as cursor:
                    cursor.execute(query, {'id':id, 'email':request.session['useremail'], 'num':i+1, 'status':'Not Sold'})
                    cursor.execute("COMMIT")

        return HttpResponseRedirect(reverse('accounts:myaccount'))

    return render(request, 'newProduct.html', {'isloggedin': isloggedin, 'accountType': acType})

def add_advert_page(request):
    isloggedin = False
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])
    pass

def add_offer_page(request):
    isloggedin = False
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])
    pass

def check_category(category):
    query = "SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME = :category"
    with connections['oracle'].cursor() as cursor:
        cursor.execute(query , {'category' : category})
        result = cursor.fetchall()
        if(len(result) != 0):
            return True
        else:
            return False

def search_result(request, search_string):
    returnToHome = True
    for i in search_string:
        if i!='_':
            returnToHome = False
    if returnToHome:
        return HttpResponseRedirect(reverse('home_page'))

    isloggedin = False
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])

    if search_string.startswith('category_') and len(search_string)>len('category_'):
        category = search_string[len('category_'):]
        temp = ''
        for i in category.split('_'):
            if len(i)>0:
                temp += i + ' '
        category = temp[:-1]
        category = category.replace('and', '&')
        category = category.replace('Mens Fashion', 'Men\'s Fashion')
        category = category.replace('Womens Fashion', 'Women\'s Fashion')

        if(check_category(category)):
            query="""SELECT W.PRODUCT_ID, W.SELLER_ID, W.PRODUCT_NAME,  W.AVG_RATING, PP.PICTURE PIC1, PPP.PICTURE PIC2,W.PRICE,
                    W.SELLER_NAME,  W.MAX_DISCOUNT
                    FROM (SELECT X.PRODUCT_ID, X.SELLER_ID, X.PRODUCT_NAME, X.SELLER_NAME, X.PRICE, X.AVG_RATING, MAX(Y.PERCENTAGE_DISCOUNT) MAX_DISCOUNT
                    FROM ( SELECT P.PRODUCT_ID, S.SELLER_ID, P.NAME PRODUCT_NAME, S.NAME SELLER_NAME, P.PRICE, AVG(A.RATING) AVG_RATING
                    FROM PRODUCT P JOIN SELLER S ON (P.SELLER_ID = S.SELLER_ID)
                    LEFT OUTER JOIN REVIEW A ON (P.PRODUCT_ID = A.PRODUCT_ID AND P.SELLER_ID = S.SELLER_ID)
					WHERE CATEGORY_ID = (SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME = :category)
                    GROUP BY P.PRODUCT_ID, S.SELLER_ID, P.NAME, S.NAME, P.PRICE ) X
                    LEFT OUTER JOIN OFFER Y ON(X.PRODUCT_ID=Y.PRODUCT_ID AND X.SELLER_ID=Y.SELLER_ID)
                    WHERE ( Y.END_DATE >= SYSDATE OR Y.END_DATE IS NULL )
                    GROUP BY X.PRODUCT_ID, X.SELLER_ID, X.PRODUCT_NAME, X.SELLER_NAME, X.PRICE, X.AVG_RATING)W
                    LEFT OUTER JOIN PRODUCT_PICTURE PP ON (W.SELLER_ID = PP.SELLER_ID AND W.PRODUCT_ID = PP.PRODUCT_ID AND PP.PICTURE_NUMBER = 1)
                    LEFT OUTER JOIN PRODUCT_PICTURE PPP ON (W.SELLER_ID = PPP.SELLER_ID AND W.PRODUCT_ID = PPP.PRODUCT_ID AND PPP.PICTURE_NUMBER = 2)
                    WHERE ROWNUM <= 80;"""
            products = []
            with connections['oracle'].cursor() as cursor:
                cursor.execute(query, {'category':category})
                table = cursor.fetchall()
                for i in range(len(table)):
                    temp= []
                    for j in range(len(table[i])):
                        temp.append(table[i][j])
                    if( temp[3] == None ):
                        temp[3] = 0
                    if( temp[8] == None ):
                        temp[8] = 0
                    if( temp[5] == None ):
                        temp[5] = temp[4]
                    products.append(temp)

            words = []
            for i in search_string.split('_'):
                if len(i)>0:
                    words.append(i)
            words = ' '.join(words)

            productHTML = loadProductData(request, products)
            return render(request, 'search_result.html', {'isloggedin': isloggedin, 'accountType': acType, "productHTML": productHTML, "searchString": words} )

    elif search_string == 'Offers_Only':
        query =  """SELECT W.PRODUCT_ID, W.SELLER_ID, W.PRODUCT_NAME,  W.AVG_RATING, PP.PICTURE PIC1, PPP.PICTURE PIC2,W.PRICE,
                    W.SELLER_NAME,  W.MAX_DISCOUNT
                    FROM (SELECT X.PRODUCT_ID, X.SELLER_ID, X.PRODUCT_NAME, X.SELLER_NAME, X.PRICE, X.AVG_RATING, MAX(Y.PERCENTAGE_DISCOUNT) MAX_DISCOUNT
                    FROM ( SELECT P.PRODUCT_ID, S.SELLER_ID, P.NAME PRODUCT_NAME, S.NAME SELLER_NAME, P.PRICE, AVG(A.RATING) AVG_RATING
                    FROM PRODUCT P JOIN SELLER S ON (P.SELLER_ID = S.SELLER_ID)
                    LEFT OUTER JOIN REVIEW A ON (P.PRODUCT_ID = A.PRODUCT_ID AND P.SELLER_ID = S.SELLER_ID)
                    GROUP BY P.PRODUCT_ID, S.SELLER_ID, P.NAME, S.NAME, P.PRICE ) X
                    LEFT OUTER JOIN OFFER Y ON(X.PRODUCT_ID=Y.PRODUCT_ID AND X.SELLER_ID=Y.SELLER_ID)
                    WHERE ( Y.END_DATE >= SYSDATE OR Y.END_DATE IS NULL )
                    GROUP BY X.PRODUCT_ID, X.SELLER_ID, X.PRODUCT_NAME, X.SELLER_NAME, X.PRICE, X.AVG_RATING)W
                    LEFT OUTER JOIN PRODUCT_PICTURE PP ON (W.SELLER_ID = PP.SELLER_ID AND W.PRODUCT_ID = PP.PRODUCT_ID AND PP.PICTURE_NUMBER = 1)
                    LEFT OUTER JOIN PRODUCT_PICTURE PPP ON (W.SELLER_ID = PPP.SELLER_ID AND W.PRODUCT_ID = PPP.PRODUCT_ID AND PPP.PICTURE_NUMBER = 2)
                    WHERE ROWNUM <= 80 AND MAX_DISCOUNT IS NOT NULL"""
        with connections['oracle'].cursor() as cursor:
            cursor.execute(query)
            table = cursor.fetchall()
            products = []
            for i in range(len(table)):
                temp= []
                for j in range(len(table[i])):
                    temp.append(table[i][j])
                products.append(temp)
        productHTML = loadProductData(request, products)
        return render(request, 'search_result.html', {'isloggedin': isloggedin, 'accountType': acType, "productHTML": productHTML, "searchString": search_string} )

    words = []
    for i in search_string.split('_'):
        if len(i)>0:
            words.append(i)
    words = ' '.join(words)

    query =  """SELECT * FROM
                (SELECT GREATEST(STRING_SIMILARITY(W.PRODUCT_NAME,:words) , STRING_SIMILARITY(W.SELLER_NAME, :words))AS MAX_SCORE,W.PRODUCT_ID,
                W.SELLER_ID, W.PRODUCT_NAME,  W.AVG_RATING, PP.PICTURE PIC1, PPP.PICTURE PIC2,W.PRICE, W.SELLER_NAME,  W.MAX_DISCOUNT
                FROM (SELECT X.PRODUCT_ID, X.SELLER_ID, X.PRODUCT_NAME, X.SELLER_NAME, X.PRICE, X.AVG_RATING, MAX(Y.PERCENTAGE_DISCOUNT) MAX_DISCOUNT
                FROM ( SELECT P.PRODUCT_ID, S.SELLER_ID, P.NAME PRODUCT_NAME, S.NAME SELLER_NAME, P.PRICE, AVG(A.RATING) AVG_RATING
                FROM PRODUCT P JOIN SELLER S ON (P.SELLER_ID = S.SELLER_ID)
                LEFT OUTER JOIN REVIEW A ON (P.PRODUCT_ID = A.PRODUCT_ID AND P.SELLER_ID = S.SELLER_ID)
                GROUP BY P.PRODUCT_ID, S.SELLER_ID, P.NAME, S.NAME, P.PRICE ) X
                LEFT OUTER JOIN OFFER Y ON(X.PRODUCT_ID=Y.PRODUCT_ID AND X.SELLER_ID=Y.SELLER_ID)
                WHERE ( Y.END_DATE >= SYSDATE OR Y.END_DATE IS NULL )
                GROUP BY X.PRODUCT_ID, X.SELLER_ID, X.PRODUCT_NAME, X.SELLER_NAME, X.PRICE, X.AVG_RATING)W
                LEFT OUTER JOIN PRODUCT_PICTURE PP ON (W.SELLER_ID = PP.SELLER_ID AND W.PRODUCT_ID = PP.PRODUCT_ID AND PP.PICTURE_NUMBER = 1)
                LEFT OUTER JOIN PRODUCT_PICTURE PPP ON (W.SELLER_ID = PPP.SELLER_ID AND W.PRODUCT_ID = PPP.PRODUCT_ID AND PPP.PICTURE_NUMBER = 2)
                ORDER BY MAX_SCORE DESC)
                WHERE ROWNUM <= 80 AND MAX_SCORE > 0"""

    products = []
    with connections['oracle'].cursor() as cursor:
        cursor.execute(query, {'words':words})
        table = cursor.fetchall()
        for i in range(len(table)):
            temp = []
            for j in range(len(table[i])-1):
                temp.append(table[i][j+1])
            if( temp[3] == None ):
                temp[3] = 0
            if( temp[8] == None ):
                temp[8] = 0
            if( temp[5] == None ):
                temp[5] = temp[4]
            products.append(temp)

    productHTML = loadProductData(request, products)
    return render(request, 'search_result.html', {'isloggedin': isloggedin, 'accountType': acType, "productHTML": productHTML, "searchString": words} )

def loadProductData(request, products):
    total = len(products)
    productHTML = ""
    for i in range(0, total):
        productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], products[i][0], products[i][1])
        productName = products[i][2]
        if len(productName) >= 25:
            productName = productName[:22] + "..."
        productPrice = products[i][6]
        productDiscount = products[i][8]
        sellerName = products[i][7]
        if len(sellerName) >= 20:
            sellerName = sellerName[:18] + "..."
        ratingHTML = ""
        starCount = round(int(products[i][3]))
        for j in range(1, starCount+1):
            ratingHTML += '<li class="fa fa-star" style="color: #ffb300;"></li>'
        for j in range(starCount+1, 6):
            ratingHTML += ' <li class="fa fa-star" style="color: rgb(100, 0, 0);"></li>'

        image1Path = "http://{}/static/images/productImages/{}_1.jpg".format(request.META['HTTP_HOST'], products[i][0])
        image2Path = "http://{}/static/images/productImages/{}_2.jpg".format(request.META['HTTP_HOST'], products[i][0])

        productHTML += htmlGenerator(i, productURL, productName, productPrice, productDiscount, sellerName, ratingHTML, image1Path, image2Path, starCount)

        imageFile1 = open(settings.BASE_DIR+"\\static\\images\\productImages\\"+str(products[i][0])+"_1.jpg",'wb')
        imageFile2 = open(settings.BASE_DIR+"\\static\\images\\productImages\\"+str(products[i][0])+"_2.jpg",'wb')

        imageFile1.write( products[i][4].read() )
        imageFile2.write( products[i][5].read() )

        imageFile1.close()
        imageFile2.close()

    return productHTML

def htmlGenerator(i, productURL, productName, productPrice, productDiscount, sellerName, ratingHTML, image1Path, image2Path, starCount):
    showDiscount = 'none'
    if productDiscount > 0:
        showDiscount = 'inline'
    ratingVisibility = 'visible'
    if starCount == 0:
        ratingVisibility = 'hidden'
    return """<div class="productItems col-lg-3 col-md-6 col-sm-6" id="product{}" style="display: none; margin-bottom: 20px;">
        <div class="product-grid7" style="background-color: white; padding: 5px">
          <div class="product-image7">
            <a href="{}">
              <img class="pic-1" src="{}">
              <img class="pic-2" src="{}">
            </a>
          </div>
          <div class="caption">
            <p class="group inner list-group-item-heading" style="margin-bottom: 0px;"><strong> <a href="{}" style="color:black">{}</a> </strong> </p>
            <p class="group inner list-group-item-text" style="margin-bottom: 0px; color: black">  Seller -- <span class="sellerName">{}</span>  </p>
            <p class="lead" style="margin-bottom: 0px;">
                <span class="productPrices">{}</span> Tk
                <span style="font-size: 80%; color: red; display: {}"> - - upto {}% off !!! </span>
            </p>
            <ul class="rating" style="visibility: {}">
              <h5>
                  {}
              </h5>
            </ul>
          </div>
        </div>
      </div>""".format(i, productURL, image1Path, image2Path, productURL, productName, sellerName, productPrice, showDiscount, productDiscount, ratingVisibility, ratingHTML) + "\n"
