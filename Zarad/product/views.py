from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
def item_page(request, product_id, seller_id):
    return render(request, 'item.html')

def add_item_page(request):
    pass

def add_advert_page(request):
    pass

def add_offer_page(request):
    pass

def search_result(request, search_string):
    returnToHome = True
    for i in search_string:
        if i!='_':
            returnToHome = False
    if returnToHome:
        return HttpResponseRedirect(reverse('home_page'))

    isloggedin = False
    accountType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        if request.session['useremail'] == 'nazmultakbir98@gmail.com' or request.session['useremail'] == 'fatimanawmi@gmail.com':
            accountType = 'admin'
        else:
            " check accountType from database using request.session['useremail'] "
            accountType = 'customer'

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
            ' check the product table and extract all products with the given category '
    elif search_string == 'Offers_Only':
        ' check the offer table and extract all offers that have not expired yet '

    words = []
    for i in search_string.split('_'):
        if len(i)>0:
            words.append(i)
    search_string = ' '.join(words)

    """
        create the following view for each product item:
            product id, product name, category_name, description, seller id, seller name
        ' check if search_string completely matches product_id '
        ' check if search_string completely matches product_name '
        ' check if search_string completely matches a category name '
        ' check if search_string completely mathces a seller name '
        ' check for products whose name has EDS > 50 when compared to search_string. select the top 15 '
        ' check for products whose name has EDS > 50 when compared to first quarter of search_string. select the top 15 '
        ' check for products whose name has EDS > 50 when compared to second quarter of search_string. select the top 5 '
        ' check for products whose name has EDS > 50 when compared to third quarter of search_string. select the top 5 '
        ' check for products whose name has EDS > 50 when compared to fourth quarter of search_string. select the top 5 '
    """
    "features"

    return render(request, 'search_result.html', {'isloggedin': isloggedin, 'accountType': accountType})
