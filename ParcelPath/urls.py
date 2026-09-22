from django.urls import path
from . import views 
urlpatterns = [ 
    path('', views.base,name='home'), 
    path('Home/', views.home, name='home'), 
    path('book_parcel/', views.book_parcel, name="book_parcel"), 
    path('track_parcel/', views.track_parcel, name="track_parcel"), 
    path('contact/', views.contact, name="contact"), 
    path("services/", views.services, name="services"), 
    path("user_login/", views.login_view, name="user_login"), 
    path("logout/", views.logout_view, name="logout"), 
    path("register/", views.register, name="register"), 
    path("profile/", views.profile, name="profile"), 
    path("admin_page/", views.admin_page, name="admin_page"), 
    path("track_detail/<str:tracking_id>/",views.track_detail,name="track_detail"), 
    path("create-payment/", views.create_payment, name="create_payment"), 
    path("payment-success/",views.payment_success,name="payment_success"), 
    path("booking_success/",views.payment_success,name="booking_success"), 
    path("cod-payment/", views.cod_payment, name="cod_payment"),
    # path("cod_success/", views.cod_success, name="cod_success"),
    path("payment-receipt/<str:tracking_id>/",views.download_payment_receipt,name="download_payment_receipt"),

]