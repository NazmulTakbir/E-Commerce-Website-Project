from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.conf import settings
import io
import random

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


def home_page(request):
    isloggedin = False
    acType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])

    adverts = getAdverts(request)

    topHTML = topProducts(request)
    offersHTML = topOffers(request)
    categoriesHTML = topCategories(request)

    data = {'isloggedin': isloggedin, 'accountType': acType, 'advert1': adverts[0], 'advert2': adverts[1],
            'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4], 'advert6': adverts[5],
            'advert7': adverts[6], 'advert8': adverts[7], 'topHTML': topHTML, 'offersHTML': offersHTML,
            'categoriesHTML': categoriesHTML}

    return render(request, "home_page.html", data)


def topProducts(request):

    query = """SELECT DISTINCT PRODUCT_ID FROM (SELECT O.PRODUCT_ID ,COUNT(O.PRODUCT_ID) NUM
               FROM CUSTOMER_ORDER C, ORDERED_ITEMS  O, PURCHASE_ORDER P WHERE C.ORDER_ID = O.ORDER_ID
               AND O.ORDER_ID = P.ORDER_ID AND C.ORDER_DATE > (SYSDATE - 30 ) GROUP BY O.PRODUCT_ID
               ORDER BY NUM DESC) WHERE ROWNUM<=12"""

    with connections['oracle'].cursor() as cursor:
        cursor.execute(query)
        productIDs = cursor.fetchall()

    productDetails = getProductDetails(productIDs)

    topHTML = loadProductData(request, productDetails)

    return topHTML


def topOffers(request):

    query = """SELECT * FROM (SELECT PRODUCT_ID FROM PRODUCT JOIN OFFER USING(PRODUCT_ID, SELLER_ID) WHERE END_DATE > SYSDATE
               ORDER BY PERCENTAGE_DISCOUNT DESC) WHERE ROWNUM<= 6"""

    with connections['oracle'].cursor() as cursor:
        cursor.execute(query)
        productIDs = cursor.fetchall()

    productDetails = getProductDetails(productIDs)

    offersHTML = loadProductData(request, productDetails)

    return offersHTML


def topCategories(request):

    query = """SELECT CATEGORY_ID, B.CATEGORY_NAME, B.PICTURE FROM
              (SELECT DISTINCT CATEGORY_ID FROM (SELECT O.PRODUCT_ID ,
              (SELECT DISTINCT CATEGORY_ID FROM PRODUCT WHERE PRODUCT_ID = O.PRODUCT_ID) CATEGORY_ID,
              COUNT(O.PRODUCT_ID)NUM FROM CUSTOMER_ORDER C, ORDERED_ITEMS  O, PURCHASE_ORDER P
              WHERE C.ORDER_ID = O.ORDER_ID AND O.ORDER_ID = P.ORDER_ID AND C.ORDER_DATE > (SYSDATE - 30 )
              GROUP BY O.PRODUCT_ID ORDER BY NUM DESC)) A JOIN CATEGORY B USING(CATEGORY_ID);"""

    with connections['oracle'].cursor() as cursor:
        cursor.execute(query)
        categoryData = cursor.fetchall()

    return loadCategoryData(request, categoryData)


