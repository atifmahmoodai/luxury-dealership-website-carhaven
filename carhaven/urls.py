from django.contrib import admin
from django.urls import path
from inventory import views
urlpatterns=[path('staff/',admin.site.urls),path('',views.home,name='home'),path('collection/',views.inventory,name='inventory'),path('collection/<uuid:pk>/',views.vehicle,name='vehicle'),path('photos/<uuid:pk>/',views.photo,name='photo'),path('photos/vehicles/<str:filename>',views.stored_photo),path('about/',views.about,name='about'),path('contact/',views.contact,name='contact'),path('contact/received/',views.thanks,name='thanks'),path('privacy/',views.privacy,name='privacy'),path('robots.txt',views.robots),path('sitemap.xml',views.sitemap),path('health/',views.health)]
