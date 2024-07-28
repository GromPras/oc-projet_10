import time
import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Project
from users.models import User


class ProjectsTest(APITestCase):
    list_url = reverse("project-list")
    dummy_project = {
        "title": "Project Setup",
        "description": "Lorem ipsum",
        "category": "back-end",
    }

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
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Billy", "password": "password123"},
            format="json",
        )
        self.bearer = f"Bearer {json.loads(response.content)["access"]}"
        return super().setUp()

    def test_unauthenticated_get_request_returns_401(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_post_request_returns_401(self):
        response = self.client.post(self.list_url, self.dummy_project)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_defaults_for_new_project(self):
        default_title = f"Project {str(time.time).split(".")[0]}"
        response = self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.get().title, default_title)
        self.assertEqual(Project.objects.get().author, User.objects.get())
        self.assertIn(User.objects.get(), Project.objects.get().contributors.all())

    def test_list_projects_hidden_fields(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        response = self.client.get(self.list_url, headers={"Authorization": self.bearer})
        self.assertIn("title", json.loads(response.content)[0])
        self.assertNotIn("author", json.loads(response.content)[0])
        self.assertNotIn("contributors", json.loads(response.content)[0])

    def test_only_author_or_contributor_can_access_project(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.client.post(reverse("user-list"), {"username": "Joe", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.get(reverse("project-detail", kwargs={"pk": 1}), headers={"Authorization": bearer})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_project_return_all_fields(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        response = self.client.get(reverse("project-detail", kwargs={"pk": 1}), headers={"Authorization": self.bearer})
        self.assertIn("title", json.loads(response.content))
        self.assertIn("author", json.loads(response.content))
        self.assertIn("contributors", json.loads(response.content))

    def test_author_can_update_project(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        response = self.client.put(reverse("project-detail", kwargs={"pk": 1}), {"title": "Updated title"},headers={"Authorization": self.bearer})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.get().title, "Updated title")

    def test_only_author_can_update_project(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.client.post(reverse("user-list"), {"username": "Joe", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.put(reverse("project-detail", kwargs={"pk": 1}), {"title": "Updated title"},headers={"Authorization": bearer})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_destroy_project(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        response = self.client.delete(reverse("project-detail", kwargs={"pk": 1}), headers={"Authorization": self.bearer})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_only_author_can_destroy_project(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.client.post(reverse("user-list"), {"username": "Joe", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.delete(reverse("project-detail", kwargs={"pk": 1}), headers={"Authorization": bearer})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_add_contributor_to_project(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.client.post(reverse("user-list"), {"username": "Joe", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        response = self.client.post(
            "http://testserver/projects/1/add_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(User.objects.get(pk=2), Project.objects.get().contributors.all())

    def test_user_cannot_add_itself_as_contributor(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.client.post(reverse("user-list"), {"username": "Joe", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.post(
            "http://testserver/projects/1/add_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn(User.objects.get(pk=2), Project.objects.get().contributors.all())

    def test_author_can_remove_contributors(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.client.post(reverse("user-list"), {"username": "Joe", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        self.client.post(
            "http://testserver/projects/1/add_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": self.bearer}
        )
        response = self.client.post(
            "http://testserver/projects/1/remove_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(User.objects.get(pk=2), Project.objects.get().contributors.all())

    def test_contributor_cannot_remove_itself_from_contributors(self):
        self.client.post(self.list_url, {}, headers={"Authorization": self.bearer})
        self.client.post(reverse("user-list"), {"username": "Joe", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        self.client.post(
            "http://testserver/projects/1/add_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": self.bearer}
        )
        response = self.client.post(
            "http://testserver/projects/1/remove_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(User.objects.get(pk=2), Project.objects.get().contributors.all())