def getProductDetails(productIDs):
    if len(productIDs) <= 0:
        return []
    with connections['oracle'].cursor() as cursor:
        ids = {}
        for i in range(len(productIDs)):
            ids['p'+str(i)] = productIDs[i][0]

        placeholders = ':' + ', :'.join(ids.keys())

        query = """SELECT PR.PRODUCT_ID,PR.NAME PRODUCT_NAME,PR.SELLER_ID, S.NAME SELLER_NAME,PR.PRICE,MAX_DISCOUNT(PR.PRODUCT_ID, PR.SELLER_ID),
                   AVG_RATING(PR.PRODUCT_ID, PR.SELLER_ID) AVG_RATE, P.PICTURE PIC1 , PP.PICTURE PIC2
                   FROM PRODUCT PR LEFT OUTER JOIN PRODUCT_PICTURE P ON (PR.SELLER_ID = P.SELLER_ID AND PR.PRODUCT_ID = P.PRODUCT_ID AND P.PICTURE_NUMBER = 1)
                   LEFT OUTER JOIN PRODUCT_PICTURE PP ON (PR.SELLER_ID = PP.SELLER_ID AND PR.PRODUCT_ID = PP.PRODUCT_ID AND PP.PICTURE_NUMBER = 2)
                   JOIN SELLER S ON (PR.SELLER_ID = S.SELLER_ID) WHERE PR.PRODUCT_ID IN (%s) ORDER BY MAX_DISCOUNT(PR.PRODUCT_ID, PR.SELLER_ID) DESC""" % placeholders

        productDetails = []
        if(len(productIDs) > 0 ):
            cursor.execute(query, ids)
            result = cursor.fetchall()
            for i in range(len(result)):
                temp = []
                for j in range(len(result[i])):
                    temp.append(result[i][j])
                if( temp[5] == None ):
                    temp[5] = 0
                if( temp[6] == None ):
                    temp[6] = 0
                if( temp[8] == None ):
                    temp[8] = temp[7]
                productDetails.append(temp)


        return productDetails


def loadProductData(request, products):
    total = len(products)
    productHTML = ""
    for i in range(0, total):
        productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], products[i][0], products[i][2])
        productName = products[i][1]
        if len(productName) > 24:
            productName = productName[:21] + "..."
        productPrice = products[i][4]
        productDiscount = products[i][5]
        sellerName = products[i][3]
        if len(sellerName) >= 20:
            sellerName = sellerName[:18] + "..."
        ratingHTML = ""

        rating = float(products[i][6])
        temp = rating
        ratingHTML = ""
        starCount = 0
        while temp>=1:
            ratingHTML += '<i class="star fa fa-star text-warning"></i>'
            temp -= 1
            starCount += 1
        if temp>0 and temp<1:
            ratingHTML += '<i class="fa fa-star-half-o text-warning" aria-hidden="true"></i>'
            starCount += 1
        while starCount < 5:
            ratingHTML += '<i class="fa fa-star-o text-warning" aria-hidden="true"></i>'
            starCount += 1

        image1Path = "http://{}/static/images/productImages/{}_{}_1.jpg".format(request.META['HTTP_HOST'], products[i][0], products[i][2])
        image2Path = "http://{}/static/images/productImages/{}_{}_2.jpg".format(request.META['HTTP_HOST'], products[i][0], products[i][2])

        reviewCount = 0
        with connections['oracle'].cursor() as cursor:
            query = "SELECT COUNT(*) FROM REVIEW WHERE PRODUCT_ID = :product_id AND SELLER_ID = :seller_id"
            cursor.execute(query, {'product_id': products[i][0], 'seller_id': products[i][2]})
            reviewCount = int( cursor.fetchall()[0][0] )

        inStock = 0
        with connections['oracle'].cursor() as cursor:
            query = """SELECT COUNT(*) FROM PRODUCT_UNIT WHERE PRODUCT_ID = :product_id AND
                       SELLER_ID = :seller_id AND LOWER(STATUS) = 'not sold'"""
            cursor.execute(query, {'product_id': products[i][0], 'seller_id': products[i][2]})
            inStock = int( cursor.fetchall()[0][0] )

        productHTML += htmlGenerator(i, productURL, productName, productPrice, productDiscount, sellerName, ratingHTML, image1Path, image2Path, starCount, rating, reviewCount, inStock)

        imageFile1 = open(settings.BASE_DIR+"\\static\\images\\productImages\\{}_{}_1.jpg".format(products[i][0], products[i][2]),'wb')
        imageFile2 = open(settings.BASE_DIR+"\\static\\images\\productImages\\{}_{}_2.jpg".format(products[i][0], products[i][2]),'wb')

        imageFile1.write( products[i][7].read() )
        imageFile2.write( products[i][8].read() )

        imageFile1.close()
        imageFile2.close()

    return productHTML

