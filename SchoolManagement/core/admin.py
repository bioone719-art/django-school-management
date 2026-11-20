
from django.contrib import admin
from .models import (
    Teacher,
    Course,
    Student,
    Enrollment,
    Tuition,
    Installment,
    Payment
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone")
    search_fields = ("first_name", "last_name", "phone")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "capacity", "tuition_fee")
    search_fields = ("title",)
    list_filter = ("teacher",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "national_code",
        "parent_phone"
    )
    search_fields = (
        "first_name",
        "last_name",
        "national_code"
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "academic_year",
        "enrollment_date",
        "is_active"
    )
    list_filter = ("academic_year", "is_active")
    search_fields = (
        "student__first_name",
        "student__last_name",
        "course__title"
    )


@admin.register(Tuition)
class TuitionAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "total_amount",
        "total_paid_amount",
        "remaining_amount",
        "payment_status",
        "created_at"
    )
    search_fields = (
        "enrollment__student__first_name",
        "enrollment__student__last_name"
    )


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = (
        "tuition",
        "installment_number",
        "amount",
        "paid_amount",
        "remaining_amount",
        "payment_status",
        "due_date"
    )
    
    list_filter = ("due_date",)
    search_fields = (
        "tuition__enrollment__student__first_name",
        "tuition__enrollment__student__last_name"
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "installment",
        "amount",
        "payment_date",
        "tracking_code"
    )
    list_filter = ("payment_date",)
    search_fields = (
        "tracking_code",
        "installment__tuition__enrollment__student__first_name",
        "installment__tuition__enrollment__student__last_name"
    )
