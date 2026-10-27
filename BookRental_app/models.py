from django.db import models
# from django.forms import ModelForm
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

# Create your models here.
STATUS_CHOICES = [
    ('Borrowed', 'Borrowed'),
    ('Returned', 'Returned'),
    ('Overdue', 'Overdue'),
    ('Lost', 'Lost'),
]
FINE_PER_DAY = Decimal('5.00')   # change this to your own rate
class BookRental(models.Model):
    book_title = models.CharField(max_length=100)
    author_name = models.CharField(max_length=100)
    borrower_name = models.CharField(max_length=100)
    borrower_email = models.EmailField()
    return_date = models.DateField()
    rental_date = models.DateField()
    fine_amount = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0)],
        editable=False,
    )
    returned_date = models.DateField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Borrowed')

    def __str__(self) -> str:
        return self.book_title

    def update_status_and_fine(self):
        if self.status == 'Lost':
            return  # a lost book stays as it is

        today = timezone.localdate()

        if self.status == 'Returned':
            if self.returned_date is None:
                self.returned_date = today
            end_date = self.returned_date
        else:
            self.returned_date = None
            end_date = today
            self.status = 'Overdue' if today > self.return_date else 'Borrowed'

        late_days = max((end_date - self.return_date).days, 0)
        self.fine_amount = late_days * FINE_PER_DAY

    def save(self, *args, **kwargs):
        self.update_status_and_fine()
        super().save(*args, **kwargs)





