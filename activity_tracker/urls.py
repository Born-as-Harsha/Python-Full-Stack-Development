from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tracker import views
from django.contrib.auth import views as auth_views

urlpatterns = [
      path('reset-admin/', views.reset_admin),
    # 🔹 Admin
    path('admin/', admin.site.urls),

    # 🔹 Landing Page
    path('', views.landing, name='landing'),

    # 🔹 Authentication
    path('login/', views.home, name='login'),   # ✅ changed name
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # 🔐 PASSWORD RESET
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # 🔥 CAPTCHA
    path('captcha/', include('captcha.urls')),

    # 🔹 Student Features
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('add/', views.add_achievement, name='add_achievement'),
    path('view-all/', views.view_all, name='view_all'),
    path('profile/', views.profile, name='profile'),
    path('unregister/<int:achievement_id>/',
         views.unregister_achievement,
         name='unregister_achievement'),

    # 🔥 INCLUDE APP URLS (NO namespace)
    path('', include('tracker.urls')),   # ✅ correct

    # activity_tracker/urls.py

  
]

# MEDIA
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)