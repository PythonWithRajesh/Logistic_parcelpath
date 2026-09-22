from django.shortcuts import render, redirect, get_object_or_404
from .models import Contact, Book_parcel
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import random
import string
import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
import razorpay
from django.conf import settings

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.shortcuts import get_object_or_404

from .models import Book_parcel


import razorpay
from django.conf import settings
from django.shortcuts import render, redirect


client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)

def generate_tracking_id():
    while True:
        tracking_id = "PP" + "".join(
            random.choices(string.digits, k=8)
        )

        if not Book_parcel.objects.filter(
            tracking_id=tracking_id
        ).exists():
            return tracking_id


# Create your views here.
def base(request):
    return render(request,'home.html')

def home(request):
    return render(request, 'home.html')

def services(request):
    return render(request, "services.html")

def admin_page(request):
    return render(request, 'admin_page.html')

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

def booking_success(request): 
    if request.method == "POST": 

        # COD પસંદ કર્યું હોય ત્યારે 
        payment_method = request.POST.get('payment_method', 'COD') 
        payment_status = request.POST.get('payment_status', 'Pending') 

        
        return render(request, 'booking_success.html', { 'payment_method': payment_method, 'payment_status': payment_status }) 
    elif request.method == "GET": 
        # Razorpay ઓનલાઈન પેમેન્ટ પછી રિડાયરેક્ટ કરવા માટે 
        payment_id = request.GET.get('payment_id') 
        order_id = request.GET.get('order_id') 

        return render(request, 'booking_success.html', { 'payment_id': payment_id, 'payment_status': 'Paid' })
     # જો કઈ ન હોય તો બુકિંગ પેજ પર પાછા મોકલવું   
    return redirect("booking_success.html")

@login_required(login_url='user_login')
def book_parcel(request):

    if request.method == "POST":

        sender_name = request.POST.get("sender_name", "").strip()
        receiver_name = request.POST.get("receiver_name", "").strip()
        mobile_number = request.POST.get("mobile_number", "").strip()
        pickup_address = request.POST.get("pickup_address", "").strip()
        delivery_address = request.POST.get("delivery_address", "").strip()
        parcel_type = request.POST.get("parcel_type", "").strip()
        payment_method = request.POST.get("payment_method", "razorpay").lower()

        # ==================================================
        # BASIC VALIDATION
        # ==================================================

        if not sender_name or not receiver_name:
            messages.error(request, "Sender and receiver name are required.")
            return redirect("book_parcel")

        if not mobile_number or len(mobile_number) != 10 or not mobile_number.isdigit():
            messages.error(request, "Please enter a valid 10-digit mobile number.")
            return redirect("book_parcel")

        if not pickup_address or not delivery_address:
            messages.error(request, "Pickup and delivery address are required.")
            return redirect("book_parcel")

        if not parcel_type:
            messages.error(request, "Please select parcel type.")
            return redirect("book_parcel")

        # ==================================================
        # WEIGHT
        # ==================================================

        try:
            weight = float(request.POST.get("parcel_weight", 0))
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid parcel weight.")
            return redirect("book_parcel")

        if weight <= 0:
            messages.error(request, "Parcel weight must be greater than 0.")
            return redirect("book_parcel")

        # ==================================================
        # PARCEL RATES
        # ==================================================

        rates = {
            "Document": 30,
            "Electronics (Mobile, Laptop, Gadgets)": 120,
            "Clothes": 50,
            "Food Items": 80,
            "Books": 40,
            "Medicines": 70,
            "Fragile Items (Glass, Ceramic)": 150,
            "Furniture": 200,
            "Jewellery": 300,
            "Industrial Equipment": 250,
            "Gifts": 60,
            "Other": 100,
        }

        rate = rates.get(parcel_type)

        if rate is None:
            messages.error(request, "Invalid parcel type selected.")
            return redirect("book_parcel")

        # ==================================================
        # PRICE
        # ==================================================

        price = round(rate * weight, 2)

        if price <= 0:
            messages.error(request, "Invalid parcel price.")
            return redirect("book_parcel")

        # ==================================================
        # PAYMENT METHOD VALIDATION
        # ==================================================

        if payment_method not in ["razorpay", "cod"]:
            messages.error(request, "Please select a valid payment method.")
            return redirect("book_parcel")

        # ==================================================
        # SAVE PENDING BOOKING IN SESSION
        # ==================================================

        pending_booking = {
            "sender_name": sender_name,
            "receiver_name": receiver_name,
            "mobile_number": mobile_number,
            "parcel_weight": weight,
            "pickup_address": pickup_address,
            "delivery_address": delivery_address,
            "parcel_type": parcel_type,
            "price": price,
            "payment_method": payment_method,
        }

        request.session["pending_booking"] = pending_booking

        request.session.modified = True

        # ==================================================
        # CASH ON DELIVERY
        # ==================================================

        if payment_method == "cod":

            # COD = payment pending
            request.session["pending_booking"]["payment_status"] = "Pending"

            request.session.modified = True

            return redirect("payment_success")

        # ==================================================
        # RAZORPAY
        # ==================================================

        if payment_method == "razorpay":

            try:

                amount = int(round(price * 100))

                razorpay_order = client.order.create({
                    "amount": amount,
                    "currency": "INR",
                    "payment_capture": 1,
                })

            except Exception as e:

                messages.error(
                    request,
                    f"Unable to create Razorpay order: {str(e)}"
                )

                return redirect("book_parcel")

            # Save Razorpay order ID in session
            request.session["razorpay_order_id"] = razorpay_order["id"]

            request.session.modified = True

            return render(
                request,
                "payment.html",
                {
                    "order_id": razorpay_order["id"],
                    "amount": amount,
                    "price": price,
                    "razorpay_key": settings.RAZORPAY_KEY_ID,

                    # Extra data for payment page
                    "sender_name": sender_name,
                    "receiver_name": receiver_name,
                    "parcel_type": parcel_type,
                    "payment_method": payment_method,
                }
            )

    # ==================================================
    # GET REQUEST
    # ==================================================

    return render(request, "book_parcel.html")

