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

def make_image_square(img):
    width, height = img.size
    size = max(width, height)
    new_img = Image.new('RGB', (size, size), (255, 255, 255))
    new_img.paste(img, (int((size - width) / 2), int((size - height) / 2)))
    return new_img

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
    if request.session.has_key('useremail'):
        isloggedin = True
        acType = accountType(request.session['useremail'])
    return render(request, 'item.html', {'isloggedin': isloggedin, 'accountType': acType})

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
        feature1 = request.POST.get("feature1")
        feature2 = request.POST.get("feature2")
        feature3 = request.POST.get("feature3")
        feature4 = request.POST.get("feature4")
        feature5 = request.POST.get("feature5")
        feature6 = request.POST.get("feature6")
        features = [feature1, feature2, feature3, feature4, feature5, feature6]

        pics = []
        if 'productImage' in request.FILES:
            for pic in request.FILES.getlist('productImage'):
                img = Image.open(pic)
                squareImg = make_image_square(img)
                blob = io.BytesIO()
                squareImg.save(blob, 'jpeg')
                blob.seek(0)
                pics.append(blob)

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

        if ' check if category is one of the categories from the category table ':
            ' check the product table and extract <=80 products with the given category '

            # productHTML = loadProductData(request, products)
            # return render(request, 'search_result.html', {'isloggedin': isloggedin, 'accountType': acType, "productHTML": productHTML, "searchString": search_string} )
    elif search_string == 'Offers_Only':
        ' check the offer table for offers that have not expired yet '
        ' if a product has multiple offers extract the best one'
        ' get the data with the latest offer first '
        ' extract <=80 products '

        # productHTML = loadProductData(request, products)
        # return render(request, 'search_result.html', {'isloggedin': isloggedin, 'accountType': acType, "productHTML": productHTML, "searchString": search_string} )

    words = []
    for i in search_string.split('_'):
        if len(i)>0:
            words.append(i)
    words = ' '.join(words)

    ' for each product calculate the following score = max( sim with product name, sim with seller name) '
    ' rank the products in descending order '
    ' choose <=80 products '
    ' design a list of lists according to the structure below '
    ' product id, seller_id, product_name, average rating, image1, image2, price, seller_name, discount '

    img1 = Image.open(settings.BASE_DIR+"\\static\\images\\temp\\test.jpg")
    img2 = Image.open(settings.BASE_DIR+"\\static\\images\\temp\\test2.jpg")

    products = [ [1, 2, "Electric 3 in 1 Trimmer", 0, img1, img2, 1500, "Philips", 20],
                 [3, 4, "Razor", 3.5, img1, img2, 500, "Gilette", 10],
                 [5, 6, "Earphone", 4.1, img1, img2, 750, "Samsung", 0],
                 [3, 4, "Razor", 3.5, img1, img2, 500, "Dollar Shave", 5],
                 [5, 6, "Earphone", 4.1, img1, img2, 750, "XYZ", 0],
                 [3, 4, "Razor", 3.5, img1, img2, 500, "ABC", 0],
                 [5, 6, "Earphone", 4, img1, img2, 750, "MNO", 25],
                 [7, 8, "Airpod", 4.9, img1, img2, 4000, "Apple", 0] ]


    productHTML = loadProductData(request, products)
    return render(request, 'search_result.html', {'isloggedin': isloggedin, 'accountType': acType, "productHTML": productHTML, "searchString": search_string} )

def loadProductData(request, products):
    total = len(products)
    productHTML = ""
    for i in range(0, total):
        productURL = "http://{}/product/item/{}/{}/".format(request.META['HTTP_HOST'], products[i][0], products[i][1])
        productName = products[i][2]
        print(len(productName))
        if len(productName) >= 25:
            productName = productName[:22] + "..."
        productPrice = products[i][6]
        productDiscount = products[i][8]
        sellerName = products[i][7]
        if len(sellerName) >= 20:
            sellerName = sellerName[:18] + "..."
        ratingHTML = ""
        starCount = round(products[i][3])
        for j in range(1, starCount+1):
            ratingHTML += '<li class="fa fa-star" style="color: #ffb300;"></li>'
        for j in range(starCount+1, 6):
            ratingHTML += ' <li class="fa fa-star" style="color: rgb(100, 0, 0);"></li>'
        image1Path = "http://{}/static/images/productImages/{}_1.png".format(request.META['HTTP_HOST'], products[i][0])
        image2Path = "http://{}/static/images/productImages/{}_2.png".format(request.META['HTTP_HOST'], products[i][0])
        print(image1Path)
        print(image2Path)
        productHTML += htmlGenerator(i, productURL, productName, productPrice, productDiscount, sellerName, ratingHTML, image1Path, image2Path, starCount)

        products[i][4].save(settings.BASE_DIR+"\\static\\images\\productImages\\"+str(products[i][0])+"_1.png")
        products[i][5].save(settings.BASE_DIR+"\\static\\images\\productImages\\"+str(products[i][0])+"_2.png")

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
            <p class="group inner list-group-item-text" style="margin-bottom: 0px; color: black">  Seller -- {}  </p>
            <p class="lead" style="margin-bottom: 0px;">
                {} Tk
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
