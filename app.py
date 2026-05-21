from __future__ import annotations

import json
import os
import re
from html import escape
from functools import wraps
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
TESTIMONIAL_DIR = BASE_DIR / "testimonial"
TESTIMONIAL_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = BASE_DIR / "index.html"
SELECTION_FILE = TESTIMONIAL_DIR / "homepage_selection.json"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
TRACKING_PATTERN = re.compile(r"^[A-Za-z0-9_-]{4,64}$")
SLIDES_START_MARKER = "<!-- TESTIMONIAL_SLIDES_START -->"
SLIDES_END_MARKER = "<!-- TESTIMONIAL_SLIDES_END -->"

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


def _check_auth(username: str, password: str) -> bool:
    return (
        username == os.getenv("BASIC_AUTH_USER")
        and password == os.getenv("BASIC_AUTH_PASSWORD")
    )


def _auth_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        expected_user = os.getenv("BASIC_AUTH_USER")
        expected_password = os.getenv("BASIC_AUTH_PASSWORD")
        if not expected_user or not expected_password:
            return Response(
                json.dumps({"error": "Missing BASIC_AUTH_USER or BASIC_AUTH_PASSWORD environment variables"}),
                503,
                {"Content-Type": "application/json"},
            )

        auth = request.authorization
        if not auth or not _check_auth(auth.username, auth.password):
            return Response(
                json.dumps({"error": "Authentication required"}),
                401,
                {"WWW-Authenticate": 'Basic realm="Testimoni Builder"', "Content-Type": "application/json"},
            )
        return view_func(*args, **kwargs)

    return wrapped


def _sanitize_tracking_code(raw_code: str) -> str:
    code = (raw_code or "").strip()
    if not TRACKING_PATTERN.match(code):
        raise ValueError(
            "Tracking code must be 4-64 chars and only contain letters, numbers, hyphen, or underscore"
        )
    return code.lower()


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _safe_rel_image(path: str) -> str | None:
    if not path:
        return None
    normalized = path.replace("\\", "/").strip("/")
    if normalized.startswith("testimonial/"):
        file_name = normalized.split("/", 1)[1]
    else:
        file_name = normalized
    if "/" in file_name:
        return None
    if "." not in file_name:
        return None
    ext = file_name.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    return f"testimonial/{file_name}"


