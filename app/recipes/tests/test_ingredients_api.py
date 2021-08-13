from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from core.models import Recipe
from recipes.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipes:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    """Test publicly accessible endpoints of the api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving ingredients"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test privately accessible ingrediant endpoints"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for authenticated user are retrieved"""
        user2 = get_user_model().objects.create_user(
            email='user2@gmail.com',
            password='password123'
        )
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Salt'
        )
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successfull(self):
        """Test wether creation of ingredient is successfull"""
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test wether ingredients validations are performed"""
        res = self.client.post(INGREDIENTS_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test filtering ingrredients by those assigned to recipes"""
        ing1 = Ingredient.objects.create(user=self.user, name='Apples')
        ing2 = Ingredient.objects.create(user=self.user, name='Turky')
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.ingredients.add(ing1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ing1)
        serializer2 = IngredientSerializer(ing2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tag_assigned_unique(self):
        """Test filtering tags assigned returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user, name="Chicken")
        Ingredient.objects.create(user=self.user, name="Cucumber")
        recipe1 = Recipe.objects.create(
            title='chicken tikka',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Chicken curry',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
