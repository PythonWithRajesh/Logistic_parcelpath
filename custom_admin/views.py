from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum

from django.contrib import messages
from django.db.models import Q

from ParcelPath.models import Book_parcel, Contact


def custom_dashboard(request):

    # ==============================
    # DASHBOARD COUNTS
    # ==============================

    total_users = User.objects.count()

    total_parcels = Book_parcel.objects.count()

    delivered = Book_parcel.objects.filter(
        status="Delivered"
    ).count()

    cancelled = Book_parcel.objects.filter(
        status="Cancelled"
    ).count()

    pending = Book_parcel.objects.exclude(
        status__in=["Delivered", "Cancelled"]
    ).count()

    # ==============================
    # REVENUE
    # ==============================

    revenue = Book_parcel.objects.aggregate(
        total=Sum("price")
    )["total"] or 0

    # ==============================
    # CONTACTS
    # ==============================

    total_contacts = Contact.objects.count()

    # ==============================
    # RECENT PARCELS
    # ==============================

    recent_parcels = Book_parcel.objects.all().order_by("-id")[:10]

    # ==============================
    # RECENT USERS
    # ==============================

    recent_users = User.objects.all().order_by("-date_joined")[:5]

    # ==============================
    # RECENT CONTACTS
    # ==============================

    recent_contacts = Contact.objects.all().order_by("-id")[:5]

    # ==============================
    # CONTEXT
    # ==============================

    context = {
        "total_users": total_users,
        "total_parcels": total_parcels,
        "delivered": delivered,
        "pending": pending,
        "cancelled": cancelled,
        "revenue": revenue,
        "total_contacts": total_contacts,

        "recent_parcels": recent_parcels,
        "recent_users": recent_users,
        "recent_contacts": recent_contacts,
    }

    return render(
        request,
        "custom_admin/custom_dashboard.html",
        context
    )





def parcel_bookings(request):

    # ==============================
    # ALL PARCELS
    # ==============================

    parcels = Book_parcel.objects.all().order_by("-id")

    # ==============================
    # SEARCH
    # ==============================

    search = request.GET.get("search", "").strip()

    if search:
        parcels = parcels.filter(
            Q(tracking_id__icontains=search) |
            Q(sender_name__icontains=search) |
            Q(receiver_name__icontains=search) |
            Q(mobile_number__icontains=search) |
            Q(parcel_type__icontains=search)
        )

    # ==============================
    # STATUS FILTER
    # ==============================

    status = request.GET.get("status", "").strip()

    if status:
        parcels = parcels.filter(status=status)

    # ==============================
    # COUNTS
    # ==============================

    total_parcels = Book_parcel.objects.count()

    delivered = Book_parcel.objects.filter(
        status="Delivered"
    ).count()

    cancelled = Book_parcel.objects.filter(
        status="Cancelled"
    ).count()

    pending = Book_parcel.objects.exclude(
        status__in=["Delivered", "Cancelled"]
    ).count()

    context = {
        "parcels": parcels,

        "total_parcels": total_parcels,
        "delivered": delivered,
        "pending": pending,
        "cancelled": cancelled,

        "search": search,
        "selected_status": status,
    }

    return render(
        request,
        "custom_admin/parcel_bookings.html",
        context
    )


# ==========================================
# VIEW PARCEL
# ==========================================

def parcel_detail(request, parcel_id):

    parcel = get_object_or_404(
        Book_parcel,
        id=parcel_id
    )

    return render(
        request,
        "custom_admin/parcel_detail.html",
        {
            "parcel": parcel
        }
    )


# ==========================================
# UPDATE STATUS
# ==========================================

def update_parcel_status(request, parcel_id):

    if request.method == "POST":

        parcel = get_object_or_404(
            Book_parcel,
            id=parcel_id
        )

        new_status = request.POST.get("status")

        allowed_statuses = [
            "Parcel Booked",
            "Picked Up",
            "In Transit",
            "Out for Delivery",
            "Delivered",
            "Cancelled",
        ]

        if new_status in allowed_statuses:

            parcel.status = new_status
            parcel.save(update_fields=["status"])

            messages.success(
                request,
                f"Parcel {parcel.tracking_id} status updated successfully."
            )

        else:

            messages.error(
                request,
                "Invalid parcel status."
            )

    return redirect("custom_admin:parcel_bookings")


# ==========================================
# DELETE PARCEL
# ==========================================

