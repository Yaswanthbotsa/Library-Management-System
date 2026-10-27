# from django.urls import path
# from rest_framework.routers import DefaultRouter
#
# from . import views
# ----------------
# urlpatterns = [
#     path('home/', views.Home_page, name='home'),
#     path('rental-list/<int:by>/', views.rental_list, name='rental_list'),
#     path('add/', views.rental_detail_page, name='add_rental'),
#     path('update/<int:pk>/', views.update_rental.as_view(), name='update_rental'),
#     path('delete/<int:pk>/', views.delete_rental.as_view(), name='delete_rental'),
# ]
# ------------------
# urlpatterns = [
#     path('home/', views.Home, name='Home'),
#     path('Book_rental_list/', views.Book_rental_list, name='bookrental'),
#     path('Rental_detail/<int:rid>/', views.Rental_detail, name='rental_detail'),
#     path('Add_rental/', views.Add_rental.as_view(), name='Add_rental'),
#     path('Update_rental/<int:pk>/', views.Update_rental.as_view(), name='Update_rental'),
#     path('Delete_rental/<int:pk>/', views.Delete_rental.as_view(), name='Delete_rental'),
# ]
#
# router = DefaultRouter()
# router.register('Book_rental',views.BookRentalViewSet,basename='Book_rental')
# urlpatterns += router.urls

# ----------------------------------------------------------------------------------------------

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('Book_rental', views.BookRentalViewSet, basename='Book_rental')

urlpatterns = [
    path('', views.Home, name='Home'),
    path('Book_rental_list/', views.Book_rental_list, name='bookrental'),
    path('Rental_detail/<int:rid>/', views.Rental_detail, name='rental_detail'),
    path('Add_rental/', views.Add_rental.as_view(), name='Add_rental'),
    path('Update_rental/<int:pk>/', views.Update_rental.as_view(), name='Update_rental'),
    path('Delete_rental/<int:pk>/', views.Delete_rental.as_view(), name='Delete_rental'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]