from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from .forms import BookRentalForm
from .models import BookRental, FINE_PER_DAY


def make_rental(**overrides):
    """Create a rental with sensible defaults; override any field you need."""
    today = timezone.localdate()
    data = dict(
        book_title='Test Book',
        author_name='Test Author',
        borrower_name='Test Borrower',
        borrower_email='test@example.com',
        rental_date=today - timedelta(days=5),
        return_date=today + timedelta(days=9),
        status='Borrowed',
    )
    data.update(overrides)
    return BookRental.objects.create(**data)


class ModelLogicTests(TestCase):
    def test_on_time_rental_has_no_fine(self):
        rental = make_rental()
        self.assertEqual(rental.status, 'Borrowed')
        self.assertEqual(rental.fine_amount, 0)

    def test_due_today_is_not_overdue(self):
        rental = make_rental(return_date=timezone.localdate())
        self.assertEqual(rental.status, 'Borrowed')
        self.assertEqual(rental.fine_amount, 0)

    def test_late_rental_becomes_overdue_with_fine(self):
        rental = make_rental(return_date=timezone.localdate() - timedelta(days=10))
        self.assertEqual(rental.status, 'Overdue')
        self.assertEqual(rental.fine_amount, 10 * FINE_PER_DAY)

    def test_returned_late_stops_the_fine(self):
        rental = make_rental(
            return_date=timezone.localdate() - timedelta(days=4),
            status='Returned',
        )
        self.assertEqual(rental.returned_date, timezone.localdate())
        self.assertEqual(rental.fine_amount, 4 * FINE_PER_DAY)
        rental.save()   # saving again must not change the fine
        self.assertEqual(rental.fine_amount, 4 * FINE_PER_DAY)

    def test_lost_book_is_left_alone(self):
        rental = make_rental(
            return_date=timezone.localdate() - timedelta(days=30),
            status='Lost',
        )
        self.assertEqual(rental.status, 'Lost')
        self.assertEqual(rental.fine_amount, 0)


class FormTests(TestCase):
    def form_data(self, **overrides):
        today = timezone.localdate()
        data = {
            'book_title': 'Form Book',
            'author_name': 'Form Author',
            'borrower_name': 'Form Borrower',
            'borrower_email': 'form@example.com',
            'rental_date': today.isoformat(),
            'return_date': (today + timedelta(days=7)).isoformat(),
            'status': 'Borrowed',
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        self.assertTrue(BookRentalForm(data=self.form_data()).is_valid())

    def test_return_before_rental_is_rejected(self):
        today = timezone.localdate()
        form = BookRentalForm(data=self.form_data(
            rental_date=today.isoformat(),
            return_date=(today - timedelta(days=1)).isoformat(),
        ))
        self.assertFalse(form.is_valid())
        self.assertIn('return_date', form.errors)

    def test_fine_cannot_be_typed_in(self):
        self.assertNotIn('fine_amount', BookRentalForm().fields)


class PageTests(TestCase):
    def test_home_page(self):
        self.assertEqual(self.client.get(reverse('Home')).status_code, 200)

    def test_list_page_shows_titles(self):
        make_rental(book_title='Wings of Fire')
        response = self.client.get(reverse('bookrental'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wings of Fire')

    def test_empty_list_message(self):
        response = self.client.get(reverse('bookrental'))
        self.assertContains(response, 'No rentals found.')

    def test_detail_page(self):
        rental = make_rental(book_title='Detail Book')
        response = self.client.get(reverse('rental_detail', args=[rental.id]))
        self.assertContains(response, 'Detail Book')

    def test_detail_page_404_for_missing_id(self):
        response = self.client.get(reverse('rental_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_add_rental(self):
        today = timezone.localdate()
        response = self.client.post(reverse('Add_rental'), {
            'book_title': 'Added Book',
            'author_name': 'Someone',
            'borrower_name': 'Someone Else',
            'borrower_email': 'a@example.com',
            'rental_date': today.isoformat(),
            'return_date': (today + timedelta(days=7)).isoformat(),
            'status': 'Borrowed',
        })
        self.assertRedirects(response, reverse('bookrental'))
        self.assertTrue(BookRental.objects.filter(book_title='Added Book').exists())

    def test_update_rental(self):
        rental = make_rental()
        response = self.client.post(reverse('Update_rental', args=[rental.id]), {
            'book_title': 'Renamed Book',
            'author_name': rental.author_name,
            'borrower_name': rental.borrower_name,
            'borrower_email': rental.borrower_email,
            'rental_date': rental.rental_date.isoformat(),
            'return_date': rental.return_date.isoformat(),
            'status': 'Borrowed',
        })
        self.assertRedirects(response, reverse('bookrental'))
        rental.refresh_from_db()
        self.assertEqual(rental.book_title, 'Renamed Book')

    def test_delete_rental(self):
        rental = make_rental()
        response = self.client.post(reverse('Delete_rental', args=[rental.id]))
        self.assertRedirects(response, reverse('bookrental'))
        self.assertFalse(BookRental.objects.filter(id=rental.id).exists())


class ApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='pass12345')
        self.client = APIClient()

    def test_anonymous_user_is_blocked(self):
        response = self.client.get(reverse('Book_rental-list'))
        self.assertIn(response.status_code, (401, 403))

    def test_logged_in_user_can_list(self):
        make_rental()
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('Book_rental-list'))
        self.assertEqual(response.status_code, 200)

    def test_partial_update_does_not_crash(self):
        rental = make_rental()
        self.client.force_authenticate(self.user)
        url = reverse('Book_rental-detail', args=[rental.id])
        response = self.client.patch(url, {'status': 'Returned'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_api_rejects_return_before_rental(self):
        rental = make_rental()
        self.client.force_authenticate(self.user)
        url = reverse('Book_rental-detail', args=[rental.id])
        early = (rental.rental_date - timedelta(days=1)).isoformat()
        response = self.client.patch(url, {'return_date': early}, format='json')
        self.assertEqual(response.status_code, 400)