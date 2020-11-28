from django.conf.urls import url
from . import views

app_name = 'product'

urlpatterns = [
    url(r"item/(?P<product_id>\d+)/(?P<seller_id>\d+)/$", views.item_page, name='item'),
    url(r"additem/$", views.add_item_page, name='additem'),
    url(r"search/(?P<search_string>\w+)/$", views.search_result, name='search_result'),
    url(r"editproduct/(?P<product_id>\d+)/(?P<seller_id>\d+)/$", views.edit_product_page, name='editproduct'),
]
