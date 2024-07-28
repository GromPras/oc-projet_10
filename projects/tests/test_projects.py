import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class ProjectsTest(APITestCase):
    list_url = reverse("project-list")
    dummy_project = {
        "title": "Project Setup",
        "description": "Lorem ipsum",
        "category": "back-end",
    }

    def setup(self):
        url = reverse("user-list")
        data = {
            "username": "Billy",
            "password": "password123",
            "birthdate": "2000-01-01",
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
        self.bearer = f"Bearer {json.loads(response.content)["access"]}"

    def test_unauthenticated_get_request_returns_401(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_post_request_returns_401(self):
        response = self.client.post(self.list_url, self.dummy_project)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