@login_required(login_url='user_login')
def track_parcel(request):
    parcel = None

    if request.method == "POST":
        tracking_id = request.POST.get("tracking_id")

        try:
            parcel = Book_parcel.objects.get(tracking_id=tracking_id)
        except Book_parcel.DoesNotExist:
            messages.error(request, "❌ Invalid Tracking ID! Please enter a valid Tracking ID.")

    return render(request, "track_parcel.html", {
        "parcel": parcel
    })


def track_detail(request, tracking_id):

    parcel = get_object_or_404(
        Book_parcel,
        tracking_id=tracking_id
    )

    return render(
        request,
        'track_detail.html',
        {
            'parcel': parcel
        }
    )

@login_required(login_url='user_login')
def contact(request):
    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        date = request.POST.get('date')
        message = request.POST.get('message')
        
        obj = Contact(name=name,email=email,mobile=mobile,date=date,message=message)
        obj.save()
        messages.success(request, "Your message has been sent successfully!")
        return redirect("home")
    return render(request, "contact.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "user_login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect("user_login")

    return render(request, "register.html")

@login_required(login_url='user_login')
def profile(request):

    # ==============================
    # TOTAL PARCELS
    # ==============================

    total_parcels = Book_parcel.objects.count()


    # ==============================
    # DELIVERED PARCELS
    # ==============================

    delivered = Book_parcel.objects.filter(
        status="Delivered"
    ).count()


    # ==============================
    # IN TRANSIT
    # ==============================
    # Delivered અને Cancelled સિવાયના
    # બધા parcels currently active/in-transit ગણાશે.

    pending = Book_parcel.objects.exclude(
        status__in=["Delivered", "Cancelled"]
    ).count()


    # ==============================
    # CANCELLED
    # ==============================

    cancelled = Book_parcel.objects.filter(
        status="Cancelled"
    ).count()


    # ==============================
    # TOTAL REVENUE
    # ==============================

    revenue = Book_parcel.objects.aggregate(
        total=Sum("price")
    )["total"] or 0


    # ==============================
    # CONTEXT
    # ==============================

    context = {
        "total_parcels": total_parcels,
        "delivered": delivered,
        "pending": pending,
        "cancelled": cancelled,
        "revenue": revenue,
    }


    # IMPORTANT:
    # context અહીં render માં આપવું જરૂરી છે.

    return render(request,"profile.html",context)



def create_payment(request):

    if request.method != "POST":
        return redirect("book_parcel")

    # =====================================================
    # GET FORM DATA
    # =====================================================

    sender_name = request.POST.get("sender_name", "").strip()
    receiver_name = request.POST.get("receiver_name", "").strip()
    mobile_number = request.POST.get("mobile_number", "").strip()
    parcel_weight = request.POST.get("parcel_weight", "").strip()
    pickup_address = request.POST.get("pickup_address", "").strip()
    delivery_address = request.POST.get("delivery_address", "").strip()
    parcel_type = request.POST.get("parcel_type", "").strip()
    payment_method = request.POST.get("payment_method", "razorpay").lower()

    # =====================================================
    # VALIDATION
    # =====================================================

    if not parcel_weight or not parcel_type:
        messages.error(request, "Please enter parcel weight and parcel type.")
        return redirect("book_parcel")

    # =====================================================
    # RATES
    # =====================================================

    rates = {
        "Document": 30,
        "Electronics (Mobile, Laptop, Gadgets)": 120,
        "Clothes": 50,
        "Food Items": 80,
        "Books": 40,
        "Medicines": 70,
        "Fragile Items (Glass, Ceramic)": 150,
        "Furniture": 400,
        "Jewellery": 500,
        "Industrial Equipment": 250,
        "Gifts": 60,
        "Other": 100,
    }

    if parcel_type not in rates:
        messages.error(request, "Invalid parcel type.")
        return redirect("book_parcel")

    # =====================================================
    # CALCULATE PRICE
    # =====================================================

    try:
        weight = float(parcel_weight)
    except (TypeError, ValueError):

        messages.error(request, "Invalid parcel weight.")
        return redirect("book_parcel")

    if weight <= 0:
        messages.error(request, "Parcel weight must be greater than 0.")
        return redirect("book_parcel")

    price = weight * rates[parcel_type]

    # =====================================================
    # SAVE PENDING BOOKING
    # =====================================================

    request.session["pending_booking"] = {
        "sender_name": sender_name,
        "receiver_name": receiver_name,
        "mobile_number": mobile_number,
        "parcel_weight": parcel_weight,
        "pickup_address": pickup_address,
        "delivery_address": delivery_address,
        "parcel_type": parcel_type,
        "price": price,
        "payment_method": payment_method,
    }

    request.session.modified = True

    # =====================================================
    # COD
    # =====================================================

    if payment_method == "cod":

        return redirect("cod_payment")

    # =====================================================
    # RAZORPAY
    # =====================================================

    amount = int(round(price * 100))

    print("\n========================================")
    print("CREATING RAZORPAY ORDER")
    print("PRICE:", price)
    print("AMOUNT PAISA:", amount)
    print("KEY ID:", settings.RAZORPAY_KEY_ID)
    print("========================================")

    try:

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": f"parcel_{request.user.id}_{int(price)}",
        })

        print("\n========================================")
        print("✅ RAZORPAY ORDER CREATED")
        print("ORDER ID:", razorpay_order["id"])
        print("========================================")

    except Exception as e:

        print("\n========================================")
        print("❌ RAZORPAY ORDER CREATION FAILED")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        print("========================================")

        messages.error(
            request,
            f"Razorpay error: {str(e)}"
        )

        return redirect("book_parcel")

    request.session["razorpay_order_id"] = razorpay_order["id"]
    request.session.modified = True

    # =====================================================
    # PAYMENT PAGE
    # =====================================================

    context = {
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "price": price,
        "payment_method": payment_method,

        "sender_name": sender_name,
        "receiver_name": receiver_name,
        "mobile_number": mobile_number,
        "parcel_weight": parcel_weight,
        "pickup_address": pickup_address,
        "delivery_address": delivery_address,
        "parcel_type": parcel_type,
    }

    return render(
        request,
        "payment.html",
        context
    )

