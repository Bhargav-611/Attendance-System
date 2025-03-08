from django import forms
from django.contrib.auth.hashers import make_password
from .models import Attendance, Faculty, Leave, Student, Subject, Notification, Lecture
from registration.models import CustomUser

# Student Registration Form
class StudentForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    # role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = Student
        fields = ["username", "email", "password", "name", "mobile_no", "degree", "graduation_date"]
        widgets = {
            'username': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.Select(attrs={'class': 'form-control'}),
            'graduation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
    def clean_password(self):
        password = self.cleaned_data.get("password")

        # Enforce password requirement only for new users
        if not self.instance.pk and not password:
            raise forms.ValidationError("Password is required for new users.")

        return password
    
    def save(self, commit=True):
        student = super().save(commit=False)
        student.password = make_password(self.cleaned_data["password"])
        if commit:
            student.save()
        return student


# Faculty Registration Form
class FacultyForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    # role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    subject = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = Faculty
        fields = ["username", "email", "password", "name", "department", "salary", "subject"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # Enforce password requirement only for new users
        if not self.instance.pk and not password:
            raise forms.ValidationError("Password is required for new users.")

        return password
    
    def save(self, commit=True):
        faculty = super().save(commit=False)
        faculty.password = make_password(self.cleaned_data["password"])
        if commit:
            faculty.save()
        return faculty


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["to", "title", "message"]
        widgets = {
            'to': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
            }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["student", "lecture", "faculty", "date", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "student": forms.Select(attrs={"class": "form-control"}),
            "lecture": forms.Select(attrs={"class": "form-control"}),
            "faculty": forms.Select(attrs={"class": "form-control"}),
        }

class AttendanceEditForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
        }

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ["reason", "discription", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "reason": forms.TextInput(attrs={"class": "form-control"}),
            "discription": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ["subject", "date"]
        widgets = {
            "subject": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateTimeInput(attrs={"type": "datetime", "class": "form-control"}),
        }