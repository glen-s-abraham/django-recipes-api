from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipes.serializers import TagSerializer


TAGS_URL = reverse('recipes:tag-list')


class PublicTagsApiTest(TestCase):
    """Test publicly accessible endpoints of the api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test Private endpoints of api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test the tags are retrieved for authenticated users"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test the returned tags are limited to authenticated users"""
        user2 = get_user_model().objects.create_user(
            email='user2@gmail.com',
            password='password123'
        )
        tag = Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=user2, name='Desert')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successfull(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test for tag validation"""
        res = self.client.post(TAGS_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