def payment_success(request):

    # =====================================================
    # GET RAZORPAY RESPONSE
    # =====================================================

    payment_id = request.GET.get("razorpay_payment_id")
    order_id = request.GET.get("razorpay_order_id")
    signature = request.GET.get("razorpay_signature")

    # Old parameter support
    if not payment_id:
        payment_id = request.GET.get("payment_id")

    if not order_id:
        order_id = request.GET.get("order_id")

    if not signature:
        signature = request.GET.get("signature")

    print("\n========================================")
    print("RAZORPAY PAYMENT ID :", payment_id)
    print("RAZORPAY ORDER ID   :", order_id)
    print("RAZORPAY SIGNATURE  :", signature)
    print("========================================\n")

    # =====================================================
    # CHECK RAZORPAY DATA
    # =====================================================

    if not payment_id or not order_id or not signature:

        messages.error(
            request,
            "Payment verification details are missing."
        )

        return redirect("book_parcel")

    # =====================================================
    # CREATE RAZORPAY CLIENT
    # =====================================================

    try:

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

    except Exception as e:

        print("RAZORPAY CLIENT ERROR:", str(e))

        messages.error(
            request,
            "Razorpay configuration error."
        )

        return redirect("book_parcel")

    # =====================================================
    # VERIFY PAYMENT SIGNATURE
    # =====================================================

    try:

        client.utility.verify_payment_signature({

            "razorpay_payment_id": payment_id,

            "razorpay_order_id": order_id,

            "razorpay_signature": signature

        })

        print("========================================")
        print("RAZORPAY VERIFICATION SUCCESS")
        print("========================================")

    except razorpay.errors.SignatureVerificationError as e:

        print("========================================")
        print("RAZORPAY SIGNATURE VERIFICATION FAILED")
        print(str(e))
        print("========================================")

        messages.error(
            request,
            "Payment verification failed. Please contact ParcelPath support."
        )

        return redirect("book_parcel")

    except Exception as e:

        print("========================================")
        print("RAZORPAY VERIFICATION ERROR")
        print(str(e))
        print("========================================")

        messages.error(
            request,
            "Payment verification failed."
        )

        return redirect("book_parcel")

    # =====================================================
    # GET PENDING BOOKING
    # =====================================================

    booking = request.session.get("pending_booking")

    print("PENDING BOOKING:", booking)

    if not booking:

        messages.error(
            request,
            "Booking information was not found."
        )

        return redirect("book_parcel")

    # =====================================================
    # GET PRICE
    # =====================================================

    try:

        price = float(
            booking.get("price", 0)
        )

    except (TypeError, ValueError):

        price = 0

    if price <= 0:

        messages.error(
            request,
            "Invalid booking amount."
        )

        return redirect("book_parcel")

    # =====================================================
    # CREATE TRACKING ID
    # =====================================================

    tracking_id = generate_tracking_id()

    # =====================================================
    # CREATE PARCEL
    # =====================================================

    try:

        parcel = Book_parcel.objects.create(

            sender_name=booking.get(
                "sender_name",
                ""
            ),

            receiver_name=booking.get(
                "receiver_name",
                ""
            ),

            mobile_number=booking.get(
                "mobile_number",
                ""
            ),

            parcel_weight=booking.get(
                "parcel_weight",
                ""
            ),

            pickup_address=booking.get(
                "pickup_address",
                ""
            ),

            delivery_address=booking.get(
                "delivery_address",
                ""
            ),

            parcel_type=booking.get(
                "parcel_type",
                ""
            ),

            price=price,

            tracking_id=tracking_id,

            status="Parcel Booked"

        )

        print("========================================")
        print("BOOKING CREATED SUCCESSFULLY")
        print("TRACKING ID:", parcel.tracking_id)
        print("========================================")

    except Exception as e:

        print("========================================")
        print("BOOKING SAVE ERROR:", str(e))
        print("========================================")

        messages.error(
            request,
            f"Booking could not be saved: {str(e)}"
        )

        return redirect("book_parcel")

    # =====================================================
    # QR CODE
    # =====================================================

    # IMPORTANT:
    # QR code ને હાલમાં optional રાખ્યો છે.
    # પહેલા payment + booking success perfectly ચાલવા દઈએ.

    try:

        if hasattr(parcel, "qr_code"):

            track_url = request.build_absolute_uri(
                reverse(
                    "track_detail",
                    args=[parcel.tracking_id]
                )
            )

            qr = qrcode.make(track_url)

            buffer = BytesIO()

            qr.save(
                buffer,
                format="PNG"
            )

            buffer.seek(0)

            parcel.qr_code.save(
                f"{parcel.tracking_id}.png",
                File(buffer),
                save=True
            )

            print("QR CODE CREATED")

    except Exception as e:

        print("QR CODE ERROR:", str(e))

    # =====================================================
    # CLEAR PENDING BOOKING
    # =====================================================

    request.session.pop(
        "pending_booking",
        None
    )

    request.session.pop(
        "razorpay_order_id",
        None
    )

    request.session.modified = True

    # =====================================================
    # BOOKING SUCCESS PAGE
    # =====================================================

    return render(
        request,
        "booking_success.html",
        {
            "parcel": parcel,

            "tracking_id": parcel.tracking_id,

            "payment_id": payment_id,

            "order_id": order_id,

            "payment_status": "Paid",

            "payment_method": "Online Payment",

            "price": parcel.price,
        }
    )

