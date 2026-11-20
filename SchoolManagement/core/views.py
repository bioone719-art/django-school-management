
import calendar
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum


from .forms import StudentForm, EnrollmentForm, TuitionForm, InstallmentForm
from .models import Student, Installment, Tuition, Payment


def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'دانش‌آموز با موفقیت ثبت شد.')
            return redirect('student_create')

    else:
        form = StudentForm()

    return render(request, 'core/student_form.html', {'form': form})


def student_list(request):
    students = Student.objects.all()

    return render(
        request,
        'core/student_list.html',
        {'students': students}
    )


def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'ثبت‌نام دانش‌آموز با موفقیت انجام شد.')
            return redirect('enrollment_create')

    else:
        form = EnrollmentForm()

    return render(
        request,
        'core/enrollment_form.html',
        {'form': form}
    )



def tuition_create(request):
    if request.method == 'POST':
        form = TuitionForm(request.POST)

        if form.is_valid():
            tuition = form.save(commit=False)

            installment_count = form.cleaned_data['installment_count']
            first_due_date = form.cleaned_data['first_due_date']
        

            total_amount = int(tuition.total_amount)

            if installment_count > total_amount:
                form.add_error(
                    'installment_count',
                    'تعداد اقساط نمی‌تواند از مبلغ شهریه بیشتر باشد.'
                )
            else:
                with transaction.atomic():
                    tuition.save()

                    base_amount, remainder = divmod(
                        total_amount,
                        installment_count
                    )

                    for number in range(1, installment_count + 1):
                        amount = base_amount

                        if number <= remainder:
                            amount += 1

                        month_index = (
                            first_due_date.month - 1 + number - 1
                        )

                        year = first_due_date.year + month_index // 12
                        month = month_index % 12 + 1

                        day = min(
                            first_due_date.day,
                            calendar.monthrange(year, month)[1]
                        )

                        due_date = first_due_date.replace(
                            year=year,
                            month=month,
                            day=day
                        )

                        Installment.objects.create(
                            tuition=tuition,
                            installment_number=number,
                            amount=amount,
                            due_date=due_date
                        )

                messages.success(
                    request,
                    'شهریه و اقساط با موفقیت ثبت شدند.'
                )
                return redirect('tuition_create')

    else:
        form = TuitionForm()

    return render(
        request,
        'core/tuition_form.html',
        {'form': form}
    )



def installment_create(request):
    if request.method == 'POST':
        form = InstallmentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'قسط با موفقیت ثبت شد.')
            return redirect('installment_create')

    else:
        form = InstallmentForm()

    return render(
        request,
        'core/installment_form.html',
        {'form': form}
    )


def financial_report(request):
    total_tuition = Tuition.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_paid = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_remaining = total_tuition - total_paid

    paid_count = 0
    partial_count = 0
    unpaid_count = 0

    tuitions = Tuition.objects.all()

    for tuition in tuitions:
        if tuition.payment_status == 'تسویه‌شده':
            paid_count += 1
        elif tuition.payment_status == 'پرداخت ناقص':
            partial_count += 1
        else:
            unpaid_count += 1

    context = {
        'total_tuition': total_tuition,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'paid_count': paid_count,
        'partial_count': partial_count,
        'unpaid_count': unpaid_count,
        'tuitions': tuitions,
    }

    return render(
        request,
        'core/financial_report.html',
        context
    )
