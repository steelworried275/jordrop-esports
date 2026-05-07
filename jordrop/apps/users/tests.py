from django.test import TestCase
from .models import User


class UserRoleTest(TestCase):
    def test_visitor_is_not_contributor(self):
        u = User(role=User.VISITOR)
        self.assertFalse(u.is_contributor)
        self.assertFalse(u.is_moderator)

    def test_contributor_is_contributor_not_moderator(self):
        u = User(role=User.CONTRIBUTOR)
        self.assertTrue(u.is_contributor)
        self.assertFalse(u.is_moderator)

    def test_moderator_is_both(self):
        u = User(role=User.MODERATOR)
        self.assertTrue(u.is_contributor)
        self.assertTrue(u.is_moderator)

    def test_admin_is_all(self):
        u = User(role=User.ADMIN)
        self.assertTrue(u.is_contributor)
        self.assertTrue(u.is_moderator)
        self.assertTrue(u.is_admin_role)