@login_required(login_url="user_login")
def cod_payment(request):

    booking = request.session.get("pending_booking")

    # =====================================================
    # CHECK BOOKING
    # =====================================================

    if not booking:
        messages.error(
            request,
            "Booking details not found. Please complete parcel booking first."
        )
        return redirect("book_parcel")

    # =====================================================
    # GET - SHOW COD PAGE
    # =====================================================

    if request.method == "GET":

        try:
            price = float(booking.get("price", 0))
        except (TypeError, ValueError):
            price = 0

        return render(
            request,
            "cod_payment.html",
            {
                "sender_name": booking.get("sender_name", ""),
                "receiver_name": booking.get("receiver_name", ""),
                "mobile_number": booking.get("mobile_number", ""),
                "parcel_weight": booking.get("parcel_weight", ""),
                "pickup_address": booking.get("pickup_address", ""),
                "delivery_address": booking.get("delivery_address", ""),
                "parcel_type": booking.get("parcel_type", ""),
                "price": price,
            }
        )

    # =====================================================
    # POST - CONFIRM COD
    # =====================================================

    if request.method == "POST":

        try:
            price = float(
                booking.get("price", 0)
            )
        except (TypeError, ValueError):

            price = 0

        if price <= 0:
            messages.error(
                request,
                "Invalid parcel price."
            )
            return redirect("book_parcel")

        # =================================================
        # GENERATE TRACKING ID
        # =================================================

        tracking_id = generate_tracking_id()

        # =================================================
        # CREATE PARCEL
        # =================================================

        try:

            parcel = Book_parcel.objects.create(

                sender_name=booking.get(
                    "sender_name",
                    ""
                ),

                receiver_name=booking.get(
                    "receiver_name",
                    ""
                ),

                mobile_number=booking.get(
                    "mobile_number",
                    ""
                ),

                parcel_weight=booking.get(
                    "parcel_weight",
                    ""
                ),

                pickup_address=booking.get(
                    "pickup_address",
                    ""
                ),

                delivery_address=booking.get(
                    "delivery_address",
                    ""
                ),

                parcel_type=booking.get(
                    "parcel_type",
                    ""
                ),

                price=price,

                tracking_id=tracking_id,

                status="COD - Order Confirmed",
            )

        except Exception as e:

            print(
                "COD BOOKING SAVE ERROR:",
                e
            )

            messages.error(
                request,
                f"Booking could not be saved: {str(e)}"
            )

            return redirect("book_parcel")

        # =================================================
        # QR CODE
        # =================================================

        try:

            track_url = request.build_absolute_uri(
                reverse(
                    "track_detail",
                    args=[parcel.tracking_id]
                )
            )

            qr = qrcode.make(track_url)

            buffer = BytesIO()

            qr.save(
                buffer,
                format="PNG"
            )

            buffer.seek(0)

            # IMPORTANT:
            # Only use qr_code if model has this field

            if hasattr(parcel, "qr_code"):

                parcel.qr_code.save(
                    f"{parcel.tracking_id}.png",
                    File(buffer),
                    save=True
                )

        except Exception as e:

            print(
                "COD QR ERROR:",
                e
            )

        # =================================================
        # CLEAR SESSION
        # =================================================

        request.session.pop(
            "pending_booking",
            None
        )

        request.session.pop(
            "razorpay_order_id",
            None
        )

        request.session.modified = True

        # =================================================
        # SUCCESS PAGE
        # =================================================

        return render(
            request,
            "booking_success.html",
            {
                "parcel": parcel,

                "tracking_id": parcel.tracking_id,

                "payment_method": "Cash on Delivery",

                "payment_status": "Pending - Pay on Delivery",

                "payment_id": "",

                "order_id": "",

                "price": parcel.price,
            }
        )

    return redirect("cod_payment")





