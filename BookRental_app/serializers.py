from rest_framework import serializers
from .models import BookRental

class BookRentalSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookRental
        fields = '__all__'

    def validate(self, data):
        # Use the new value if it was sent, otherwise the saved value (when updating)
        rental = data.get('rental_date', getattr(self.instance, 'rental_date', None))
        ret = data.get('return_date', getattr(self.instance, 'return_date', None))

        if rental and ret and ret < rental:
            raise serializers.ValidationError(
                {'return_date': 'Return date cannot be before rental date.'})
        return data