from django.urls import path
from . import views


urlpatterns=[
    path('',views.index,name='home'),
    path('about/',views.about,name='about'),
    path('review/',views.review,name='review'),
    path('login/',views.login,name='login'),
    path('register/',views.register,name='register'),
    path('order/',views.order,name='order'),
    path('add_cart/<cake_uid>',views.add_cart,name='add_cart'),
    path('remove_cart/<cart_items_uid>',views.remove_cart,name='remove_cart'),
    path('pay/',views.pay,name='pay'),
    path('success/',views.success,name='success'),
   

    

    
]
