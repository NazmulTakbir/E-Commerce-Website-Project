from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required

def accountType(email):
    cursor.execute("SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID "+ email)
    results = cursor.fetchall()
    if(len(results) == 0):
        cursor.execute("SELECT EMPLOYEE_ID FROM DELIVERY_GUY WHERE EMAIL_ID "+ email)
        results = cursor.fetchall()
        if(len(results) == 0):
            cursor.execute("SELECT CUSTOMER_ID FROM CUSTOMER WHERE EMAIL_ID "+ email)
            results = cursor.fetchall()
            if(len(results) == 0):
                  cursor.execute("SELECT EMPLOYEE_ID FROM CUSTOMER_CARE_EMPLOYEE WHERE EMAIL_ID "+ email)
                  results = cursor.fetchall()
                  if(len(results) == 0):
                      cursor.execute("SELECT EMPLOYEE_ID FROM ADMIN WHERE EMAIL_ID "+ email)
                      results = cursor.fetchall()
                      if(len(results) != 0):
                          return 'admin'
                  else :
                      return 'customerCare'
            else:
                return 'customer'
        else:
            return 'deliveryGuy'
    else:
        return 'seller'
# Create your views here.
def home_page(request):
    isloggedin = False
    accountType = 'none'
    if request.session.has_key('useremail'):
        isloggedin = True
        if request.session['useremail'] == 'nazmultakbir98@gmail.com' or request.session['useremail'] == 'fatimanawmi@gmail.com':
            accountType = 'admin'
        else:
            accountType = accountType(request.session['useremail'])
    return render(request, "home_page.html", {'isloggedin': isloggedin, 'accountType': accountType})
