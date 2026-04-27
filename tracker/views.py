# =========================
# 🔹 DJANGO CORE
# =========================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Achievement, Registration


# =========================
# 🔹 MODELS
# =========================
from .models import (
    Achievement,
    StudentProfile,
    Activity,
    Registration,
    Stall,
    StallBooking
)

# =========================
# 🔹 FORMS
# =========================
from .forms import RegisterForm, LoginForm

# =========================
# 🔹 UTILITIES
# =========================
import random
import time

# =========================
# 🔹 EMAIL (OTP)
# =========================
from django.core.mail import send_mail
from django.conf import settings
# =========================
# 🔹 LANDING PAGE
# =========================
def landing(request):
    return render(request, 'landing.html')


# =========================
# 🔹 LOGIN WITH OTP (EMAIL)
# =========================

def home(request):
    form = LoginForm()
    otp_sent = request.session.get("otp_sent", False)

    if request.method == "POST":
        step = request.POST.get("step")

        # ===============================
        # 🔹 STEP 1: VERIFY + SEND OTP
        # ===============================
        if step == "verify":
            form = LoginForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                phone = request.POST.get("phone")

                # SAVE TEMP DATA (IMPORTANT FIX)
                request.session['temp_username'] = username
                request.session['temp_password'] = password
                request.session['temp_phone'] = phone

                # PHONE VALIDATION
                if not phone or not phone.isdigit() or len(phone) != 10:
                    messages.error(request, "Enter valid 10-digit phone number")
                    return redirect('home')

                user = authenticate(request, username=username, password=password)

                if user:
                    profile, created = StudentProfile.objects.get_or_create(user=user)

                    if created:
                        profile.phone = phone
                        profile.save()

                    if profile.phone != phone:
                        messages.error(request, "Phone number does not match")
                        return redirect('home')

                    # OTP cooldown
                    last_sent = request.session.get("otp_last_sent", 0)
                    if time.time() - last_sent < 30:
                        messages.warning(request, "Wait 30 seconds before requesting OTP")
                        return redirect('home')

                    # GENERATE OTP
                    otp = str(random.randint(100000, 999999))
                    print("🔥 OTP:", otp)

                    request.session['login_otp'] = otp
                    request.session['otp_time'] = time.time()
                    request.session['otp_last_sent'] = time.time()
                    request.session['otp_attempts'] = 0
                    request.session['user_id'] = user.id
                    request.session['otp_sent'] = True

                    send_mail(
                        'Login OTP - KL University',
                        f'Your login OTP is {otp}',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )

                    messages.success(request, "OTP sent successfully")
                    return redirect('home')

                else:
                    messages.error(request, "Invalid Student ID or Password")

            else:
                messages.error(request, "Invalid CAPTCHA")

        # ===============================
        # 🔹 STEP 2: VERIFY OTP
        # ===============================
        elif step == "login":
            entered_otp = request.POST.get("otp")

            session_otp = request.session.get("login_otp")
            otp_time = request.session.get("otp_time")
            user_id = request.session.get("user_id")

            if not session_otp or not otp_time or not user_id:
                messages.error(request, "Session expired. Please login again.")
                return redirect('home')

            if time.time() - otp_time > 60:
                messages.error(request, "OTP expired")
                request.session.pop("otp_sent", None)
                return redirect('home')

            attempts = request.session.get("otp_attempts", 0)
            if attempts >= 3:
                messages.error(request, "Too many attempts")
                request.session.pop("otp_sent", None)
                return redirect('home')

            if entered_otp != session_otp:
                request.session['otp_attempts'] = attempts + 1
                messages.error(request, "Invalid OTP")
                return redirect('home')

            # LOGIN SUCCESS
            user = User.objects.get(id=user_id)
            login(request, user)

            # CLEAR SESSION
            for key in [
                'login_otp','otp_time','otp_last_sent',
                'otp_attempts','user_id','otp_sent',
                'temp_username','temp_password','temp_phone'
            ]:
                request.session.pop(key, None)

            return redirect("student_dashboard")

    return render(request, "login.html", {
        "form": form,
        "otp_sent": otp_sent,
        "username": request.session.get("temp_username"),
        "password": request.session.get("temp_password"),
        "phone": request.session.get("temp_phone"),
    })# =========================
