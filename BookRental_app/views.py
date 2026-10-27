from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from rest_framework import viewsets

from .forms import BookRentalForm
from .models import BookRental
from .serializers import BookRentalSerializers

# FBV'S
def Home(request):
    return render(request,'Home.html')

def Book_rental_list(request):
    bookrental = BookRental.objects.all()
    return render(request, 'Book_rental_list.html', {'RBooks': bookrental})

def Rental_detail(request,rid):
    bookrental = get_object_or_404(BookRental, id=rid)
    return render(request, 'Rental_detail.html', {"bookrental": bookrental})

# CBV'S

class Add_rental(CreateView):
    model = BookRental
    form_class = BookRentalForm
    template_name = 'form.html'
    # context_object_name = 'form'
    success_url = reverse_lazy('bookrental')

class Update_rental(UpdateView):
    model = BookRental
    form_class = BookRentalForm
    template_name = 'form.html'
    # context_object_name = 'form'
    success_url = reverse_lazy('bookrental')

class Delete_rental(DeleteView):
    model = BookRental
    template_name = 'delete.html'
    context_object_name = 'bookrental'
    success_url = reverse_lazy('bookrental')

class BookRentalViewSet(viewsets.ModelViewSet):
    queryset = BookRental.objects.order_by('-created_at')
    serializer_class = BookRentalSerializers
    # form_class = BookRentalForm