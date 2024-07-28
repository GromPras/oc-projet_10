from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class UsersTest(APITestCase):
    def test_user_registration(self):
        """
        Clients can create new users.
        """
        url = reverse("user-list")
        data = {
            "username": "Billy",
            "password": "password123",
            "birth_date": "2000-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "Billy")
