from django.db import models
import uuid


def generate_tracking_id():
    return "PP" + uuid.uuid4().hex[:8].upper()


# ==========================================
# CONTACT MODEL
# ==========================================
class Contact(models.Model):

    name = models.CharField(max_length=50)

    email = models.EmailField()

    mobile = models.CharField(max_length=10)

    date = models.DateField()

    message = models.TextField()

    def __str__(self):
        return self.name


# ==========================================
# BOOK PARCEL MODEL
# ==========================================
class Book_parcel(models.Model):

    # ==========================================
    # SENDER / RECEIVER DETAILS
    # ==========================================

    sender_name = models.CharField(
        max_length=50
    )

    receiver_name = models.CharField(
        max_length=50
    )

    mobile_number = models.CharField(
        max_length=10
    )

    # ==========================================
    # PARCEL DETAILS
    # ==========================================

    parcel_weight = models.CharField(
        max_length=4
    )

    pickup_address = models.CharField(
        max_length=50
    )

    delivery_address = models.CharField(
        max_length=50
    )

    parcel_type = models.CharField(
        max_length=10
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # ==========================================
    # TRACKING
    # ==========================================

    tracking_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        default="Parcel Booked"
    )

    # ==========================================
    # PAYMENT METHOD
    # ==========================================

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("ONLINE", "Online Payment"),
            ("COD", "Cash on Delivery"),
        ],
        default="ONLINE"
    )

    # ==========================================
    # PAYMENT STATUS
    # ==========================================

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("Paid", "Paid"),
            ("Pending", "Pending"),
        ],
        default="Pending"
    )

    # ==========================================
    # RAZORPAY PAYMENT ID
    # ==========================================

    payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # ==========================================
    # RAZORPAY ORDER ID
    # ==========================================

    order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # ==========================================
    # QR CODE
    # ==========================================

    qr_code = models.ImageField(
        upload_to="qr_codes/",
        blank=True,
        null=True
    )

    # ==========================================
    # SAVE METHOD
    # ==========================================

    def save(self, *args, **kwargs):

        if not self.tracking_id:
            self.tracking_id = generate_tracking_id()

        super().save(*args, **kwargs)

    # ==========================================
    # STRING REPRESENTATION
    # ==========================================

    def __str__(self):
        return self.tracking_id