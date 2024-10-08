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

    def test_author_of_project_can_create_issue(self):
        self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": self.bearer}
        )
        issue = Issue.objects.get()
        self.assertEqual(Issue.objects.count(), 1)
        self.assertEqual(issue.author, User.objects.get(pk=1))
        self.assertEqual(issue.assigned_to, User.objects.get(pk=2))

    def test_only_author_or_contributor_can_create_issue(self):
        self.client.post(reverse("user-list"), {"username": "Jimbob", "birth_date": "2000-01-01", "password": "password123"}, format="json")
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "Jimbob", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Issue.objects.count(), 0)

    def test_only_author_or_contributor_can_access_issue(self):
        self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": self.bearer}
        )
        self.client.post(reverse("user-list"), {
            "username": "Jimbob",
            "password": "password123",
            "birth_date": "2000-01-01",
            "can_be_contacted": True,
            "can_data_be_shared": True,
        }, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Jimbob", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.get(reverse("issue-detail", kwargs={"pk": 1}), headers={"Authorization": bearer})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_list_project_issues(self):
        self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": self.bearer}
        )
        response = self.client.get(reverse("project-issues", kwargs={"pk": 1}),headers={"Authorization": self.bearer})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_can_update_issue(self):
        self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": self.bearer}
        )
        issue = Issue.objects.get()
        self.assertEqual(issue.status, "to-do")
        self.client.put(
            reverse("issue-detail", kwargs={"pk": 1}),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "in-progress"
            },
            headers={"Authorization": self.bearer}
        )
        issue = Issue.objects.get()
        self.assertEqual(issue.status, "in-progress")

    def test_only_author_can_update_issue(self):
        self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": self.bearer}
        )
        issue = Issue.objects.get()
        self.assertEqual(issue.status, "to-do")
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        self.client.put(
            reverse("issue-detail", kwargs={"pk": 1}),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "in-progress"
            },
            headers={"Authorization": bearer}
        )
        issue = Issue.objects.get()
        self.assertEqual(issue.status, "to-do")

    def test_author_can_destroy_issue(self):
        self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(Issue.objects.count(), 1)
        response = self.client.delete(
            reverse("issue-detail", kwargs={"pk": 1}),
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Issue.objects.count(), 0)

    def test_only_author_can_destroy_issue(self):
        self.client.post(
            reverse("issue-list"),
            {
                "project": 1,
                "title": "Issue 1",
                "description": "Issue description",
                "assigned_to": 2,
                "priority": "low",
                "tag": "bug",
                "status": "to-do"
            },
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(Issue.objects.count(), 1)
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.delete(
            reverse("issue-detail", kwargs={"pk": 1}),
            headers={"Authorization": bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Issue.objects.count(), 1)
