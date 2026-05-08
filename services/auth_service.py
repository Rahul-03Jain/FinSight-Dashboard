from __future__ import annotations

from functools import wraps

from flask import redirect, session, url_for

from models.user_model import User


def get_current_user() -> User | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def authenticate_user(email: str, password: str) -> User | None:
    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    if user.password != password:
        return None
    return user

