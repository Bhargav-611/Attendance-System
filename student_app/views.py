import csv  
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from admin_app.models import Leave, Student, Attendance, Lecture, Faculty, Subject, Notification
from django.http import HttpResponse
from django.utils.timezone import localtime
from admin_app.forms import LeaveForm
# Create your views here.




# decoraters
def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("registration:login")  # Redirect unauthenticated users to login page

        if request.user.role == "student":
            return view_func(request, *args, **kwargs)

        logout(request)  # Log out unauthorized users
        return redirect("registration:login")  # Redirect unauthorized users
    return wrapper



@student_required
def student_dashboard(request):
    return render(request, "student_app/dashboard.html", {"username": request.user.username})

@student_required
def profile(request):
    student = Student.objects.get(user=request.user)
    return render(request, "profile.html", {"obj": student})

# @student_required
# def show_attendance(request):
#     attendance = Attendance.objects.filter(student=Student.objects.get(user=request.user))
#     return render(request, "student_app/show_attendance.html", {"attendance": attendance})

@student_required
def daily_attendance(request):
    student = Student.objects.get(user=request.user)
    
    attendance_records = Attendance.objects.filter(student=student).order_by("-lecture__date")

    daily_attendance = {}
    for record in attendance_records:
        date_key = record.lecture.date.date()
        if date_key not in daily_attendance:
            daily_attendance[date_key] = []
        daily_attendance[date_key].append({
            "subject": record.lecture.subject.name,
            "status": record.status
        })

    return render(request, "student_app/daily_attendance.html", {
        "daily_attendance": daily_attendance
    })
@student_required
def subject_wise_attendance(request):
    student = Student.objects.get(user=request.user)
    subject_attendance = []

    # Get the subjects the student is enrolled in
    subjects = student.subjects.all()

    for subject in subjects:
        lectures = Lecture.objects.filter(subject=subject)  # Get all lectures for the subject
        total_lectures = lectures.count()
        # print(total_lectures)
        attended_lectures = Attendance.objects.filter(student=student, lecture__subject=subject, status="present").count()

        # print(attended_lectures)

        attendance_percentage = round((attended_lectures / total_lectures) * 100, 2) if total_lectures > 0 else 0

        subject_attendance.append({
            'subject': subject.name,
            'attendance_percentage': attendance_percentage
        })
    
    return render(request, "student_app/subject_wise_attendance.html", {"subject_attendance": subject_attendance})


@student_required
def generate_report(request):
    student = Student.objects.get(user=request.user)
    
    # Prepare the HTTP response with CSV content
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{student.name}_attendance_report.csv"'

    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow(["Date", "Subject", "Status"])  # CSV Headers

    # Fetch attendance records for the student
    attendance_records = Attendance.objects.filter(student=student).order_by("lecture__date")

    for record in attendance_records:
        writer.writerow([
            localtime(record.lecture.date).strftime("%Y-%m-%d"),  # Format date
            record.lecture.subject.name,
            record.status.capitalize(),
        ])

    return response

@student_required
def show_notification(request):
    notifications = Notification.objects.filter(to="student").order_by("-created_at")
    return render(request, "notifications.html", {"notifications": notifications})

@student_required
def request_leave(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()

            messages.success(request, "Leave request submitted successfully!")
            return redirect("student_app:student_dashboard")  
    else:
        form = LeaveForm()

    return render(request, "request_leave.html", {"form": form})

@student_required
def view_leave(request):
    leaves = Leave.objects.filter(user=request.user).order_by("status")
    return render(request, "view_leave.html", {"leaves": leaves})