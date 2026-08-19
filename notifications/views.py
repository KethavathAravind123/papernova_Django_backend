import os
from functools import wraps
from secrets import compare_digest
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .firebase_config import FirebaseConfigurationError, get_db
from .email_services import send_paper_notification


def require_notifications_api_key(view):
    """Protect operational endpoints from unauthenticated public requests."""
    @wraps(view)
    def wrapped_view(request, *args, **kwargs):
        expected_key = os.getenv("NOTIFICATIONS_API_KEY", "")
        supplied_key = request.headers.get("X-API-Key", "")
        if not expected_key or not compare_digest(supplied_key, expected_key):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return view(request, *args, **kwargs)

    return wrapped_view


@require_POST
@csrf_exempt
@require_notifications_api_key
def test_email(request):

    recipient_email = request.POST.get("email")

    if not recipient_email:
        return JsonResponse({
            "error": "Email is required"
        }, status=400)

    send_mail(
        subject="PaperNova Test Email",
        message="""Hello!

This is a test email from PaperNova.

The Django email system is working successfully.
""",
        from_email=None,
        recipient_list=[recipient_email],
        fail_silently=False,
    )

    return JsonResponse({
        "message": "Email sent successfully",
        "email": recipient_email
    })


@require_POST
@require_notifications_api_key
def test_firebase(request):
    try:
        users = get_db().collection("users").limit(5).stream()
    except FirebaseConfigurationError:
        return JsonResponse({"error": "Firebase is not configured"}, status=503)

    result = []

    for user in users:
        result.append(user.to_dict())

    return JsonResponse({
        "users": result
    })


@require_POST
@require_notifications_api_key
@csrf_exempt
def notify_paper_uploaded(request):

    paper_id = request.POST.get("paper_id")

    if not paper_id:
        return JsonResponse({
            "error": "paper_id is required"
        }, status=400)

    # Get the uploaded paper
    try:
        db = get_db()
        paper_ref = db.collection("papers").document(paper_id)
        paper_snapshot = paper_ref.get()
    except FirebaseConfigurationError:
        return JsonResponse({"error": "Firebase is not configured"}, status=503)

    if not paper_snapshot.exists:
        return JsonResponse({
            "error": "Paper not found",
            "paper_id": paper_id
        }, status=404)

    paper = paper_snapshot.to_dict()

    # Get paper information
    title = paper.get("title", "New Paper")
    subject = paper.get("subject", "")
    branch = paper.get("branch", "")
    year = paper.get("year", "")
    semester = paper.get("semester", "")
    paper_type = paper.get("type", "")
    university = paper.get("university", "")
    uploader_name = paper.get("uploaderName", "")
    file_url = paper.get("fileUrl", "")

    sent = 0
    failed = 0

    # Get users
    users = db.collection("users").stream()

    for user in users:

        data = user.to_dict()

        email = data.get("email")

        if not email:
            continue

        try:

            send_paper_notification(
                recipient_email=email,
                title=title,
                subject=subject,
                branch=branch,
                year=year,
                semester=semester,
                paper_type=paper_type,
                university=university,
                uploader_name=uploader_name,
                file_url=file_url,
            )

            sent += 1

        except Exception as e:

            print(f"Failed to send email to {email}: {e}")
            failed += 1

    return JsonResponse({
        "message": "Notification process completed",
        "paper_id": paper_id,
        "paper": paper,
        "sent": sent,
        "failed": failed,
    })

def home(request):
    return JsonResponse({
        "status": "success",
        "message": "PaperNova backend is running"
    })