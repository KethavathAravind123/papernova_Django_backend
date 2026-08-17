from django.core.mail import send_mail


def send_paper_notification(
    recipient_email,
    title,
    subject,
    branch,
    year,
    semester,
    paper_type,
    university,
    uploader_name,
    file_url,
):

    email_subject = f"New Paper Uploaded - {title}"

    email_message = f"""
Hello!

A new paper has been uploaded to PaperNova.

Paper Details
-------------

Title: {title}
Subject: {subject}
Branch: {branch}
Year: {year}
Semester: {semester}
Type: {paper_type}
University: {university}
Uploaded by: {uploader_name}

View Paper:
{file_url}

Open PaperNova to access the paper.

Regards,
PaperNova Team
"""

    send_mail(
        subject=email_subject,
        message=email_message,
        from_email=None,
        recipient_list=[recipient_email],
        fail_silently=False,
    )