# 🔹 REGISTER → SEND OTP
# =========================
def register(request):
    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone = request.POST.get('phone')

            # 🔒 DUPLICATE CHECKS
            if User.objects.filter(username=username).exists():
                messages.error(request, "Student ID already exists. Please login.")
                return redirect('home')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists. Use another email.")
                return redirect('register')

            if StudentProfile.objects.filter(phone=phone).exists():
                messages.error(request, "Phone number already registered.")
                return redirect('register')

            # 🔐 GENERATE OTP
            otp = str(random.randint(100000, 999999))
            print("🔥 OTP GENERATED:", otp)
            print("📧 Sending to:", email)

            request.session['otp'] = otp
            request.session['otp_time'] = time.time()
            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password
            request.session['phone'] = phone

            # 📧 SEND EMAIL
            send_mail(
                'KL University OTP Verification',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email")
            return redirect('verify_otp')

        else:
            messages.error(request, "Invalid input or captcha")

    return render(request, 'register.html', {"form": form})


# =========================
# 🔹 VERIFY OTP → CREATE ACCOUNT
# =========================
def verify_otp(request):

    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        otp_time = request.session.get('otp_time')

        # ❌ SESSION EXPIRED
        if not session_otp:
            messages.error(request, "Session expired")
            return redirect('register')

        # ⏳ OTP EXPIRED
        if time.time() - otp_time > 60:
            messages.error(request, "OTP expired")
            return redirect('register')

        # ❌ WRONG OTP
        if entered_otp != session_otp:
            messages.error(request, "Invalid OTP")
            return redirect('verify_otp')

        # ✅ GET DATA
        username = request.session.get('username')
        email = request.session.get('email')
        password = request.session.get('password')
        phone = request.session.get('phone')

        # FINAL SAFETY
        if User.objects.filter(username=username).exists():
            messages.error(request, "Student ID already exists.")
            return redirect('home')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        # ✅ CREATE USER
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # ✅ CREATE PROFILE WITH PHONE
        StudentProfile.objects.create(
            user=user,
            phone=phone
        )

        # 🔥 CLEAR SESSION
        for key in ['otp', 'otp_time', 'username', 'email', 'password', 'phone']:
            request.session.pop(key, None)

        messages.success(request, "Account created successfully!")
        return redirect('home')

    return render(request, 'verify_otp.html')


# =========================
# 🔹 DASHBOARD
# =========================
import json
@login_required
def dashboard(request):
    user = request.user
    registrations = Registration.objects.filter(user=user)

    chart_data = {
        "approved": registrations.filter(status='approved').count(),
        "pending": registrations.filter(status='pending').count(),
        "waitlist": registrations.filter(status='waitlist').count(),
    }

    context = {
        'total_activities': Activity.objects.count(),
        'total_registrations': registrations.count(),
        'approved': chart_data["approved"],
        'pending': chart_data["pending"],
        'waitlist': chart_data["waitlist"],
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'student_dashboard.html', context)
# =========================
# 🔹 ADD ACHIEVEMENT
# =========================
@login_required(login_url="home")
def add_achievement(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        Achievement.objects.create(
            user=request.user,
            title=request.POST.get("title"),
            category=request.POST.get("category"),
            date_achieved=request.POST.get("date"),
            description=request.POST.get("description"),
            proof=request.FILES.get("proof")
        )

        messages.success(request, "Achievement added successfully!")
        return redirect("student_dashboard")

    return render(request, "add_achievement.html", {"profile": profile})


# =========================
# 🔹 DELETE ACHIEVEMENT
# =========================
@login_required(login_url="home")
def unregister_achievement(request, achievement_id):
    activity = get_object_or_404(Achievement, id=achievement_id, user=request.user)
    activity.delete()
    messages.warning(request, "Activity removed")
    return redirect("student_dashboard")


# =========================
# 🔹 VIEW ALL
# =========================
@login_required(login_url="home")
def view_all(request):
    activities = Achievement.objects.filter(user=request.user)
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    return render(request, "view_all.html", {
        "activities": activities,
        "profile": profile
    })


# =========================
# 🔹 PROFILE
# =========================
@login_required
def profile(request):
    profile = request.user.studentprofile

    if request.method == "POST":
        # update user
        request.user.email = request.POST.get("email")
        request.user.save()

        # update profile
        profile.department = request.POST.get("department")
        profile.phone = request.POST.get("phone")

        # image upload
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES.get("profile_pic")

        profile.save()

        messages.success(request, "Profile updated successfully")

    return render(request, "profile.html", {"profile": profile})


# =========================
# 🔹 LOGOUT
# =========================
def user_logout(request):
    logout(request)
    return redirect("home")


# =========================
# 🔹 ACTIVITIES
# =========================
@login_required(login_url="home")
def activities(request):
    acts = Activity.objects.all()

    category = request.GET.get('category')
    if category and category != "All":
        acts = acts.filter(category__iexact=category)

    return render(request, 'activities.html', {
        'activities': acts   # 🔥 THIS WAS MISSING
    })
import qrcode
from io import BytesIO
from django.core.files import File


@login_required
def register_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    # Already registered
    if Registration.objects.filter(user=request.user, activity=activity).exists():
        messages.warning(request, "Already registered")
        return redirect('activities')

    # 🔥 AUTO APPROVAL LOGIC
    if activity.filled_seats < activity.total_seats:
        status = 'approved'
        activity.filled_seats += 1
        activity.save()
    else:
        status = 'waitlist'

    reg = Registration.objects.create(
        user=request.user,
        activity=activity,
        status=status
    )

    # 🔥 QR GENERATION (only if approved)
    if status == 'approved':
        import qrcode
        from io import BytesIO
        from django.core.files import File

        qr_data = f"{request.user.username}-{activity.title}-{reg.id}"
        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer)
        filename = f'qr_{reg.id}.png'

        reg.qr_code.save(filename, File(buffer), save=True)

    if status == 'approved':
        messages.success(request, "Registered successfully (Approved)")
    else:
        messages.info(request, "Activity full → Added to waitlist")

    return redirect('my_registrations')
# =========================
# 🔹 STALLS
# =========================
@login_required(login_url="home")
def stalls(request):
    return render(request, "stalls.html", {"stalls": Stall.objects.all()})


@login_required(login_url="home")
def book_stall(request, stall_id):
    stall = get_object_or_404(Stall, id=stall_id)

    if stall.booked_slots < stall.total_slots:
        StallBooking.objects.create(user=request.user, stall=stall)
        stall.booked_slots += 1
        stall.save()
        messages.success(request, "Stall booked successfully!")
    else:
        messages.error(request, "No slots available")

    return redirect("stalls")

# =========================
# 🔹 STALLS
# =========================
@login_required(login_url="home")
def book_stall(request, stall_id):
    ...
    return redirect("stalls")


# =========================
# 🔹 UNREGISTER ACTIVITY (ADD HERE)
# =========================
@login_required(login_url="home")
def unregister_activity(request, reg_id):
    reg = get_object_or_404(Registration, id=reg_id, user=request.user)
    activity = reg.activity

    if reg.status == "approved":
        activity.filled_seats -= 1
        activity.save()

        promote_waitlist(activity)

    reg.delete()

    messages.success(request, "Unregistered successfully")
    return redirect("my_registrations")


# =========================
# 🔹 MY REGISTRATIONS VIEW (ADD HERE)
# =========================
@login_required(login_url="home")
def my_registrations(request):
    regs = Registration.objects.filter(user=request.user)
    return render(request, "my_registrations.html", {"registrations": regs})

# =========================
# 🔹 WAITLIST PROMOTION
# =========================
def promote_waitlist(activity):
    next_user = Registration.objects.filter(
        activity=activity,
        status='waitlist'
    ).first()

    if next_user:
        next_user.status = 'approved'
        next_user.save()

        activity.filled_seats += 1
        activity.save()

# =========================
# 🔹 LIVE SEAT API
# =========================
from django.http import JsonResponse

def activity_seats(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    return JsonResponse({
        "filled": activity.filled_seats,
        "total": activity.total_seats
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum

@staff_member_required
def admin_dashboard(request):
    total_activities = Activity.objects.count()
    total_users = User.objects.count()
    total_regs = Registration.objects.count()

    total_filled = Activity.objects.aggregate(
        total=Sum('filled_seats')
    )['total'] or 0

    return render(request, 'admin_dashboard.html', {
        'activities': total_activities,
        'users': total_users,
        'registrations': total_regs,
        'filled': total_filled
    })

from django.http import JsonResponse

def activity_seats(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    return JsonResponse({
        "filled": activity.filled_seats,
        "total": activity.total_seats
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Activity, Registration


@login_required(login_url="home")
def student_dashboard(request):

    total_activities = Activity.objects.count()
    total_registrations = Registration.objects.filter(user=request.user).count()

    approved = Registration.objects.filter(user=request.user, status='approved').count()
    pending = Registration.objects.filter(user=request.user, status='pending').count()
    waitlist = Registration.objects.filter(user=request.user, status='waitlist').count()

    context = {
        "total_activities": total_activities,
        "total_registrations": total_registrations,
        "approved": approved,
        "pending": pending,
        "waitlist": waitlist,
    }

    return render(request, "student_dashboard.html", context)

from django.http import JsonResponse

@login_required
def chart_data_api(request):
    user = request.user

    approved = Registration.objects.filter(user=user, status='approved').count()
    pending = Registration.objects.filter(user=user, status='pending').count()
    waitlist = Registration.objects.filter(user=user, status='waitlist').count()

    return JsonResponse({
        'approved': approved,
        'pending': pending,
        'waitlist': waitlist
    })

@login_required
def activity_analytics(request):
    data = Activity.objects.all()

    labels = []
    counts = []

    for act in data:
        labels.append(act.title)
        counts.append(act.registration_set.count())

    return JsonResponse({
        'labels': labels,
        'counts': counts
    })

from tracker import views
from django.contrib.auth.models import User
from django.http import HttpResponse

def reset_admin(request):
    user, created = User.objects.get_or_create(username='admin')
    user.set_password('admin123')
    user.is_staff = True
    user.is_superuser = True
    user.email = "admin@gmail.com"
    user.save()
    return HttpResponse("Admin ready")