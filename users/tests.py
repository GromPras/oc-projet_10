import json
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

    def test_user_registration_validation(self):
        test_cases = [
            {
                "username": "",
                "password": "password123",
                "birth_date": "2000-01-01",
            },
            {
                "username": "Billy",
                "password": "",
                "birth_date": "2000-01-01",
            },
            {
                "username": "Billy",
                "password": "password123",
                "birth_date": "",
            },
            {
                "username": "Billy",
                "password": "password123",
                "birth_date": "2000-01-01",
                "can_be_contacted": "Oui",
            },
        ]
        url = reverse("user-list")
        for data in test_cases:
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_registered_user_can_authenticate(self):
        url = reverse("user-list")
        data = {
            "username": "Billy",
            "password": "password123",
            "birth_date": "2000-01-01",
        }
        response = self.client.post(url, data, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Billy", "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unregistered_users_cannot_authenticate(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Billy", "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rgpd_default_underaged_users(self):
        url = reverse("user-list")
        data = {
            "username": "Billy",
            "password": "password123",
            "birth_date": "2020-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().can_be_contacted, False)
        self.assertEqual(User.objects.get().can_data_be_shared, False)

    def test_user_can_update_data(self):
        url = reverse("user-list")
        data = {
            "username": "Billy",
            "password": "password123",
            "birth_date": "2000-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }
        response = self.client.post(url, data, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Billy", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        self.assertEqual(User.objects.get().can_be_contacted, True)
        self.assertEqual(User.objects.get().can_data_be_shared, True)
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": 1}),
            {
                "can_be_contacted": False,
                "can_data_be_shared": False
            },
            headers={"Authorization": bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().can_be_contacted, False)
        self.assertEqual(User.objects.get().can_data_be_shared, False)

    def test_only_owner_can_update_user_data(self):
        url = reverse("user-list")
        data = {
            "username": "Billy",
            "password": "password123",
            "birth_date": "2000-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }
        response = self.client.post(url, data, format="json")
        data = {
            "username": "Joe",
            "password": "password123",
            "birth_date": "2000-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }
        response = self.client.post(url, data, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Billy", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        self.assertEqual(User.objects.get(pk=2).can_be_contacted, True)
        self.assertEqual(User.objects.get(pk=2).can_data_be_shared, True)
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": 2}),
            {
                "can_be_contacted": False,
                "can_data_be_shared": False
            },
            headers={"Authorization": bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.get(pk=2).can_be_contacted, True)
        self.assertEqual(User.objects.get(pk=2).can_data_be_shared, True)
