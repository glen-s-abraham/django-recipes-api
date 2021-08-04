from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public paths of the API"""

    def setUP(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test wether the user is created with correct payload"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'password123',
            'name': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creation of user that already exists"""
        payload = {'email': 'test@gmail.com', 'password': 'password123'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test wether password is more than five characters"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'pw',
            'name': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
    
    def test_create_token_for_user(self):
        """Test wether a token is created for a valid user"""
        payload = {'email': 'test@gmail.com', 'password': 'password123'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL,payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created for invalid credentials"""
        create_user(email='test@gmail.com', password='password123')
        payload = {'email': 'test@gmail.com', 'password': 'wrong123'}
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created for non existent users"""
        payload = {'email': 'test@gmail.com', 'password': 'password123'}
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_password(self):
        """Test that token is not created for blank"""
        payload = {'email': 'test@gmail.com', 'password': ''}
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  
