from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Achievement,
    StudentProfile,
    Activity,
    Registration,
    Stall,
    StallBooking
)


# ==============================
# 🔹 Custom User Admin
# ==============================
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'is_staff',
        'is_superuser',
        'date_joined'
    )
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ==============================
# 🔹 Achievement Admin
# ==============================
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'category',
        'date_achieved',
        'is_verified'
    )

    list_filter = (
        'category',
        'is_verified',
        'date_achieved'
    )

    search_fields = (
        'title',
        'user__username',
        'user__email'
    )

    ordering = ('-date_achieved',)

    actions = ['mark_as_verified']

    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)

    mark_as_verified.short_description = "Mark selected achievements as Verified"


# ==============================
# 🔹 Student Profile Admin
# ==============================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone')
    search_fields = ('user__username', 'user__email', 'department')
    ordering = ('user',)


# ==============================
# 🔹 Activity Admin
# ==============================
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'date',
        'total_seats',
        'filled_seats'
    )

    list_filter = ('category', 'date')
    search_fields = ('title', 'category')
    ordering = ('-date',)


# ==============================
# 🔹 Registration Admin (FIXED)
# ==============================
@admin.register(Registration)

class RegistrationAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'activity',
        'status',
        'created_at'
    )

    list_editable = ['status']

    list_filter = ('status',)

    search_fields = (
        'user__username',
        'activity__title'
    )

    ordering = ('-created_at',)

    exclude = ('qr_code',)  # optional

    # 🔥 AUTO SEAT MANAGEMENT
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Registration.objects.get(pk=obj.pk)

            # ✅ APPROVED
            if old_obj.status != 'approved' and obj.status == 'approved':
                if obj.activity.filled_seats < obj.activity.total_seats:
                    obj.activity.filled_seats += 1
                    obj.activity.save()

                    # 📧 SEND EMAIL
                    send_mail(
                        'Registration Approved 🎉',
                        f'Your registration for {obj.activity.title} is approved.',
                        settings.EMAIL_HOST_USER,
                        [obj.user.email],
                        fail_silently=True,
                    )

            # ❌ REMOVE APPROVAL
            if old_obj.status == 'approved' and obj.status != 'approved':
                if obj.activity.filled_seats > 0:
                    obj.activity.filled_seats -= 1
                    obj.activity.save()

        super().save_model(request, obj, form, change)


# ==============================
# 🔹 Stall Admin
# ==============================
@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'location',
        'total_slots',
        'booked_slots'
    )

    search_fields = ('name', 'location')


# ==============================
# 🔹 Stall Booking Admin
# ==============================
@admin.register(StallBooking)
class StallBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'stall', 'booked_at')
    search_fields = ('user__username', 'stall__name')