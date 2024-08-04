import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Comment
from users.models import User


class CommentsTest(APITestCase):
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
        self.client.post(url, {
            "username": "Jimbob",
            "birth_date": "2000-01-01",
            "password": "password123"
        }, format="json")
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "Billy", "password": "password123"},
            format="json",
        )
        self.bearer = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.post(
            url,
            {"username": "Joe", "password": "password123"},
            format="json",
        )
        self.bearer_contributor = f"Bearer {json.loads(response.content)["access"]}"
        response = self.client.post(
            url,
            {"username": "Jimbob", "password": "password123"},
            format="json",
        )
        self.bearer_outsider = f"Bearer {json.loads(response.content)["access"]}"
        self.client.post(reverse("project-list"), {}, headers={"Authorization": self.bearer})
        self.client.post(
            "http://testserver/projects/1/add_contributors/",
            { "contributor_ids": [2] },
            headers={"Authorization": self.bearer}
        )
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
        return super().setUp()

    def test_cannot_get_all_comments(self):
        response = self.client.get(reverse("comment-list"), headers={"Authorization": self.bearer})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_or_contributor_of_project_can_create_comment(self):
        self.client.post(
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum dolor sit amet"
            },
            headers={"Authorization": self.bearer}
        )
        self.client.post(
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum dolor sit amet contributores"
            },
            headers={"Authorization": self.bearer_contributor}
        )
        self.assertEqual(Comment.objects.count(), 2)
        comments = Comment.objects.all()
        self.assertEqual(comments[0].author, User.objects.get(pk=1))
        self.assertEqual(comments[0].description, "Lorem ipsum dolor sit amet")
        self.assertEqual(comments[1].author, User.objects.get(pk=2))
        self.assertEqual(comments[1].description, "Lorem ipsum dolor sit amet contributores")

    def test_only_author_and_contributor_can_create_comment(self):
        response = self.client.post(
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Unauthorized comment",
            },
            headers={"Authorization": self.bearer_outsider}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 0)

    def test_author_or_contributor_can_access_comment(self):
        response = self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        comment_id = Comment.objects.get().id
        for bearer in [self.bearer, self.bearer_contributor]:
            response = self.client.get(reverse("comment-detail", kwargs={"pk": comment_id}), headers={"Authorization": bearer})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_author_or_contributor_can_access_comment(self):
        response = self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        comment_id = Comment.objects.get().id
        response = self.client.get(reverse("comment-detail", kwargs={"pk": comment_id}), headers={"Authorization": self.bearer_outsider})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_list_issues_comments(self):
        self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        for bearer in [self.bearer, self.bearer_contributor]:
            response = self.client.get(reverse("issue-comments", kwargs={"pk": 1}), headers={"Authorization": bearer})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_author_or_contributor_can_list_issues_comments(self):
        self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        response = self.client.get(reverse("issue-comments", kwargs={"pk": 1}), headers={"Authorization": self.bearer_outsider})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_comment(self):
        self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        comment = Comment.objects.get()
        self.assertEqual(comment.description, "Lorem ipsum")
        response = self.client.put(
            reverse("comment-detail", kwargs={"pk": comment.id}),
            {
                "issue": 1,
                "description": "dolor sit amet"
            },
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment = Comment.objects.get()
        self.assertEqual(comment.description, "dolor sit amet")

    def test_only_author_can_update_comment(self):
        self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        comment = Comment.objects.get()
        self.assertEqual(comment.description, "Lorem ipsum")
        for bearer in [self.bearer_contributor, self.bearer_outsider]:
            response = self.client.put(
                reverse("comment-detail", kwargs={"pk": comment.id}),
                {
                    "issue": 1,
                    "description": "dolor sit amet"
                },
                headers={"Authorization": bearer}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            comment = Comment.objects.get()
            self.assertEqual(comment.description, "Lorem ipsum")

    def test_author_can_destroy_comment(self):
        self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment_id = Comment.objects.get().id
        response = self.client.delete(
            reverse("comment-detail", kwargs={"pk": comment_id}),
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_only_author_can_destroy_comment(self):
        self.client.post( 
            reverse("comment-list"),
            {
                "issue": 1,
                "description": "Lorem ipsum"
            },
            headers={"Authorization": self.bearer}
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment_id = Comment.objects.get().id
        for bearer in [self.bearer_contributor, self.bearer_outsider]:
            response = self.client.delete(
                reverse("comment-detail", kwargs={"pk": comment_id}),
                headers={"Authorization": bearer}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(Comment.objects.count(), 1)
