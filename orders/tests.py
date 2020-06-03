from django.test import TestCase

from django.contrib.auth.models import User

# Create your tests here.
class UsersTestCase(TestCase):

    def setUp(self):

        # Create users.
        user = User.objects.create_user("test1", "test@domain.com", "testpass")
        u = User.objects.get(username='test1')
        
        user.last_name = "testlast"
        user.save()
        
    def test_users_count(self):
        u = User.objects.filter(username='test1').count()
        self.assertEqual(u, 1)



   