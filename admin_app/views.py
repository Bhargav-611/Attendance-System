from functools import wraps
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout


from registration.models import CustomUser

from .forms import FacultyForm, StudentForm, NotificationForm
from .models import AttendanceFaculty, Faculty, Student, Notification, Leave

@staff_member_required
def admin_dashboard(request):
    student_count = Student.objects.count()
    faculty_count = Faculty.objects.count()

    return render(request, "admin_app/dashboard.html", {
        "student_count": student_count,
        "faculty_count": faculty_count
})

@staff_member_required
def manage_user(request):
    return render(request, "admin_app/manage_user.html")
        
@staff_member_required
def student_info(request):
    students = Student.objects.all()
    return render(request, "admin_app/student_info.html", {"students": students})

@staff_member_required
def student_add(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)   # for upload image in html file
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            messages.error(request, "Username, Email, and Password are required.")
            return redirect("admin_app:student_add")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("admin_app:student_add")

        if form.is_valid():
            # Create CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role="student"
            )

            # Create Student and associate it with the user
            student = form.save(commit=False)
            student.user = user
            student.save()

            messages.success(request, "Student added successfully!")
            return redirect("admin_app:student_info")
    else:
        form = StudentForm()
    return render(request, "admin_app/register.html", {"form": form})


@staff_member_required
def student_edit(request, s_id):
    student = get_object_or_404(Student, pk=s_id)
    user1 = get_object_or_404(CustomUser, pk=student.user.id)
    student.user = user1
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data["password"]:
                user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("admin_app:student_info")
    else:
        form = StudentForm(instance=student)
    return render(request, "admin_app/register.html", {"form": form})
        
@staff_member_required
def student_delete(request, s_id):
    student = get_object_or_404(Student, pk=s_id)
    student.delete()
    return redirect("admin_app:student_info")


@staff_member_required
def faculty_info(request):
    faculties = Faculty.objects.all()
    return render(request, "admin_app/faculty_info.html", {"faculties": faculties})

@staff_member_required
def faculty_add(request):
    if request.method == "POST":

        form = FacultyForm(request.POST, request.FILES)     # for upload image in html file
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            messages.error(request, "Username, Email, and Password are required.")
            return redirect("admin_app:faculty_add")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("admin_app:faculty_add")

        if form.is_valid():
            # Create CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role="faculty"
            )

            faculty = form.save(commit=False)
            faculty.user = user
            faculty.save()

            messages.success(request, "faculty added successfully!")
            return redirect("admin_app:faculty_info")
    else:
        form = FacultyForm()
    return render(request, "admin_app/register.html", {"form": form})

@staff_member_required
def faculty_edit(request, f_id):
    faculty = get_object_or_404(Faculty, pk=f_id)

    if request.method == "POST":
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data["password"]:
                user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("admin_app:faculty_info")
    else:
        form = FacultyForm(instance=faculty)

    return render(request, "admin_app/register.html", {"form": form})
        
@staff_member_required
def faculty_delete(request, f_id):
    faculty = get_object_or_404(Faculty, pk=f_id)
    faculty.delete()
    return redirect("admin_app:faculty_info")

@staff_member_required
def notification(request):
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_app:admin_dashboard")
    else: 
        form = NotificationForm()
    return render(request, "admin_app/notification.html", {"form": form})

@staff_member_required
def leave(request):
    leaves = Leave.objects.all()
    return render(request, "admin_app/leave.html", {"leaves": leaves})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_leave_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            leave_id = data.get("leave_id")
            new_status = data.get("status")

            leave = Leave.objects.get(id=leave_id)
            leave.status = new_status
            leave.save()

            return JsonResponse({"success": True})
        except Leave.DoesNotExist:
            return JsonResponse({"success": False, "error": "Leave not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


import cv2 # type: ignore
from pyzbar.pyzbar import decode # type: ignore

def scan_barcode(camera_index=0):
    """Scans a barcode and returns the student ID."""
    print("📷 Starting camera...")

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("❌ Error: Camera not found or cannot be opened.")
        return None

    print("🔍 Scanning for student barcode... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame. Exiting.")
            break

        barcodes = decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')  # Extract student ID
            print(f"✅ Detected Barcode: {barcode_data}")

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
            print("👋 Exiting barcode scanner.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

@staff_member_required
def mark_faculty_attendance(request):
    facultys = Faculty.objects.all()
    for faculty in facultys:
        AttendanceFaculty.objects.create(faculty=faculty)
    
    faculty_id = scan_barcode()

    if faculty_id:
        faculty_id = faculty_id.lower()
        try:
            user = CustomUser.objects.get(username=faculty_id)
            faculty = Student.objects.get(user=user)
            attendanceFaculty = AttendanceFaculty.objects.filter(faculty=faculty)
            
            if attendanceFaculty.exists():
                attendanceFaculty.update(status="present")
                print(f"Attendance marked for {faculty_id}")
            else:
                print(f"No attendance record found for {faculty_id}")

        except CustomUser.DoesNotExist:
            print(f"No user found with ID {faculty_id}")
        except Student.DoesNotExist:
            print(f"No student record found for ID {faculty_id}")
        return redirect("admin_app:mark_faculty_attendance")
    else:
        return redirect("admin_app:admin_dashboard")