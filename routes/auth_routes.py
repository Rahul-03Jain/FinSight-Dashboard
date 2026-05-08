from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth_service import authenticate_user, get_current_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    current_user = get_current_user()
    if current_user:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        user = authenticate_user(email, password)
        if not user:
            flash("Invalid email or password. Use one of the demo accounts.", "danger")
            return render_template("login.html")

        session["user_id"] = user.id
        flash(f"Welcome back, {user.name}.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
