from django.db import models
import uuid

def generate_tracking_id():
    return "PP" + uuid.uuid4().hex[:8].upper()

# Create your models here.
class Book_parcel(models.Model):
                
    sender_name = models.CharField(max_length=50)
    receiver_name = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=10)
    parcel_weight = models.CharField(max_length=4)
    pickup_address = models.CharField(max_length=50)
    delivery_address = models.CharField(max_length=50)
    parcel_type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tracking_id = models.CharField(
            max_length=20,
            unique=True,
            default=generate_tracking_id
        )
    status = models.CharField(max_length=50,default="Parcel Booked")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = "PP" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

class Contact(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    date = models.DateTimeField()
    message = models.TextField()


    def __str__(self):
        return self.name


class Book_parcel(models.Model):
    sender_name = models.CharField(max_length=50)
    receiver_name = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=10)
    parcel_weight = models.CharField(max_length=4)
    pickup_address = models.CharField(max_length=50)
    delivery_address = models.CharField(max_length=50)
    parcel_type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tracking_id = models.CharField(
        max_length=20,
        unique=True,
        default=generate_tracking_id
    )
    status = models.CharField(
        max_length=50,
        default="Parcel Booked"
    )

    qr_code = models.ImageField(
        upload_to="qr_codes/",
        blank=True,
        null=True
    )

    # PAYMENT FIELDS
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("razorpay", "Razorpay"),
            ("cod", "COD"),
        ],
        default="cod"
    )

    payment_status = models.CharField(
        max_length=20,
        default="pending"
    )

    payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = "PP" + uuid.uuid4().hex[:8].upper()

        super().save(*args, **kwargs)