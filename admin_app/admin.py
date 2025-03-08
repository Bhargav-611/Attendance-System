from django.contrib import admin, messages
from .models import *

# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ("get_username", "get_email", "get_role", "name", "degree", "graduation_date")
    search_fields = ("user__username", "user__email", "id_no")
    readonly_fields = ("get_email", "get_role")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def get_role(self, obj):
        return obj.user.role
    get_role.short_description = "Role"

    def save_model(self, request, obj, form, change):
        # Ensure that only students are added to Student table
        if obj.user.role != "student":
            messages.error(request, "Only users with the 'Student' role can be added to Students.")
            return
        super().save_model(request, obj, form, change)


class FacultyAdmin(admin.ModelAdmin):
    list_display = ("get_username", "get_email", "get_role", "name", "department")
    search_fields = ("user__username", "user__email", "faculty_id")
    readonly_fields = ("get_email", "get_role")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def get_role(self, obj):
        return obj.user.role
    get_role.short_description = "Role"

    def save_model(self, request, obj, form, change):
        # Ensure that only faculty members are added to Faculty table
        if obj.user.role != "faculty":
            messages.error(request, "Only users with the 'Faculty' role can be added to Faculty.")
            return    
        super().save_model(request, obj, form, change)

class LeaveAdmin(admin.ModelAdmin):
    list_display = ("user", "reason", "status")
    ordering = ["status"]

admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Subject)
admin.site.register(Notification)
admin.site.register(Leave, LeaveAdmin)
admin.site.register(Attendance)
admin.site.register(Lecture)
admin.site.register(AttendanceFaculty)