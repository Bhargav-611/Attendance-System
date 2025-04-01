import csv
from functools import wraps
from time import localtime
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from admin_app.models import Attendance, AttendanceFaculty, Faculty, Leave, Lecture, Notification, Student, Subject
from admin_app.forms import AttendanceEditForm, LeaveForm, LectureForm
from django.contrib import messages

from registration.models import CustomUser

import cv2 # type: ignore
from pyzbar.pyzbar import decode # type: ignore

# Create your views here.

def faculty_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("registration:login")  # Redirect unauthenticated users to login page

        if request.user.role == "faculty":
            return view_func(request, *args, **kwargs)

        logout(request)  # Log out unauthorized users
        return redirect("registration:login")  # Redirect unauthorized users
    return wrapper

@faculty_required
def faculty_dashboard(request):
    return render(request, "faculty_app/dashboard.html", {"username": request.user.username})

@faculty_required
def profile(request):
    faculty = Faculty.objects.get(user=request.user)
    return render(request, "profile.html", {"obj": faculty})
    
@faculty_required
def view_attendance(request):
    faculty = Faculty.objects.get(user=request.user)
    attendance = AttendanceFaculty.objects.filter(faculty=faculty).order_by("date")
    return render(request, "faculty_app/view_attendance.html", {"attendance": attendance})


@faculty_required
def show_student_attendance(request):
    faculty = Faculty.objects.get(user=request.user)
    attendances = Attendance.objects.filter(faculty=faculty).order_by("date")
    return render(request, "faculty_app/show_student_attendance.html", {"attendances": attendances})

def scan_barcode(camera_index=0):
    """Scans a barcode and returns the student ID."""
    print("Starting camera...")

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: Camera not found or cannot be opened.")
        return None

    print("Scanning for student barcode... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break

        barcodes = decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')  # Extract student ID
            print(f"Detected Barcode: {barcode_data}")

            # Draw a rectangle around the barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {barcode_data}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cap.release()
            cv2.destroyAllWindows()
            return barcode_data  # Return scanned ID and exit loop

        # Display the frame with barcode detection
        cv2.imshow("Barcode Scanner", frame)

        # Press 'q' to exit scanning
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting barcode scanner.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


@faculty_required
def mark_student_attendance(request):
    faculty = Faculty.objects.get(user=request.user)
    if request.method == "POST":
        form = LectureForm(request.POST)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.faculty = faculty
            lecture.save()
            subject = lecture.subject
            students = Student.objects.filter(subjects=subject)
            for student in students:
                attendance = Attendance.objects.create(student=student, faculty=faculty, lecture=lecture)
            return redirect("faculty_app:mark_student_attendance2", lecture.id)
    else:
        form = LectureForm()
        return render(request, "faculty_app/mark_student_attendance.html", {"form": form})


@faculty_required
def mark_student_attendance2(request, lecture_id):
    lecture = Lecture.objects.get(id=lecture_id)
    attendance_records = Attendance.objects.filter(lecture=lecture)
    
    student_id = scan_barcode(1)

    if student_id:
        student_id = student_id.lower()
        try:
            user = CustomUser.objects.get(username=student_id)
            student = Student.objects.get(user=user)
            attendance = Attendance.objects.filter(lecture=lecture, student=student)
            
            if attendance.exists():
                attendance.update(status="present")
                print(f"Attendance marked for {student_id}")
            else:
                print(f"No attendance record found for {student_id}")

        except CustomUser.DoesNotExist:
            print(f"No user found with ID {student_id}")
        except Student.DoesNotExist:
            print(f"No student record found for ID {student_id}")
        return redirect("faculty_app:mark_student_attendance2", lecture_id)
    else:
        return redirect("faculty_app:faculty_dashboard")
    
        

@faculty_required
def edit_student_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)
    if request.method == "POST":
        form = AttendanceEditForm(request.POST)
        if(form.is_valid()):
            attendance.status = request.POST.get("status")
            attendance.save()
            return redirect("faculty_app:show_student_attendance")  # Redirect after update
    else:
        form = AttendanceEditForm(instance=attendance)
        return render(request, "faculty_app/edit_student_attendance.html", {"form": form, "attendance": attendance})

@faculty_required
def generate_report(request):
    faculty = Faculty.objects.get(user=request.user)
    
    # Prepare the HTTP response with CSV content
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{faculty.name}_attendance_report.csv"'

    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow(["Date", "Status"])  # CSV Headers

    # Fetch attendance records for the student
    attendance_records = AttendanceFaculty.objects.filter(faculty=faculty).order_by("date")

    for record in attendance_records:
        writer.writerow([
            record.date.strftime("%Y-%m-%d"),  # Format date
            record.status.capitalize(),
        ])

    return response

@faculty_required
def show_notification(request):
    notifications = Notification.objects.filter(to="faculty").order_by("-created_at")
    return render(request, "notifications.html", {"notifications": notifications})

@faculty_required
def request_leave(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()

            messages.success(request, "Leave request submitted successfully!")
            return redirect("faculty_app:faculty_dashboard")  
    else:
        form = LeaveForm()

    return render(request, "request_leave.html", {"form": form})

@faculty_required
def view_leave(request):
    leaves = Leave.objects.filter(user=request.user).order_by("status")
    return render(request, "view_leave.html", {"leaves": leaves})