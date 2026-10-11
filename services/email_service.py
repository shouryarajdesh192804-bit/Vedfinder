import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


try:
    from dotenv import load_dotenv

    load_dotenv()

except Exception:
    pass


def _get_email_address():
    return (
        os.environ.get(
            "EMAIL_ADDRESS"
        )
        or os.environ.get(
            "EMAIL_USER"
        )
        or os.environ.get(
            "MAIL_USERNAME"
        )
        or ""
    ).strip()


def _get_email_password():
    return (
        os.environ.get(
            "EMAIL_APP_PASSWORD"
        )
        or os.environ.get(
            "EMAIL_PASSWORD"
        )
        or os.environ.get(
            "MAIL_PASSWORD"
        )
        or ""
    ).strip()


def send_email(
    receiver,
    subject,
    body,
):
    sender = _get_email_address()
    password = _get_email_password()

    if not sender:
        raise RuntimeError(
            "EMAIL_ADDRESS is not configured."
        )

    if not password:
        raise RuntimeError(
            "EMAIL_APP_PASSWORD is not configured."
        )

    if not receiver:
        raise ValueError(
            "Receiver email is required."
        )

    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject

    message.attach(
        MIMEText(
            body,
            "plain",
            "utf-8"
        )
    )

    try:

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=20
        ) as smtp:

            smtp.login(
                sender,
                password
            )

            smtp.sendmail(
                sender,
                [receiver],
                message.as_string()
            )

        print(
            "[VedFinder] "
            f"Email sent to {receiver}"
        )

        return True

    except smtplib.SMTPAuthenticationError:

        raise RuntimeError(
            "Gmail authentication failed. "
            "Use a Gmail App Password, not your normal Gmail password."
        )

    except smtplib.SMTPException as error:

        raise RuntimeError(
            f"Email sending failed: {error}"
        )

    except OSError as error:

        raise RuntimeError(
            f"SMTP connection failed: {error}"
        )