def delete_parcel(request, parcel_id):

    if request.method == "POST":

        parcel = get_object_or_404(
            Book_parcel,
            id=parcel_id
        )

        tracking_id = parcel.tracking_id

        parcel.delete()

        messages.success(
            request,
            f"Parcel {tracking_id} deleted successfully."
        )

    return redirect("custom_admin:parcel_bookings")
# Create your views here.
def main(request):
    return render(request,'custom_admin/main.html')


def cs_customer(request):

    # =========================
    # DELETE CUSTOMER / PARCEL
    # =========================

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "delete":

            customer_id = request.POST.get("customer_id")

            try:

                customer = Book_parcel.objects.get(
                    id=customer_id
                )

                customer.delete()

                messages.success(
                    request,
                    "Customer deleted successfully."
                )

            except Book_parcel.DoesNotExist:

                messages.error(
                    request,
                    "Customer not found."
                )

            return redirect("cs_customer")


    # =========================
    # ALL REAL CUSTOMERS
    # =========================

    customers = Book_parcel.objects.all().order_by("-id")


    # =========================
    # REAL COUNTS
    # =========================

    total_customers = customers.count()

    total_orders = customers.count()


    delivered_orders = customers.filter(
        status__iexact="Delivered"
    ).count()


    pending_deliveries = customers.exclude(
        status__iexact="Delivered"
    ).count()


    # =========================
    # CONTEXT
    # =========================

    context = {

        "customers": customers,

        "total_customers": total_customers,

        "total_orders": total_orders,

        "delivered_orders": delivered_orders,

        "pending_deliveries": pending_deliveries,

    }


    return render(
        request,
        "custom_admin/cs_customer.html",context
    )

def cs_parcel(request):
    parcels = Book_parcel.objects.all().order_by("-id")

    context = {"parcels": parcels,}

    return render(request,"custom_admin/cs_parcel.html",context)

from django.shortcuts import render
from .models import Book_parcel


def cs_payment(request):

    payments = Book_parcel.objects.all().order_by("-id")

    print("================================")
    print("PAYMENT PAGE")
    print("TOTAL RECORDS :", payments.count())
    print("================================")

    context = {
        "payments": payments,
        "total_payments": payments.count(),
        "successful_payments": payments.count(),
        "pending_payments": 0,
        "total_revenue": sum(
            p.price for p in payments
            if p.price
        ),
    }

    return render(
        request,
        "custom_admin/cs_payment.html",
        context
    )

from django.shortcuts import render
from django.db.models import Sum
from ParcelPath.models import Book_parcel


def cs_reports(request):

    # ==========================================
    # ALL PARCELS
    # ==========================================

    parcels = Book_parcel.objects.all().order_by("-id")


    # ==========================================
    # TOTAL PARCELS
    # ==========================================

    total_parcels = Book_parcel.objects.count()


    # ==========================================
    # DELIVERED
    # ==========================================

    delivered = Book_parcel.objects.filter(
        status__iexact="Delivered"
    ).count()


    # ==========================================
    # IN TRANSIT
    # ==========================================

    transit = Book_parcel.objects.filter(
        status__iexact="In Transit"
    ).count()


    # ==========================================
    # CANCELLED
    # ==========================================

    cancelled = Book_parcel.objects.filter(
        status__iexact="Cancelled"
    ).count()


    # ==========================================
    # TOTAL REVENUE
    # ==========================================

    revenue_result = Book_parcel.objects.aggregate(
        total=Sum("price")
    )

    revenue = revenue_result["total"] or 0


    # ==========================================
    # CONTEXT
    # ==========================================

    context = {

        "parcels": parcels,

        "total_parcels": total_parcels,

        "delivered": delivered,

        "transit": transit,

        "cancelled": cancelled,

        "revenue": revenue,

    }


    return render(
        request,
        "custom_admin/cs_reports.html",
        context
    )


def cs_track(request):

    parcel = None
    error = None

    tracking_id = request.GET.get("tracking_id", "").strip()

    if tracking_id:

        try:
            parcel = Book_parcel.objects.get(
                tracking_id__iexact=tracking_id
            )

        except Book_parcel.DoesNotExist:
            error = "Tracking ID not found."

    context = {
        "parcel": parcel,
        "error": error,
        "tracking_id": tracking_id,
    }

    return render(
        request,
        "custom_admin/cs_track.html",
        context
    )

def cs_settings(request):
    return render(request, 'custom_admin/cs_settings.html')

