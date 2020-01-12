from django.test import TestCase
from rango.models import Category

class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        Ensures the number of views received for a Category are positive or zero.
        """
        category = Category(name='test', views=-1, likes=0)
        category.save()

        self.assertEqual((category.views >=0), True)
