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

    data = {'isloggedin': isloggedin, 'accountType': acType, 'advert1': adverts[0], 'advert2': adverts[1],
            'advert3': adverts[2], 'advert4': adverts[3], 'advert5': adverts[4], 'advert6': adverts[5],
            'advert7': adverts[6], 'advert8': adverts[7]}
    return render(request, "home_page.html", data)
