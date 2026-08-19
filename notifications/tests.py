from django.test import SimpleTestCase, override_settings
from django.urls import reverse


@override_settings(SECURE_SSL_REDIRECT=False)
class NotificationEndpointSecurityTests(SimpleTestCase):
    def test_notification_endpoint_rejects_unauthenticated_requests(self):
        response = self.client.post(reverse("notify_users"), {"paper_id": "paper-1"})

        self.assertEqual(response.status_code, 401)

    def test_notification_endpoint_does_not_allow_get_requests(self):
        response = self.client.get(reverse("notify_users"))

        self.assertEqual(response.status_code, 405)
