from django.urls import resolve, reverse
from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    # def test_list_reverse(self):
    #    """users:list should reverse to /users/."""
    #    self.assertEqual(reverse("users:list"), "/users/")

    # def test_list_resolve(self):
    #    """/users/ should resolve to users:list."""
    #    self.assertEqual(resolve("/users/").view_name, "users:list")

    def test_redirect_reverse(self):
        """users:redirect should reverse to /users/~redirect/."""
        self.assertEqual(reverse("ce_ui:user-redirect"), "/ui/user-redirect/")

    def test_redirect_resolve(self):
        """/users/~redirect/ should resolve to users:redirect."""
        self.assertEqual(
            resolve("/ui/user-redirect/").view_name, "ce_ui:user-redirect"
        )

    def test_detail_reverse(self):
        """users:detail should reverse to /users/testuser/."""
        self.assertEqual(
            reverse("ce_ui:user-detail", kwargs={"username": "testuser"}),
            "/ui/user/testuser/",
        )

    def test_detail_resolve(self):
        """/users/testuser/ should resolve to users:detail."""
        self.assertEqual(
            resolve("/ui/user/testuser/").view_name, "ce_ui:user-detail"
        )

    def test_update_reverse(self):
        """users:update should reverse to /users/~update/."""
        self.assertEqual(reverse("ce_ui:user-update"), "/ui/user-update/")

    def test_update_resolve(self):
        """/users/~update/ should resolve to users:update."""
        self.assertEqual(
            resolve("/ui/user-update/").view_name, "ce_ui:user-update"
        )
