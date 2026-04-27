from django.urls import path
from . import views

urlpatterns = [

    # 🔹 Activities
    path('activities/', views.activities, name='activities'),
    path('register/<int:activity_id>/', views.register_activity, name='register_activity'),
    path('seats/<int:activity_id>/', views.activity_seats, name='activity_seats'),

    # 🔹 Registrations
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('unregister/<int:reg_id>/', views.unregister_activity, name='unregister_activity'),

    # 🔹 Stalls
    path('stalls/', views.stalls, name='stalls'),
    path('book-stall/<int:stall_id>/', views.book_stall, name='book_stall'),

    # 🔹 OTP
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # 🔹 Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('chart-data/', views.chart_data_api, name='chart_data_api'),

    path('activity-analytics/', views.activity_analytics, name='activity_analytics'),

    path('create-admin/', views.create_admin, name='create_admin'),
]