def cs_shipment(request):
    parcels = Book_parcel.objects.all().order_by("-id")

    context = {
        "parcels": parcels,

        "total_shipments": Book_parcel.objects.count(),

        "delivered": Book_parcel.objects.filter(status="Delivered").count(),

        "in_transit": Book_parcel.objects.filter(status__in=["In Transit","Picked Up","Out for Delivery"]).count(),

        "pending": Book_parcel.objects.filter(status="Parcel Booked").count(),}

    return render(request,"custom_admin/cs_shipment.html",context)





# =========================================================
# CONTACT MANAGEMENT
# =========================================================

from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from ParcelPath.models import Contact


def cs_contact(request):

    search = request.GET.get("search", "").strip()

    contacts = Contact.objects.all().order_by("-date", "-id")

    # =========================
    # SEARCH
    # =========================
    if search:
        contacts = contacts.filter(
            Q(name__icontains=search)
            | Q(email__icontains=search)
            | Q(mobile__icontains=search)
            | Q(message__icontains=search)
        )

    # =========================
    # TOTAL
    # =========================
    total_messages = Contact.objects.count()

    # =========================
    # TODAY
    # =========================
    today = timezone.localdate()

    today_messages = Contact.objects.filter(
        date=today
    ).count()

    # =========================
    # STATUS
    # =========================

    # જો હાલ Contact model માં status field નથી,
    # તો temporarily 0 રાખીએ.
    unread_messages = 0
    replied_messages = 0

    context = {
        "contacts": contacts,
        "total_messages": total_messages,
        "unread_messages": unread_messages,
        "replied_messages": replied_messages,
        "today_messages": today_messages,
        "search": search,
    }

    return render(
        request,
        "custom_admin/cs_contact.html",
        context
    )


# =========================================================
# ADD NEW CONTACT MESSAGE
# =========================================================

def cs_contact_add(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        message_text = request.POST.get("message", "").strip()

        # Validation
        if not name or not email or not mobile or not message_text:
            messages.error(
                request,
                "Please fill all required fields."
            )

            return redirect("cs_contact_add")

        Contact.objects.create(
            name=name,
            email=email,
            mobile=mobile,
            message=message_text,
            date=timezone.localdate(),
        )

        messages.success(
            request,
            "New contact message added successfully."
        )

        return redirect("cs_contact")

    return render(
        request,
        "custom_admin/contact_form.html",
        {
            "page_title": "New Contact Message",
            "button_text": "Create Message",
        }
    )


# =========================================================
# VIEW CONTACT MESSAGE
# =========================================================

def cs_contact_view(request, contact_id):

    contact = get_object_or_404(
        Contact,
        id=contact_id
    )

    return render(
        request,
        "custom_admin/contact_view.html",
        {
            "contact": contact
        }
    )


# =========================================================
# EDIT CONTACT MESSAGE
# =========================================================

def cs_contact_edit(request, contact_id):

    contact = get_object_or_404(
        Contact,
        id=contact_id
    )

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        message_text = request.POST.get("message", "").strip()

        if not name or not email or not mobile or not message_text:
            messages.error(
                request,
                "All fields are required."
            )

            return redirect(
                "cs_contact_edit",
                contact_id=contact.id
            )

        contact.name = name
        contact.email = email
        contact.mobile = mobile
        contact.message = message_text

        contact.save()

        messages.success(
            request,
            "Contact message updated successfully."
        )

        return redirect("cs_contact")

    return render(
        request,
        "custom_admin/contact_form.html",
        {
            "contact": contact,
            "page_title": "Edit Contact Message",
            "button_text": "Update Message",
        }
    )


# =========================================================
# MARK AS REPLIED
# =========================================================

def cs_contact_reply(request, contact_id):

    contact = get_object_or_404(
        Contact,
        id=contact_id
    )

    if request.method == "POST":

        contact.save(update_fields=["status"])

        messages.success(
            request,
            f"Message from {contact.name} marked as Replied."
        )

    return redirect("cs_contact")


# =========================================================
# DELETE CONTACT
# =========================================================

def cs_contact_delete(request, contact_id):

    contact = get_object_or_404(
        Contact,
        id=contact_id
    )

    if request.method == "POST":

        contact_name = contact.name

        contact.delete()

        messages.success(
            request,
            f"Contact message from {contact_name} deleted successfully."
        )

    return redirect("cs_contact")