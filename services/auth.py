import sqlite3
from pathlib import Path

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

DATABASE = (
    BASE_DIR
    / "database"
    / "vedfinder.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    DATABASE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(
        str(DATABASE),
        timeout=10
    )

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE USERS TABLE
# =========================================================

def init_auth_database():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            created_at TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()

    conn.close()


# =========================================================
# INITIALIZE PENDING SIGNUPS TABLE
# =========================================================

def init_pending_signups_table():

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

    conn.close()


# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(
    password
):

    return generate_password_hash(
        password
    )


# =========================================================
# USER EXISTS
# =========================================================

def user_exists(
    username=None,
    email=None
):

    init_auth_database()

    conn = get_connection()

    cur = conn.cursor()

    if username:

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            LIMIT 1
            """,
            (
                username,
            )
        )

        if cur.fetchone() is not None:

            conn.close()

            return True

    if email:

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            LIMIT 1
            """,
            (
                email.lower(),
            )
        )

        if cur.fetchone() is not None:

            conn.close()

            return True

    conn.close()

    return False


# =========================================================
# CREATE USER
# =========================================================

def create_user(
    username,
    email,
    password
):

    init_auth_database()

    username = (
        username or ""
    ).strip()

    email = (
        email or ""
    ).strip().lower()

    password = (
        password or ""
    )

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

    password_hash = hash_password(
        password
    )

    return create_user_from_hash(
        username,
        email,
        password_hash
    )


# =========================================================
# CREATE USER FROM HASH
# =========================================================

def create_user_from_hash(
    username,
    email,
    password_hash
):

    init_auth_database()

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

    if not password_hash:

        raise ValueError(
            "Password hash is required."
        )

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

    conn = get_connection()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password
            )
            VALUES
            (
                ?,
                ?,
                ?
            )
            """,
            (
                username,
                email,
                password_hash
            )
        )

        conn.commit()

    except sqlite3.IntegrityError as error:

        conn.rollback()

        message = str(
            error
        ).lower()

        if "username" in message:

            raise ValueError(
                "Username already exists."
            )

        if "email" in message:

            raise ValueError(
                "Email address already exists."
            )

        raise ValueError(
            "Could not create account."
        )

    finally:

        conn.close()

    return username


# =========================================================
# LOGIN
# =========================================================

def login_user(
    username_or_email,
    password
):

    init_auth_database()

    username_or_email = (
        username_or_email or ""
    ).strip()

    password = (
        password or ""
    )

    if not username_or_email:

        return False

    if not password:

        return False

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            username,
            password
        FROM users
        WHERE
            username = ?
            OR email = ?
        LIMIT 1
        """,
        (
            username_or_email,
            username_or_email.lower()
        )
    )

    row = cur.fetchone()

    conn.close()

    if row is None:

        return False

    stored_password = (
        row["password"]
    )

    if not stored_password:

        return False

    try:

        valid = check_password_hash(
            stored_password,
            password
        )

    except Exception:

        return False

    if not valid:

        return False

    return row["username"]


# =========================================================
# STARTUP
# =========================================================

init_auth_database()

init_pending_signups_table()