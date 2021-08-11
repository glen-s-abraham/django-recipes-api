from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from core.models import Tag
from core.models import Ingredient
from recipes.serializers import RecipeSerializer
from recipes.serializers import RecipeDetailSerializer

RECIPES_URL = reverse('recipes:recipe-list')


def detail_url(recipe_id):
    """return detail url for recipe"""
    return reverse('recipes:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(
        user=user,
        **defaults
    )


class PublicRecipeApiTests(TestCase):
    """Test public api endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that authentication is required for API"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test private endpoints of the api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreiving_recipes(self):
        """Test retrieve a list of recipes"""
        sample_recipe(self.user)
        sample_recipe(self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test the recipes of logged in user is retrieved"""
        user2 = get_user_model().objects.create_user(
            email='user2@gmail.com',
            password='password123'
        )
        sample_recipe(self.user)
        sample_recipe(user2)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test detaile view of a recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ing1 = sample_ingredient(user=self.user, name="Beef")
        ing2 = sample_ingredient(user=self.user, name="Butter")
        payload = {
            'title': 'Beef steak',
            'price': 20.00,
            'time_minutes': 60,
            'ingredients': [ing1.id, ing2.id],
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ings = recipe.ingredients.all()
        self.assertEqual(ings.count(), 2)
        self.assertIn(ing1, ings)
        self.assertIn(ing2, ings)

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Desert")
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_parital_update_recipe(self):
        """Test updating on recipes endpoint with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')
        payload = {
            'title': 'Chicken ticka',
            'tags': new_tag.id
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test full update on recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Sphagetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
