from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
class UserTest(TestCase):
    def test_create(self):
        user = User(
            username = "TestUser",
            password = "TestUser"
        )
        user.save()
        user = User.objects.get(username="TestUser")
        self.assertEqual(user.username, "TestUser")
        self.assertEqual(user.password, "TestUser")
