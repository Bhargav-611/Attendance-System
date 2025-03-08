from django.urls import path, include

from . import views

app_name = "faculty_app"

urlpatterns = [ 
    path("faculty_dashboard/", views.faculty_dashboard, name="faculty_dashboard"),
    path("profile/", views.profile, name="profile"),
    path("view_attendance/", views.view_attendance, name="view_attendance"),
    path("generate_report/", views.generate_report, name="generate_report"),
    path("show_notification/", views.show_notification, name="show_notification"),
    path("request_leave/", views.request_leave, name="request_leave"),
    path("view_leave/", views.view_leave, name="view_leave"),
    path("show_student_attendance", views.show_student_attendance, name="show_student_attendance"),
    path("edit_student_attendance/<int:attendance_id>", views.edit_student_attendance, name="edit_student_attendance"),
    path("mark_student_attendance/", views.mark_student_attendance, name="mark_student_attendance"),
    path("mark_student_attendance2/<int:lecture_id>/", views.mark_student_attendance2, name="mark_student_attendance2"),
]
