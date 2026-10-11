import hashlib
import hmac
import os
import sqlite3
import secrets
import time

from services.auth import (
    get_connection,
    create_user_from_hash,
    hash_password,
    user_exists
)

from services.email_service import (
    send_email
)


# =========================================================
# SETTINGS
# =========================================================

OTP_EXPIRY_SECONDS = int(
    os.environ.get(
        "OTP_EXPIRY_SECONDS",
        "600"
    )
)

RESEND_COOLDOWN_SECONDS = int(
    os.environ.get(
        "OTP_RESEND_COOLDOWN_SECONDS",
        "30"
    )
)


# =========================================================
# GENERATE OTP
# =========================================================

def generate_otp():

    return str(
        secrets.randbelow(900000)
        + 100000
    )


# =========================================================
# HASH OTP
# =========================================================

def _hash_otp(otp):

    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


# =========================================================
# START SIGNUP
# =========================================================

def start_signup(
    username,
    email,
    password
):

    username = (
        username or ""
    ).strip()

    email = (
        email or ""
    ).strip().lower()

    if not username:

        raise ValueError(
            "Username is required."
        )

    if not email:

        raise ValueError(
            "Email address is required."
        )

    if not password:

        raise ValueError(
            "Password is required."
        )

    if len(username) < 3:

        raise ValueError(
            "Username must be at least 3 characters."
        )

    if len(password) < 6:

        raise ValueError(
            "Password must be at least 6 characters."
        )

    # -----------------------------------------------------
    # CHECK EXISTING ACCOUNT
    # -----------------------------------------------------

    if user_exists(
        username=username
    ):

        raise ValueError(
            "Username already exists."
        )

    if user_exists(
        email=email
    ):

        raise ValueError(
            "Email address already exists."
        )

    # -----------------------------------------------------
    # CREATE OTP
    # -----------------------------------------------------

    otp = generate_otp()

    otp_hash = _hash_otp(
        otp
    )

    password_hash = hash_password(
        password
    )

    now = time.time()

    expires_at = (
        now
        + OTP_EXPIRY_SECONDS
    )

    # -----------------------------------------------------
    # SAVE PENDING SIGNUP
    # -----------------------------------------------------

    conn = get_connection()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_signups (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                email TEXT UNIQUE NOT NULL,

                password_hash TEXT NOT NULL,

                otp_hash TEXT NOT NULL,

                expires_at REAL NOT NULL,

                last_sent_at REAL NOT NULL,

                created_at TEXT
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cur.execute(
            """
            DELETE FROM pending_signups

            WHERE
                username = ?
                OR email = ?
            """,
            (
                username,
                email
            )
        )

        cur.execute(
            """
            INSERT INTO pending_signups
            (
                username,
                email,
                password_hash,
                otp_hash,
                expires_at,
                last_sent_at
            )

            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                username,
                email,
                password_hash,
                otp_hash,
                expires_at,
                now
            )
        )

        conn.commit()

    except sqlite3.IntegrityError as error:

        conn.rollback()

        raise ValueError(
            f"Could not create verification request: {error}"
        )

    finally:

        conn.close()

    # -----------------------------------------------------
    # SEND EMAIL
    # -----------------------------------------------------

    body = f"""
Welcome to VedFinder!

Your verification code is:

{otp}

This code is valid for 10 minutes.

Do not share this code with anyone.

VedFinder by Guru
Search the Future
"""

    try:

        send_email(
            email,
            "VedFinder Verification Code",
            body
        )

    except Exception:

        # Remove pending signup if email failed.

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM pending_signups

            WHERE username = ?
            """,
            (
                username,
            )
        )

        conn.commit()

        conn.close()

        raise

    return True


# =========================================================
# VERIFY OTP
# =========================================================

def verify_signup_otp(
    username,
    otp
):

    username = (
        username or ""
    ).strip()

    otp = (
        otp or ""
    ).strip()

    if not username:

        raise ValueError(
            "Signup session not found."
        )

    if not otp:

        raise ValueError(
            "Enter the verification code."
        )

    if (
        not otp.isdigit()
        or len(otp) != 6
    ):

        raise ValueError(
            "OTP must be exactly 6 digits."
        )

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pending_signups (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            otp_hash TEXT NOT NULL,

            expires_at REAL NOT NULL,

            last_sent_at REAL NOT NULL,

            created_at TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()

    cur.execute(
        """
        SELECT
            username,
            email,
            password_hash,
            otp_hash,
            expires_at

        FROM pending_signups

        WHERE username = ?

        LIMIT 1
        """,
        (
            username,
        )
    )

    row = cur.fetchone()

    if row is None:

        conn.close()

        raise ValueError(
            "Verification request not found. "
            "Please create the account again."
        )

    # -----------------------------------------------------
    # EXPIRATION
    # -----------------------------------------------------

    if time.time() > float(
        row["expires_at"]
    ):

        cur.execute(
            """
            DELETE FROM pending_signups

            WHERE username = ?
            """,
            (
                username,
            )
        )

        conn.commit()

        conn.close()

        raise ValueError(
            "OTP has expired. "
            "Please request a new code."
        )

    # -----------------------------------------------------
    # CHECK OTP
    # -----------------------------------------------------

    supplied_hash = _hash_otp(
        otp
    )

    if not hmac.compare_digest(
        supplied_hash,
        row["otp_hash"]
    ):

        conn.close()

        raise ValueError(
            "Invalid verification code."
        )

    # -----------------------------------------------------
    # CREATE REAL USER
    # -----------------------------------------------------

    try:

        created_username = (
            create_user_from_hash(
                row["username"],
                row["email"],
                row["password_hash"]
            )
        )

        cur.execute(
            """
            DELETE FROM pending_signups

            WHERE username = ?
            """,
            (
                username,
            )
        )

        conn.commit()

    except Exception:

        conn.rollback()

        conn.close()

        raise

    conn.close()

    return created_username


# =========================================================
# RESEND OTP
# =========================================================

def resend_signup_otp(
    username
):

    username = (
        username or ""
    ).strip()

    if not username:

        raise ValueError(
            "Signup session not found."
        )

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pending_signups (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            otp_hash TEXT NOT NULL,

            expires_at REAL NOT NULL,

            last_sent_at REAL NOT NULL,

            created_at TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()

    cur.execute(
        """
        SELECT
            username,
            email,
            password_hash,
            last_sent_at

        FROM pending_signups

        WHERE username = ?

        LIMIT 1
        """,
        (
            username,
        )
    )

    row = cur.fetchone()

    if row is None:

        conn.close()

        raise ValueError(
            "Verification request not found. "
            "Please create the account again."
        )

    # -----------------------------------------------------
    # RESEND COOLDOWN
    # -----------------------------------------------------

    now = time.time()

    elapsed = (
        now
        - float(row["last_sent_at"])
    )

    if elapsed < RESEND_COOLDOWN_SECONDS:

        remaining = int(
            RESEND_COOLDOWN_SECONDS
            - elapsed
        )

        conn.close()

        raise ValueError(
            f"Please wait {remaining} seconds "
            "before requesting another code."
        )

    # -----------------------------------------------------
    # NEW OTP
    # -----------------------------------------------------

    otp = generate_otp()

    otp_hash = _hash_otp(
        otp
    )

    expires_at = (
        now
        + OTP_EXPIRY_SECONDS
    )

    cur.execute(
        """
        UPDATE pending_signups

        SET
            otp_hash = ?,
            expires_at = ?,
            last_sent_at = ?

        WHERE username = ?
        """,
        (
            otp_hash,
            expires_at,
            now,
            username
        )
    )

    conn.commit()

    email = row["email"]

    conn.close()

    # -----------------------------------------------------
    # SEND NEW EMAIL
    # -----------------------------------------------------

    body = f"""
VedFinder verification code:

{otp}

This code is valid for 10 minutes.

Do not share this code with anyone.

VedFinder by Guru
Search the Future
"""

    send_email(
        email,
        "VedFinder New Verification Code",
        body
    )

    return True


# =========================================================
# COMPATIBILITY FUNCTIONS
# =========================================================

def send_otp(
    email,
    username=None
):

    """
    Compatibility helper.

    The main signup flow uses start_signup().
    """

    otp = generate_otp()

    body = f"""
VedFinder Verification Code

Your OTP is:

{otp}

This code is valid for 10 minutes.

VedFinder by Guru
Search the Future
"""

    send_email(
        email,
        "VedFinder Verification Code",
        body
    )

    return otp