def loadCategoryData(request, categoryData):
    total = len(categoryData)
    categoryHTML = ""

    for i in range(0, total):

        categoryName = 'category_' + '_'.join(categoryData[i][1].replace('&', 'and').replace("'", '').split())
        categoryURL = "http://{}/product/search/{}/".format(request.META['HTTP_HOST'], categoryName)

        image = open(settings.BASE_DIR+"\\static\\images\\category_images\\{}.jpg".format(categoryName),'wb')
        image.write(categoryData[i][2].read())
        image.close()

        imagePath = "http://{}/static/images/category_images/{}.jpg".format(request.META['HTTP_HOST'], categoryName)

        categoryHTML += """<div class="col-md-6 col-lg-3" >
                             <div class="card shadow p-3 mb-5 bg-white rounded" style="width: 16rem;">
                               <a href="{}"><img class="card-img-top" src="{}" alt="Card image cap"></a>
                               <div class="card-body">
                                 <h6 class="card-text" style="text-align: center">{}</h6>
                               </div>
                             </div>
                           </div>""".format(categoryURL, imagePath, categoryData[i][1])

    return categoryHTML

def htmlGenerator(i, productURL, productName, productPrice, productDiscount, sellerName, ratingHTML, image1Path, image2Path, starCount, rating, reviewCount, inStock):
    hasOffer = "no"
    if float(productDiscount)>0:
        hasOffer = "yes"
    reviewText = 'reviews'
    if reviewCount == 1:
        reviewText = 'review'
    stockIcon = '<i style="margin-left: 20px" class="text-danger fa fa-times-circle" aria-hidden="true"></i>'
    discountIcon = '<i style="margin-left: 20px" class="text-danger fa fa-times-circle" aria-hidden="true"></i>'
    if productDiscount is None:
        productDiscount = 0
    productDiscount = int(productDiscount)
    if( productDiscount > 0 ):
        discountIcon = '<i style="margin-left: 20px" class="text-success fa fa-check-circle" aria-hidden="true"></i>'
    if( inStock > 0 ):
        stockIcon = '<i style="margin-left: 20px" class="text-success fa fa-check-circle" aria-hidden="true"></i>'
    return """<div class="productItems col-md-6 col-lg-3" id="product{}">
                <label class="searchRank" style="display:none">{}</label>
                <label class="productRatings" style="display:none">{}</label>
                <label class="hasOffer" style="display:none">{}</label>
                <div class="card shadow border-light mb-4" style="background-color: #f2f8f8">
                <div class="product-grid7" style="padding: 0.5px; background-color: rgba(31, 171, 136, 0.1);">
                <div class="product-image7">
                    <a href="{}">
                        <img class="pic-1" src="{}">
                        <img class="pic-2" src="{}">
                    </a>
                </div>
                </div>
                        <div style="padding: 10px; padding-top:5px;" class="card-body">
                            <a href="{}">
                                <p style="margin:0px; padding:0px" class="font-weight-normal">{}</p>
                            </a>
                            <div class="post-meta"><span class="small lh-120"><i class="fa fa-building" aria-hidden="true"></i> <span class="sellerName">{}</span></span></div>
                            <div style="padding-top: 5px; padding-bottom: 5px">
                                {} <span class="badge badge-pill badge-secondary ml-2">{}</span>
                  <small class="text-info" style="font-size: 10px">&nbsp;{} {} </small>
                </div>
                            <div class="d-flex justify-content-between" style="padding-top: 0px">
                                <div class="col pl-0" style="padding: 1px">
                    <span class="text-muted font-small d-block">Price</span>
                    <span class="text-dark font-weight-bold">
                      <span style="font-size: 13px"><strong>৳</strong><span class="productPrices">{}</span></span>
                    </span>
                  </div>
                                <div class="col" style="padding: 1px">
                    <span class="text-muted font-small d-block">In Stock</span>
                    {}
                  </div>
                                <div class="col pr-0" style="padding: 1px">
                    <span class="text-muted font-small d-block">Discount</span>
                    {}
                  </div>
                            </div>
                        </div>
                    </div>
                </div>""".format(i, i, rating, hasOffer, productURL, image1Path, image2Path, productURL, productName, sellerName, ratingHTML, rating, reviewCount, reviewText, productPrice, stockIcon, discountIcon) + "\n"
