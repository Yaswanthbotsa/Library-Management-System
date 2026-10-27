from django.forms import ModelForm, DateInput
from .models import BookRental

class BookRentalForm(ModelForm):
    class Meta:
        model = BookRental
        fields = "__all__"
        widgets = {
            'rental_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'return_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean(self):
        cleaned = super().clean()
        rental, ret = cleaned.get('rental_date'), cleaned.get('return_date')
        if rental and ret and ret < rental:
            self.add_error('return_date', 'Return date cannot be before rental date.')
        return cleaned