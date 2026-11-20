
from django import forms
from .models import Student, Enrollment, Tuition, Installment


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'national_code',
            'parent_phone',
        ]

        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'national_code': 'کد ملی',
            'parent_phone': 'شماره تماس والدین',
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = [
            'student',
            'course',
            'academic_year',
            'is_active',
        ]

        labels = {
            'student': 'دانش‌آموز',
            'course': 'کلاس',
            'academic_year': 'سال تحصیلی',
            'is_active': 'ثبت‌نام فعال',
        }

        widgets = {
            'academic_year': forms.TextInput(
                attrs={'placeholder': 'مثلاً ۱۴۰۵-۱۴۰۶'}
            ),
        }



class TuitionForm(forms.ModelForm):
    installment_count = forms.IntegerField(
        min_value=1,
        label='تعداد اقساط',
        initial=1,
    )

    first_due_date = forms.DateField(
        label='تاریخ سررسید اولین قسط',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Tuition
        fields = [
            'enrollment',
            'total_amount',
            'installment_count',
            'first_due_date',
        ]

        labels = {
            'enrollment': 'ثبت‌نام دانش‌آموز',
            'total_amount': 'مبلغ کل شهریه (تومان)',
        }

        widgets = {
            'total_amount': forms.NumberInput(
                attrs={'min': '1', 'placeholder': 'مبلغ شهریه را وارد کنید'}
            ),
        }

        
class InstallmentForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = [
            'tuition',
            'installment_number',
            'amount',
            'due_date',
        ]

        labels = {
            'tuition': 'شهریه دانش‌آموز',
            'installment_number': 'شماره قسط',
            'amount': 'مبلغ قسط (تومان)',
            'due_date': 'تاریخ سررسید',
        }

        widgets = {
            'amount': forms.NumberInput(
                attrs={'min': '1', 'placeholder': 'مبلغ قسط را وارد کنید'}
            ),
            'due_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }