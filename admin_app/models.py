from django.db import models
from datetime import datetime, date
from registration.models import CustomUser

# Create your models here.


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

# Student Table (Linked to CustomUser)
class Student(models.Model):
    DEGREE_CHOICES = [
        ("CE", "Computer Engineering"),
        ("IT", "Information Technology"),
        ("EC", "Electronics & Communication"),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="student_id")
    mobile_no = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES)
    graduation_date = models.DateField()
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.user.username + '-' + self.degree


class Faculty(models.Model):
    DEPARTMENT_CHOICES = [
        ("CE", "Computer Engineering"),
        ("IT", "Information Technology"),
        ("EC", "Electronics & Communication"),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="faculty")
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    salary = models.IntegerField(default=0)
    subject = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.user.username + '-' + self.department
    

class Notification(models.Model):
    NOTIFICATION_CHOICES = [
        ("student", "Student"),
        ("faculty", "Faculty"),
    ]
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notification")
    title=models.CharField(max_length=255)
    message=models.TextField()
    to = models.CharField(max_length=10, choices=NOTIFICATION_CHOICES)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification: {self.to} - {self.title}" 
        
class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ("panding", "Panding"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="leave")
    reason = models.CharField(max_length=50)
    discription = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES, default="pending")

    def __str__(self):
        return self.user.username + '-' + self.status
    

class Lecture(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.today)

    def __str__(self):
        return f"{self.subject.name} - {self.date}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="marked_attendances")
    date = models.DateTimeField(default=datetime.today)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="absent")

    class Meta:
        unique_together = ('student', 'lecture')  # Ensures a student has only one record per subject per day

    def __str__(self):
        return f"{self.student.user.username} - {self.lecture.subject.name} - {self.date} - {self.status}"

class AttendanceFaculty(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="attendance_faculty")
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="absent")

    class Meta:
        unique_together = ('faculty', 'date')

    def __str__(self):
        return f"{self.faculty.name} - {self.date} - {self.status}"