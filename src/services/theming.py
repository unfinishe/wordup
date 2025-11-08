import os
import secrets
from typing import Optional

from sqlalchemy.engine.url import make_url
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def _resolve_database_path(app) -> Optional[str]:
    """Return the filesystem path for the configured SQLite database."""
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not database_uri:
        return None

    url = make_url(database_uri)
    if url.drivername != "sqlite":
        return None
    return url.database


def get_theming_folder(app) -> str:
    """Return the theming folder path, creating it if necessary."""
    db_path = _resolve_database_path(app)
    if not db_path or db_path == ":memory:":
        base_dir = app.instance_path
    else:
        base_dir = os.path.dirname(db_path)

    folder = os.path.join(base_dir, "theming")
    os.makedirs(folder, exist_ok=True)
    return folder


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_background_image(app, file_storage: FileStorage) -> str:
    """Persist a background image and return the stored filename."""
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided")

    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type. Allowed: PNG, JPG, JPEG, WEBP")

    ext = os.path.splitext(secure_filename(file_storage.filename))[1].lower()
    filename = f"background_{secrets.token_hex(8)}{ext}"
    target_folder = get_theming_folder(app)
    target_path = os.path.join(target_folder, filename)
    file_storage.save(target_path)
    return filename


def delete_background_image(app, filename: Optional[str]) -> None:
    if not filename:
        return
    folder = get_theming_folder(app)
    target_path = os.path.join(folder, filename)
    if os.path.exists(target_path):
        os.remove(target_path)