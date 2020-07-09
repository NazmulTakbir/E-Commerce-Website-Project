from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
def home_page(request):
    return render(request, "home_page.html")

def test_page(request):
    query = "SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME FROM CUSTOMER"
    with connections['oracle'].cursor() as cursor:
        cursor.execute(query)
        headers = ["CUSTOMER_ID", "FIRST_NAME", "LAST_NAME"]
        headers = ["CUSTOMER_ID", "FIRST_NAME", "LAST_NAME"]
        return HttpResponse( toHTML(headers, cursor) )

def toHTML(headers, cursor):
    html = "<table border=1>"
    html += "<tr>"
    for header in headers:
        html += "<th>" + header + "</th>"
    html += "</tr>"
    for row in cursor.fetchall():
        html += "<tr>"
        for col in row:
            html += "<td>" + str(col) + "</td>"
        html += "</tr>"
    html += "</table>"
    return html
