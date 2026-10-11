
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    Response
)

import json
import os

from config import Config

from services.search_engine import (
    search
)

from services.auth import (
    login_user
)

from services.email_otp import (
    start_signup,
    verify_signup_otp,
    resend_signup_otp
)

from services.history import (
    save_history,
    get_history
)


# =========================================================
# APP
# =========================================================

app = Flask(__name__)

app.config.from_object(
    Config
)


# =========================================================
# SECRET KEY
# =========================================================

if not app.config.get(
    "SECRET_KEY"
):

    app.config["SECRET_KEY"] = (
        os.environ.get(
            "SECRET_KEY"
        )
        or "vedfinder-development-secret-key"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(

        "index.html",

        query="",

        mode="normal",

        summary=None,

        knowledge=None,

        websites=[],

        images=[],

        videos=[],

        news=[],

        maps=None

    )


# =========================================================
# SEARCH
# =========================================================

@app.route(
    "/search",
    methods=[
        "GET",
        "POST"
    ]
)
def search_route():

    if request.method == "GET":

        query = request.args.get(
            "q",
            ""
        ).strip()

        mode = request.args.get(
            "mode",
            "normal"
        ).strip().lower()

    else:

        query = request.form.get(
            "query",
            ""
        ).strip()

        mode = request.form.get(
            "mode",
            "normal"
        ).strip().lower()

    if mode not in (
        "normal",
        "go"
    ):

        mode = "normal"

    if not query:

        return redirect(
            url_for(
                "home"
            )
        )

    try:

        data = search(
            query,
            mode
        )

    except Exception as error:

        print(
            "[VedFinder] Search error: "
            f"{error}"
        )

        data = {
            "mode": mode,
            "summary": None,
            "knowledge": None,
            "websites": [],
            "images": [],
            "videos": [],
            "news": [],
            "maps": None
        }

    if not isinstance(
        data,
        dict
    ):

        data = {
            "mode": mode,
            "summary": None,
            "knowledge": None,
            "websites": [],
            "images": [],
            "videos": [],
            "news": [],
            "maps": None
        }

    # -----------------------------------------------------
    # HISTORY
    # -----------------------------------------------------

    if (
        "username" in session
        and mode == "normal"
    ):

        try:

            save_history(
                session["username"],
                query
            )

        except Exception as error:

            print(
                "[VedFinder] History error: "
                f"{error}"
            )

    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render_template(

        "index.html",

        query=query,

        mode=mode,

        summary=data.get(
            "summary"
        ),

        knowledge=data.get(
            "knowledge"
        ),

        websites=data.get(
            "websites",
            []
        ),

        images=data.get(
            "images",
            []
        ),

        videos=data.get(
            "videos",
            []
        ),

        news=data.get(
            "news",
            []
        ),

        maps=data.get(
            "maps"
        )

    )


# =========================================================
# OPENSEARCH
# =========================================================

@app.route(
    "/opensearch.xml"
)
def opensearch():

    try:

        with open(
            "static/opensearch.xml",
            "r",
            encoding="utf-8"
        ) as file:

            xml = file.read()

        return Response(

            xml,

            mimetype=(
                "application/"
                "opensearchdescription+xml"
            )

        )

    except OSError as error:

        print(
            "[VedFinder] OpenSearch error: "
            f"{error}"
        )

        return Response(

            "OpenSearch configuration unavailable.",

            status=500,

            mimetype="text/plain"

        )


# =========================================================
# SUGGEST
# =========================================================

@app.route(
    "/suggest"
)
def suggest():

    query = request.args.get(
        "q",
        ""
    ).strip()

    if not query:

        response_data = [
            "",
            []
        ]

    else:

        response_data = [
            query,
            [
                query
            ]
        ]

    return Response(

        json.dumps(
            response_data,
            ensure_ascii=False
        ),

        mimetype=(
            "application/"
            "x-suggestions+json"
        )

    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)
def login():

    if request.method == "POST":

        username_or_email = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        try:

            authenticated_username = (
                login_user(
                    username_or_email,
                    password
                )
            )

        except Exception as error:

            print(
                "[VedFinder] Login error: "
                f"{error}"
            )

            authenticated_username = False

        if authenticated_username:

            session.clear()

            session["username"] = (
                authenticated_username
            )

            flash(
                "Welcome back!"
            )

            return redirect(
                url_for(
                    "dashboard"
                )
            )

        flash(
            "Invalid username or password."
        )

    return render_template(
        "login.html"
    )


# =========================================================
# SIGNUP
# =========================================================

@app.route(
    "/signup",
    methods=[
        "GET",
        "POST"
    ]
)
def signup():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm = request.form.get(
            "confirm",
            ""
        )

        if not confirm:

            confirm = request.form.get(
                "confirm_password",
                ""
            )

        if password != confirm:

            flash(
                "Passwords do not match."
            )

            return render_template(
                "signup.html"
            )

        try:

            start_signup(
                username,
                email,
                password
            )

            session[
                "pending_signup_username"
            ] = username

            session[
                "pending_signup_email"
            ] = email

            flash(
                "Verification code sent to your email."
            )

            return redirect(
                url_for(
                    "verify_otp"
                )
            )

        except Exception as error:

            print(
                "[VedFinder] Signup error: "
                f"{error}"
            )

            flash(
                str(error)
            )

    return render_template(
        "signup.html"
    )


# =========================================================
# VERIFY OTP
# =========================================================

@app.route(
    "/verify-otp",
    methods=[
        "GET",
        "POST"
    ]
)
def verify_otp():

    username = session.get(
        "pending_signup_username"
    )

    email = session.get(
        "pending_signup_email"
    )

    if not username:

        flash(
            "No active signup request."
        )

        return redirect(
            url_for(
                "signup"
            )
        )

    if request.method == "POST":

        otp = request.form.get(
            "otp",
            ""
        ).strip()

        try:

            created_username = (
                verify_signup_otp(
                    username,
                    otp
                )
            )

            session.clear()

            session["username"] = (
                created_username
            )

            flash(
                "Account created successfully!"
            )

            return redirect(
                url_for(
                    "dashboard"
                )
            )

        except Exception as error:

            print(
                "[VedFinder] OTP error: "
                f"{error}"
            )

            flash(
                str(error)
            )

    return render_template(

        "verify_otp.html",

        email=email,

        username=username

    )


# =========================================================
# RESEND OTP
# =========================================================

@app.route(
    "/resend-otp",
    methods=[
        "POST"
    ]
)
def resend_otp():

    username = session.get(
        "pending_signup_username"
    )

    if not username:

        flash(
            "No active signup request."
        )

        return redirect(
            url_for(
                "signup"
            )
        )

    try:

        resend_signup_otp(
            username
        )

        flash(
            "A new verification code has been sent."
        )

    except Exception as error:

        print(
            "[VedFinder] Resend OTP error: "
            f"{error}"
        )

        flash(
            str(error)
        )

    return redirect(
        url_for(
            "verify_otp"
        )
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route(
    "/dashboard"
)
def dashboard():

    if "username" not in session:

        return redirect(
            url_for(
                "login"
            )
        )

    try:

        history = get_history(
            session["username"]
        )

    except Exception as error:

        print(
            "[VedFinder] Dashboard history error: "
            f"{error}"
        )

        history = []

    return render_template(

        "dashboard.html",

        username=session[
            "username"
        ],

        history=history

    )


# =========================================================
# SETTINGS
# =========================================================

@app.route(
    "/settings"
)
def settings():

    if "username" not in session:

        return redirect(
            url_for(
                "login"
            )
        )

    return render_template(

        "settings.html",

        username=session[
            "username"
        ]

    )


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    flash(
        "Logged out successfully."
    )

    return redirect(
        url_for(
            "home"
        )
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def server_error(error):

    return render_template(
        "500.html"
    ), 500


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=Config.DEBUG

    )