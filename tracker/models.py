from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import datetime
import qrcode
from io import BytesIO
from django.core.files import File


# =========================
# 🔹 STUDENT PROFILE
# =========================
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, default="Not Assigned")

    # 🔐 UNIQUE PHONE FOR OTP LOGIN
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


# =========================
# 🔹 AUTO CREATE PROFILE
# =========================
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()


# =========================
# 🔹 ACHIEVEMENTS
# =========================
class Achievement(models.Model):

    CATEGORY_CHOICES = [
        ('Hackathon', 'Hackathon'),
        ('Workshop', 'Workshop'),
        ('Sports', 'Sports'),
        ('Certification', 'Certification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    date_achieved = models.DateField()
    description = models.TextField()

    proof = models.FileField(upload_to='proofs/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.date_achieved > datetime.date.today():
            raise ValidationError("Date cannot be future.")

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# =========================
# 🔹 UPDATED ACTIVITY (NEW)
# =========================
class Activity(models.Model):

    CATEGORY_CHOICES = [
        ('Cultural', 'Cultural'),
        ('Sports', 'Sports'),
        ('Technical', 'Technical'),
        ('NCC & Outreach', 'NCC & Outreach'),
        ('College Fest', 'College Fest'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()

    total_seats = models.IntegerField()
    filled_seats = models.IntegerField(default=0)

    date = models.DateField()

    def seats_left(self):
        return self.total_seats - self.filled_seats

    def is_full(self):
        return self.filled_seats >= self.total_seats

    # 🔥 ADD THIS (FIX)
    def is_available(self):
        return self.filled_seats < self.total_seats

    def __str__(self):
        return self.title

# =========================
# 🔹 UPDATED REGISTRATION (NEW)
# =========================
class Registration(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlist', 'Waitlist'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'activity']

    def __str__(self):
        return f"{self.user.username} -> {self.activity.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 🔥 Generate QR only if not exists
        if not self.qr_code:
            qr_data = f"{self.user.username}-{self.activity.title}-{self.id}"

            qr = qrcode.make(qr_data)

            buffer = BytesIO()
            qr.save(buffer)

            filename = f'qr_{self.id}.png'
            self.qr_code.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)


# =========================
# 🔹 STALL
# =========================
class Stall(models.Model):
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=50)
    price = models.IntegerField()
    location = models.CharField(max_length=200)
    rating = models.FloatField(default=4.0)

    total_slots = models.PositiveIntegerField(default=1)
    booked_slots = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True)

    def is_available(self):
        return self.booked_slots < self.total_slots

    def __str__(self):
        return self.name


# =========================
# 🔹 STALL BOOKING
# =========================
class StallBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stall = models.ForeignKey(Stall, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stall')

    def __str__(self):
        return f"{self.user.username} -> {self.stall.name}"
    
def seats_left(self):
    return self.total_seats - self.filled_seats