def download_payment_receipt(request, tracking_id):

    # Get parcel using tracking ID
    parcel = get_object_or_404(
        Book_parcel,
        tracking_id=tracking_id
    )

    # =====================================================
    # PAYMENT METHOD
    # =====================================================

    payment_method = str(
        getattr(parcel, "payment_method", "")
    ).upper()

    # COD receipt is not available before delivery
    if payment_method == "COD":
        return HttpResponse(
            "COD payment receipt is not available before delivery.",
            status=403
        )

    # =====================================================
    # PAYMENT INFORMATION
    # =====================================================

    if payment_method == "ONLINE":
        payment_method_display = "Online Payment"
    else:
        payment_method_display = "Online Payment"

    payment_status = str(
        getattr(parcel, "payment_status", "Pending")
    )

    if payment_status.lower() == "paid":
        payment_status_display = "PAID"
    else:
        payment_status_display = payment_status.upper()

    # =====================================================
    # CREATE PDF RESPONSE
    # =====================================================

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename='
        f'"ParcelPath_Payment_Receipt_{parcel.tracking_id}.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=A4
    )

    width, height = A4

    # =====================================================
    # HEADER
    # =====================================================

    pdf.setFillColor(
        colors.HexColor("#0d6efd")
    )

    pdf.rect(
        0,
        height - 75,
        width,
        75,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(colors.white)

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawString(
        40,
        height - 45,
        "PARCELPATH"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawRightString(
        width - 40,
        height - 45,
        "PAYMENT RECEIPT"
    )

    # =====================================================
    # PAYMENT SUCCESS MESSAGE
    # =====================================================

    y = height - 115

    pdf.setFillColor(
        colors.HexColor("#198754")
    )

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        40,
        y,
        "✓ PAYMENT SUCCESSFUL"
    )

    y -= 35

    # =====================================================
    # PAYMENT DETAILS
    # =====================================================

    pdf.setFillColor(colors.black)

    receipt_data = [

        (
            "Tracking ID",
            parcel.tracking_id
        ),

        (
            "Customer Name",
            parcel.sender_name or "N/A"
        ),

        (
            "Mobile",
            parcel.mobile_number or "N/A"
        ),

        (
            "Payment Method",
            payment_method_display
        ),

        (
            "Payment Status",
            payment_status_display
        ),

        (
            "Amount Paid",
            f"Rs. {parcel.price:.2f}"
        ),

        (
            "Payment ID",
            getattr(parcel, "payment_id", None) or "N/A"
        ),

        (
            "Order ID",
            getattr(parcel, "order_id", None) or "N/A"
        ),
    ]

    for label, value in receipt_data:

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.drawString(
            50,
            y,
            f"{label}:"
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawString(
            180,
            y,
            str(value)[:70]
        )

        y -= 28

    # =====================================================
    # DIVIDER
    # =====================================================

    pdf.setStrokeColor(
        colors.lightgrey
    )

    pdf.line(
        40,
        y,
        width - 40,
        y
    )

    y -= 35

    # =====================================================
    # BOOKING DETAILS
    # =====================================================

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        40,
        y,
        "Booking Details"
    )

    y -= 28

    booking_data = [

        (
            "Receiver Name",
            parcel.receiver_name or "N/A"
        ),

        (
            "Receiver Address",
            parcel.delivery_address or "N/A"
        ),

        (
            "Parcel Type",
            parcel.parcel_type or "N/A"
        ),

        (
            "Weight",
            f"{parcel.parcel_weight or '0'} kg"
        ),

        (
            "Booking Status",
            parcel.status or "Parcel Booked"
        ),
    ]

    for label, value in booking_data:

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.drawString(
            50,
            y,
            f"{label}:"
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawString(
            180,
            y,
            str(value)[:70]
        )

        y -= 25

    # =====================================================
    # CUSTOMER / SENDER ADDRESS
    # =====================================================

    y -= 5

    pdf.setStrokeColor(
        colors.lightgrey
    )

    pdf.line(
        40,
        y,
        width - 40,
        y
    )

    y -= 30

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        40,
        y,
        "Pickup Details"
    )

    y -= 25

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        50,
        y,
        "Pickup Address:"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        180,
        y,
        str(parcel.pickup_address or "N/A")[:70]
    )

    y -= 30

    # =====================================================
    # FOOTER
    # =====================================================

    pdf.setFillColor(
        colors.HexColor("#0d6efd")
    )

    pdf.rect(
        0,
        0,
        width,
        45,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(colors.white)

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawCentredString(
        width / 2,
        18,
        "Thank you for using ParcelPath Logistics"
    )

    # =====================================================
    # SAVE PDF
    # =====================================================

    pdf.save()

    return response