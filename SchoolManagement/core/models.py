
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Sum


class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    title = models.CharField(max_length=100)

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    capacity = models.PositiveIntegerField()

    tuition_fee = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )

    def __str__(self):
        return self.title


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    national_code = models.CharField(
        max_length=10,
        unique=True
    )

    parent_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Enrollment(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="enrollments"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="enrollments"
    )

    enrollment_date = models.DateField(auto_now_add=True)

    academic_year = models.CharField(max_length=9)

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "academic_year"],
                name="unique_student_course_year"
            )
        ]

    def clean(self):
        super().clean()

        if self.is_active and self.course_id:

            active_count = Enrollment.objects.filter(
                course_id=self.course_id,
                is_active=True
            ).exclude(pk=self.pk).count()

            if active_count >= self.course.capacity:
                raise ValidationError(
                    "ظرفیت این کلاس تکمیل شده است."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.course}"


class Tuition(models.Model):

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.PROTECT,
        related_name="tuition"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )

    created_at = models.DateField(auto_now_add=True)

    def clean(self):
        super().clean()

        if self.total_amount is not None and self.total_amount <= 0:
            raise ValidationError(
                "مبلغ شهریه باید بیشتر از صفر باشد."
            )

        if self.pk and self.total_amount is not None:

            installments_total = self.installments.aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")

            if installments_total > self.total_amount:
                raise ValidationError(
                    "مبلغ شهریه نمی‌تواند کمتر از مجموع اقساط باشد."
                )

            paid_total = Payment.objects.filter(
                installment__tuition_id=self.pk
            ).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")

            if paid_total > self.total_amount:
                raise ValidationError(
                    "مبلغ شهریه نمی‌تواند کمتر از مجموع پرداخت‌ها باشد."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_paid_amount(self):

        total = self.installments.aggregate(
            total=Sum("payments__amount")
        )["total"]

        return total or Decimal("0")

    @property
    def remaining_amount(self):
        return self.total_amount - self.total_paid_amount

    @property
    def payment_status(self):

        if self.total_paid_amount == 0:
            return "پرداخت‌نشده"

        elif self.total_paid_amount < self.total_amount:
            return "پرداخت ناقص"

        else:
            return "تسویه‌شده"

    def __str__(self):
        return f"{self.enrollment} - {self.total_amount}"


class Installment(models.Model):

    tuition = models.ForeignKey(
        Tuition,
        on_delete=models.CASCADE,
        related_name="installments"
    )

    installment_number = models.PositiveIntegerField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )

    due_date = models.DateField()

    def clean(self):
        super().clean()

        if self.amount is not None and self.amount <= 0:
            raise ValidationError(
                "مبلغ قسط باید بیشتر از صفر باشد."
            )

        if self.tuition_id and self.amount is not None:

            previous_total = Installment.objects.filter(
                tuition_id=self.tuition_id
            ).exclude(pk=self.pk).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")

            if previous_total + self.amount > self.tuition.total_amount:
                raise ValidationError(
                    "مجموع اقساط نمی‌تواند از مبلغ کل شهریه بیشتر باشد."
                )

            paid_total = Payment.objects.filter(
                installment_id=self.pk
            ).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")

            if paid_total > self.amount:
                raise ValidationError(
                    "مبلغ قسط نمی‌تواند کمتر از مجموع پرداخت‌های آن باشد."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def paid_amount(self):

        total = self.payments.aggregate(
            total=Sum("amount")
        )["total"]

        return total or Decimal("0")

    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount

    @property
    def payment_status(self):

        if self.paid_amount == 0:
            return "پرداخت‌نشده"

        elif self.paid_amount < self.amount:
            return "پرداخت ناقص"

        else:
            return "تسویه‌شده"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tuition", "installment_number"],
                name="unique_tuition_installment_number"
            )
        ]

    def __str__(self):
        return f"قسط {self.installment_number} - {self.tuition}"


class Payment(models.Model):

    installment = models.ForeignKey(
        Installment,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )

    payment_date = models.DateField(auto_now_add=True)

    tracking_code = models.CharField(
        max_length=50,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    def clean(self):
        super().clean()

        if self.amount is not None and self.amount <= 0:
            raise ValidationError(
                "مبلغ پرداخت باید بیشتر از صفر باشد."
            )

        if self.installment_id and self.amount is not None:

            paid_before = Payment.objects.filter(
                installment_id=self.installment_id
            ).exclude(pk=self.pk).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")

            if paid_before + self.amount > self.installment.amount:
                raise ValidationError(
                    "مبلغ پرداخت از مانده قسط بیشتر است."
                )

            tuition_paid_before = Payment.objects.filter(
                installment__tuition_id=self.installment.tuition_id
            ).exclude(pk=self.pk).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")

            if tuition_paid_before + self.amount > self.installment.tuition.total_amount:
                raise ValidationError(
                    "مجموع پرداخت‌ها از مبلغ کل شهریه بیشتر است."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"پرداخت {self.amount} - {self.installment}"
