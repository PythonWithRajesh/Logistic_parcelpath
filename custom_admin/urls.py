from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_dashboard,name='custom_dashboard'),
    path('custom_dashboard/', views.custom_dashboard, name='custom_dashboard'),
    path("parcel-bookings/",views.parcel_bookings,name="parcel_bookings"),

    path("parcel/<int:parcel_id>/",views.parcel_detail,name="parcel_detail"),

    path("parcel/<int:parcel_id>/update-status/",views.update_parcel_status,name="update_parcel_status"),

    path("parcel/<int:parcel_id>/delete/",views.delete_parcel,name="delete_parcel"),
    
    path('cs_customer/', views.cs_customer, name='cs_customer'),
    path('cs_parcel/', views.cs_parcel, name='cs_parcel'),
    path('cs_payment/', views.cs_payment, name='cs_payment'),
    path('cs_reports/', views.cs_reports, name='cs_reports'),
    path('cs_settings/', views.cs_settings, name='cs_settings'),
    path('cs_shipment/', views.cs_shipment, name='cs_shipment'),
    path('cs_track/', views.cs_track, name='cs_track'),


     # Contact Management
    path("cs_contact/",views.cs_contact,name="cs_contact"),
    path("cs_contact/add/",views.cs_contact_add,name="cs_contact_add"),
    path("cs_contact/view/<int:contact_id>/",views.cs_contact_view,name="cs_contact_view"),
    path("cs_contact/edit/<int:contact_id>/",views.cs_contact_edit,name="cs_contact_edit"),
    path("cs_contact/reply/<int:contact_id>/",views.cs_contact_reply,name="cs_contact_reply"),
    path("cs_contact/delete/<int:contact_id>/",views.cs_contact_delete,name="cs_contact_delete"),

]

