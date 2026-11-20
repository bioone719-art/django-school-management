
from django.urls import path
from . import views

urlpatterns = [
    path('students/create/', views.student_create, name='student_create'),
    path('students/', views.student_list, name='student_list'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
    path('tuitions/create/', views.tuition_create, name='tuition_create'),
    path('installments/create/', views.installment_create, name='installment_create'),
    path('financial-report/', views.financial_report, name='financial_report'),
]
