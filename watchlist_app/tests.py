from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from . import models


class StreamPlatformsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="example", password="password")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.stream = models.StreamPlatform.objects.create(
            name="stream", about="stream", website="http://example.com"
        )

    def test_streamplatform_create(self):
        data = {
            "name": "test platform",
            "description": "test",
            "website": "https://example.com",
        }

        response = self.client.post(reverse("streamplatform-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_streamplatform_list(self):
        response = self.client.get(reverse("streamplatform-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_streamplatform_detail(self):
        response = self.client.get(
            reverse("streamplatform-detail", args=(self.stream.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_streamplatform_update(self):
        response = self.client.put(
            reverse("streamplatform-detail", args=(self.stream.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_streamplatform_delete(self):
        response = self.client.delete(
            reverse("streamplatform-detail", args=(self.stream.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WatchListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="example", password="password")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.stream = models.StreamPlatform.objects.create(
            name="stream", about="stream", website="http://example.com"
        )
        self.watchlist = models.WatchList.objects.create(
            platform=self.stream,
            title="test movie",
            storyline="test movie",
            active=True,
        )

    def test_watchlist_create(self):
        data = {
            "platform": self.stream,
            "title": "test",
            "storyline": "test",
            "active": True,
        }
        response = self.client.post(reverse("movie-list"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_watchlist_list(self):
        response = self.client.get(reverse("movie-detail", args=(self.watchlist.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.WatchList.objects.count(), 1)
        self.assertEqual(models.WatchList.objects.get().title, response.data["title"])


class ReviewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="example2", password="password")
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.stream = models.StreamPlatform.objects.create(
            name="stream", about="stream", website="http://example.com"
        )
        self.watchlist = models.WatchList.objects.create(
            platform=self.stream,
            title="test movie",
            storyline="test movie",
            active=True,
        )
        self.watchlist2 = models.WatchList.objects.create(
            platform=self.stream,
            title="test movie",
            storyline="test movie",
            active=True,
        )
        self.review = models.Review.objects.create(
            review_user=self.user,
            rating=5,
            description="test revieew",
            watchlist=self.watchlist2,
            active=True,
        )

    def test_review_create(self):
        data = {
            "review_user": str(self.user),
            "rating": 5,
            "description": "test review movie",
            "watchlist": str(self.watchlist),
            "active": True,
        }
        response = self.client.post(
            reverse("review-create", args=(self.watchlist.id,)), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Review.objects.count(), 2)

        response = self.client.post(
            reverse("review-create", args=(self.watchlist.id,)), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_unauth(self):
        data = {
            "review_user": str(self.user),
            "rating": 5,
            "description": "test review movie",
            "watchlist": str(self.watchlist),
            "active": True,
        }

        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("review-create", args=(self.watchlist.id,)), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_update(self):
        data = {
            "rating": 5,
            "description": "test review movie",
            "active": True,
        }
        response = self.client.put(
            reverse("review-detail", args=(self.review.id,)), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_list(self):
        response = self.client.get(reverse("review-list", args=(self.watchlist.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_detail(self):
        response = self.client.get(reverse("review-detail", args=(self.review.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_delete_unauth(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            reverse("review-detail", args=(self.watchlist.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_delete(self):
        response = self.client.delete(
            reverse("review-detail", args=(self.watchlist.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_review_user(self):
        response = self.client.get("/watch/reviews/?username" + self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
