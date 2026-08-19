import os
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class FirebaseConfigurationError(RuntimeError):
    """Raised when the Firebase service-account credentials are unavailable."""



def get_db():
    """Return Firestore only after explicitly configured credentials are available."""
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

    if service_account_json:
        try:
            service_account = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise FirebaseConfigurationError("FIREBASE_SERVICE_ACCOUNT_JSON is not valid JSON.") from exc
        credential = credentials.Certificate(service_account)
    elif service_account_path:
        credential = credentials.Certificate(service_account_path)
    else:
        raise FirebaseConfigurationError(
            "Configure FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH."
        )

    if not firebase_admin._apps:
        firebase_admin.initialize_app(credential)

    return firestore.client()
