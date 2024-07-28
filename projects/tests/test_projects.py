from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class ProjectsTest(APITestCase):
    list_url = reverse("project-list")

    def test_unauthenticated_get_request_returns_401(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
