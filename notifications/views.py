from django.core.mail import send_mail
from django.http import JsonResponse
from .firebase_config import db
from .email_services import send_paper_notification


def test_email(request):

    recipient_email = request.GET.get("email")

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


def test_firebase(request):

    users = (
        db.collection("users")
        .limit(5)
        .stream()
    )

    result = []

    for user in users:
        result.append(user.to_dict())

    return JsonResponse({
        "users": result
    })


def notify_paper_uploaded(request):

    paper_id = request.GET.get("paper_id")

    if not paper_id:
        return JsonResponse({
            "error": "paper_id is required"
        }, status=400)

    # Get the uploaded paper
    paper_ref = db.collection("papers").document(paper_id)
    paper_snapshot = paper_ref.get()

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