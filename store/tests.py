from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Customer, Favorite, Product


class FavoriteFlowTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="jane", password="secret123")
		Customer.objects.create(
			user=self.user,
			name="Jane Doe",
			email="jane@example.com",
			address="123 Palm Ave",
		)
		self.product = Product.objects.create(
			name="White Roses",
			pack_quantity="10",
			type="Roses",
			unit_price="2.50",
			description="Fresh roses",
			color="White",
			code="WR-10",
			pack_unit="st",
		)

	def test_toggle_favorite_adds_product(self):
		self.client.force_login(self.user)

		response = self.client.post(reverse("toggle_favorite", args=[self.product.pk]), {
			"next": reverse("catalog"),
		})

		self.assertRedirects(response, reverse("catalog"))
		self.assertTrue(Favorite.objects.filter(user=self.user, product=self.product).exists())

	def test_toggle_favorite_removes_existing_product(self):
		Favorite.objects.create(user=self.user, product=self.product)
		self.client.force_login(self.user)

		response = self.client.post(reverse("toggle_favorite", args=[self.product.pk]), {
			"next": f"{reverse('profile')}?tab=favorites",
		})

		self.assertRedirects(response, f"{reverse('profile')}?tab=favorites")
		self.assertFalse(Favorite.objects.filter(user=self.user, product=self.product).exists())

	def test_profile_view_exposes_favorites(self):
		favorite = Favorite.objects.create(user=self.user, product=self.product)
		self.client.force_login(self.user)

		response = self.client.get(reverse("profile"), {"tab": "favorites"})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(list(response.context["favorites"]), [favorite])
		self.assertEqual(response.context["active_tab"], "favorites")
