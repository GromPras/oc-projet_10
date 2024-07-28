import time
import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Issue
from users.models import User


class IssuesTest(APITestCase):
    def setUp(self):
        url = reverse("user-list")
        data = {
            "username": "Billy",
            "password": "password123",
            "birth_date": "2000-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }
        response = self.client.post(url, data, format="json")
        self.client.post(url, {
            "username": "Joe",
            "password": "password123",
            "birth_date": "2000-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Billy", "password": "password123"},
            format="json",
        )
        self.bearer = f"Bearer {json.loads(response.content)["access"]}"
        self.client.post(reverse("project-list"), {}, headers={"Authorization": self.bearer})
        self.client.post(
            "http://testserver/projects/1/add_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": self.bearer}
        )
        return super().setUp()

    def test_cannot_get_all_issues(self):
        response = self.client.get(reverse("issue-list"), headers={"Authorization": self.bearer})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