def _parse_metadata_files() -> list[dict]:
    metadata_entries = []
    for metadata_file in TESTIMONIAL_DIR.glob("*.json"):
        if metadata_file.name == SELECTION_FILE.name:
            continue
        try:
            parsed = json.loads(metadata_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        code = parsed.get("tracking_code")
        image_rel = _safe_rel_image(parsed.get("image", ""))
        if not code or not image_rel:
            continue

        image_file = BASE_DIR / image_rel
        if not image_file.exists() or not image_file.is_file():
            continue

        metadata_entries.append(
            {
                "id": f"meta:{code}",
                "tracking_code": code,
                "customer_name": parsed.get("customer_name", ""),
                "testimonial_text": parsed.get("testimonial_text", ""),
                "image": image_rel,
                "source": "metadata",
                "updated_at": metadata_file.stat().st_mtime,
            }
        )

    metadata_entries.sort(key=lambda item: item["updated_at"], reverse=True)
    return metadata_entries


def _parse_image_only_files(excluded_images: set[str]) -> list[dict]:
    image_entries = []
    for image_file in TESTIMONIAL_DIR.iterdir():
        if not image_file.is_file():
            continue
        if image_file.suffix.lower().lstrip(".") not in ALLOWED_EXTENSIONS:
            continue

        rel_image = f"testimonial/{image_file.name}"
        if rel_image in excluded_images:
            continue

        image_entries.append(
            {
                "id": f"img:{image_file.name}",
                "tracking_code": "",
                "customer_name": "",
                "testimonial_text": "",
                "image": rel_image,
                "source": "image",
                "updated_at": image_file.stat().st_mtime,
            }
        )

    image_entries.sort(key=lambda item: item["updated_at"], reverse=True)
    return image_entries


def _load_available_testimonials() -> list[dict]:
    metadata_entries = _parse_metadata_files()
    excluded = {entry["image"] for entry in metadata_entries}
    image_entries = _parse_image_only_files(excluded)
    return metadata_entries + image_entries


def _load_selected_ids() -> list[str]:
    if not SELECTION_FILE.exists():
        return []
    try:
        data = json.loads(SELECTION_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    raw_ids = data.get("selected_ids", [])
    if not isinstance(raw_ids, list):
        return []
    return [str(item) for item in raw_ids if isinstance(item, str)]


def _save_selected_ids(selected_ids: list[str]) -> None:
    payload = {"selected_ids": selected_ids}
    SELECTION_FILE.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def _build_homepage_items(available_items: list[dict], selected_ids: list[str]) -> tuple[list[dict], bool]:
    available_by_id = {item["id"]: item for item in available_items}

    if selected_ids:
        selected_items = [available_by_id[item_id] for item_id in selected_ids if item_id in available_by_id]
        if selected_items:
            return selected_items, False

    latest_metadata = [item for item in available_items if item["source"] == "metadata"][:10]
    if latest_metadata:
        return latest_metadata, True

    fallback_images = [item for item in available_items if item["source"] == "image"][:10]
    return fallback_images, True


def _render_slides(items: list[dict]) -> str:
    if not items:
        return """        <div class=\"swiper-slide\">\n          <div class=\"bg-white rounded-2xl shadow-sm overflow-hidden flex items-center justify-center h-72 px-4 text-center text-gray-500\">\n            Belum ada testimoni untuk ditampilkan\n          </div>\n        </div>"""

    slides = []
    for item in items:
        image = item["image"]
        caption = item.get("customer_name") or "Review pelanggan Couche Home"
        alt = escape(caption)
        slides.append(
            "\n".join(
                [
                    '        <div class="swiper-slide">',
                    '          <div class="bg-white rounded-2xl shadow-sm overflow-hidden flex items-center justify-center h-72 cursor-pointer hover:shadow-md transition-shadow"',
                    f'               @click="lightboxImg=\'{image}\'">',
                    f'            <img src="{image}" alt="{alt}" class="max-h-full max-w-full object-contain" loading="lazy" />',
                    "          </div>",
                    "        </div>",
                ]
            )
        )

    return "\n".join(slides)


def _write_slides_to_index(slides_markup: str) -> None:
    if not INDEX_FILE.exists():
        return

    source = INDEX_FILE.read_text(encoding="utf-8")
    start = source.find(SLIDES_START_MARKER)
    end = source.find(SLIDES_END_MARKER)

    if start == -1 or end == -1 or end <= start:
        return

    start += len(SLIDES_START_MARKER)
    updated = source[:start] + "\n" + slides_markup + "\n      " + source[end:]
    INDEX_FILE.write_text(updated, encoding="utf-8")


def _refresh_homepage_testimonials() -> tuple[list[dict], bool]:
    available = _load_available_testimonials()
    selected_ids = _load_selected_ids()
    homepage_items, using_default = _build_homepage_items(available, selected_ids)
    _write_slides_to_index(_render_slides(homepage_items))
    return homepage_items, using_default


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/testimoni.html")
@_auth_required
def testimoni_page():
    return send_from_directory(BASE_DIR, "testimoni.html")


@app.post("/api/testimonials")
@_auth_required
def create_testimonial():
    tracking_code = request.form.get("tracking_code", "")
    testimonial_text = request.form.get("testimonial_text", "").strip()
    customer_name = request.form.get("customer_name", "").strip()
    image = request.files.get("image")

    if not testimonial_text:
        return jsonify({"error": "Testimonial text is required"}), 400
    if not customer_name:
        return jsonify({"error": "Customer name is required"}), 400
    if image is None or image.filename == "":
        return jsonify({"error": "Image is required"}), 400

    try:
        safe_code = _sanitize_tracking_code(tracking_code)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not _allowed_file(image.filename):
        return jsonify({"error": "Image must be png, jpg, jpeg, or webp"}), 400

    metadata_path = TESTIMONIAL_DIR / f"{safe_code}.json"
    if metadata_path.exists():
        return jsonify({"error": "Tracking code already exists"}), 409

    extension = secure_filename(image.filename).rsplit(".", 1)[1].lower()
    image_filename = f"{safe_code}.{extension}"
    image_path = TESTIMONIAL_DIR / image_filename

    image.save(image_path)

    payload = {
        "tracking_code": safe_code,
        "customer_name": customer_name,
        "testimonial_text": testimonial_text,
        "image": f"testimonial/{image_filename}",
    }
    metadata_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    _refresh_homepage_testimonials()

    return jsonify({"message": "Testimonial saved", "data": payload}), 201


@app.get("/api/testimonials")
@_auth_required
def get_testimonials():
    available = _load_available_testimonials()
    selected_ids = _load_selected_ids()
    homepage_items, using_default = _build_homepage_items(available, selected_ids)

    return jsonify(
        {
            "available": available,
            "selected_ids": selected_ids,
            "homepage": homepage_items,
            "using_default": using_default,
        }
    )


@app.post("/api/homepage-testimonials")
@_auth_required
def set_homepage_testimonials():
    payload = request.get_json(silent=True) or {}
    selected_ids = payload.get("selected_ids", [])

    if not isinstance(selected_ids, list):
        return jsonify({"error": "selected_ids must be a list"}), 400

    requested_ids = [str(item) for item in selected_ids if isinstance(item, str)]
    requested_ids = list(dict.fromkeys(requested_ids))
    if len(requested_ids) > 30:
        return jsonify({"error": "Maximum 30 selected testimonials"}), 400

    available_ids = {item["id"] for item in _load_available_testimonials()}
    sanitized_ids = [item_id for item_id in requested_ids if item_id in available_ids]

    _save_selected_ids(sanitized_ids)
    homepage_items, using_default = _refresh_homepage_testimonials()

    return jsonify(
        {
            "message": "Homepage testimonials updated",
            "selected_ids": sanitized_ids,
            "homepage": homepage_items,
            "using_default": using_default,
        }
    )


@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/<path:requested_path>")
def static_files(requested_path: str):
    target = BASE_DIR / requested_path
    if target.is_file():
        return send_from_directory(BASE_DIR, requested_path)
    abort(404)


if __name__ == "__main__":
    _refresh_homepage_testimonials()
    port = int(os.getenv("PORT", "80"))
    app.run(host="0.0.0.0", port=port)
