from django.urls import path, include
from . import views


app_name = "student_app" 

urlpatterns = [
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    path("profile/", views.profile, name="profile"),
    # path("show_attendance/", views.show_attendance, name="show_attendance"),
    path("daily_attendance/", views.daily_attendance, name="daily_attendance"),
    path("subject_wise_attendance/", views.subject_wise_attendance, name="subject_wise_attendance"),
    path("generate_report/", views.generate_report, name="generate_report"),
    path("show_notification/", views.show_notification, name="show_notification"),
    path("request_leave/", views.request_leave, name="request_leave"),
    path("view_leave/", views.view_leave, name="view_leave"),
]
