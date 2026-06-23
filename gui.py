import base64
import calendar
import csv
import hashlib
import html
import hmac
import json
import math
import os
import queue
import random
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.request
from urllib.parse import quote, urlsplit, urlunsplit
from pathlib import Path
import webbrowser
import threading
import tkinter as tk
from datetime import datetime, timezone
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog


APP_TITLE = "yt-dlp GUI for OSINT"
APP_VERSION = "v0.2026.0623"
APP_RELEASES_LATEST_URL = "https://github.com/jmashuque/ytdlp-gui-for-osint/releases/latest"
APP_WINDOW_WIDTH = 1180
APP_WINDOW_HEIGHT_BASE = 950
APP_WINDOW_HEIGHT_WITH_VPN = 1010
APP_WINDOW_MIN_WIDTH = 1050
APP_WINDOW_MIN_HEIGHT_BASE = 840
APP_WINDOW_MIN_HEIGHT_WITH_VPN = 900
URL_ROW_MIN_HEIGHT = 215

APP_GITHUB_LATEST_API_URL = "https://api.github.com/repos/jmashuque/ytdlp-gui-for-osint/releases/latest"
SETTINGS_SCHEMA_VERSION = 25
CAPTURE_DATE_MIN = datetime(2000, 1, 1)

ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(ROOT, "gui-settings.json")
JOBS_FILE = os.path.join(ROOT, "gui-jobs.json")
URL_BOX_PERSISTENCE_FILE = os.path.join(ROOT, "gui-url-box.txt")
UNIVERSAL_ARCHIVE_FILE = os.path.join(ROOT, "universal-download-archive.txt")
JOBS_FILE_VERSION = 2
DEFAULT_PROFILE_NAME = "Default"

DEFAULTS = {
    "script_path": os.path.join(ROOT, "script.ps1"),
    "yt_dlp_path": os.path.join(ROOT, "yt-dlp.exe"),
    "input_file": os.path.join(ROOT, "urls.txt"),
    "case_name": "Case-%datetime%",
    "cookies_file": os.path.join(ROOT, "cookies.txt"),
    "use_cookies_file": False,
    "output_root": os.path.join(ROOT, "Investigations"),
    "ffmpeg_folder": ROOT,
    "impersonate_target": "None",
    "prefer_mp4": False,
    "format_strategy": "best",
    "capture_mode": "media",
    "source_scope": "single",
    "playlist_items_enabled": False,
    "playlist_items": "",
    "playlist_order_enabled": False,
    "playlist_order": "normal",
    "max_playlist_items_enabled": False,
    "max_playlist_items": "",
    "break_on_existing": False,
    "skip_playlist_after_errors_enabled": False,
    "skip_playlist_after_errors": "",
    "archive_mode": "use",
    "max_resolution": "best",
    "gui_cache_mode": "after_run",
    "manifest_mode": "full",
    "save_playlist_metadata": False,
    "generate_url_shortcuts": False,
    "match_keywords": "",
    "reject_keywords": "",
    "failure_handling": "continue",
    "show_all_impersonate_targets": False,
    "date_after_enabled": False,
    "date_after_year": "",
    "date_after_month": "",
    "date_after_day": "",
    "date_before_enabled": False,
    "date_before_year": "",
    "date_before_month": "",
    "date_before_day": "",
    "rate_limit": "normal",
    "download_speed_limit_enabled": False,
    "download_speed_limit": "1 MiB/s",
    "retry_behavior": "normal",
    "throttle_detection_enabled": False,
    "throttled_rate": "100 KiB/s",
    "http_chunk_size_enabled": False,
    "http_chunk_size": "10 MiB",
    "concurrent_captures": "1",
    "concurrent_fragments": "1",
    "keep_partials": False,
    "write_info_json": True,
    "write_source_link": True,
    "write_description": False,
    "write_thumbnail": False,
    "write_subs": False,
    "write_auto_subs": False,
    "write_comments": False,
    "embed_metadata": False,
    "embed_thumbnail": False,
    "embed_subs": False,
    "embed_chapters": False,
    "embed_info_json": False,
    "vpn_adapter_name": "",
    "split_queue_mode": "per_group",
    "split_queue_urls_per_group": "10",
    "split_queue_group_count": "2",
    "url_preview_pacing": "10 sec + up to 15 sec jitter",
    "url_preview_thumbnail_mode": "Fast",
    "url_preview_rate_limit_thumbnails": True,
    "url_preview_cache_mode": "Temporary",
    "url_preview_playlist_mode": "Fast playlist scan",
    "url_preview_max_playlist_items": "50",
    "url_preview_timeout": "120",
}

DOWNLOAD_SPEED_MIN_BYTES = 1024
DOWNLOAD_SPEED_MAX_BYTES = 1024 ** 3
DOWNLOAD_SPEED_SLIDER_MAX = 1000
DOWNLOAD_SPEED_DEFAULT_BYTES = 1024 ** 2


DOMAIN_PRESET_SETTING_KEYS = [
    "prefer_mp4",
    "format_strategy",
    "capture_mode",
    "source_scope",
    "playlist_items_enabled",
    "playlist_items",
    "playlist_order_enabled",
    "playlist_order",
    "max_playlist_items_enabled",
    "max_playlist_items",
    "break_on_existing",
    "skip_playlist_after_errors_enabled",
    "skip_playlist_after_errors",
    "archive_mode",
    "max_resolution",
    "gui_cache_mode",
    "manifest_mode",
    "save_playlist_metadata",
    "generate_url_shortcuts",
    "match_keywords",
    "reject_keywords",
    "failure_handling",
    "date_after_enabled",
    "date_after_year",
    "date_after_month",
    "date_after_day",
    "date_before_enabled",
    "date_before_year",
    "date_before_month",
    "date_before_day",
    "rate_limit",
    "download_speed_limit_enabled",
    "download_speed_limit",
    "retry_behavior",
    "throttle_detection_enabled",
    "throttled_rate",
    "http_chunk_size_enabled",
    "http_chunk_size",
    "concurrent_captures",
    "concurrent_fragments",
    "keep_partials",
    "write_info_json",
    "write_source_link",
    "write_description",
    "write_thumbnail",
    "write_subs",
    "write_auto_subs",
    "write_comments",
    "embed_metadata",
    "embed_thumbnail",
    "embed_subs",
    "embed_chapters",
    "embed_info_json",
]

PROXY_PROTOCOL_OPTIONS = ["None", "http", "https", "socks4", "socks5"]

APP_SETTINGS_DEFAULTS = {
    "delete_cookies_on_exit": False,
    "check_vpn": False,
    "dark_mode": False,
    "case_browser_filter": "All",
    "case_browser_sort": "Name",
    "case_browser_current_only": False,
    "case_browser_icon_scale": "Medium",
    "job_persistence": True,
    "url_box_persistence": False,
    "universal_archive_enabled": False,
    "proxy_protocol": "None",
    "proxy_address": "",
    "proxy_port": "",
    "proxy_username": "",
    "proxy_password": "",
    "proxy_no_save": False,
}

DEFAULT_IMPERSONATE_TARGETS = ["None", "chrome", "edge", "firefox"]
BROWSER_COOKIE_OPTIONS = ["chrome", "edge", "firefox"]

COOKIE_ENCRYPTION_MAGIC = "YTDLP_COOKIE_ENC"
COOKIE_ENCRYPTION_VERSION = 1
COOKIE_PBKDF2_ITERATIONS = 600_000
COOKIE_SALT_BYTES = 32
COOKIE_NONCE_BYTES = 32
COOKIE_MIN_PASSWORD_LENGTH = 8

running_process = None
temp_url_file = None
last_vpn_status = "unknown"
adapter_display_map = {}
settings_store = {}
profile_menu = None
last_capture_context = {}
last_successful_case_summary = ""
job_queue = []
job_queue_window = None
job_queue_tree = None
job_queue_progress_var = None
job_queue_status_var = None
job_queue_running = False
job_queue_pause_after_current = False
job_queue_current_job_id = None
job_queue_running_processes = {}
job_queue_run_filter_ids = None
job_queue_state_loading = False
url_view_mode = "all"
url_all_view_cache = []
domain_preset_window = None
case_browser_reload_after_id = None
case_browser_active_token = None
case_browser_result_queue = queue.Queue()
case_browser_result_poller_running = False
playlist_preview_reload_after_id = None
playlist_preview_candidate_urls = []
playlist_preview_source_signature = ""
playlist_preview_loaded_signature = ""
playlist_preview_tab_loaded = False
url_preview_pending_playlist_name = ""
url_box_autoload_ready = False

FRESH_STARTUP_MESSAGES = []


def fresh_arg_requested():
    return any(str(arg).strip().lower() == "--fresh" for arg in sys.argv[1:])


def collect_fresh_output_roots_from_settings():
    output_roots = {os.path.abspath(os.path.join(ROOT, "Investigations"))}

    if not os.path.isfile(SETTINGS_FILE):
        return sorted(output_roots)

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return sorted(output_roots)

    def add_output_root(value):
        value = str(value or "").strip()
        if not value:
            return

        try:
            output_roots.add(os.path.abspath(os.path.expandvars(os.path.expanduser(value))))
        except Exception:
            pass

    if isinstance(raw, dict):
        profiles = raw.get("profiles", {})
        if isinstance(profiles, dict):
            for profile_settings in profiles.values():
                if isinstance(profile_settings, dict):
                    add_output_root(profile_settings.get("output_root"))

        add_output_root(raw.get("output_root"))

    return sorted(output_roots)


def run_fresh_startup_cleanup_if_requested():
    if not fresh_arg_requested():
        return []

    file_targets = [
        SETTINGS_FILE,
        JOBS_FILE,
        URL_BOX_PERSISTENCE_FILE,
        UNIVERSAL_ARCHIVE_FILE,
    ]
    dir_targets = []

    for output_root in collect_fresh_output_roots_from_settings():
        file_targets.append(os.path.join(output_root, "gui-captured-urls.txt"))
        file_targets.append(os.path.join(output_root, "gui-failed-urls.txt"))
        dir_targets.append(os.path.join(output_root, ".gui-cache"))

    seen = set()
    deleted_files = []
    deleted_dirs = []
    failed = []

    for target in file_targets:
        try:
            normalized = os.path.abspath(target)
        except Exception:
            normalized = str(target)

        if normalized in seen:
            continue
        seen.add(normalized)

        if not os.path.exists(normalized):
            continue

        if not os.path.isfile(normalized):
            failed.append((normalized, "not a regular file"))
            continue

        try:
            os.remove(normalized)
            deleted_files.append(normalized)
        except Exception as e:
            failed.append((normalized, str(e)))

    for target in dir_targets:
        try:
            normalized = os.path.abspath(target)
        except Exception:
            normalized = str(target)

        if normalized in seen:
            continue
        seen.add(normalized)

        if not os.path.exists(normalized):
            continue

        if not os.path.isdir(normalized):
            failed.append((normalized, "not a directory"))
            continue

        try:
            shutil.rmtree(normalized)
            deleted_dirs.append(normalized)
        except Exception as e:
            failed.append((normalized, str(e)))

    messages = [
        "--fresh was passed. Startup cleanup ran before settings/jobs were loaded.",
        f"Deleted {len(deleted_files)} file(s) and {len(deleted_dirs)} output-root cache folder(s).",
    ]

    if deleted_files:
        messages.append("Deleted files:")
        messages.extend(f"- {path}" for path in deleted_files)

    if deleted_dirs:
        messages.append("Deleted output-root cache folders:")
        messages.extend(f"- {path}" for path in deleted_dirs)

    if failed:
        messages.append("Failed:")
        messages.extend(f"- {path}: {error}" for path, error in failed)

    if not deleted_files and not deleted_dirs and not failed:
        messages.append("No existing settings/jobs/captured/failed files or output-root cache folders were found to delete.")

    return messages


FRESH_STARTUP_MESSAGES = run_fresh_startup_cleanup_if_requested()


CASE_BROWSER_TREE_BATCH_SIZE = 75
CASE_BROWSER_CARD_BATCH_SIZE = 24


def join_input_file_paths(paths):
    clean_paths = [str(path).strip().strip('"') for path in (paths or []) if str(path).strip()]
    return "; ".join(clean_paths)


def parse_input_file_paths(value=None):
    raw = input_file_var.get() if value is None else value
    raw = str(raw or "").strip()

    if not raw:
        return []

    # Existing single-file settings remain valid. Multiple selections are stored
    # as semicolon-separated paths in the visible Input File field.
    parts = [part.strip().strip('"') for part in re.split(r"[;\n]+", raw) if part.strip()]
    return parts


def get_existing_input_file_paths(value=None):
    return [path for path in parse_input_file_paths(value) if os.path.isfile(path)]


def describe_input_file_paths(paths=None):
    paths = list(paths if paths is not None else parse_input_file_paths())
    if not paths:
        return ""

    if len(paths) == 1:
        return paths[0]

    return "\n".join(f"- {path}" for path in paths)


def browse_file(var, title="Select file"):
    if var is input_file_var or str(title).lower().startswith("input file"):
        paths = filedialog.askopenfilenames(
            title=title,
            initialdir=ROOT,
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )
        if paths:
            var.set(join_input_file_paths(paths))
        return

    path = filedialog.askopenfilename(title=title)
    if path:
        var.set(path)


def browse_folder(var, title="Select folder"):
    path = filedialog.askdirectory(title=title)
    if path:
        var.set(path)


def append_log(text):
    log_box.insert("end", text)
    log_box.see("end")


def set_status(text):
    status_var.set(text)


def get_theme_colors():
    if dark_mode_var.get():
        return {
            "bg": "#1E1E1E",
            "panel": "#252526",
            "field": "#1B1B1B",
            "fg": "#F0F0F0",
            "muted": "#C8C8C8",
            "disabled": "#777777",
            "border": "#3A3A3A",
            "select_bg": "#264F78",
            "select_fg": "#FFFFFF",
            "button_bg": "#333333",
            "button_active": "#404040",
            "preflight_fg": "#7DB7FF",
            "start_fg": "#63C46B",
            "stop_fg": "#FF6B6B",
            "copy_fg": "#FFD166",
            "text_insert": "#FFFFFF",
        }

    return {
        "bg": "#F0F0F0",
        "panel": "#F0F0F0",
        "field": "#FFFFFF",
        "fg": "#000000",
        "muted": "#333333",
        "disabled": "#777777",
        "border": "#D0D0D0",
        "select_bg": "#0078D7",
        "select_fg": "#FFFFFF",
        "button_bg": "#F0F0F0",
        "button_active": "#E5E5E5",
        "preflight_fg": "#003366",
        "start_fg": "green",
        "stop_fg": "red",
        "copy_fg": "#8A6500",
        "text_insert": "#000000",
    }


def configure_tk_widget_theme(widget, colors):
    try:
        widget_class = widget.winfo_class()
    except Exception:
        return

    try:
        if widget_class in {"Frame", "Labelframe", "Toplevel"}:
            widget.configure(bg=colors["bg"])
        elif widget_class in {"Canvas"}:
            widget.configure(bg=colors["bg"], highlightbackground=colors["border"])
        elif widget_class in {"Text"}:
            widget.configure(
                bg=colors["field"],
                fg=colors["fg"],
                insertbackground=colors["text_insert"],
                selectbackground=colors["select_bg"],
                selectforeground=colors["select_fg"],
            )
        elif widget_class in {"Button"}:
            widget.configure(
                bg=colors["button_bg"],
                activebackground=colors["button_active"],
                relief="raised",
            )
        elif widget_class in {"Label"}:
            widget.configure(bg=colors["bg"], fg=colors["fg"])
        elif widget_class in {"Entry"}:
            widget.configure(
                bg=colors["field"],
                fg=colors["fg"],
                insertbackground=colors["text_insert"],
                selectbackground=colors["select_bg"],
                selectforeground=colors["select_fg"],
            )
        elif widget_class in {"Menu"}:
            widget.configure(
                bg=colors["panel"],
                fg=colors["fg"],
                activebackground=colors["select_bg"],
                activeforeground=colors["select_fg"],
            )
    except Exception:
        pass

    try:
        for child in widget.winfo_children():
            configure_tk_widget_theme(child, colors)
    except Exception:
        pass


def configure_menu_theme(menu, colors):
    try:
        menu.configure(
            bg=colors["panel"],
            fg=colors["fg"],
            activebackground=colors["select_bg"],
            activeforeground=colors["select_fg"],
            disabledforeground=colors["disabled"],
        )
    except Exception:
        pass


def configure_action_buttons_theme(colors):
    try:
        preflight_button.configure(
            fg=colors["preflight_fg"],
            activeforeground=colors["preflight_fg"],
            bg=colors["button_bg"],
            activebackground=colors["button_active"],
        )
    except Exception:
        pass

    try:
        start_button.configure(
            fg=colors["start_fg"],
            activeforeground=colors["start_fg"],
            bg=colors["button_bg"],
            activebackground=colors["button_active"],
        )
    except Exception:
        pass

    try:
        start_menu_button.configure(
            fg=colors["start_fg"],
            activeforeground=colors["start_fg"],
            bg=colors["button_bg"],
            activebackground=colors["button_active"],
        )
    except Exception:
        pass

    try:
        start_capture_split_frame.configure(bg=colors["bg"])
    except Exception:
        pass

    try:
        configure_menu_theme(start_capture_menu, colors)
    except Exception:
        pass

    try:
        stop_button.configure(
            fg=colors["stop_fg"],
            activeforeground=colors["stop_fg"],
            bg=colors["button_bg"],
            activebackground=colors["button_active"],
        )
    except Exception:
        pass

    try:
        copy_summary_button.configure(
            fg=colors["copy_fg"],
            activeforeground=colors["copy_fg"],
            bg=colors["button_bg"],
            activebackground=colors["button_active"],
            disabledforeground=colors["disabled"],
        )
    except Exception:
        pass


def apply_app_theme():
    try:
        colors = get_theme_colors()
    except Exception:
        return

    try:
        style = ttk.Style(root)

        if dark_mode_var.get():
            try:
                style.theme_use("clam")
            except Exception:
                pass
        else:
            try:
                if ORIGINAL_TTK_THEME:
                    style.theme_use(ORIGINAL_TTK_THEME)
            except Exception:
                pass

        style.configure(".", background=colors["bg"], foreground=colors["fg"])
        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabelframe", background=colors["bg"], foreground=colors["fg"], bordercolor=colors["border"])
        style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("TButton", background=colors["button_bg"], foreground=colors["fg"])
        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"])
        style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"])
        style.configure("TMenubutton", background=colors["button_bg"], foreground=colors["fg"])
        style.configure("TEntry", fieldbackground=colors["field"], foreground=colors["fg"])
        style.configure("TCombobox", fieldbackground=colors["field"], foreground=colors["fg"])
        style.configure("TScrollbar", background=colors["panel"], troughcolor=colors["bg"])
        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("Bottom.TNotebook", background=colors["bg"], borderwidth=0, tabposition="s")
        style.configure("TNotebook.Tab", background=colors["panel"], foreground=colors["fg"], padding=(12, 6))
        style.map(
            "TNotebook.Tab",
            background=[("selected", colors["field"]), ("active", colors["button_active"])],
            foreground=[("selected", colors["fg"]), ("disabled", colors["disabled"])],
        )
        style.configure("Treeview", background=colors["field"], fieldbackground=colors["field"], foreground=colors["fg"])
        style.configure("Treeview.Heading", background=colors["panel"], foreground=colors["fg"])

        style.map(
            "TButton",
            background=[("active", colors["button_active"]), ("disabled", colors["panel"])],
            foreground=[("disabled", colors["disabled"])],
        )
        style.map(
            "TCheckbutton",
            background=[("active", colors["bg"]), ("disabled", colors["bg"])],
            foreground=[("disabled", colors["disabled"])],
        )
        style.map(
            "TRadiobutton",
            background=[("active", colors["bg"]), ("disabled", colors["bg"])],
            foreground=[("disabled", colors["disabled"])],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", colors["field"])],
            foreground=[("readonly", colors["fg"])],
            selectbackground=[("readonly", colors["select_bg"])],
            selectforeground=[("readonly", colors["select_fg"])],
        )
    except Exception:
        pass

    try:
        root.configure(bg=colors["bg"])
        configure_tk_widget_theme(root, colors)
    except Exception:
        pass

    for menu in [
        menu_bar,
        file_menu,
        capture_menu,
        cookies_menu,
        tools_menu,
        profile_menu,
        settings_menu,
        help_menu,
    ]:
        try:
            configure_menu_theme(menu, colors)
        except Exception:
            pass

    configure_action_buttons_theme(colors)


def toggle_dark_mode_setting():
    apply_app_theme()
    save_app_settings(show_popup=False)


def update_window_title():
    profile_name = DEFAULT_PROFILE_NAME

    try:
        profile_name = selected_profile_var.get().strip() or DEFAULT_PROFILE_NAME
    except Exception:
        pass

    root.title(f"{APP_TITLE} - Profile: {profile_name}")


def normalize_impersonate_target(value):
    value = value.strip()
    if not value or value.lower() == "none":
        return ""

    # The "Show all targets" list displays the OS beside each target, e.g.
    # "chrome-124 (windows-10)", but yt-dlp only wants the target token.
    if " (" in value:
        value = value.split(" (", 1)[0].strip()

    return value.split()[0].lower()


def get_capture_date_max():
    now = datetime.now()
    return datetime(now.year, now.month, now.day)


def format_capture_date_for_message(date_obj):
    return date_obj.strftime("%b %d, %Y")


def normalize_capture_date(year, month, day, label):
    year = str(year).strip()
    month = str(month).strip()
    day = str(day).strip()

    if not year and not month and not day:
        return ""

    if not (year and month and day):
        raise ValueError(f"{label} date is incomplete. Select year, month, and day.")

    try:
        date_obj = datetime(int(year), int(month), int(day))
    except Exception:
        raise ValueError(f"{label} date is invalid or does not exist.")

    max_date = get_capture_date_max()

    if date_obj < CAPTURE_DATE_MIN:
        raise ValueError(f"{label} cannot be before {format_capture_date_for_message(CAPTURE_DATE_MIN)}.")

    if date_obj > max_date:
        raise ValueError(f"{label} cannot be in the future.")

    return date_obj.strftime("%Y%m%d")


def get_enabled_capture_dates():
    date_after = ""
    date_before = ""

    if date_after_enabled_var.get():
        date_after = normalize_capture_date(
            date_after_year_var.get(),
            date_after_month_var.get(),
            date_after_day_var.get(),
            "Date after",
        )

    if date_before_enabled_var.get():
        date_before = normalize_capture_date(
            date_before_year_var.get(),
            date_before_month_var.get(),
            date_before_day_var.get(),
            "Date before",
        )

    if date_after and date_before and date_after > date_before:
        raise ValueError("Date after cannot be later than Date before.")

    return date_after, date_before


def clamp_capture_date(year, month, day, default_date):
    max_date = get_capture_date_max()

    try:
        year_int = int(str(year).strip())
        month_int = int(str(month).strip())
        day_int = int(str(day).strip())
    except Exception:
        date_obj = default_date
    else:
        year_int = max(CAPTURE_DATE_MIN.year, min(max_date.year, year_int))
        month_int = max(1, min(12, month_int))
        last_day = calendar.monthrange(year_int, month_int)[1]
        day_int = max(1, min(last_day, day_int))

        date_obj = datetime(year_int, month_int, day_int)

    if date_obj < CAPTURE_DATE_MIN:
        date_obj = CAPTURE_DATE_MIN

    if date_obj > max_date:
        date_obj = max_date

    return date_obj


def get_allowed_month_values(year):
    max_date = get_capture_date_max()

    try:
        year_int = int(str(year).strip())
    except Exception:
        year_int = max_date.year

    start_month = 1
    end_month = 12

    if year_int <= CAPTURE_DATE_MIN.year:
        start_month = CAPTURE_DATE_MIN.month

    if year_int >= max_date.year:
        end_month = max_date.month

    return [f"{month:02d}" for month in range(start_month, end_month + 1)]


def get_allowed_day_values(year, month):
    max_date = get_capture_date_max()

    try:
        year_int = int(str(year).strip())
        month_int = int(str(month).strip())
    except Exception:
        year_int = max_date.year
        month_int = max_date.month

    last_day = calendar.monthrange(year_int, month_int)[1]
    start_day = 1
    end_day = last_day

    if year_int == CAPTURE_DATE_MIN.year and month_int == CAPTURE_DATE_MIN.month:
        start_day = CAPTURE_DATE_MIN.day

    if year_int == max_date.year and month_int == max_date.month:
        end_day = min(end_day, max_date.day)

    return [f"{day:02d}" for day in range(start_day, end_day + 1)]


def set_capture_date_vars(prefix, date_obj):
    if prefix == "after":
        date_after_year_var.set(str(date_obj.year))
        date_after_month_var.set(f"{date_obj.month:02d}")
        date_after_day_var.set(f"{date_obj.day:02d}")
    else:
        date_before_year_var.set(str(date_obj.year))
        date_before_month_var.set(f"{date_obj.month:02d}")
        date_before_day_var.set(f"{date_obj.day:02d}")


def get_capture_date_vars(prefix):
    if prefix == "after":
        return date_after_year_var, date_after_month_var, date_after_day_var

    return date_before_year_var, date_before_month_var, date_before_day_var


def update_date_filter_day_values(prefix, initialize_missing=False):
    try:
        year_var, month_var, day_var = get_capture_date_vars(prefix)

        default_date = CAPTURE_DATE_MIN if prefix == "after" else get_capture_date_max()

        if initialize_missing and not (year_var.get() and month_var.get() and day_var.get()):
            date_obj = default_date
        else:
            date_obj = clamp_capture_date(year_var.get(), month_var.get(), day_var.get(), default_date)

        set_capture_date_vars(prefix, date_obj)

        month_values = get_allowed_month_values(date_obj.year)
        day_values = get_allowed_day_values(date_obj.year, date_obj.month)

        if prefix == "after":
            date_after_month_menu["values"] = month_values
            date_after_day_menu["values"] = day_values
        else:
            date_before_month_menu["values"] = month_values
            date_before_day_menu["values"] = day_values

        update_capture_options_summary()
    except Exception:
        pass


def update_date_filter_states(*args):
    try:
        after_state = "readonly" if date_after_enabled_var.get() else "disabled"
        before_state = "readonly" if date_before_enabled_var.get() else "disabled"

        if date_after_enabled_var.get():
            update_date_filter_day_values("after", initialize_missing=True)

        if date_before_enabled_var.get():
            update_date_filter_day_values("before", initialize_missing=True)

        for widget in (date_after_year_menu, date_after_month_menu, date_after_day_menu):
            widget.config(state=after_state)

        for widget in (date_before_year_menu, date_before_month_menu, date_before_day_menu):
            widget.config(state=before_state)

        update_capture_options_summary()
    except Exception:
        pass


def on_date_filter_combo_changed(prefix):
    update_date_filter_day_values(prefix)


def safe_case_name(name):
    invalid_chars = '\\/:*?"<>|'
    return "".join("_" if ch in invalid_chars else ch for ch in name).strip()


def format_case_tag_list(values, fallback="none"):
    cleaned = []
    seen = set()

    for value in values or []:
        item = safe_case_name(str(value or "").strip())
        item = re.sub(r"_+", "_", item).strip("_")
        if not item or item in seen:
            continue
        seen.add(item)
        cleaned.append(item)

    return "-".join(cleaned) if cleaned else fallback


def format_case_playlist_tag(value):
    item = safe_case_name(str(value or "").strip())
    item = re.sub(r"_+", "_", item).strip("_")
    return item or "playlist"


def get_case_template_values(now=None, domains=None, presets=None, playlist=None):
    now = now or datetime.now()
    utc_now = now.astimezone(timezone.utc) if getattr(now, "tzinfo", None) else datetime.now(timezone.utc)

    return {
        "%date%": now.strftime("%Y-%m-%d"),
        "%time%": now.strftime("%H%M%S"),
        "%datetime%": now.strftime("%Y-%m-%d_%H%M%S"),
        "%utcdatetime%": utc_now.strftime("%Y%m%d_%H%M%SZ"),
        "%domains%": format_case_tag_list(domains, "domains"),
        "%presets%": format_case_tag_list(presets, "presets"),
        "%playlist%": format_case_playlist_tag(playlist),
        "%year%": now.strftime("%Y"),
        "%month%": now.strftime("%m"),
        "%day%": now.strftime("%d"),
        "%hour%": now.strftime("%H"),
        "%minute%": now.strftime("%M"),
        "%second%": now.strftime("%S"),
    }


def render_case_name_template(template, now=None, domains=None, presets=None, playlist=None):
    rendered = str(template or "").strip()

    for tag, value in get_case_template_values(now, domains=domains, presets=presets, playlist=playlist).items():
        rendered = rendered.replace(tag, value)

    return rendered


def get_resolved_case_name(now=None, domains=None, presets=None, playlist=None):
    template = case_name_var.get().strip()
    rendered = render_case_name_template(template, now=now, domains=domains, presets=presets, playlist=playlist)
    return safe_case_name(rendered)


def set_url_preview_pending_playlist_name(value):
    global url_preview_pending_playlist_name
    url_preview_pending_playlist_name = str(value or "").strip()


def consume_url_preview_pending_playlist_name():
    global url_preview_pending_playlist_name
    value = str(url_preview_pending_playlist_name or "").strip()
    url_preview_pending_playlist_name = ""
    return value


def insert_case_name_tag(tag):
    try:
        case_name_entry.insert("insert", tag)
        case_name_entry.focus_set()
    except Exception:
        current = case_name_var.get()
        case_name_var.set(f"{current}{tag}")


def append_playlist_tag_to_case_template(template):
    template = str(template or "").strip()

    if "%playlist%" in template.lower():
        return template

    return f"{template}-%playlist%" if template else "%playlist%"


def get_current_case_folder(now=None, domains=None, presets=None):
    output_root = output_root_var.get().strip()
    case_name = get_resolved_case_name(now=now, domains=domains, presets=presets)

    if not output_root:
        raise ValueError("Output Root is blank.")

    if not case_name:
        raise ValueError("Case Name is blank after resolving the template.")

    return os.path.join(output_root, case_name)


def case_folder_is_populated(case_folder):
    """Return True only when a case folder contains meaningful non-cache content."""

    if not os.path.isdir(case_folder):
        return False

    ignored_dirs = {".gui-cache", "__pycache__"}
    ignored_files = {".ds_store", "desktop.ini", "thumbs.db"}

    try:
        for root_dir, dir_names, file_names in os.walk(case_folder):
            dir_names[:] = [name for name in dir_names if name.lower() not in ignored_dirs]

            for file_name in file_names:
                if file_name.lower() in ignored_files:
                    continue
                return True
    except Exception:
        return False

    return False


def update_case_folder_preview(*args):
    try:
        output_root = output_root_var.get().strip()
        resolved_name = get_resolved_case_name()

        if not output_root:
            case_folder_preview_var.set("Resolved case folder: Output Root is blank")
            return

        if not resolved_name:
            case_folder_preview_var.set("Resolved case folder: Case name is blank after resolving template")
            return

        case_folder = os.path.join(output_root, resolved_name)

        if case_folder_is_populated(case_folder):
            case_folder_preview_var.set(f"Resolved case folder: {case_folder}  [existing case files]")
        elif os.path.isdir(case_folder):
            case_folder_preview_var.set(f"Resolved case folder: {case_folder}  [folder exists]")
        else:
            case_folder_preview_var.set(f"Resolved case folder: {case_folder}")
    except Exception as e:
        try:
            case_folder_preview_var.set(f"Resolved case folder: unavailable ({e})")
        except Exception:
            pass


def confirm_case_folder_collision(case_folder=None):
    try:
        case_folder = case_folder or get_current_case_folder()
    except Exception as e:
        messagebox.showerror("Invalid case folder", str(e))
        return False

    if case_folder_is_populated(case_folder):
        return messagebox.askyesno(
            "Existing populated case folder",
            "The resolved case folder already exists and contains files or folders:\n\n"
            f"{case_folder}\n\n"
            "Starting this capture may add files to the existing case and reuse its archive/history.\n\n"
            "Continue?",
        )

    return True


def get_tool_first_line(command, cwd=None, timeout=20):
    try:
        result = subprocess.run(
            command,
            cwd=cwd or ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout or result.stderr or "").strip()
        first_line = output.splitlines()[0].strip() if output else ""
        return {
            "command": " ".join(command),
            "exit_code": result.returncode,
            "version": first_line or "unavailable",
            "ok": result.returncode == 0 and bool(first_line),
        }
    except Exception as e:
        return {
            "command": " ".join(command),
            "exit_code": None,
            "version": f"error: {e}",
            "ok": False,
        }


def resolve_deno_executable_for_gui():
    candidate = os.path.join(ROOT, "deno.exe")
    if os.path.isfile(candidate):
        return candidate

    return shutil.which("deno.exe") or shutil.which("deno") or "deno"


def resolve_ffmpeg_executable_for_gui(tool_name):
    ffmpeg_folder = ffmpeg_folder_var.get().strip()

    if ffmpeg_folder:
        candidate = os.path.join(ffmpeg_folder, tool_name)
        if os.path.isfile(candidate):
            return candidate

    return shutil.which(tool_name) or shutil.which(os.path.splitext(tool_name)[0]) or tool_name


def query_capture_tool_versions_for_log():
    yt_dlp_path = yt_dlp_path_var.get().strip()
    ffmpeg_exe = resolve_ffmpeg_executable_for_gui("ffmpeg.exe")
    ffprobe_exe = resolve_ffmpeg_executable_for_gui("ffprobe.exe")
    deno_exe = resolve_deno_executable_for_gui()

    versions = {
        "app": APP_VERSION,
        "powershell_script": script_path_var.get().strip(),
        "yt_dlp_path": yt_dlp_path,
        "yt_dlp": get_tool_first_line([yt_dlp_path, "--version"], cwd=os.path.dirname(os.path.abspath(yt_dlp_path)) or ROOT) if yt_dlp_path else {"version": "not configured", "ok": False},
        "ffmpeg_path": ffmpeg_exe,
        "ffmpeg": get_tool_first_line([ffmpeg_exe, "-version"]),
        "ffprobe_path": ffprobe_exe,
        "ffprobe": get_tool_first_line([ffprobe_exe, "-version"]),
        "deno_path": deno_exe,
        "deno": get_tool_first_line([deno_exe, "--version"]),
    }

    return versions


def query_capture_tool_versions_for_job(settings):
    script_path = settings.get("script_path", "")
    yt_dlp_path = settings.get("yt_dlp_path", "")
    ffmpeg_folder = settings.get("ffmpeg_folder", "")

    deno_exe = os.path.join(os.path.dirname(os.path.abspath(yt_dlp_path)), "deno.exe") if yt_dlp_path else "deno"
    ffmpeg_exe = os.path.join(ffmpeg_folder, "ffmpeg.exe") if ffmpeg_folder else resolve_ffmpeg_executable_for_gui("ffmpeg.exe")
    ffprobe_exe = os.path.join(ffmpeg_folder, "ffprobe.exe") if ffmpeg_folder else resolve_ffmpeg_executable_for_gui("ffprobe.exe")

    versions = {
        "app": APP_VERSION,
        "powershell_script": script_path,
        "yt_dlp_path": yt_dlp_path,
        "yt_dlp": get_tool_first_line(
            [yt_dlp_path, "--version"],
            cwd=os.path.dirname(os.path.abspath(yt_dlp_path)) if yt_dlp_path else ROOT,
        ) if yt_dlp_path else {"version": "not configured", "ok": False},
        "ffmpeg_path": ffmpeg_exe,
        "ffmpeg": get_tool_first_line([ffmpeg_exe, "-version"]) if ffmpeg_exe else {"version": "not configured", "ok": False},
        "ffprobe_path": ffprobe_exe,
        "ffprobe": get_tool_first_line([ffprobe_exe, "-version"]) if ffprobe_exe else {"version": "not configured", "ok": False},
        "deno_path": deno_exe,
        "deno": get_tool_first_line([deno_exe, "--version"]) if deno_exe else {"version": "not configured", "ok": False},
    }

    return versions


def log_capture_tool_versions(versions):
    append_log("Tool and script versions:\n")
    append_log(f"  App: {versions.get('app', APP_VERSION)}\n")
    append_log(f"  PowerShell script: {versions.get('powershell_script', '')}\n")
    append_log(f"  yt-dlp path: {versions.get('yt_dlp_path', '')}\n")
    append_log(f"  yt-dlp: {versions.get('yt_dlp', {}).get('version', 'unavailable')}\n")
    append_log(f"  FFmpeg path: {versions.get('ffmpeg_path', '')}\n")
    append_log(f"  FFmpeg: {versions.get('ffmpeg', {}).get('version', 'unavailable')}\n")
    append_log(f"  FFprobe path: {versions.get('ffprobe_path', '')}\n")
    append_log(f"  FFprobe: {versions.get('ffprobe', {}).get('version', 'unavailable')}\n")
    append_log(f"  Deno path: {versions.get('deno_path', '')}\n")
    append_log(f"  Deno: {versions.get('deno', {}).get('version', 'unavailable')}\n\n")




def parse_universal_archive_skip_output_line(line):
    text = str(line or "").rstrip("\r\n")
    if not text.startswith("GUI_UNIVERSAL_ARCHIVE_SKIP\t"):
        return None

    parts = text.split("\t", 4)
    if len(parts) < 5:
        return None

    try:
        url_index = int(parts[1])
    except Exception:
        url_index = 0

    try:
        url_total = int(parts[2])
    except Exception:
        url_total = 0

    return {
        "url_index": url_index,
        "url_total": url_total,
        "archive_id": parts[3].strip(),
        "url": parts[4].strip(),
    }


def parse_universal_archive_skip_summary_line(line):
    text = str(line or "").rstrip("\r\n")
    if not text.startswith("GUI_UNIVERSAL_ARCHIVE_SKIP_SUMMARY\t"):
        return None

    parts = text.split("\t", 3)
    if len(parts) < 4:
        return None

    try:
        count = int(parts[1])
    except Exception:
        count = 0

    return {
        "count": count,
        "json_path": parts[2].strip(),
        "csv_path": parts[3].strip(),
    }


def format_universal_archive_skip_record_for_log(record):
    archive_id = str((record or {}).get("archive_id") or "").strip() or "unknown archive id"
    url = str((record or {}).get("url") or "").strip()
    url_index = int((record or {}).get("url_index") or 0)
    url_total = int((record or {}).get("url_total") or 0)
    prefix = f"URL {url_index}/{url_total}: " if url_index and url_total else ""
    return f"Universal archive skip detected: {prefix}{archive_id} | {url}"


def append_universal_archive_skip_summary(skip_records=None, skip_summary=None):
    skip_records = list(skip_records or [])
    skip_summary = skip_summary or {}
    count = len(skip_records) or int(skip_summary.get("count") or 0)

    append_log("Universal archive skipped items: ")
    append_log(f"{count}\n")

    if count <= 0:
        return

    for index, record in enumerate(skip_records[:50], start=1):
        archive_id = str(record.get("archive_id") or "").strip() or "unknown archive id"
        url = str(record.get("url") or "").strip()
        append_log(f"  {index}. {archive_id}")
        if url:
            append_log(f" | {url}")
        append_log("\n")

    if len(skip_records) > 50:
        append_log(f"  ... {len(skip_records) - 50} more skipped item(s) not shown.\n")

    if skip_summary.get("json_path"):
        append_log(f"Universal archive skip JSON: {skip_summary.get('json_path')}\n")
    if skip_summary.get("csv_path"):
        append_log(f"Universal archive skip CSV: {skip_summary.get('csv_path')}\n")


def is_case_verification_ignored_path(path):
    try:
        parts = {part.lower() for part in os.path.normpath(path).split(os.sep)}
        return ".gui-cache" in parts or "manifests" in parts
    except Exception:
        lowered = str(path).lower()
        return ".gui-cache" in lowered or "manifests" in lowered


def count_case_files(case_folder):
    counts = {
        "files": 0,
        "media": 0,
        "metadata": 0,
        "logs": 0,
        "manifests": 0,
    }

    if not os.path.isdir(case_folder):
        return counts

    for root_dir, dir_names, file_names in os.walk(case_folder):
        dir_names[:] = [name for name in dir_names if name.lower() not in {"__pycache__", ".gui-cache"}]

        for file_name in file_names:
            path = os.path.join(root_dir, file_name)
            ext = os.path.splitext(file_name)[1].lower()
            counts["files"] += 1

            if is_browser_media_file(path):
                counts["media"] += 1
            elif ext == ".json":
                counts["metadata"] += 1
            elif ext == ".log":
                counts["logs"] += 1
            elif "manifest" in file_name.lower():
                counts["manifests"] += 1

    return counts


def build_case_summary_text(exit_code, submitted_url_count, paths, versions, counts, settings=None, universal_skip_records=None, universal_skip_summary=None):
    settings = settings if isinstance(settings, dict) else {}

    def setting_value(key, fallback):
        if key in settings:
            return settings.get(key)
        return fallback

    lines = [
        "yt-dlp GUI for OSINT - Case Summary",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"App version: {APP_VERSION}",
        f"Exit code: {exit_code}",
        f"Submitted URLs: {submitted_url_count}",
        "",
        "Case paths:",
        f"  Case folder: {paths.get('case_folder', '')}",
        f"  Media folder: {paths.get('media_folder', '')}",
        f"  Logs folder: {paths.get('logs_folder', '')}",
        f"  Manifests folder: {paths.get('manifests_folder', '')}",
        f"  Download archive: {paths.get('download_archive', '')}",
        f"  Universal archive: {paths.get('universal_archive', UNIVERSAL_ARCHIVE_FILE)}",
        "",
        "Counts:",
        f"  Total files: {counts.get('files', 0)}",
        f"  Media files: {counts.get('media', 0)}",
        f"  Metadata JSON files: {counts.get('metadata', 0)}",
        f"  Log files: {counts.get('logs', 0)}",
        f"  Manifest files: {counts.get('manifests', 0)}",
        f"  Universal archive skipped items: {len(list(universal_skip_records or [])) or int((universal_skip_summary or {}).get('count') or 0)}",
        "",
        "Tools:",
        f"  PowerShell script: {versions.get('powershell_script', '')}",
        f"  yt-dlp path: {versions.get('yt_dlp_path', '')}",
        f"  yt-dlp: {versions.get('yt_dlp', {}).get('version', 'unavailable')}",
        f"  FFmpeg path: {versions.get('ffmpeg_path', '')}",
        f"  FFmpeg: {versions.get('ffmpeg', {}).get('version', 'unavailable')}",
        f"  FFprobe path: {versions.get('ffprobe_path', '')}",
        f"  FFprobe: {versions.get('ffprobe', {}).get('version', 'unavailable')}",
        f"  Deno path: {versions.get('deno_path', '')}",
        f"  Deno: {versions.get('deno', {}).get('version', 'unavailable')}",
        "",
        "Capture options:",
        f"  Profile: {setting_value('_profile_name', selected_profile_var.get())}",
        f"  Case name template: {setting_value('case_name', case_name_var.get())}",
        f"  Resolved case name: {os.path.basename(paths.get('case_folder', ''))}",
        f"  Capture mode: {setting_value('capture_mode', capture_mode_var.get())}",
        f"  Format strategy: {setting_value('format_strategy', format_strategy_var.get())}",
        f"  Source scope: {setting_value('source_scope', source_scope_var.get())}",
        f"  Archive mode: {setting_value('archive_mode', archive_mode_var.get())}",
        f"  Universal archive: {'enabled; used with Archive Mode = Use and synced to the case archive' if universal_archive_enabled_var.get() else 'disabled'}",
        f"  Max resolution: {setting_value('max_resolution', max_resolution_var.get())}",
        f"  Display cache: {setting_value('gui_cache_mode', gui_cache_mode_var.get())}",
        f"  File manifest: {setting_value('manifest_mode', manifest_mode_var.get())}",
        f"  Failure handling: {setting_value('failure_handling', failure_handling_var.get())}",
        f"  Rate limit: {setting_value('rate_limit', rate_limit_var.get())}",
        f"  Download speed limit: {'enabled' if download_speed_limit_enabled_var.get() else 'disabled'}; {setting_value('download_speed_limit', download_speed_limit_var.get())}",
        f"  Retry behavior: {setting_value('retry_behavior', retry_behavior_var.get())}",
        f"  Throttle detection: {'enabled' if throttle_detection_enabled_var.get() else 'disabled'}; {setting_value('throttled_rate', throttled_rate_var.get())}",
        f"  HTTP chunk size: {'enabled' if http_chunk_size_enabled_var.get() else 'disabled'}; {setting_value('http_chunk_size', http_chunk_size_var.get())}",
        f"  Concurrent captures: {setting_value('concurrent_captures', concurrent_captures_var.get())}",
        f"  Concurrent fragments: {setting_value('concurrent_fragments', concurrent_fragments_var.get())}",
        f"  Impersonate target: {setting_value('impersonate_target', impersonate_var.get())}",
        f"  Proxy: {get_proxy_status_summary()}",
        f"  VPN check: {'enabled' if check_vpn_var.get() else 'disabled'}",
    ]

    return "\n".join(lines)


def copy_case_summary():
    if not last_successful_case_summary:
        messagebox.showinfo("No successful summary", "No successful case summary is available yet.")
        return

    root.clipboard_clear()
    root.clipboard_append(last_successful_case_summary)
    append_log("\nCase summary copied to clipboard.\n")


def get_expected_run_paths():
    case_folder = get_current_case_folder()
    return {
        "case_folder": case_folder,
        "media_folder": os.path.join(case_folder, "media"),
        "logs_folder": os.path.join(case_folder, "logs"),
        "manifests_folder": os.path.join(case_folder, "manifests"),
        "download_archive": os.path.join(case_folder, "download-archive.txt"),
        "universal_archive": UNIVERSAL_ARCHIVE_FILE,
    }


def open_output_folder():
    path = output_root_var.get().strip()
    if os.path.isdir(path):
        os.startfile(path)
    else:
        messagebox.showwarning("Folder not found", "Output root folder does not exist.")


def open_current_case_folder():
    try:
        path = get_current_case_folder()
    except Exception as e:
        messagebox.showerror("Invalid case path", str(e))
        return

    if os.path.isdir(path):
        os.startfile(path)
    else:
        messagebox.showwarning(
            "Case folder not found",
            f"The current case folder does not exist yet:\n\n{path}",
        )


def delete_current_case_folder():
    try:
        case_folder = get_current_case_folder()
    except Exception as e:
        messagebox.showerror("Invalid case path", str(e))
        return

    if not os.path.isdir(case_folder):
        messagebox.showinfo(
            "Case folder not found",
            f"The current case folder does not exist:\n\n{case_folder}",
        )
        return

    confirm = messagebox.askyesno(
        "Delete current case folder?",
        "This will permanently delete the current case folder and all files inside it:\n\n"
        f"{case_folder}\n\n"
        "Continue?",
    )

    if not confirm:
        return

    try:
        shutil.rmtree(case_folder)
        append_log(f"\nDeleted case folder: {case_folder}\n")
        messagebox.showinfo("Deleted", "The current case folder was deleted.")
    except Exception as e:
        messagebox.showerror("Delete failed", f"Could not delete the case folder:\n\n{e}")


def write_temp_url_input_file(lines, prefix="yt-dlp-gui-urls-"):
    global temp_url_file

    clean_lines = [
        str(line).strip()
        for line in (lines or [])
        if str(line).strip() and not str(line).strip().startswith("#")
    ]

    if not clean_lines:
        raise ValueError("No usable URLs were found.")

    fd, path = tempfile.mkstemp(prefix=prefix, suffix=".txt", text=True)
    os.close(fd)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(clean_lines))
        f.write("\n")

    temp_url_file = path
    return path


def create_url_input_file():
    pasted = urls_text.get("1.0", "end").strip()

    if pasted:
        lines = []
        for line in pasted.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                lines.append(line)

        if not lines:
            raise ValueError("The pasted URL box does not contain any usable URLs.")

        return write_temp_url_input_file(lines)

    input_paths = parse_input_file_paths()

    if not input_paths:
        return ""

    if len(input_paths) == 1:
        return input_paths[0]

    combined_lines = []
    for input_path in input_paths:
        if not os.path.isfile(input_path):
            continue
        for line in read_text_file_best_effort(input_path, log_errors=True).splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                combined_lines.append(line)

    if not combined_lines:
        raise ValueError("The selected Input File entries did not contain any usable URLs.")

    append_log(f"\nCombined {len(input_paths)} input files into a temporary capture URL file.\n")
    return write_temp_url_input_file(combined_lines, prefix="yt-dlp-gui-multi-urls-")


def create_url_input_file_from_lines(lines):
    clean_lines = [
        str(line).strip()
        for line in (lines or [])
        if str(line).strip() and not str(line).strip().startswith("#")
    ]

    if not clean_lines:
        raise ValueError("The queue job does not contain any usable URLs.")

    fd, path = tempfile.mkstemp(prefix="yt-dlp-gui-queue-urls-", suffix=".txt", text=True)
    os.close(fd)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(clean_lines))
        f.write("\n")

    return path


def count_submitted_urls():
    pasted = urls_text.get("1.0", "end").strip()

    if pasted:
        return len([
            line for line in pasted.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ])

    input_paths = get_existing_input_file_paths()
    if input_paths:
        try:
            total = 0
            for input_path in input_paths:
                total += len([
                    line for line in read_text_file_best_effort(input_path, log_errors=True).splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ])
            return total
        except Exception:
            return "Unknown"

    return 0


def normalize_url_box_text_block(content):
    # Keep intentional internal line structure, but remove outer blank lines so
    # Load/Append can be composed without introducing visual blank rows.
    return str(content or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def append_text_to_urls_box(content):
    content = normalize_url_box_text_block(content)

    if not content:
        return

    existing = normalize_url_box_text_block(urls_text.get("1.0", "end"))

    if existing:
        urls_text.delete("1.0", "end")
        urls_text.insert("1.0", existing + "\n" + content)
    else:
        urls_text.delete("1.0", "end")
        urls_text.insert("1.0", content)


def read_one_input_file_for_url_box(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read(), "utf-8-sig", path
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="cp1252") as f:
                return f.read(), "cp1252", path
        except Exception as e:
            messagebox.showerror("Read error", f"Could not read input file:\n\n{path}\n\n{e}")
            return None, None, path
    except Exception as e:
        messagebox.showerror("Read error", f"Could not read input file:\n\n{path}\n\n{e}")
        return None, None, path


def read_input_file_for_url_box(prompt_if_missing=True):
    paths = get_existing_input_file_paths()

    if not paths:
        if not prompt_if_missing:
            messagebox.showerror("Input file not found", "Input File is missing or invalid.")
            return None, None, ""

        selected_paths = filedialog.askopenfilenames(
            title="Select URL input file(s)",
            initialdir=ROOT,
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )

        if not selected_paths:
            append_log("\nURL input file selection canceled. URL box was not changed.\n")
            return None, None, ""

        paths = list(selected_paths)
        input_file_var.set(join_input_file_paths(paths))

    contents = []
    encodings = set()
    readable_paths = []

    for path in paths:
        content, encoding_name, read_path = read_one_input_file_for_url_box(path)
        if content is None:
            continue
        contents.append(normalize_url_box_text_block(content))
        encodings.add(encoding_name)
        readable_paths.append(read_path)

    if not contents:
        return None, None, describe_input_file_paths(paths)

    combined = "\n".join(part for part in contents if part)
    encoding_label = "mixed" if len(encodings) > 1 else next(iter(encodings), "utf-8-sig")
    return combined, encoding_label, describe_input_file_paths(readable_paths)


def load_urls_from_input_file():
    content, encoding_name, path = read_input_file_for_url_box(prompt_if_missing=True)

    if content is None:
        return

    urls_text.delete("1.0", "end")
    urls_text.insert("1.0", normalize_url_box_text_block(content))
    append_log(f"\nLoaded URLs from input file(s) and replaced the URL box contents:\n{path}\n")


def append_urls_from_input_file():
    content, encoding_name, path = read_input_file_for_url_box(prompt_if_missing=True)

    if content is None:
        return

    append_text_to_urls_box(content)
    if encoding_name == "cp1252":
        append_log(f"\nLoaded URLs from input file(s) using cp1252 fallback and appended them to the URL box:\n{path}\n")
    elif encoding_name == "mixed":
        append_log(f"\nLoaded URLs from input file(s) using mixed encoding fallbacks and appended them to the URL box:\n{path}\n")
    else:
        append_log(f"\nLoaded URLs from input file(s) and appended them to the URL box:\n{path}\n")


def url_box_text_is_empty():
    try:
        return not normalize_url_box_text_block(urls_text.get("1.0", "end"))
    except Exception:
        return True


def set_url_box_text_silent(content):
    content = normalize_url_box_text_block(content)
    urls_text.delete("1.0", "end")
    if content:
        urls_text.insert("1.0", content)

    try:
        urls_text.edit_modified(False)
    except Exception:
        pass


def read_valid_input_files_for_url_box_silent():
    paths = get_existing_input_file_paths()

    if not paths:
        return "", ""

    contents = []
    readable_paths = []

    for path in paths:
        content = normalize_url_box_text_block(read_text_file_best_effort(path, log_errors=False))
        if not content:
            continue

        contents.append(content)
        readable_paths.append(path)

    combined = normalize_url_box_text_block("\n".join(contents))

    if not combined or not extract_urls_from_text(combined):
        return "", describe_input_file_paths(readable_paths or paths)

    return combined, describe_input_file_paths(readable_paths)


def load_url_box_persistence_if_enabled():
    if not url_box_persistence_var.get():
        return False

    if not os.path.isfile(URL_BOX_PERSISTENCE_FILE):
        return False

    try:
        content = Path(URL_BOX_PERSISTENCE_FILE).read_text(encoding="utf-8-sig")
        set_url_box_text_silent(content)
        return True
    except Exception as e:
        try:
            append_log(f"\nWARNING: Could not load URL Box Persistence file:\n{URL_BOX_PERSISTENCE_FILE}\n{e}\n")
        except Exception:
            pass
        return False


def save_url_box_persistence_if_enabled():
    if not url_box_persistence_var.get():
        return

    try:
        content = urls_text.get("1.0", "end-1c").replace("\r\n", "\n").replace("\r", "\n")
        Path(URL_BOX_PERSISTENCE_FILE).write_text(content, encoding="utf-8")
    except Exception as e:
        try:
            append_log(f"\nWARNING: Could not save URL Box Persistence file:\n{URL_BOX_PERSISTENCE_FILE}\n{e}\n")
        except Exception:
            pass


def auto_populate_url_box_from_input_files_if_empty():
    if not url_box_text_is_empty():
        return False

    content, _path_label = read_valid_input_files_for_url_box_silent()

    if not content:
        return False

    set_url_box_text_silent(content)
    try:
        schedule_playlist_preview_autoload()
    except Exception:
        pass
    return True


def initialize_url_box_from_persistence_and_input_files():
    global url_box_autoload_ready

    load_url_box_persistence_if_enabled()
    auto_populate_url_box_from_input_files_if_empty()
    url_box_autoload_ready = True


def handle_input_file_var_changed(*args):
    try:
        schedule_playlist_preview_autoload()
    except Exception:
        pass

    if not url_box_autoload_ready:
        return

    auto_populate_url_box_from_input_files_if_empty()


def save_urls_to_input_file():
    content = urls_text.get("1.0", "end").strip()

    if not content:
        messagebox.showwarning("No URLs", "The URL box is empty.")
        return

    current_input_file = input_file_var.get().strip()
    initial_dir = ROOT
    initial_file = f"{safe_case_name(case_name_var.get().strip() or 'urls')}_urls.txt"

    if current_input_file:
        try:
            current_input_paths = parse_input_file_paths(current_input_file)
            first_input_path = current_input_paths[0] if current_input_paths else current_input_file
            initial_dir = os.path.dirname(os.path.abspath(first_input_path)) or ROOT
            initial_file = os.path.basename(first_input_path) or initial_file
        except Exception:
            pass

    path = filedialog.asksaveasfilename(
        title="Save URLs to file",
        defaultextension=".txt",
        initialdir=initial_dir,
        initialfile=initial_file,
        filetypes=[
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )

    if not path:
        return

    try:
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            f.write("\n")

        input_file_var.set(path)
        append_log(f"\nSaved URL box contents to file: {path}\n")
    except Exception as e:
        messagebox.showerror("Save failed", f"Could not save URLs to file:\n\n{e}")


def save_urls_to_file():
    save_urls_to_input_file()


def clear_urls():
    urls_text.delete("1.0", "end")
    append_log("\nCleared URL box.\n")


def strip_url_extra_ampersand_tags():
    content = urls_text.get("1.0", "end").strip()

    if not content:
        messagebox.showwarning("No URLs", "The URL box is empty.")
        return

    output_lines = []
    changed = 0
    parameter_pattern = re.compile(r"&[A-Za-z][A-Za-z0-9_-]*=")

    for line in content.splitlines():
        original_line = line
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith("#"):
            output_lines.append(original_line)
            continue

        decoded_line = html.unescape(stripped_line)
        match = parameter_pattern.search(decoded_line)

        if match:
            new_url = decoded_line[:match.start()]
        else:
            new_url = decoded_line

        if new_url != stripped_line:
            changed += 1

        output_lines.append(new_url)

    urls_text.delete("1.0", "end")
    urls_text.insert("1.0", "\n".join(output_lines).strip() + "\n")
    append_log(f"\nStripped parameter-like ampersand tags from {changed} URL(s) in the URL box.\n")


def clean_extracted_url(url):
    cleaned = html.unescape(str(url or "").strip())
    cleaned = cleaned.strip(" \t\r\n<>'\"")
    cleaned = cleaned.rstrip(".,;)]}")
    return cleaned


def extract_urls_from_text(text_value):
    text_value = str(text_value or "")
    starts = [match.start() for match in re.finditer(r"https?://", text_value, flags=re.IGNORECASE)]
    urls = []

    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text_value)
        segment = text_value[start:end]
        delimiter_match = re.search(r"[\s,;|<>'\"]", segment)
        if delimiter_match:
            segment = segment[:delimiter_match.start()]
        url = clean_extracted_url(segment)
        if url:
            urls.append(url)

    return urls


def normalize_url_for_compare(url):
    url = clean_extracted_url(url)
    try:
        parsed = urlsplit(url)
    except Exception:
        return url.strip().lower()

    scheme = (parsed.scheme or "").lower()
    netloc = (parsed.netloc or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    fragment = ""

    normalized = urlunsplit((scheme, netloc, path, query, fragment))
    if normalized.endswith("/"):
        normalized = normalized[:-1]
    return normalized


def url_shape_is_valid(url):
    try:
        parsed = urlsplit(clean_extracted_url(url))
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and "." in parsed.netloc
    except Exception:
        return False


def read_text_file_best_effort(path, log_errors=False):
    path = str(path or "").strip().strip('"')

    if not path:
        return ""

    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            return Path(path).read_text(encoding="cp1252")
        except Exception as e:
            if log_errors:
                append_log(f"\nWARNING: Could not read text file with cp1252 fallback: {path}\n{e}\n")
            return ""
    except Exception as e:
        if log_errors:
            append_log(f"\nWARNING: Could not read text file: {path}\n{e}\n")
        return ""


def get_current_url_source_text():
    pasted = urls_text.get("1.0", "end").strip()
    if pasted:
        return pasted

    input_paths = get_existing_input_file_paths()
    if input_paths:
        return "\n".join(
            normalize_url_box_text_block(read_text_file_best_effort(path, log_errors=True))
            for path in input_paths
        )

    return ""


def get_current_url_list_for_tools(use_all_cache=True):
    if use_all_cache and url_view_mode == "failed" and url_all_view_cache:
        return list(url_all_view_cache)

    pasted = urls_text.get("1.0", "end").strip()
    pasted_urls = extract_urls_from_text(pasted)

    if pasted_urls:
        return pasted_urls

    input_paths = get_existing_input_file_paths()
    if input_paths:
        urls = []
        for input_path in input_paths:
            urls.extend(extract_urls_from_text(read_text_file_best_effort(input_path, log_errors=True)))
        return urls

    return []


def set_url_box_urls(urls, include_group_headers=False):
    urls_text.delete("1.0", "end")
    if not urls:
        return

    urls_text.insert("1.0", "\n".join(urls).strip())


def get_gui_failed_urls_path(output_root=None):
    root_path = output_root or output_root_var.get().strip()
    return os.path.join(root_path, "gui-failed-urls.txt") if root_path else ""


def get_gui_captured_urls_path(output_root=None):
    root_path = output_root or output_root_var.get().strip()
    return os.path.join(root_path, "gui-captured-urls.txt") if root_path else ""


def parse_gui_url_record_line(line):
    line = str(line or "").strip()
    if not line:
        return None

    parts = line.split("\t")
    url = ""
    case_name = ""
    status = ""
    detail = ""

    if len(parts) >= 4 and parts[3].lower().startswith(("http://", "https://")):
        status = parts[1] if len(parts) > 1 else ""
        case_name = parts[2] if len(parts) > 2 else ""
        url = parts[3]
        detail = parts[4] if len(parts) > 4 else ""
    else:
        found = extract_urls_from_text(line)
        if found:
            url = found[0]
            case_name = parts[2] if len(parts) > 2 else ""

    if not url:
        return None

    return {
        "case": case_name,
        "status": status,
        "url": clean_extracted_url(url),
        "detail": detail,
        "normalized": normalize_url_for_compare(url),
    }


def read_gui_url_records(path):
    records = []
    if not path or not os.path.isfile(path):
        return records

    for line in read_text_file_best_effort(path).splitlines():
        record = parse_gui_url_record_line(line)
        if record:
            records.append(record)

    return records


def get_failed_url_records():
    return read_gui_url_records(get_gui_failed_urls_path())


def get_captured_url_records():
    records = read_gui_url_records(get_gui_captured_urls_path())

    output_root = output_root_var.get().strip()
    if output_root and os.path.isdir(output_root):
        try:
            for log_path in Path(output_root).rglob("*.log"):
                text_value = read_text_file_best_effort(log_path)
                for line in text_value.splitlines():
                    if line.startswith("GUI_QUEUE_URL_COMPLETE\t"):
                        found = extract_urls_from_text(line)
                        for url in found:
                            records.append({
                                "case": log_path.parent.parent.name if log_path.parent else "",
                                "status": "captured",
                                "url": clean_extracted_url(url),
                                "detail": "run log",
                                "normalized": normalize_url_for_compare(url),
                            })
        except Exception:
            pass

    return records


def toggle_failed_url_view():
    global url_view_mode, url_all_view_cache

    if url_view_mode == "all":
        url_all_view_cache = get_current_url_list_for_tools(use_all_cache=False)
        base_set = {normalize_url_for_compare(url) for url in url_all_view_cache}
        failed_records = get_failed_url_records()

        failed_urls = []
        seen = set()

        for record in failed_records:
            normalized = record.get("normalized", "")
            if base_set and normalized not in base_set:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            failed_urls.append(record["url"])

        if not failed_urls:
            messagebox.showinfo("No failed URLs", "No failed URLs were found for the current Output Root/current URL set.")
            return

        set_url_box_urls(failed_urls)
        url_view_mode = "failed"
        try:
            failed_url_toggle_button.config(text="All")
        except Exception:
            pass
        append_log(f"\nShowing {len(failed_urls)} failed URL(s) in the URL box.\n")
        return

    set_url_box_urls(url_all_view_cache)
    url_view_mode = "all"
    try:
        failed_url_toggle_button.config(text="Failed")
    except Exception:
        pass
    append_log("\nRestored all URLs in the URL box.\n")


def group_urls_by_tld():
    urls = get_current_url_list_for_tools(use_all_cache=False)
    if not urls:
        messagebox.showwarning("No URLs", "No URLs are available to group.")
        return

    groups = {}
    order = []

    for url in urls:
        domain = get_url_domain_key(url) or "unknown"
        if domain not in groups:
            groups[domain] = []
            order.append(domain)
        groups[domain].append(url)

    output_lines = []
    for domain in sorted(order):
        output_lines.append(f"# {domain}")
        output_lines.extend(groups[domain])
        output_lines.append("")

    urls_text.delete("1.0", "end")
    urls_text.insert("1.0", "\n".join(output_lines).strip())
    append_log(f"\nGrouped {len(urls)} URL(s) by {len(groups)} domain(s).\n")


def show_url_statistics():
    urls = get_current_url_list_for_tools(use_all_cache=False)
    if not urls:
        messagebox.showinfo("URL Statistics", "No URLs found.")
        return

    counts = {}
    for url in urls:
        domain = get_url_domain_key(url) or "unknown"
        counts[domain] = counts.get(domain, 0) + 1

    lines = [
        f"Total URLs: {len(urls)}",
        f"Unique URLs: {len({normalize_url_for_compare(url) for url in urls})}",
        f"Domains: {len(counts)}",
        "",
        "Total by domain:",
    ]
    for domain, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"  {domain}: {count}")

    dialog = tk.Toplevel(root)
    dialog.title("URL Statistics")
    dialog.geometry("560x420")
    dialog.minsize(460, 320)

    box = scrolledtext.ScrolledText(dialog, wrap="word")
    box.pack(fill="both", expand=True, padx=12, pady=12)
    box.insert("1.0", "\n".join(lines))
    box.configure(state="disabled")

    ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=(0, 12))


def remove_duplicate_urls_from_box():
    source_text = get_current_url_source_text()
    if not source_text.strip():
        messagebox.showwarning("No URLs", "No URL text or input file contents were found.")
        return

    extracted = extract_urls_from_text(source_text)
    output_urls = []
    seen = set()
    duplicate_count = 0

    for url in extracted:
        cleaned = clean_extracted_url(url)
        normalized = normalize_url_for_compare(cleaned)
        if normalized in seen:
            duplicate_count += 1
            continue
        seen.add(normalized)
        output_urls.append(cleaned)

    set_url_box_urls(output_urls)
    messagebox.showinfo(
        "Duplicates Removed",
        f"Unique URLs kept: {len(output_urls)}\nDuplicates removed: {duplicate_count}",
    )
    append_log(f"\nRemoved {duplicate_count} duplicate URL(s); kept {len(output_urls)} unique URL(s).\n")


def analyze_url_source_text(source_text):
    source_text = str(source_text or "")

    extracted = extract_urls_from_text(source_text)
    invalid_lines = []

    for line in source_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not extract_urls_from_text(stripped):
            invalid_lines.append(stripped)

    seen = set()
    valid_urls = []
    duplicate_count = 0
    invalid_url_shapes = []

    for url in extracted:
        cleaned = clean_extracted_url(url)
        normalized = normalize_url_for_compare(cleaned)

        if normalized in seen:
            duplicate_count += 1
        else:
            seen.add(normalized)

        if not url_shape_is_valid(cleaned):
            invalid_url_shapes.append(cleaned)
            continue

        valid_urls.append(cleaned)

    captured_records = get_captured_url_records()
    captured_by_url = {}

    for record in captured_records:
        captured_by_url.setdefault(record.get("normalized", ""), []).append(record)

    already_captured = [
        url for url in valid_urls
        if normalize_url_for_compare(url) in captured_by_url
    ]

    return {
        "valid_urls": valid_urls,
        "duplicate_count": duplicate_count,
        "invalid_lines": invalid_lines,
        "invalid_url_shapes": invalid_url_shapes,
        "already_captured": already_captured,
        "captured_by_url": captured_by_url,
    }


def build_url_validation_messages(analysis, normalized=False):
    valid_urls = analysis["valid_urls"]
    duplicate_count = analysis["duplicate_count"]
    invalid_lines = analysis["invalid_lines"]
    invalid_url_shapes = analysis["invalid_url_shapes"]
    already_captured = analysis["already_captured"]
    captured_by_url = analysis["captured_by_url"]

    messages = [
        f"Valid URLs found: {len(valid_urls)}",
        f"Duplicate URLs detected: {duplicate_count}",
    ]

    if normalized:
        messages.append("Normalized URL box: yes")
        messages.append("Comments/blank lines removed from URL box: yes")
        messages.append("Invalid URL shapes excluded from URL box: yes")
    else:
        messages.append("URL box or input file changed: no")

    if duplicate_count:
        messages.append("Use the Duplicates button to remove duplicate URLs.")

    if invalid_lines:
        messages.append("")
        messages.append(f"Lines without valid URL starts: {len(invalid_lines)}")
        messages.extend(f"  {item[:160]}" for item in invalid_lines[:10])
        if len(invalid_lines) > 10:
            messages.append(f"  ...and {len(invalid_lines) - 10} more")

    if invalid_url_shapes:
        messages.append("")
        label = "Invalid URL shapes excluded" if normalized else "Invalid URL shapes detected"
        messages.append(f"{label}: {len(invalid_url_shapes)}")
        messages.extend(f"  {item[:160]}" for item in invalid_url_shapes[:10])
        if len(invalid_url_shapes) > 10:
            messages.append(f"  ...and {len(invalid_url_shapes) - 10} more")

    if already_captured:
        messages.append("")
        messages.append(f"Previously captured URL warning: {len(already_captured)}")
        for url in already_captured[:10]:
            record = captured_by_url.get(normalize_url_for_compare(url), [{}])[0]
            case_name = record.get("case", "")
            messages.append(f"  {url}" + (f"  [{case_name}]" if case_name else ""))
        if len(already_captured) > 10:
            messages.append(f"  ...and {len(already_captured) - 10} more")

    return messages


def validate_urls_in_box():
    source_text = get_current_url_source_text()
    if not source_text.strip():
        messagebox.showwarning("No URLs", "No URL text or input file contents were found.")
        return

    analysis = analyze_url_source_text(source_text)
    messages = build_url_validation_messages(analysis, normalized=False)

    messagebox.showinfo("URL Validation", "\n".join(messages))
    append_log(
        f"\nValidated URL source without changes: {len(analysis['valid_urls'])} valid URL(s), "
        f"{analysis['duplicate_count']} duplicate(s) detected.\n"
    )


def normalize_urls_in_box():
    source_text = get_current_url_source_text()
    if not source_text.strip():
        messagebox.showwarning("No URLs", "No URL text or input file contents were found.")
        return

    analysis = analyze_url_source_text(source_text)
    valid_urls = analysis["valid_urls"]

    if not valid_urls:
        messagebox.showwarning("No valid URLs", "No valid URLs were found to normalize.")
        return

    set_url_box_urls(valid_urls)
    messages = build_url_validation_messages(analysis, normalized=True)

    messagebox.showinfo("URL Normalize", "\n".join(messages))
    append_log(
        f"\nNormalized URL source into URL box: {len(valid_urls)} valid URL(s), "
        f"{analysis['duplicate_count']} duplicate(s) detected.\n"
    )


def copy_urls_from_box():
    content = urls_text.get("1.0", "end-1c")

    if not content.strip():
        source_text = get_current_url_source_text()
        content = source_text if source_text.strip() else ""

    if not content.strip():
        messagebox.showwarning("No URLs", "No URL box contents or input file contents were found to copy.")
        return

    try:
        root.clipboard_clear()
        root.clipboard_append(content)
        root.update()
        append_log(f"\nCopied URL text to clipboard ({len(content)} character(s)).\n")
    except Exception as e:
        messagebox.showerror("Copy failed", f"Could not copy URL text to the clipboard:\n\n{e}")


def derive_cookie_keys(password, salt):
    key_material = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        COOKIE_PBKDF2_ITERATIONS,
        dklen=64,
    )
    return key_material[:32], key_material[32:]


def hmac_stream_xor(data, key, nonce):
    output = bytearray()
    counter = 0

    while len(output) < len(data):
        counter_bytes = counter.to_bytes(8, "big")
        block = hmac.new(key, nonce + counter_bytes, hashlib.sha256).digest()
        output.extend(block)
        counter += 1

    keystream = bytes(output[:len(data)])
    return bytes(a ^ b for a, b in zip(data, keystream))


def build_cookie_auth_payload(record):
    auth_record = {
        "magic": record["magic"],
        "version": record["version"],
        "kdf": record["kdf"],
        "iterations": record["iterations"],
        "salt": record["salt"],
        "nonce": record["nonce"],
        "ciphertext": record["ciphertext"],
    }
    return json.dumps(auth_record, sort_keys=True, separators=(",", ":")).encode("utf-8")


def encrypt_cookie_bytes(plain_bytes, password):
    salt = secrets.token_bytes(COOKIE_SALT_BYTES)
    nonce = secrets.token_bytes(COOKIE_NONCE_BYTES)

    enc_key, mac_key = derive_cookie_keys(password, salt)
    cipher_bytes = hmac_stream_xor(plain_bytes, enc_key, nonce)

    record = {
        "magic": COOKIE_ENCRYPTION_MAGIC,
        "version": COOKIE_ENCRYPTION_VERSION,
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": COOKIE_PBKDF2_ITERATIONS,
        "cipher": "HMAC-SHA256-STREAM-XOR",
        "auth": "HMAC-SHA256",
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(cipher_bytes).decode("ascii"),
    }

    tag = hmac.new(mac_key, build_cookie_auth_payload(record), hashlib.sha256).digest()
    record["tag"] = base64.b64encode(tag).decode("ascii")

    return json.dumps(record, indent=2).encode("utf-8")


def decrypt_cookie_bytes(encrypted_bytes, password):
    try:
        record = json.loads(encrypted_bytes.decode("utf-8"))
    except Exception:
        raise ValueError("Encrypted cookies file is not valid UTF-8 JSON.")

    if record.get("magic") != COOKIE_ENCRYPTION_MAGIC:
        raise ValueError("This file does not look like a supported encrypted cookies file.")

    if record.get("version") != COOKIE_ENCRYPTION_VERSION:
        raise ValueError("Unsupported encrypted cookies file version.")

    iterations = int(record.get("iterations", 0))
    if iterations < 100_000:
        raise ValueError("Encrypted cookies file has an unexpectedly low KDF iteration count.")

    salt = base64.b64decode(record["salt"])
    nonce = base64.b64decode(record["nonce"])
    cipher_bytes = base64.b64decode(record["ciphertext"])
    expected_tag = base64.b64decode(record["tag"])

    enc_key, mac_key = derive_cookie_keys(password, salt)
    actual_tag = hmac.new(mac_key, build_cookie_auth_payload(record), hashlib.sha256).digest()

    if not hmac.compare_digest(expected_tag, actual_tag):
        raise ValueError("Password is incorrect or the encrypted file has been modified.")

    return hmac_stream_xor(cipher_bytes, enc_key, nonce)


def validate_cookie_password(password, confirm=None):
    if len(password) < COOKIE_MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {COOKIE_MIN_PASSWORD_LENGTH} characters long.")

    if confirm is not None and password != confirm:
        raise ValueError("Passwords do not match.")


def encrypt_cookies_dialog():
    messagebox.showwarning(
        "Cookies file security warning",
        "A cookies file can function like a logged-in browser session and should be treated like a credential.\n\n"
        "Do not share raw cookies files unencrypted. This tool encrypts the file for storage only; "
        "yt-dlp still requires plaintext cookies when it performs a capture.\n\n"
        "This uses Python standard-library cryptography primitives: PBKDF2-HMAC-SHA256 key derivation, "
        "HMAC-SHA256 stream encryption, and HMAC-SHA256 integrity checking.",
    )

    dialog = tk.Toplevel(root)
    dialog.title("Encrypt Cookies for Storage")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    input_cookie_var = tk.StringVar(value=cookies_file_var.get().strip() or os.path.join(ROOT, "cookies.txt"))
    output_enc_var = tk.StringVar(value=(input_cookie_var.get().strip() or os.path.join(ROOT, "cookies.txt")) + ".enc")
    password_var = tk.StringVar()
    confirm_var = tk.StringVar()

    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Raw cookies file").grid(row=0, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=input_cookie_var, width=62).grid(row=0, column=1, sticky="ew", padx=6, pady=4)

    def browse_input():
        path = filedialog.askopenfilename(
            title="Select raw cookies file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            input_cookie_var.set(path)
            if not output_enc_var.get().strip():
                output_enc_var.set(path + ".enc")

    ttk.Button(frame, text="Browse...", command=browse_input).grid(row=0, column=2, sticky="e", pady=4)

    ttk.Label(frame, text="Encrypted output file").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=output_enc_var, width=62).grid(row=1, column=1, sticky="ew", padx=6, pady=4)

    def browse_output():
        path = filedialog.asksaveasfilename(
            title="Save encrypted cookies file",
            defaultextension=".enc",
            initialfile="cookies.txt.enc",
            filetypes=[("Encrypted cookies", "*.enc"), ("All files", "*.*")],
        )
        if path:
            output_enc_var.set(path)

    ttk.Button(frame, text="Browse...", command=browse_output).grid(row=1, column=2, sticky="e", pady=4)

    ttk.Label(frame, text="Password").grid(row=2, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=password_var, show="*", width=62).grid(row=2, column=1, columnspan=2, sticky="ew", padx=6, pady=4)

    ttk.Label(frame, text="Confirm password").grid(row=3, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=confirm_var, show="*", width=62).grid(row=3, column=1, columnspan=2, sticky="ew", padx=6, pady=4)

    note = (
        f"Minimum password length: {COOKIE_MIN_PASSWORD_LENGTH} characters.\n"
        "This does not delete the original plaintext cookies file. Delete or secure it separately if required."
    )
    ttk.Label(frame, text=note, justify="left").grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 8))

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=5, column=0, columnspan=3, sticky="e", pady=(8, 0))

    def do_encrypt():
        input_path = input_cookie_var.get().strip()
        output_path = output_enc_var.get().strip()
        password = password_var.get()
        confirm = confirm_var.get()

        try:
            validate_cookie_password(password, confirm)

            if not input_path or not os.path.isfile(input_path):
                raise ValueError("Raw cookies file is missing or invalid.")

            if not output_path:
                raise ValueError("Encrypted output file cannot be blank.")

            with open(input_path, "rb") as f:
                plain = f.read()

            encrypted = encrypt_cookie_bytes(plain, password)

            with open(output_path, "wb") as f:
                f.write(encrypted)

            append_log(f"\nEncrypted cookies file written to: {output_path}\n")
            messagebox.showinfo("Encrypted", f"Encrypted cookies file written to:\n\n{output_path}")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Encryption failed", str(e))

    ttk.Button(button_frame, text="Encrypt", command=do_encrypt).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=6)

    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")


def decrypt_cookies_dialog():
    messagebox.showwarning(
        "Cookies file handling warning",
        "Decryption creates a plaintext cookies file at the location you choose.\n\n"
        "yt-dlp needs plaintext cookies to use them. Do not share the decrypted cookies file, "
        "and do not leave it in broadly accessible folders.\n\n"
        "This tool does not delete encrypted or decrypted files automatically.",
    )

    dialog = tk.Toplevel(root)
    dialog.title("Decrypt Cookies from Storage")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    input_enc_var = tk.StringVar(value=os.path.join(ROOT, "cookies.txt.enc"))
    output_cookie_var = tk.StringVar(value=os.path.join(ROOT, "cookies.txt"))
    password_var = tk.StringVar()

    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Encrypted cookies file").grid(row=0, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=input_enc_var, width=62).grid(row=0, column=1, sticky="ew", padx=6, pady=4)

    def browse_input():
        path = filedialog.askopenfilename(
            title="Select encrypted cookies file",
            filetypes=[("Encrypted cookies", "*.enc"), ("All files", "*.*")],
        )
        if path:
            input_enc_var.set(path)

    ttk.Button(frame, text="Browse...", command=browse_input).grid(row=0, column=2, sticky="e", pady=4)

    ttk.Label(frame, text="Decrypted output file").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=output_cookie_var, width=62).grid(row=1, column=1, sticky="ew", padx=6, pady=4)

    def browse_output():
        path = filedialog.asksaveasfilename(
            title="Save decrypted cookies file",
            defaultextension=".txt",
            initialfile="cookies.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            output_cookie_var.set(path)

    ttk.Button(frame, text="Browse...", command=browse_output).grid(row=1, column=2, sticky="e", pady=4)

    ttk.Label(frame, text="Password").grid(row=2, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=password_var, show="*", width=62).grid(row=2, column=1, columnspan=2, sticky="ew", padx=6, pady=4)

    note = (
        "You may decrypt the cookies file to any location.\n"
        "The Cookies File field will be updated to the decrypted output path."
    )
    ttk.Label(frame, text=note, justify="left").grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 8))

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=4, column=0, columnspan=3, sticky="e", pady=(8, 0))

    def do_decrypt():
        input_path = input_enc_var.get().strip()
        output_path = output_cookie_var.get().strip()
        password = password_var.get()

        try:
            validate_cookie_password(password)

            if not input_path or not os.path.isfile(input_path):
                raise ValueError("Encrypted cookies file is missing or invalid.")

            if not output_path:
                raise ValueError("Decrypted output file cannot be blank.")

            with open(input_path, "rb") as f:
                encrypted = f.read()

            plain = decrypt_cookie_bytes(encrypted, password)

            with open(output_path, "wb") as f:
                f.write(plain)

            cookies_file_var.set(output_path)
            append_log(f"\nDecrypted cookies file written to: {output_path}\n")
            messagebox.showinfo(
                "Decrypted",
                f"Decrypted cookies file written to:\n\n{output_path}\n\n"
                "The Cookies File field has been updated.",
            )
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Decryption failed", str(e))

    ttk.Button(button_frame, text="Decrypt", command=do_decrypt).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=6)

    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")


def validate_inputs():
    script_path = script_path_var.get().strip()
    yt_dlp_path = yt_dlp_path_var.get().strip()
    input_file_paths = parse_input_file_paths()
    cookies_file = cookies_file_var.get().strip()
    output_root = output_root_var.get().strip()
    ffmpeg_folder = ffmpeg_folder_var.get().strip()

    pasted_urls = urls_text.get("1.0", "end").strip()

    if not script_path or not os.path.isfile(script_path):
        raise ValueError("PowerShell script path is missing or invalid.")

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        raise ValueError("yt-dlp path is missing or invalid.")

    if not pasted_urls:
        if not input_file_paths:
            raise ValueError("Input file is missing or invalid, and no URLs were pasted.")

        missing_input_files = [path for path in input_file_paths if not os.path.isfile(path)]
        if missing_input_files:
            raise ValueError(
                "One or more Input File entries are missing or invalid, and no URLs were pasted.\n\n"
                + "\n".join(missing_input_files)
            )

    if use_cookies_file_var.get() and cookies_file and not os.path.isfile(cookies_file):
        raise ValueError("Cookies file is invalid.")

    if output_root and not os.path.isdir(output_root):
        os.makedirs(output_root, exist_ok=True)

    if ffmpeg_folder and not os.path.isdir(ffmpeg_folder):
        raise ValueError("FFmpeg folder is invalid.")

    if not case_name_var.get().strip():
        raise ValueError("Case name cannot be blank.")

    get_enabled_capture_dates()
    update_case_folder_preview()


def build_powershell_command():
    input_path = create_url_input_file()
    capture_timestamp = datetime.now()
    resolved_case_name = get_resolved_case_name(now=capture_timestamp)

    if not resolved_case_name:
        raise ValueError("Case Name is blank after resolving the template.")

    if resolved_case_name != case_name_var.get().strip():
        append_log(f"\nResolved case name template: {case_name_var.get().strip()} -> {resolved_case_name}\n")

    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        script_path_var.get().strip(),
        "-YtDlpPath",
        yt_dlp_path_var.get().strip(),
        "-InputFile",
        input_path,
        "-CaseName",
        resolved_case_name,
        "-OutputRoot",
        output_root_var.get().strip(),
    ]

    cookies_file = cookies_file_var.get().strip()
    if use_cookies_file_var.get() and cookies_file:
        cmd += ["-CookiesFile", cookies_file]

    ffmpeg_folder = ffmpeg_folder_var.get().strip()
    if ffmpeg_folder:
        cmd += ["-FFmpegFolder", ffmpeg_folder]

    impersonate_target = normalize_impersonate_target(impersonate_var.get())
    if impersonate_target:
        cmd += ["-ImpersonateTarget", impersonate_target]

    proxy_url = get_proxy_url_for_command()
    if proxy_url:
        cmd += ["-ProxyUrl", proxy_url]

    format_strategy = normalize_format_strategy(format_strategy_var.get())
    if format_strategy != "best":
        cmd += ["-FormatStrategy", {
            "prefer_mp4": "PreferMp4",
            "strict_mp4": "StrictMp4",
            "audio_only": "AudioOnly",
            "low_bandwidth": "LowBandwidth",
        }.get(format_strategy, "Best")]

    capture_mode = normalize_capture_mode(capture_mode_var.get())
    media_only = capture_mode == "media_only"
    sidecars_enabled = capture_mode in {"media", "metadata_only"}
    embed_enabled = capture_mode in {"media", "media_embedded"}

    if media_only:
        cmd += ["-MediaOnly"]
    elif capture_mode == "metadata_only":
        cmd += ["-MetadataOnly"]

    include_playlist = source_scope_var.get() == "include_playlist"
    if include_playlist:
        cmd += ["-IncludePlaylist"]

        if playlist_items_enabled_var.get():
            raw_playlist_items = playlist_items_var.get().strip()
            playlist_items = normalize_playlist_items(raw_playlist_items)
            if not playlist_items:
                raise ValueError("Playlist items is enabled but invalid. Use indexes or ranges such as 1:10,30,35:40.")
            cmd += ["-PlaylistItems", playlist_items]

        if playlist_order_enabled_var.get():
            playlist_order = normalize_playlist_order(playlist_order_var.get())
            if playlist_order != "normal":
                cmd += ["-PlaylistOrder", script_playlist_order(playlist_order)]

        if max_playlist_items_enabled_var.get():
            max_playlist_items = normalize_optional_positive_int_string(max_playlist_items_var.get())
            if not max_playlist_items:
                raise ValueError("Max playlist items is enabled but blank or invalid.")
            cmd += ["-MaxPlaylistItems", max_playlist_items]

        if break_on_existing_var.get():
            cmd += ["-BreakOnExisting"]

        if skip_playlist_after_errors_enabled_var.get():
            skip_errors = normalize_optional_positive_int_string(skip_playlist_after_errors_var.get())
            if not skip_errors:
                raise ValueError("Skip after failed items is enabled but blank or invalid.")
            cmd += ["-SkipPlaylistAfterErrors", skip_errors]

    archive_mode = archive_mode_var.get().strip() or "use"
    if archive_mode == "ignore":
        cmd += ["-ArchiveMode", "Ignore"]
    elif archive_mode == "force":
        cmd += ["-ArchiveMode", "Force"]
    else:
        cmd += ["-ArchiveMode", "Use"]

    if should_pass_universal_archive(archive_mode):
        cmd += ["-UniversalArchiveFile", UNIVERSAL_ARCHIVE_FILE]

    max_resolution = max_resolution_var.get().strip() or "best"
    if max_resolution != "best":
        cmd += ["-MaxResolution", max_resolution]

    cmd += ["-GuiCacheMode", script_gui_cache_mode(gui_cache_mode_var.get())]
    cmd += ["-ManifestMode", script_manifest_mode(manifest_mode_var.get())]

    if save_playlist_metadata_var.get() and sidecars_enabled:
        cmd += ["-SavePlaylistMetadata"]

    if generate_url_shortcuts_var.get() and sidecars_enabled:
        cmd += ["-GenerateUrlShortcuts"]

    match_keywords = match_keywords_var.get().strip()
    if match_keywords:
        cmd += ["-MatchKeywords", match_keywords]

    reject_keywords = reject_keywords_var.get().strip()
    if reject_keywords:
        cmd += ["-RejectKeywords", reject_keywords]

    failure_handling = failure_handling_var.get().strip() or "continue"
    if failure_handling == "stop":
        cmd += ["-FailureHandling", "Stop"]
    else:
        cmd += ["-FailureHandling", "Continue"]

    date_after, date_before = get_enabled_capture_dates()

    if date_after:
        cmd += ["-DateAfter", date_after]

    if date_before:
        cmd += ["-DateBefore", date_before]

    rate_limit = rate_limit_var.get().strip() or "normal"
    if rate_limit == "none":
        cmd += ["-RateLimit", "None"]
    elif rate_limit == "fast":
        cmd += ["-RateLimit", "Fast"]
    elif rate_limit == "cautious":
        cmd += ["-RateLimit", "Cautious"]
    else:
        cmd += ["-RateLimit", "Normal"]

    if download_speed_limit_enabled_var.get():
        download_speed_limit = download_speed_limit_to_ytdlp_value(download_speed_limit_var.get())
        if not download_speed_limit or download_speed_limit == "disabled":
            raise ValueError("Download Speed Limit is invalid. Use a value from 1 KiB/s to 1 GiB/s.")
        cmd += ["-DownloadSpeedLimit", download_speed_limit]

    retry_behavior = normalize_retry_behavior(retry_behavior_var.get())
    cmd += ["-RetryBehavior", retry_behavior.capitalize()]

    if throttle_detection_enabled_var.get():
        throttled_rate = download_speed_limit_to_ytdlp_value(throttled_rate_var.get())
        if not throttled_rate or throttled_rate == "disabled":
            raise ValueError("Throttled Rate is invalid. Use a value from 1 KiB/s to 1 GiB/s.")
        cmd += ["-ThrottledRate", throttled_rate]

    if http_chunk_size_enabled_var.get():
        chunk_size = binary_size_to_ytdlp_value(http_chunk_size_var.get())
        if not chunk_size:
            raise ValueError("HTTP Chunk Size is invalid.")
        cmd += ["-HttpChunkSize", chunk_size]

    concurrent_fragments = get_concurrent_fragment_limit()
    if concurrent_fragments > 1:
        cmd += ["-ConcurrentFragments", str(concurrent_fragments)]

    if keep_partials_var.get():
        cmd += ["-KeepPartials"]

    if sidecars_enabled:
        if write_info_json_var.get():
            cmd += ["-WriteInfoJson"]

        if write_source_link_var.get():
            cmd += ["-WriteSourceLink"]

        if write_description_var.get():
            cmd += ["-WriteDescription"]

        if write_thumbnail_var.get():
            cmd += ["-WriteThumbnail"]

        if write_subs_var.get():
            cmd += ["-WriteSubs"]

        if write_auto_subs_var.get():
            cmd += ["-WriteAutoSubs"]

        if write_comments_var.get():
            cmd += ["-WriteComments"]

    if embed_enabled:
        if embed_metadata_var.get():
            cmd += ["-EmbedMetadata"]

        if embed_thumbnail_var.get():
            cmd += ["-EmbedThumbnail"]

        if embed_subs_var.get():
            cmd += ["-EmbedSubs"]

        if embed_chapters_var.get():
            cmd += ["-EmbedChapters"]

        if embed_info_json_var.get():
            cmd += ["-EmbedInfoJson"]

    return cmd


def get_enabled_capture_dates_from_settings(settings):
    date_after = ""
    date_before = ""

    if bool(settings.get("date_after_enabled", DEFAULTS["date_after_enabled"])):
        date_after = normalize_capture_date(
            settings.get("date_after_year", ""),
            settings.get("date_after_month", ""),
            settings.get("date_after_day", ""),
            "Date after",
        )

    if bool(settings.get("date_before_enabled", DEFAULTS["date_before_enabled"])):
        date_before = normalize_capture_date(
            settings.get("date_before_year", ""),
            settings.get("date_before_month", ""),
            settings.get("date_before_day", ""),
            "Date before",
        )

    if date_after and date_before and date_after > date_before:
        raise ValueError("Date after cannot be later than Date before.")

    return date_after, date_before


def get_interrupted_resume_index(job):
    try:
        completed = int(job.get("completed_urls", 0) or 0)
    except Exception:
        completed = 0

    return max(0, min(completed, len(job.get("urls", []) or [])))


def get_queue_job_run_urls(job):
    urls = list(job.get("urls", []) or [])

    if job.get("_run_mode") == "continue":
        start_index = get_interrupted_resume_index(job)
        return urls[start_index:]

    return urls


def prepare_queue_job_for_restart(job):
    job["settings_schema_version"] = SETTINGS_SCHEMA_VERSION
    job["status"] = "pending"
    job["completed_urls"] = 0
    job["started"] = ""
    job["finished"] = ""
    job["exit_code"] = ""
    job["summary"] = ""
    job["interrupted_reason"] = ""
    job["interrupted_at"] = ""
    job["_run_mode"] = "restart"
    job["_resume_base_completed"] = 0


def prepare_queue_job_for_continue(job):
    resume_index = get_interrupted_resume_index(job)

    if resume_index >= len(job.get("urls", []) or []):
        job["status"] = "completed"
        job["finished"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job["exit_code"] = "0"
        return False

    job["settings_schema_version"] = SETTINGS_SCHEMA_VERSION
    job["status"] = "pending"
    job["started"] = ""
    job["finished"] = ""
    job["exit_code"] = ""
    job["summary"] = ""
    job["_run_mode"] = "continue"
    job["_resume_base_completed"] = resume_index
    return True


def validate_queue_job_inputs(job):
    settings = job.get("settings", {})
    urls = get_queue_job_run_urls(job)

    script_path = settings.get("script_path", "").strip()
    yt_dlp_path = settings.get("yt_dlp_path", "").strip()
    cookies_file = settings.get("cookies_file", "").strip()
    output_root = settings.get("output_root", "").strip()
    ffmpeg_folder = settings.get("ffmpeg_folder", "").strip()
    resolved_case_name = job.get("resolved_case_name", "").strip()

    if not script_path or not os.path.isfile(script_path):
        raise ValueError("PowerShell script path is missing or invalid.")

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        raise ValueError("yt-dlp path is missing or invalid.")

    if not urls:
        raise ValueError("The queue job does not contain any URLs.")

    if bool(settings.get("use_cookies_file", DEFAULTS["use_cookies_file"])) and cookies_file and not os.path.isfile(cookies_file):
        raise ValueError("Cookies file is invalid.")

    if output_root and not os.path.isdir(output_root):
        os.makedirs(output_root, exist_ok=True)

    if ffmpeg_folder and not os.path.isdir(ffmpeg_folder):
        raise ValueError("FFmpeg folder is invalid.")

    if not resolved_case_name:
        raise ValueError("Queue job resolved case name is blank.")

    get_enabled_capture_dates_from_settings(settings)


def get_expected_run_paths_for_values(output_root, resolved_case_name):
    case_folder = os.path.join(output_root, resolved_case_name)
    return {
        "case_folder": case_folder,
        "media_folder": os.path.join(case_folder, "media"),
        "logs_folder": os.path.join(case_folder, "logs"),
        "manifests_folder": os.path.join(case_folder, "manifests"),
        "download_archive": os.path.join(case_folder, "download-archive.txt"),
        "universal_archive": UNIVERSAL_ARCHIVE_FILE,
    }


def build_powershell_command_for_job(job):
    settings = job.get("settings", {})
    input_path = create_url_input_file_from_lines(get_queue_job_run_urls(job))
    resolved_case_name = job.get("resolved_case_name", "").strip()

    if not resolved_case_name:
        raise ValueError("Queue job resolved case name is blank.")

    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        settings.get("script_path", "").strip(),
        "-YtDlpPath",
        settings.get("yt_dlp_path", "").strip(),
        "-InputFile",
        input_path,
        "-CaseName",
        resolved_case_name,
        "-OutputRoot",
        settings.get("output_root", "").strip(),
    ]

    cookies_file = settings.get("cookies_file", "").strip()
    if bool(settings.get("use_cookies_file", DEFAULTS["use_cookies_file"])) and cookies_file:
        cmd += ["-CookiesFile", cookies_file]

    ffmpeg_folder = settings.get("ffmpeg_folder", "").strip()
    if ffmpeg_folder:
        cmd += ["-FFmpegFolder", ffmpeg_folder]

    impersonate_target = normalize_impersonate_target(settings.get("impersonate_target", ""))
    if impersonate_target:
        cmd += ["-ImpersonateTarget", impersonate_target]

    proxy_url = get_proxy_url_for_command()
    if proxy_url:
        cmd += ["-ProxyUrl", proxy_url]

    format_strategy = normalize_format_strategy(settings.get("format_strategy", DEFAULTS["format_strategy"]))
    if format_strategy != "best":
        cmd += ["-FormatStrategy", {
            "prefer_mp4": "PreferMp4",
            "strict_mp4": "StrictMp4",
            "audio_only": "AudioOnly",
            "low_bandwidth": "LowBandwidth",
        }.get(format_strategy, "Best")]

    capture_mode = normalize_capture_mode(settings.get("capture_mode", DEFAULTS["capture_mode"]))
    media_only = capture_mode == "media_only"
    sidecars_enabled = capture_mode in {"media", "metadata_only"}
    embed_enabled = capture_mode in {"media", "media_embedded"}

    if media_only:
        cmd += ["-MediaOnly"]
    elif capture_mode == "metadata_only":
        cmd += ["-MetadataOnly"]

    include_playlist = settings.get("source_scope", DEFAULTS["source_scope"]) == "include_playlist"
    if include_playlist:
        cmd += ["-IncludePlaylist"]

        if bool(settings.get("playlist_items_enabled", DEFAULTS["playlist_items_enabled"])):
            raw_playlist_items = str(settings.get("playlist_items", DEFAULTS["playlist_items"]) or "").strip()
            playlist_items = normalize_playlist_items(raw_playlist_items)
            if not playlist_items:
                raise ValueError("Playlist items is enabled but invalid. Use indexes or ranges such as 1:10,30,35:40.")
            cmd += ["-PlaylistItems", playlist_items]

        if bool(settings.get("playlist_order_enabled", DEFAULTS["playlist_order_enabled"])):
            playlist_order = normalize_playlist_order(settings.get("playlist_order", DEFAULTS["playlist_order"]))
            if playlist_order != "normal":
                cmd += ["-PlaylistOrder", script_playlist_order(playlist_order)]

        if bool(settings.get("max_playlist_items_enabled", DEFAULTS["max_playlist_items_enabled"])):
            max_playlist_items = normalize_optional_positive_int_string(settings.get("max_playlist_items", DEFAULTS["max_playlist_items"]))
            if not max_playlist_items:
                raise ValueError("Max playlist items is enabled but blank or invalid.")
            cmd += ["-MaxPlaylistItems", max_playlist_items]

        if bool(settings.get("break_on_existing", DEFAULTS["break_on_existing"])):
            cmd += ["-BreakOnExisting"]

        if bool(settings.get("skip_playlist_after_errors_enabled", DEFAULTS["skip_playlist_after_errors_enabled"])):
            skip_errors = normalize_optional_positive_int_string(settings.get("skip_playlist_after_errors", DEFAULTS["skip_playlist_after_errors"]))
            if not skip_errors:
                raise ValueError("Skip after failed items is enabled but blank or invalid.")
            cmd += ["-SkipPlaylistAfterErrors", skip_errors]

    archive_mode = str(settings.get("archive_mode", DEFAULTS["archive_mode"]) or "use").strip()
    if archive_mode == "ignore":
        cmd += ["-ArchiveMode", "Ignore"]
    elif archive_mode == "force":
        cmd += ["-ArchiveMode", "Force"]
    else:
        cmd += ["-ArchiveMode", "Use"]

    if should_pass_universal_archive(archive_mode):
        cmd += ["-UniversalArchiveFile", UNIVERSAL_ARCHIVE_FILE]

    max_resolution = str(settings.get("max_resolution", DEFAULTS["max_resolution"]) or "best").strip()
    if max_resolution != "best":
        cmd += ["-MaxResolution", max_resolution]

    cmd += ["-GuiCacheMode", script_gui_cache_mode(settings.get("gui_cache_mode", DEFAULTS["gui_cache_mode"]))]
    cmd += ["-ManifestMode", script_manifest_mode(settings.get("manifest_mode", DEFAULTS["manifest_mode"]))]

    if bool(settings.get("save_playlist_metadata", DEFAULTS["save_playlist_metadata"])) and sidecars_enabled:
        cmd += ["-SavePlaylistMetadata"]

    if bool(settings.get("generate_url_shortcuts", DEFAULTS["generate_url_shortcuts"])) and sidecars_enabled:
        cmd += ["-GenerateUrlShortcuts"]

    match_keywords = str(settings.get("match_keywords", "") or "").strip()
    if match_keywords:
        cmd += ["-MatchKeywords", match_keywords]

    reject_keywords = str(settings.get("reject_keywords", "") or "").strip()
    if reject_keywords:
        cmd += ["-RejectKeywords", reject_keywords]

    failure_handling = str(settings.get("failure_handling", DEFAULTS["failure_handling"]) or "continue").strip()
    if failure_handling == "stop":
        cmd += ["-FailureHandling", "Stop"]
    else:
        cmd += ["-FailureHandling", "Continue"]

    date_after, date_before = get_enabled_capture_dates_from_settings(settings)

    if date_after:
        cmd += ["-DateAfter", date_after]

    if date_before:
        cmd += ["-DateBefore", date_before]

    rate_limit = str(settings.get("rate_limit", DEFAULTS["rate_limit"]) or "normal").strip()
    if rate_limit == "none":
        cmd += ["-RateLimit", "None"]
    elif rate_limit == "fast":
        cmd += ["-RateLimit", "Fast"]
    elif rate_limit == "cautious":
        cmd += ["-RateLimit", "Cautious"]
    else:
        cmd += ["-RateLimit", "Normal"]

    if bool(settings.get("download_speed_limit_enabled", DEFAULTS["download_speed_limit_enabled"])):
        download_speed_limit = download_speed_limit_to_ytdlp_value(settings.get("download_speed_limit", DEFAULTS["download_speed_limit"]))
        if not download_speed_limit or download_speed_limit == "disabled":
            raise ValueError("Download Speed Limit is invalid. Use a value from 1 KiB/s to 1 GiB/s.")
        cmd += ["-DownloadSpeedLimit", download_speed_limit]

    retry_behavior = normalize_retry_behavior(settings.get("retry_behavior", DEFAULTS["retry_behavior"]))
    cmd += ["-RetryBehavior", retry_behavior.capitalize()]

    if bool(settings.get("throttle_detection_enabled", DEFAULTS["throttle_detection_enabled"])):
        throttled_rate = download_speed_limit_to_ytdlp_value(settings.get("throttled_rate", DEFAULTS["throttled_rate"]))
        if not throttled_rate or throttled_rate == "disabled":
            raise ValueError("Throttled Rate is invalid. Use a value from 1 KiB/s to 1 GiB/s.")
        cmd += ["-ThrottledRate", throttled_rate]

    if bool(settings.get("http_chunk_size_enabled", DEFAULTS["http_chunk_size_enabled"])):
        chunk_size = binary_size_to_ytdlp_value(settings.get("http_chunk_size", DEFAULTS["http_chunk_size"]))
        if not chunk_size:
            raise ValueError("HTTP Chunk Size is invalid.")
        cmd += ["-HttpChunkSize", chunk_size]

    concurrent_fragments = get_concurrent_fragment_limit(settings)
    if concurrent_fragments > 1:
        cmd += ["-ConcurrentFragments", str(concurrent_fragments)]

    if bool(settings.get("keep_partials", DEFAULTS["keep_partials"])):
        cmd += ["-KeepPartials"]

    if sidecars_enabled:
        if bool(settings.get("write_info_json", DEFAULTS["write_info_json"])):
            cmd += ["-WriteInfoJson"]

        if bool(settings.get("write_source_link", DEFAULTS["write_source_link"])):
            cmd += ["-WriteSourceLink"]

        if bool(settings.get("write_description", DEFAULTS["write_description"])):
            cmd += ["-WriteDescription"]

        if bool(settings.get("write_thumbnail", DEFAULTS["write_thumbnail"])):
            cmd += ["-WriteThumbnail"]

        if bool(settings.get("write_subs", DEFAULTS["write_subs"])):
            cmd += ["-WriteSubs"]

        if bool(settings.get("write_auto_subs", DEFAULTS["write_auto_subs"])):
            cmd += ["-WriteAutoSubs"]

        if bool(settings.get("write_comments", DEFAULTS["write_comments"])):
            cmd += ["-WriteComments"]

    if embed_enabled:
        if bool(settings.get("embed_metadata", DEFAULTS["embed_metadata"])):
            cmd += ["-EmbedMetadata"]

        if bool(settings.get("embed_thumbnail", DEFAULTS["embed_thumbnail"])):
            cmd += ["-EmbedThumbnail"]

        if bool(settings.get("embed_subs", DEFAULTS["embed_subs"])):
            cmd += ["-EmbedSubs"]

        if bool(settings.get("embed_chapters", DEFAULTS["embed_chapters"])):
            cmd += ["-EmbedChapters"]

        if bool(settings.get("embed_info_json", DEFAULTS["embed_info_json"])):
            cmd += ["-EmbedInfoJson"]

    return cmd



def preflight_check(show_success_popup=True):
    append_log("\n========== Preflight Check ==========")
    append_log("\nRunning preflight check...\n\n")

    checks = []

    def add_check(name, passed, detail=""):
        checks.append((name, passed, detail))
        status = "PASS" if passed else "FAIL"
        append_log(f"[{status}] {name}")
        if detail:
            append_log(f" - {detail}")
        append_log("\n")

    script_path = script_path_var.get().strip()
    yt_dlp_path = yt_dlp_path_var.get().strip()
    input_file_paths = parse_input_file_paths()
    cookies_file = cookies_file_var.get().strip()
    output_root = output_root_var.get().strip()
    ffmpeg_folder = ffmpeg_folder_var.get().strip()
    pasted_urls = urls_text.get("1.0", "end").strip()

    add_check("PowerShell script exists", os.path.isfile(script_path), script_path)
    add_check("yt-dlp exists", os.path.isfile(yt_dlp_path), yt_dlp_path)

    deno_path = os.path.join(os.path.dirname(os.path.abspath(yt_dlp_path)), "deno.exe") if yt_dlp_path else ""
    add_check("deno.exe exists beside yt-dlp.exe", os.path.isfile(deno_path), deno_path)

    ffmpeg_path = os.path.join(ffmpeg_folder, "ffmpeg.exe") if ffmpeg_folder else ""
    ffprobe_path = os.path.join(ffmpeg_folder, "ffprobe.exe") if ffmpeg_folder else ""

    add_check("ffmpeg.exe exists in FFmpeg folder", os.path.isfile(ffmpeg_path), ffmpeg_path)
    add_check("ffprobe.exe exists in FFmpeg folder", os.path.isfile(ffprobe_path), ffprobe_path)

    if pasted_urls:
        url_count = count_submitted_urls()
        add_check("URLs provided in pasted URL box", url_count != 0, f"{url_count} URL(s)")
    else:
        if not input_file_paths:
            add_check("Input file(s) selected", False, "No Input File(s) selected")
        else:
            missing_input_files = [path for path in input_file_paths if not os.path.isfile(path)]
            if missing_input_files:
                add_check("Input file(s) exist", False, "\n".join(missing_input_files))
            else:
                total_urls = count_submitted_urls()
                file_label = f"{len(input_file_paths)} file(s)"
                if isinstance(total_urls, int):
                    file_label += f"; {total_urls} URL(s)"
                add_check("Input file(s) exist", True, file_label)

    if use_cookies_file_var.get():
        if cookies_file:
            add_check("Cookies file exists", os.path.isfile(cookies_file), cookies_file)
        else:
            add_check("Cookies file", True, "Enabled, but not specified")
    else:
        add_check("Cookies file", True, "Disabled by app setting; skipped")

    try:
        proxy_url = get_proxy_url_for_command()
        if proxy_url:
            add_check("Proxy", True, mask_proxy_url(proxy_url))
        else:
            add_check("Proxy", True, "Disabled")
    except Exception as e:
        add_check("Proxy", False, str(e))

    try:
        if output_root:
            os.makedirs(output_root, exist_ok=True)
        add_check("Output root exists or can be created", os.path.isdir(output_root), output_root)
    except Exception as e:
        add_check("Output root exists or can be created", False, str(e))

    if os.path.isfile(yt_dlp_path):
        version_info = get_tool_first_line(
            [yt_dlp_path, "--version"],
            cwd=os.path.dirname(os.path.abspath(yt_dlp_path)) or ROOT,
            timeout=20,
        )
        add_check("yt-dlp can run", version_info["ok"], version_info["version"])

        if version_info["ok"]:
            yt_dlp_version_status_var.set(f"yt-dlp: {version_info['version']}")
        else:
            yt_dlp_version_status_var.set("yt-dlp: version check failed")
    else:
        yt_dlp_version_status_var.set("yt-dlp: not found")
        add_check("yt-dlp can run", False, "yt-dlp path is invalid")

    if os.path.isfile(ffmpeg_path):
        version_info = get_tool_first_line([ffmpeg_path, "-version"], timeout=20)
        add_check("ffmpeg can run", version_info["ok"], version_info["version"])
    else:
        add_check("ffmpeg can run", False, "ffmpeg path is invalid")

    if os.path.isfile(ffprobe_path):
        version_info = get_tool_first_line([ffprobe_path, "-version"], timeout=20)
        add_check("ffprobe can run", version_info["ok"], version_info["version"])
    else:
        add_check("ffprobe can run", False, "ffprobe path is invalid")

    if os.path.isfile(deno_path):
        version_info = get_tool_first_line([deno_path, "--version"], timeout=20)
        add_check("deno can run", version_info["ok"], version_info["version"])
    else:
        add_check("deno can run", False, "deno path is invalid")

    failed = [item for item in checks if not item[1]]

    append_log("\nPreflight complete.\n")
    append_log(f"Passed: {len(checks) - len(failed)} / {len(checks)}\n")
    append_log("=====================================\n")

    if failed:
        set_status("Preflight failed")
        if show_success_popup:
            messagebox.showwarning(
                "Preflight failed",
                f"{len(failed)} check(s) failed. Review the output log before starting capture.",
            )
        return False

    set_status("Preflight passed")
    if show_success_popup:
        messagebox.showinfo("Preflight passed", "All preflight checks passed.")
    return True


def run_preflight_check():
    preflight_done_var.set(False)

    try:
        passed = preflight_check(show_success_popup=True)
    except Exception as e:
        set_status("Preflight failed")
        append_log(f"\nPreflight error: {e}\n")
        messagebox.showerror("Preflight failed", str(e))
        return

    preflight_done_var.set(passed is True)


def normalize_capture_mode(value):
    value = str(value or "").strip().lower()
    if value in {"media", "media_embedded", "media_only", "metadata_only"}:
        return value
    return DEFAULTS["capture_mode"]


def get_settings_dict():
    return {
        "script_path": script_path_var.get(),
        "yt_dlp_path": yt_dlp_path_var.get(),
        "input_file": input_file_var.get(),
        "case_name": case_name_var.get(),
        "cookies_file": cookies_file_var.get(),
        "use_cookies_file": use_cookies_file_var.get(),
        "output_root": output_root_var.get(),
        "ffmpeg_folder": ffmpeg_folder_var.get(),
        "impersonate_target": impersonate_var.get(),
        "prefer_mp4": prefer_mp4_var.get(),
        "format_strategy": format_strategy_var.get(),
        "capture_mode": capture_mode_var.get(),
        "source_scope": source_scope_var.get(),
        "playlist_items_enabled": playlist_items_enabled_var.get(),
        "playlist_items": normalize_playlist_items(playlist_items_var.get()),
        "playlist_order_enabled": playlist_order_enabled_var.get(),
        "playlist_order": normalize_playlist_order(playlist_order_var.get()),
        "max_playlist_items_enabled": max_playlist_items_enabled_var.get(),
        "max_playlist_items": normalize_optional_positive_int_string(max_playlist_items_var.get()),
        "break_on_existing": break_on_existing_var.get(),
        "skip_playlist_after_errors_enabled": skip_playlist_after_errors_enabled_var.get(),
        "skip_playlist_after_errors": normalize_optional_positive_int_string(skip_playlist_after_errors_var.get()),
        "archive_mode": archive_mode_var.get(),
        "max_resolution": max_resolution_var.get(),
        "gui_cache_mode": normalize_gui_cache_mode(gui_cache_mode_var.get()),
        "manifest_mode": normalize_manifest_mode(manifest_mode_var.get()),
        "save_playlist_metadata": save_playlist_metadata_var.get(),
        "generate_url_shortcuts": generate_url_shortcuts_var.get(),
        "match_keywords": match_keywords_var.get(),
        "reject_keywords": reject_keywords_var.get(),
        "failure_handling": failure_handling_var.get(),
        "show_all_impersonate_targets": show_all_impersonate_targets_var.get(),
        "date_after_enabled": date_after_enabled_var.get(),
        "date_after_year": date_after_year_var.get(),
        "date_after_month": date_after_month_var.get(),
        "date_after_day": date_after_day_var.get(),
        "date_before_enabled": date_before_enabled_var.get(),
        "date_before_year": date_before_year_var.get(),
        "date_before_month": date_before_month_var.get(),
        "date_before_day": date_before_day_var.get(),
        "rate_limit": rate_limit_var.get(),
        "download_speed_limit_enabled": download_speed_limit_enabled_var.get(),
        "download_speed_limit": normalize_download_speed_limit_value(download_speed_limit_var.get()) or DEFAULTS["download_speed_limit"],
        "retry_behavior": retry_behavior_var.get(),
        "throttle_detection_enabled": throttle_detection_enabled_var.get(),
        "throttled_rate": normalize_download_speed_limit_value(throttled_rate_var.get()) or DEFAULTS["throttled_rate"],
        "http_chunk_size_enabled": http_chunk_size_enabled_var.get(),
        "http_chunk_size": normalize_binary_size_value(http_chunk_size_var.get(), DEFAULTS["http_chunk_size"]),
        "concurrent_captures": concurrent_captures_var.get(),
        "concurrent_fragments": concurrent_fragments_var.get(),
        "keep_partials": keep_partials_var.get(),
        "write_info_json": write_info_json_var.get(),
        "write_source_link": write_source_link_var.get(),
        "write_description": write_description_var.get(),
        "write_thumbnail": write_thumbnail_var.get(),
        "write_subs": write_subs_var.get(),
        "write_auto_subs": write_auto_subs_var.get(),
        "write_comments": write_comments_var.get(),
        "embed_metadata": embed_metadata_var.get(),
        "embed_thumbnail": embed_thumbnail_var.get(),
        "embed_subs": embed_subs_var.get(),
        "embed_chapters": embed_chapters_var.get(),
        "embed_info_json": embed_info_json_var.get(),
        "vpn_adapter_name": vpn_adapter_var.get(),
        "split_queue_mode": split_queue_mode_var.get(),
        "split_queue_urls_per_group": normalize_positive_int_string(
            split_queue_urls_per_group_var.get(),
            DEFAULTS["split_queue_urls_per_group"],
        ),
        "split_queue_group_count": normalize_positive_int_string(
            split_queue_group_count_var.get(),
            DEFAULTS["split_queue_group_count"],
        ),
        "url_preview_pacing": normalize_url_preview_pacing(url_preview_pacing_var.get()),
        "url_preview_thumbnail_mode": normalize_url_preview_thumbnail_mode(url_preview_thumbnail_mode_var.get()),
        "url_preview_rate_limit_thumbnails": bool(url_preview_rate_limit_thumbnails_var.get()),
        "url_preview_cache_mode": normalize_url_preview_cache_mode(url_preview_cache_mode_var.get()),
        "url_preview_playlist_mode": normalize_url_preview_playlist_mode(url_preview_playlist_mode_var.get()),
        "url_preview_max_playlist_items": normalize_url_preview_max_playlist_items(url_preview_max_playlist_items_var.get()),
        "url_preview_timeout": normalize_url_preview_timeout(url_preview_timeout_var.get()),
    }


def apply_settings_dict(settings):
    script_path_var.set(settings.get("script_path", DEFAULTS["script_path"]))
    yt_dlp_path_var.set(settings.get("yt_dlp_path", DEFAULTS["yt_dlp_path"]))
    input_file_var.set(settings.get("input_file", DEFAULTS["input_file"]))
    case_name_var.set(settings.get("case_name", DEFAULTS["case_name"]))
    cookies_file_var.set(settings.get("cookies_file", DEFAULTS["cookies_file"]))
    use_cookies_file_var.set(bool(settings.get("use_cookies_file", DEFAULTS["use_cookies_file"])))
    update_cookies_file_control_state()
    output_root_var.set(settings.get("output_root", DEFAULTS["output_root"]))
    ffmpeg_folder_var.set(settings.get("ffmpeg_folder", DEFAULTS["ffmpeg_folder"]))
    impersonate_var.set(settings.get("impersonate_target", DEFAULTS["impersonate_target"]))
    prefer_mp4_var.set(bool(settings.get("prefer_mp4", DEFAULTS["prefer_mp4"])))
    if "format_strategy" in settings:
        format_strategy_var.set(normalize_format_strategy(settings.get("format_strategy", DEFAULTS["format_strategy"])))
    elif bool(settings.get("prefer_mp4", DEFAULTS["prefer_mp4"])):
        format_strategy_var.set("prefer_mp4")
    else:
        format_strategy_var.set(DEFAULTS["format_strategy"])
    capture_mode_var.set(normalize_capture_mode(settings.get("capture_mode", DEFAULTS["capture_mode"])))
    source_scope_var.set(settings.get("source_scope", DEFAULTS["source_scope"]))
    playlist_items_enabled_var.set(bool(settings.get("playlist_items_enabled", DEFAULTS["playlist_items_enabled"])))
    playlist_items_var.set(normalize_playlist_items(settings.get("playlist_items", DEFAULTS["playlist_items"])))
    playlist_order_enabled_var.set(bool(settings.get("playlist_order_enabled", DEFAULTS["playlist_order_enabled"])))
    playlist_order_var.set(normalize_playlist_order(settings.get("playlist_order", DEFAULTS["playlist_order"])))
    max_playlist_items_enabled_var.set(bool(settings.get("max_playlist_items_enabled", DEFAULTS["max_playlist_items_enabled"])))
    max_playlist_items_var.set(normalize_optional_positive_int_string(settings.get("max_playlist_items", DEFAULTS["max_playlist_items"])))
    break_on_existing_var.set(bool(settings.get("break_on_existing", DEFAULTS["break_on_existing"])))
    skip_playlist_after_errors_enabled_var.set(bool(settings.get("skip_playlist_after_errors_enabled", DEFAULTS["skip_playlist_after_errors_enabled"])))
    skip_playlist_after_errors_var.set(normalize_optional_positive_int_string(settings.get("skip_playlist_after_errors", DEFAULTS["skip_playlist_after_errors"])))
    archive_mode_var.set(settings.get("archive_mode", DEFAULTS["archive_mode"]))
    max_resolution_var.set(settings.get("max_resolution", DEFAULTS["max_resolution"]))
    gui_cache_mode_var.set(display_gui_cache_mode(settings.get("gui_cache_mode", DEFAULTS["gui_cache_mode"])))
    manifest_mode_var.set(display_manifest_mode(settings.get("manifest_mode", DEFAULTS["manifest_mode"])))
    save_playlist_metadata_var.set(bool(settings.get("save_playlist_metadata", DEFAULTS["save_playlist_metadata"])))
    generate_url_shortcuts_var.set(bool(settings.get("generate_url_shortcuts", DEFAULTS["generate_url_shortcuts"])))
    match_keywords_var.set(settings.get("match_keywords", DEFAULTS["match_keywords"]))
    reject_keywords_var.set(settings.get("reject_keywords", DEFAULTS["reject_keywords"]))
    failure_handling_var.set(settings.get("failure_handling", DEFAULTS["failure_handling"]))
    show_all_impersonate_targets_var.set(bool(settings.get("show_all_impersonate_targets", DEFAULTS["show_all_impersonate_targets"])))
    date_after_enabled_var.set(bool(settings.get("date_after_enabled", DEFAULTS["date_after_enabled"])))
    date_after_year_var.set(settings.get("date_after_year", DEFAULTS["date_after_year"]))
    date_after_month_var.set(settings.get("date_after_month", DEFAULTS["date_after_month"]))
    date_after_day_var.set(settings.get("date_after_day", DEFAULTS["date_after_day"]))
    date_before_enabled_var.set(bool(settings.get("date_before_enabled", DEFAULTS["date_before_enabled"])))
    date_before_year_var.set(settings.get("date_before_year", DEFAULTS["date_before_year"]))
    date_before_month_var.set(settings.get("date_before_month", DEFAULTS["date_before_month"]))
    date_before_day_var.set(settings.get("date_before_day", DEFAULTS["date_before_day"]))
    rate_limit_var.set(settings.get("rate_limit", DEFAULTS["rate_limit"]))

    raw_download_speed_limit = settings.get("download_speed_limit", DEFAULTS["download_speed_limit"])
    saved_download_speed_limit = normalize_download_speed_limit_value(raw_download_speed_limit)
    if not saved_download_speed_limit or saved_download_speed_limit == "disabled":
        saved_download_speed_limit = DEFAULTS["download_speed_limit"]

    download_speed_limit_var.set(saved_download_speed_limit)

    # Backward compatibility: old settings stored only "disabled" or a value.
    if "download_speed_limit_enabled" in settings:
        download_speed_limit_enabled_var.set(bool(settings.get("download_speed_limit_enabled", DEFAULTS["download_speed_limit_enabled"])))
    else:
        download_speed_limit_enabled_var.set(str(raw_download_speed_limit or "").strip().lower() not in ("", "disabled"))

    try:
        sync_download_speed_limit_controls_from_var(show_errors=False)
    except Exception:
        pass

    retry_behavior_var.set(normalize_retry_behavior(settings.get("retry_behavior", DEFAULTS["retry_behavior"])))

    throttle_detection_enabled_var.set(bool(settings.get("throttle_detection_enabled", DEFAULTS["throttle_detection_enabled"])))
    saved_throttled_rate = normalize_download_speed_limit_value(settings.get("throttled_rate", DEFAULTS["throttled_rate"]))
    throttled_rate_var.set(saved_throttled_rate if saved_throttled_rate and saved_throttled_rate != "disabled" else DEFAULTS["throttled_rate"])
    update_throttled_rate_state()

    http_chunk_size_enabled_var.set(bool(settings.get("http_chunk_size_enabled", DEFAULTS["http_chunk_size_enabled"])))
    http_chunk_size_var.set(normalize_binary_size_value(settings.get("http_chunk_size", DEFAULTS["http_chunk_size"]), DEFAULTS["http_chunk_size"]))
    update_http_chunk_size_state()

    concurrent_captures_var.set(str(settings.get("concurrent_captures", DEFAULTS["concurrent_captures"]) or DEFAULTS["concurrent_captures"]))
    if concurrent_captures_var.get() not in {"1", "2", "3", "4"}:
        concurrent_captures_var.set(DEFAULTS["concurrent_captures"])

    concurrent_fragments_var.set(str(settings.get("concurrent_fragments", DEFAULTS["concurrent_fragments"]) or DEFAULTS["concurrent_fragments"]))
    if concurrent_fragments_var.get() not in {"1", "2", "4", "8"}:
        concurrent_fragments_var.set(DEFAULTS["concurrent_fragments"])

    keep_partials_var.set(bool(settings.get("keep_partials", DEFAULTS["keep_partials"])))
    write_info_json_var.set(bool(settings.get("write_info_json", DEFAULTS["write_info_json"])))
    write_source_link_var.set(bool(settings.get("write_source_link", DEFAULTS["write_source_link"])))
    write_description_var.set(bool(settings.get("write_description", DEFAULTS["write_description"])))
    write_thumbnail_var.set(bool(settings.get("write_thumbnail", DEFAULTS["write_thumbnail"])))
    write_subs_var.set(bool(settings.get("write_subs", DEFAULTS["write_subs"])))
    write_auto_subs_var.set(bool(settings.get("write_auto_subs", DEFAULTS["write_auto_subs"])))
    write_comments_var.set(bool(settings.get("write_comments", DEFAULTS["write_comments"])))
    embed_metadata_var.set(bool(settings.get("embed_metadata", DEFAULTS["embed_metadata"])))
    embed_thumbnail_var.set(bool(settings.get("embed_thumbnail", DEFAULTS["embed_thumbnail"])))
    embed_subs_var.set(bool(settings.get("embed_subs", DEFAULTS["embed_subs"])))
    embed_chapters_var.set(bool(settings.get("embed_chapters", DEFAULTS["embed_chapters"])))
    embed_info_json_var.set(bool(settings.get("embed_info_json", DEFAULTS["embed_info_json"])))
    vpn_adapter_var.set(settings.get("vpn_adapter_name", DEFAULTS["vpn_adapter_name"]))
    split_queue_mode_var.set(normalize_split_queue_mode(settings.get("split_queue_mode", DEFAULTS["split_queue_mode"])))
    split_queue_urls_per_group_var.set(normalize_positive_int_string(
        settings.get("split_queue_urls_per_group", DEFAULTS["split_queue_urls_per_group"]),
        DEFAULTS["split_queue_urls_per_group"],
    ))
    split_queue_group_count_var.set(normalize_positive_int_string(
        settings.get("split_queue_group_count", DEFAULTS["split_queue_group_count"]),
        DEFAULTS["split_queue_group_count"],
    ))
    url_preview_pacing_var.set(normalize_url_preview_pacing(settings.get("url_preview_pacing", DEFAULTS["url_preview_pacing"])))
    url_preview_thumbnail_mode_var.set(normalize_url_preview_thumbnail_mode(settings.get("url_preview_thumbnail_mode", DEFAULTS["url_preview_thumbnail_mode"])))
    url_preview_rate_limit_thumbnails_var.set(bool(settings.get("url_preview_rate_limit_thumbnails", DEFAULTS["url_preview_rate_limit_thumbnails"])))
    url_preview_cache_mode_var.set(normalize_url_preview_cache_mode(settings.get("url_preview_cache_mode", DEFAULTS["url_preview_cache_mode"])))
    url_preview_playlist_mode_var.set(normalize_url_preview_playlist_mode(settings.get("url_preview_playlist_mode", DEFAULTS["url_preview_playlist_mode"])))
    url_preview_max_playlist_items_var.set(normalize_url_preview_max_playlist_items(settings.get("url_preview_max_playlist_items", DEFAULTS["url_preview_max_playlist_items"])))
    url_preview_timeout_var.set(normalize_url_preview_timeout(settings.get("url_preview_timeout", DEFAULTS["url_preview_timeout"])))
    update_capture_options_summary()


def normalize_proxy_protocol(value):
    value = str(value or "").strip().lower()

    if value in {"", "none", "disabled"}:
        return "None"

    for option in PROXY_PROTOCOL_OPTIONS:
        if value == option.lower():
            return option

    return "None"


def normalize_proxy_port(value):
    value = str(value or "").strip()

    if not value:
        return ""

    if not value.isdigit():
        return ""

    port = int(value)
    if port < 1 or port > 65535:
        return ""

    return str(port)


def get_proxy_settings_dict(include_sensitive=True):
    protocol = normalize_proxy_protocol(proxy_protocol_var.get())
    no_save = bool(proxy_no_save_var.get())

    if no_save and not include_sensitive:
        return {
            "proxy_protocol": "None",
            "proxy_address": "",
            "proxy_port": "",
            "proxy_username": "",
            "proxy_password": "",
            "proxy_no_save": True,
        }

    return {
        "proxy_protocol": protocol,
        "proxy_address": proxy_address_var.get().strip(),
        "proxy_port": normalize_proxy_port(proxy_port_var.get()),
        "proxy_username": proxy_username_var.get().strip(),
        "proxy_password": proxy_password_var.get(),
        "proxy_no_save": no_save,
    }


def build_proxy_url_from_values(protocol, address, port, username="", password=""):
    protocol = normalize_proxy_protocol(protocol)

    if protocol == "None":
        return ""

    address = str(address or "").strip()
    port = normalize_proxy_port(port)
    username = str(username or "").strip()
    password = str(password or "")

    if not address:
        raise ValueError("Proxy Address is required when proxy is enabled.")

    if not port:
        raise ValueError("Proxy Port must be a number from 1 to 65535 when proxy is enabled.")

    if password and not username:
        raise ValueError("Proxy Username is required when a proxy password is provided.")

    address = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", "", address).strip().strip("/")
    if "@" in address:
        raise ValueError("Proxy Address should not include credentials. Use the Username and Password fields.")

    auth = ""
    if username:
        auth = quote(username, safe="")
        if password:
            auth += ":" + quote(password, safe="")
        auth += "@"

    return f"{protocol}://{auth}{address}:{port}/"


def get_proxy_url_for_command():
    return build_proxy_url_from_values(
        proxy_protocol_var.get(),
        proxy_address_var.get(),
        proxy_port_var.get(),
        proxy_username_var.get(),
        proxy_password_var.get(),
    )


def mask_proxy_url(value):
    value = str(value or "")

    if not value:
        return ""

    try:
        parts = urlsplit(value)
        if not parts.scheme or not parts.netloc:
            return "[proxy configured]"

        host = parts.hostname or ""
        port = f":{parts.port}" if parts.port else ""
        credential_marker = "***@" if (parts.username or parts.password) else ""
        return urlunsplit((parts.scheme, f"{credential_marker}{host}{port}", parts.path or "/", "", ""))
    except Exception:
        return "[proxy configured]"


def format_command_for_log(cmd):
    safe_parts = []
    skip_next_proxy = False

    for index, part in enumerate(cmd):
        if skip_next_proxy:
            skip_next_proxy = False
            continue

        if part in {"-ProxyUrl", "--proxy"} and index + 1 < len(cmd):
            safe_parts.append(part)
            safe_parts.append(mask_proxy_url(cmd[index + 1]))
            skip_next_proxy = True
            continue

        safe_parts.append(part)

    return " ".join(f'"{part}"' if " " in str(part) else str(part) for part in safe_parts)


def get_proxy_status_summary():
    protocol = normalize_proxy_protocol(proxy_protocol_var.get())

    if protocol == "None":
        return "disabled"

    address = proxy_address_var.get().strip()
    port = normalize_proxy_port(proxy_port_var.get())
    save_state = "temporary only" if proxy_no_save_var.get() else "saved in settings"
    target = f"{protocol}://{address}:{port}" if address and port else protocol
    return f"enabled ({target}; {save_state})"


URL_PREVIEW_PACING_OPTIONS = {
    "5 sec + up to 10 sec jitter": (5, 10),
    "10 sec + up to 15 sec jitter": (10, 15),
    "15 sec + up to 20 sec jitter": (15, 20),
}
URL_PREVIEW_THUMBNAIL_MODE_OPTIONS = ["Off", "Fast", "Reliable"]
URL_PREVIEW_CACHE_MODE_OPTIONS = ["Temporary", "Reuse cached thumbnails"]
URL_PREVIEW_PLAYLIST_MODE_OPTIONS = ["Fast playlist scan", "Deep metadata first N"]


def normalize_url_preview_pacing(value):
    value = str(value or "").strip()
    if value in URL_PREVIEW_PACING_OPTIONS:
        return value
    return DEFAULTS["url_preview_pacing"]


def normalize_url_preview_thumbnail_mode(value):
    value = str(value or "").strip().lower()
    for option in URL_PREVIEW_THUMBNAIL_MODE_OPTIONS:
        if value == option.lower():
            return option
    return DEFAULTS["url_preview_thumbnail_mode"]


def normalize_url_preview_cache_mode(value):
    value = str(value or "").strip().lower()
    for option in URL_PREVIEW_CACHE_MODE_OPTIONS:
        if value == option.lower():
            return option
    return DEFAULTS["url_preview_cache_mode"]


def normalize_url_preview_playlist_mode(value):
    value = str(value or "").strip().lower()
    for option in URL_PREVIEW_PLAYLIST_MODE_OPTIONS:
        if value == option.lower():
            return option
    return DEFAULTS["url_preview_playlist_mode"]


def normalize_url_preview_max_playlist_items(value):
    value = str(value or "").strip()
    if value.lower() in {"", "all", "0"}:
        return "0" if value == "0" else value
    if value.isdigit():
        return str(max(1, min(5000, int(value))))
    return DEFAULTS["url_preview_max_playlist_items"]


def normalize_url_preview_timeout(value):
    value = str(value or "").strip()
    if value.isdigit():
        return str(max(10, min(900, int(value))))
    return DEFAULTS["url_preview_timeout"]


def make_default_profile_settings():
    return DEFAULTS.copy()


def get_app_settings_dict():
    settings = {
        "delete_cookies_on_exit": delete_cookies_on_exit_var.get(),
        "check_vpn": check_vpn_var.get(),
        "dark_mode": dark_mode_var.get(),
        "case_browser_filter": case_browser_filter_var.get(),
        "case_browser_sort": case_browser_sort_var.get(),
        "case_browser_current_only": case_browser_current_only_var.get(),
        "case_browser_icon_scale": case_browser_icon_scale_var.get(),
        "job_persistence": job_persistence_var.get(),
        "url_box_persistence": url_box_persistence_var.get(),
        "universal_archive_enabled": universal_archive_enabled_var.get(),
    }
    settings.update(get_proxy_settings_dict(include_sensitive=False))
    return settings


def apply_app_settings_dict(settings):
    settings = settings if isinstance(settings, dict) else {}
    delete_cookies_on_exit_var.set(
        bool(settings.get("delete_cookies_on_exit", APP_SETTINGS_DEFAULTS["delete_cookies_on_exit"]))
    )
    check_vpn_var.set(
        bool(settings.get("check_vpn", APP_SETTINGS_DEFAULTS["check_vpn"]))
    )
    dark_mode_var.set(
        bool(settings.get("dark_mode", APP_SETTINGS_DEFAULTS["dark_mode"]))
    )
    apply_app_theme()
    case_browser_filter_var.set(
        settings.get("case_browser_filter", APP_SETTINGS_DEFAULTS["case_browser_filter"])
    )
    case_browser_sort_var.set(
        settings.get("case_browser_sort", APP_SETTINGS_DEFAULTS["case_browser_sort"])
    )
    case_browser_current_only_var.set(
        bool(settings.get("case_browser_current_only", APP_SETTINGS_DEFAULTS["case_browser_current_only"]))
    )
    case_browser_icon_scale_var.set(
        settings.get("case_browser_icon_scale", APP_SETTINGS_DEFAULTS["case_browser_icon_scale"])
    )
    try:
        job_persistence_var.set(
            bool(settings.get("job_persistence", APP_SETTINGS_DEFAULTS["job_persistence"]))
        )
    except Exception:
        pass

    try:
        url_box_persistence_var.set(
            bool(settings.get("url_box_persistence", APP_SETTINGS_DEFAULTS["url_box_persistence"]))
        )
    except Exception:
        pass

    try:
        universal_archive_enabled_var.set(
            bool(settings.get("universal_archive_enabled", APP_SETTINGS_DEFAULTS["universal_archive_enabled"]))
        )
    except Exception:
        pass

    proxy_no_save = bool(settings.get("proxy_no_save", APP_SETTINGS_DEFAULTS["proxy_no_save"]))
    proxy_no_save_var.set(proxy_no_save)

    if proxy_no_save:
        proxy_protocol_var.set("None")
        proxy_address_var.set("")
        proxy_port_var.set("")
        proxy_username_var.set("")
        proxy_password_var.set("")
    else:
        proxy_protocol_var.set(normalize_proxy_protocol(settings.get("proxy_protocol", APP_SETTINGS_DEFAULTS["proxy_protocol"])))
        proxy_address_var.set(str(settings.get("proxy_address", APP_SETTINGS_DEFAULTS["proxy_address"]) or ""))
        proxy_port_var.set(normalize_proxy_port(settings.get("proxy_port", APP_SETTINGS_DEFAULTS["proxy_port"])))
        proxy_username_var.set(str(settings.get("proxy_username", APP_SETTINGS_DEFAULTS["proxy_username"]) or ""))
        proxy_password_var.set(str(settings.get("proxy_password", APP_SETTINGS_DEFAULTS["proxy_password"]) or ""))

    update_vpn_section_visibility()


def get_app_settings_summary_lines():
    delete_state = "enabled" if delete_cookies_on_exit_var.get() else "disabled"
    vpn_state = "enabled" if check_vpn_var.get() else "disabled"
    persistence_state = "enabled" if job_persistence_var.get() else "disabled"
    url_box_state = "enabled" if url_box_persistence_var.get() else "disabled"
    universal_archive_state = "enabled" if universal_archive_enabled_var.get() else "disabled"
    return [
        f"Delete cookies on exit: {delete_state}",
        f"Check VPN: {vpn_state}",
        f"Job persistence: {persistence_state}",
        f"URL box persistence: {url_box_state}",
        f"Universal download archive: {universal_archive_state} (applies only when Archive Mode = Use)",
        f"Universal archive file: {UNIVERSAL_ARCHIVE_FILE}",
        f"Proxy: {get_proxy_status_summary()}",
    ]


def ensure_unrecognized_settings_store(store):
    if not isinstance(store, dict):
        store = {}

    unrecognized = store.get("unrecognized_settings")
    if not isinstance(unrecognized, dict):
        unrecognized = {}

    for key in ("top_level", "profiles", "app_settings"):
        if not isinstance(unrecognized.get(key), dict):
            unrecognized[key] = {}

    store["unrecognized_settings"] = unrecognized
    return store


def ensure_app_settings_store(store):
    if not isinstance(store, dict):
        store = {}

    store = ensure_unrecognized_settings_store(store)

    raw_app_settings = store.get("app_settings", {})
    if not isinstance(raw_app_settings, dict):
        raw_app_settings = {}

    recognized = APP_SETTINGS_DEFAULTS.copy()
    app_unknown = {}

    for key, value in raw_app_settings.items():
        if key in APP_SETTINGS_DEFAULTS:
            recognized[key] = value
        else:
            app_unknown[key] = value

    existing_app_unknown = store["unrecognized_settings"].get("app_settings", {})
    if isinstance(existing_app_unknown, dict):
        existing_app_unknown.update(app_unknown)
        store["unrecognized_settings"]["app_settings"] = existing_app_unknown
    else:
        store["unrecognized_settings"]["app_settings"] = app_unknown

    store["app_settings"] = recognized
    return store


def merge_profile_settings_with_defaults(profile_settings, profile_name=None, store=None):
    profile_settings = profile_settings if isinstance(profile_settings, dict) else {}

    recognized = make_default_profile_settings()
    unknown = {}

    for key, value in profile_settings.items():
        if key in DEFAULTS:
            recognized[key] = value
        else:
            unknown[key] = value

    if profile_name and store is not None and unknown:
        store = ensure_unrecognized_settings_store(store)
        existing = store["unrecognized_settings"].setdefault("profiles", {}).get(profile_name, {})
        if not isinstance(existing, dict):
            existing = {}
        existing.update(unknown)
        store["unrecognized_settings"]["profiles"][profile_name] = existing

    return recognized


def get_domain_preset_settings_from_source(settings=None):
    source = settings if isinstance(settings, dict) else get_settings_dict()
    return {
        key: source.get(key, DEFAULTS.get(key))
        for key in DOMAIN_PRESET_SETTING_KEYS
        if key in DEFAULTS
    }


def normalize_domain_preset_key(value):
    value = " ".join(str(value or "").strip().split())
    return value


def normalize_domain_preset_domain(value):
    value = str(value or "").strip().lower()

    if not value:
        return ""

    domain = get_url_domain_key(value)

    if domain:
        return domain

    value = value.strip(".")
    if not value or "." not in value:
        return ""

    return value


def normalize_domain_preset_domains(values):
    domains = []
    seen = set()

    if isinstance(values, str):
        # Allow comma, semicolon, whitespace, or newline separated custom entries.
        values = re.split(r"[\s,;|]+", values)

    for value in values or []:
        domain = normalize_domain_preset_domain(value)
        if not domain or domain in seen:
            continue
        seen.add(domain)
        domains.append(domain)

    return domains


def normalize_domain_presets(raw_presets):
    normalized = {}

    if isinstance(raw_presets, list):
        iterable = []
        for item in raw_presets:
            if isinstance(item, dict):
                iterable.append((item.get("name", ""), item))
    elif isinstance(raw_presets, dict):
        iterable = list(raw_presets.items())
    else:
        return normalized

    for raw_name, raw_preset in iterable:
        if isinstance(raw_preset, dict):
            preset_name = normalize_domain_preset_key(raw_preset.get("name", raw_name))
            enabled = bool(raw_preset.get("enabled", False))
            raw_settings = raw_preset.get("settings", {})
            raw_domains = raw_preset.get("match_domains", raw_preset.get("domains", []))
        else:
            preset_name = normalize_domain_preset_key(raw_name)
            enabled = False
            raw_settings = {}
            raw_domains = []

        # Backward compatibility: old presets used the domain as the dictionary key
        # and did not include a separate match_domains field.
        try:
            priority = int(raw_preset.get("priority", 100)) if isinstance(raw_preset, dict) else 100
        except Exception:
            priority = 100

        if not raw_domains:
            fallback_domain = normalize_domain_preset_domain(raw_name)
            raw_domains = [fallback_domain] if fallback_domain else []

        if not preset_name:
            continue

        match_domains = normalize_domain_preset_domains(raw_domains)
        if not match_domains:
            # A preset without any domains cannot match URLs, so skip it rather than
            # silently keeping an inert record.
            continue

        raw_settings = raw_settings if isinstance(raw_settings, dict) else {}
        settings = {}

        for key in DOMAIN_PRESET_SETTING_KEYS:
            if key in raw_settings and key in DEFAULTS:
                settings[key] = raw_settings[key]

        normalized[preset_name] = {
            "enabled": enabled,
            "name": preset_name,
            "priority": priority,
            "match_domains": match_domains,
            "settings": settings,
        }

    return normalized


def normalize_domain_presets_in_place(store):
    if not isinstance(store, dict):
        store = {}

    current = store.get("domain_presets", {})
    normalized = normalize_domain_presets(current)

    if isinstance(current, dict):
        current.clear()
        current.update(normalized)
        store["domain_presets"] = current
    else:
        store["domain_presets"] = normalized

    return store


def ensure_domain_presets_store(store):
    return normalize_domain_presets_in_place(store)


def get_domain_presets():
    store = ensure_settings_store()
    store = ensure_domain_presets_store(store)
    return store.setdefault("domain_presets", {})


def save_domain_presets(show_popup=False):
    try:
        store = ensure_settings_store()
        normalize_domain_presets_in_place(store)
        store["version"] = SETTINGS_SCHEMA_VERSION

        changed = settings_payload_has_changed(SETTINGS_FILE, store)

        if not changed:
            if show_popup:
                messagebox.showinfo("Presets unchanged", f"No domain preset changes detected.\n\n{SETTINGS_FILE}")
            return True

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)

        append_log(f"\nDomain presets saved to: {SETTINGS_FILE}\n")
        log_domain_presets_status("Domain presets")

        if show_popup:
            messagebox.showinfo("Domain presets saved", f"Domain presets saved to:\n\n{SETTINGS_FILE}")

        return True
    except Exception as e:
        messagebox.showerror("Save failed", f"Could not save domain presets:\n\n{e}")
        return False


def get_domain_preset_status():
    presets = get_domain_presets()
    loaded = sorted(presets.keys(), key=str.lower)
    active = sorted([
        name
        for name, preset in presets.items()
        if isinstance(preset, dict) and bool(preset.get("enabled", False))
    ], key=str.lower)

    return loaded, active


def log_domain_presets_status(label="Domain presets"):
    try:
        loaded, active = get_domain_preset_status()

        if loaded:
            append_log(f"{label}: {len(loaded)} loaded; {len(active)} active.\n")
            append_log(f"  Loaded presets: {', '.join(loaded)}\n")
            append_log(f"  Active presets: {', '.join(active) if active else 'none'}\n")
        else:
            append_log(f"{label}: none loaded.\n")
    except Exception as e:
        append_log(f"{label}: could not read domain preset status: {e}\n")


def get_current_domain_keys_from_urls():
    domains = []
    seen = set()

    for url in get_current_url_lines_for_queue():
        domain = get_url_domain_key(url)
        if domain and domain not in seen:
            seen.add(domain)
            domains.append(domain)

    return sorted(domains)


def get_enabled_domain_preset_matches(urls):
    presets = get_domain_presets()
    url_domains = {
        domain
        for domain in (get_url_domain_key(url) for url in (urls or []))
        if domain
    }

    matches = []

    if not url_domains:
        return matches

    for name, preset in presets.items():
        if not isinstance(preset, dict):
            continue
        if not preset.get("enabled", False):
            continue

        preset_domains = set(normalize_domain_preset_domains(preset.get("match_domains", [])))
        if not preset_domains:
            continue

        overlap = sorted(url_domains & preset_domains)
        if overlap:
            matches.append((name, preset, overlap))

    return sorted(matches, key=lambda item: (int(item[1].get("priority", 100)), item[0].lower()))


def apply_checked_domain_presets_to_settings(settings, urls):
    merged = settings.copy() if isinstance(settings, dict) else get_settings_dict()
    applied = []

    matches = get_enabled_domain_preset_matches(urls)

    # Apply low priority first so higher priority presets override lower priority settings.
    for name, preset, overlap in matches:
        preset_settings = preset.get("settings", {})
        if isinstance(preset_settings, dict):
            for key in DOMAIN_PRESET_SETTING_KEYS:
                if key in preset_settings:
                    merged[key] = preset_settings[key]

    applied = [
        name
        for name, preset, overlap in sorted(matches, key=lambda item: (-int(item[1].get("priority", 100)), item[0].lower()))
    ]

    return merged, applied


def format_domain_preset_settings_summary(settings, max_items=8):
    settings = settings if isinstance(settings, dict) else {}
    parts = []

    for key in DOMAIN_PRESET_SETTING_KEYS:
        if key in settings:
            parts.append(f"{key}={settings[key]}")

    if len(parts) > max_items:
        return ", ".join(parts[:max_items]) + f", ... +{len(parts) - max_items} more"

    return ", ".join(parts) if parts else "No preset settings"


def format_domain_preset_tooltip_text(name, preset):
    preset = preset if isinstance(preset, dict) else {}
    settings = preset.get("settings", {}) if isinstance(preset.get("settings", {}), dict) else {}
    domains = normalize_domain_preset_domains(preset.get("match_domains", []))

    lines = [
        str(name),
        "",
        f"Status: {'active/checked' if bool(preset.get('enabled', False)) else 'inactive/unchecked'}",
        f"Priority: {int(preset.get('priority', 100))}",
        f"Match domains: {', '.join(domains) if domains else 'none'}",
        "",
        "Stored Capture/Advanced settings:",
    ]

    if not settings:
        lines.append("  No stored settings")
    else:
        for key in DOMAIN_PRESET_SETTING_KEYS:
            if key in settings:
                lines.append(f"  {key}: {settings[key]}")

    return "\n".join(lines)



def open_domain_presets_window():
    global domain_preset_window

    try:
        if domain_preset_window is not None and domain_preset_window.winfo_exists():
            domain_preset_window.lift()
            return
    except Exception:
        domain_preset_window = None

    store = ensure_settings_store()

    def live_presets():
        return get_domain_presets()

    domain_preset_window = tk.Toplevel(root)
    domain_preset_window.title("Domain Presets")
    domain_preset_window.geometry("900x500")
    domain_preset_window.minsize(760, 380)

    main_frame = ttk.Frame(domain_preset_window, padding=12)
    main_frame.pack(fill="both", expand=True)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)

    ttk.Label(
        main_frame,
        text=(
            "Checked presets apply automatically when one or more of their match domains are detected by "
            "Start Capture or queue job creation. Presets store only Capture Options and Advanced Options."
        ),
        wraplength=680,
        justify="left",
    ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

    list_outer = ttk.Frame(main_frame)
    list_outer.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
    list_outer.columnconfigure(0, weight=1)
    list_outer.rowconfigure(0, weight=1)

    preset_tree = ttk.Treeview(
        list_outer,
        columns=("enabled", "priority", "name", "domains"),
        show="headings",
        selectmode="browse",
    )
    preset_tree.grid(row=0, column=0, sticky="nsew")

    preset_tree.heading("enabled", text="Use")
    preset_tree.heading("priority", text="Priority")
    preset_tree.heading("name", text="Preset Name")
    preset_tree.heading("domains", text="Match Domains")
    preset_tree.column("enabled", width=70, minwidth=70, anchor="center", stretch=False)
    preset_tree.column("priority", width=80, minwidth=70, anchor="center", stretch=False)
    preset_tree.column("name", width=230, minwidth=160, anchor="w", stretch=False)
    preset_tree.column("domains", width=380, minwidth=240, anchor="w", stretch=True)

    preset_scroll_y = ttk.Scrollbar(list_outer, orient="vertical", command=preset_tree.yview)
    preset_scroll_y.grid(row=0, column=1, sticky="ns")
    preset_tree.configure(yscrollcommand=preset_scroll_y.set)

    preset_status_var = tk.StringVar(value="")

    ttk.Label(
        list_outer,
        textvariable=preset_status_var,
        anchor="w",
    ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))

    def get_checked_preset_names():
        presets = live_presets()
        return [
            name
            for name, preset in presets.items()
            if isinstance(preset, dict) and bool(preset.get("enabled", False))
        ]

    def update_preset_status():
        presets = live_presets()
        total_count = len(presets)
        checked_count = len(get_checked_preset_names())

        if total_count:
            preset_status_var.set(f"{checked_count}/{total_count} preset(s) checked")
        else:
            preset_status_var.set("No domain presets saved yet. Use Save to create a preset.")

    def set_preset_checked(name, checked):
        presets = live_presets()
        if name not in presets:
            return

        presets.setdefault(name, {"enabled": False, "priority": 100, "match_domains": [], "settings": {}})["enabled"] = bool(checked)
        save_domain_presets(show_popup=False)
        refresh_list()

    def toggle_preset_checked(name):
        presets = live_presets()
        preset = presets.get(name, {})
        set_preset_checked(name, not bool(preset.get("enabled", False)))

    def get_selected_preset_name_from_row(row_id):
        if not row_id:
            return ""
        return preset_tree.set(row_id, "name").strip()

    def on_preset_tree_click(event):
        region = preset_tree.identify("region", event.x, event.y)
        if region not in {"cell", "tree"}:
            return

        row_id = preset_tree.identify_row(event.y)
        column_id = preset_tree.identify_column(event.x)

        if not row_id:
            return

        name = get_selected_preset_name_from_row(row_id)
        presets = live_presets()
        if not name or name not in presets:
            return

        if column_id in {"#1", "#2", "#3", "#4"}:
            toggle_preset_checked(name)

    preset_tree.bind("<Button-1>", on_preset_tree_click)

    def get_preset_tree_tooltip(item_id):
        try:
            name = get_selected_preset_name_from_row(item_id)
            presets = live_presets()
            if not name or name not in presets:
                return ""
            return format_domain_preset_tooltip_text(name, presets.get(name, {}))
        except Exception:
            return ""

    TreeviewHoverTooltip(preset_tree, get_preset_tree_tooltip, delay=450, wraplength=700)

    def refresh_list():
        presets = live_presets()

        for item in preset_tree.get_children():
            preset_tree.delete(item)

        if not presets:
            update_preset_status()
            return

        ordered_names = sorted(
            presets.keys(),
            key=lambda item: (-int(presets.get(item, {}).get("priority", 100)), item.lower()),
        )

        for name in ordered_names:
            preset = presets.get(name, {})
            domains = normalize_domain_preset_domains(preset.get("match_domains", []))
            mark = "☑" if bool(preset.get("enabled", False)) else "☐"
            priority = int(preset.get("priority", 100))
            preset_tree.insert("", "end", values=(mark, priority, name, ", ".join(domains)))

        update_preset_status()

    def choose_preset_save_options(detected_domains):
        result = {"name": "", "domains": []}

        dialog = tk.Toplevel(domain_preset_window)
        dialog.title("Save Domain Preset")
        dialog.geometry("640x430")
        dialog.minsize(560, 380)
        dialog.transient(domain_preset_window)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)

        ttk.Label(frame, text="Preset name").grid(row=0, column=0, sticky="w")

        name_var = tk.StringVar(value="")
        name_entry = ttk.Entry(frame, textvariable=name_var)
        name_entry.grid(row=1, column=0, sticky="ew", pady=(2, 10))
        name_entry.focus_set()

        ttk.Label(
            frame,
            text=(
                "Match domains. Detected domains are added automatically; custom domains can be added below. "
                "Checked domains are used for matching."
            ),
            wraplength=590,
            justify="left",
        ).grid(row=2, column=0, sticky="ew", pady=(0, 6))

        add_frame = ttk.Frame(frame)
        add_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        add_frame.columnconfigure(0, weight=1)

        custom_domain_var = tk.StringVar(value="")
        custom_domain_entry = ttk.Entry(add_frame, textvariable=custom_domain_var)
        custom_domain_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        domain_frame = ttk.Frame(frame)
        domain_frame.grid(row=4, column=0, sticky="nsew")
        domain_frame.columnconfigure(0, weight=1)
        domain_frame.rowconfigure(0, weight=1)

        domain_tree = ttk.Treeview(
            domain_frame,
            columns=("enabled", "domain", "source"),
            show="headings",
            selectmode="browse",
        )
        domain_tree.grid(row=0, column=0, sticky="nsew")

        domain_tree.heading("enabled", text="Use")
        domain_tree.heading("domain", text="Domain")
        domain_tree.heading("source", text="Source")
        domain_tree.column("enabled", width=70, minwidth=70, anchor="center", stretch=False)
        domain_tree.column("domain", width=330, minwidth=220, anchor="w", stretch=True)
        domain_tree.column("source", width=120, minwidth=90, anchor="w", stretch=False)

        domain_scroll = ttk.Scrollbar(domain_frame, orient="vertical", command=domain_tree.yview)
        domain_scroll.grid(row=0, column=1, sticky="ns")
        domain_tree.configure(yscrollcommand=domain_scroll.set)

        domain_items = {}

        def domain_is_valid(domain):
            domain = str(domain or "").strip().lower()
            if not domain or "." not in domain:
                return False

            labels = domain.split(".")
            if len(labels) < 2:
                return False

            label_pattern = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)
            for label in labels:
                if not label or not label_pattern.match(label):
                    return False

            tld = labels[-1]
            if len(tld) < 2 or not re.match(r"^[a-z][a-z0-9-]*$", tld, flags=re.IGNORECASE):
                return False

            return True

        def refresh_domain_tree():
            selected = domain_tree.selection()
            selected_domain = ""
            if selected:
                try:
                    selected_domain = domain_tree.set(selected[0], "domain").strip()
                except Exception:
                    selected_domain = ""

            for item in domain_tree.get_children():
                domain_tree.delete(item)

            for domain in sorted(domain_items.keys()):
                item = domain_items[domain]
                mark = "☑" if item.get("enabled", False) else "☐"
                source_text = ", ".join(item.get("sources", []))
                row_id = domain_tree.insert("", "end", values=(mark, domain, source_text))
                if selected_domain == domain:
                    domain_tree.selection_set(row_id)
                    domain_tree.focus(row_id)

        def add_domain(domain, source="Custom", checked=True):
            domain = normalize_domain_preset_domain(domain)

            if not domain or not domain_is_valid(domain):
                return False

            item = domain_items.setdefault(domain, {"enabled": bool(checked), "sources": []})
            item["enabled"] = bool(checked) or bool(item.get("enabled", False))

            sources = item.setdefault("sources", [])
            if source not in sources:
                sources.append(source)

            return True

        for detected_domain in detected_domains:
            add_domain(detected_domain, source="Detected", checked=True)

        def parse_custom_domain_tokens(raw_value):
            raw_value = str(raw_value or "").strip()
            if not raw_value:
                return [], []

            raw_tokens = [token.strip() for token in re.split(r"[\s,;|]+", raw_value) if token.strip()]
            valid_domains = []
            invalid_tokens = []

            for token in raw_tokens:
                domain = normalize_domain_preset_domain(token)
                if domain and domain_is_valid(domain):
                    if domain not in valid_domains:
                        valid_domains.append(domain)
                else:
                    invalid_tokens.append(token)

            return valid_domains, invalid_tokens

        def add_custom_domain():
            valid_domains, invalid_tokens = parse_custom_domain_tokens(custom_domain_var.get())

            if invalid_tokens:
                messagebox.showwarning(
                    "Invalid domain",
                    "The following custom domain value(s) were not added:\n\n"
                    + "\n".join(invalid_tokens[:12])
                    + ("\n..." if len(invalid_tokens) > 12 else "")
                    + "\n\nUse domains such as example.com, sub.example.com, or example.co.uk.",
                    parent=dialog,
                )

            if not valid_domains:
                if not invalid_tokens:
                    messagebox.showwarning(
                        "No domain entered",
                        "Enter one or more custom domains such as example.com, separated by spaces or commas.",
                        parent=dialog,
                    )
                return

            for domain in valid_domains:
                add_domain(domain, source="Custom", checked=True)

            custom_domain_var.set("")
            refresh_domain_tree()

        def remove_selected_custom_domain():
            selected = domain_tree.selection()
            if not selected:
                return

            try:
                domain = domain_tree.set(selected[0], "domain").strip()
            except Exception:
                domain = ""

            if not domain or domain not in domain_items:
                return

            sources = domain_items[domain].get("sources", [])
            if "Custom" not in sources:
                messagebox.showinfo("Detected domain", "Detected domains cannot be removed here. Uncheck the domain instead.", parent=dialog)
                return

            sources = [source for source in sources if source != "Custom"]
            if sources:
                domain_items[domain]["sources"] = sources
            else:
                domain_items.pop(domain, None)

            refresh_domain_tree()

        def set_all_domains(checked):
            for item in domain_items.values():
                item["enabled"] = bool(checked)
            refresh_domain_tree()

        def toggle_domain_row(event):
            row_id = domain_tree.identify_row(event.y)
            column_id = domain_tree.identify_column(event.x)

            if not row_id:
                return

            try:
                domain = domain_tree.set(row_id, "domain").strip()
            except Exception:
                domain = ""

            if not domain or domain not in domain_items:
                return

            if column_id in {"#1", "#2", "#3"}:
                domain_items[domain]["enabled"] = not bool(domain_items[domain].get("enabled", False))
                refresh_domain_tree()

        domain_tree.bind("<Button-1>", toggle_domain_row)

        ttk.Button(add_frame, text="Add Custom", command=add_custom_domain).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(add_frame, text="Remove Custom", command=remove_selected_custom_domain).grid(row=0, column=2)

        list_buttons = ttk.Frame(frame)
        list_buttons.grid(row=5, column=0, sticky="w", pady=(8, 10))

        ttk.Button(list_buttons, text="Select All", command=lambda: set_all_domains(True)).pack(side="left", padx=(0, 6))
        ttk.Button(list_buttons, text="Select None", command=lambda: set_all_domains(False)).pack(side="left")

        ttk.Label(
            frame,
            text="The preset name does not need to match a domain. Multiple presets can use the same match domain.",
            wraplength=590,
            justify="left",
        ).grid(row=6, column=0, sticky="ew", pady=(0, 8))

        buttons = ttk.Frame(frame)
        buttons.grid(row=7, column=0, sticky="e")

        def save_choice():
            name = normalize_domain_preset_key(name_var.get())

            if not name:
                messagebox.showwarning("Preset name required", "Enter a preset name.", parent=dialog)
                return

            domains = [
                domain
                for domain in sorted(domain_items.keys())
                if bool(domain_items[domain].get("enabled", False))
            ]

            if not domains:
                messagebox.showwarning(
                    "Match domain required",
                    "Check at least one detected or custom match domain.",
                    parent=dialog,
                )
                return

            result["name"] = name
            result["domains"] = normalize_domain_preset_domains(domains)
            dialog.destroy()

        def cancel_choice():
            result["name"] = ""
            result["domains"] = []
            dialog.destroy()

        ttk.Button(buttons, text="Save", command=save_choice).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Cancel", command=cancel_choice).pack(side="left")

        custom_domain_entry.bind("<Return>", lambda event: add_custom_domain())
        dialog.bind("<Escape>", lambda event: cancel_choice())
        dialog.protocol("WM_DELETE_WINDOW", cancel_choice)

        refresh_domain_tree()

        try:
            configure_tk_widget_theme(dialog, get_theme_colors())
        except Exception:
            pass

        dialog.wait_window()
        return result["name"], result["domains"]


    def save_current_as_domain_presets():
        detected_domains = get_current_domain_keys_from_urls()
        preset_name, match_domains = choose_preset_save_options(detected_domains)

        if not preset_name:
            return

        presets = live_presets()

        if preset_name in presets:
            proceed = messagebox.askyesno(
                "Overwrite existing preset?",
                f"A domain preset named '{preset_name}' already exists.\n\n"
                "Overwrite it with the current Capture Options, Advanced Options, and selected match domains?",
                parent=domain_preset_window,
            )

            if not proceed:
                return

        preset_settings = get_domain_preset_settings_from_source()
        presets = live_presets()
        new_priority = max([int(item.get("priority", 100)) for item in presets.values() if isinstance(item, dict)] or [90]) + 10
        presets[preset_name] = {
            "enabled": True,
            "name": preset_name,
            "priority": new_priority,
            "match_domains": match_domains,
            "settings": preset_settings.copy(),
        }

        save_domain_presets(show_popup=False)
        refresh_list()
        append_log(f"\nSaved current capture/advanced options as domain preset: {preset_name}\n")
        append_log(f"Match domains: {', '.join(match_domains)}\n")
        messagebox.showinfo(
            "Domain preset saved",
            "Saved current Capture Options and Advanced Options for:\n\n"
            f"{preset_name}\n\nMatch domains:\n{', '.join(match_domains)}",
            parent=domain_preset_window,
        )

    def select_all(value):
        presets = live_presets()

        for name in list(presets.keys()):
            presets.setdefault(name, {"enabled": False, "priority": 100, "match_domains": [], "settings": {}})["enabled"] = bool(value)

        save_domain_presets(show_popup=False)
        refresh_list()

    def get_selected_preset_name():
        selection = preset_tree.selection()
        if not selection:
            return ""
        return get_selected_preset_name_from_row(selection[0])

    def adjust_selected_preset_priority(delta):
        name = get_selected_preset_name()
        presets = live_presets()

        if not name or name not in presets:
            messagebox.showinfo("No preset selected", "Select a preset first.", parent=domain_preset_window)
            return

        current = int(presets[name].get("priority", 100))
        presets[name]["priority"] = max(0, current + int(delta))
        save_domain_presets(show_popup=False)
        refresh_list()

    def normalize_preset_priorities_from_order():
        presets = live_presets()
        ordered = sorted(
            presets.keys(),
            key=lambda item: (-int(presets.get(item, {}).get("priority", 100)), item.lower()),
        )

        priority = len(ordered) * 10
        for name in ordered:
            presets[name]["priority"] = priority
            priority -= 10

        save_domain_presets(show_popup=False)
        refresh_list()

    def export_presets(selected_only=False):
        export_names = []

        if selected_only:
            export_names = get_checked_preset_names()
            if not export_names:
                messagebox.showinfo("No selected presets", "No checked presets are selected for export.", parent=domain_preset_window)
                return
        else:
            presets = live_presets()
            export_names = sorted(presets.keys(), key=str.lower)
            if not export_names:
                messagebox.showinfo("No presets", "There are no domain presets to export.", parent=domain_preset_window)
                return

        path = filedialog.asksaveasfilename(
            title="Export domain presets",
            defaultextension=".json",
            initialfile="yt-dlp-gui-domain-presets.json",
            initialdir=ROOT,
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
            parent=domain_preset_window,
        )

        if not path:
            return

        presets = live_presets()
        payload = {
            "type": "yt-dlp-gui-domain-presets",
            "version": 2,
            "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "domain_presets": {
                name: presets[name]
                for name in export_names
                if name in presets
            },
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            append_log(f"\nExported {len(export_names)} domain preset(s) to: {path}\n")
            messagebox.showinfo("Export complete", f"Exported {len(export_names)} domain preset(s) to:\n\n{path}", parent=domain_preset_window)
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export domain presets:\n\n{e}", parent=domain_preset_window)

    def make_unique_import_preset_name(base_name, existing_names):
        candidate = normalize_domain_preset_key(base_name) or "Imported preset"
        if candidate not in existing_names:
            return candidate

        index = 2
        while True:
            renamed = f"{candidate} ({index})"
            if renamed not in existing_names:
                return renamed
            index += 1

    def choose_import_conflict_mode(conflicts):
        if not conflicts:
            return "overwrite"

        result = {"mode": "skip"}

        dialog = tk.Toplevel(domain_preset_window)
        dialog.title("Import Preset Conflicts")
        dialog.geometry("620x360")
        dialog.minsize(540, 300)
        dialog.transient(domain_preset_window)
        dialog.grab_set()

        ttk.Label(
            dialog,
            text="The import file contains preset names that already exist. Choose how to handle conflicts:",
            wraplength=570,
            justify="left",
        ).pack(fill="x", padx=12, pady=(12, 8))

        text_box = scrolledtext.ScrolledText(dialog, height=8, wrap="word")
        text_box.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        text_box.insert("1.0", "\n".join(conflicts[:40]) + ("\n..." if len(conflicts) > 40 else ""))
        text_box.configure(state="disabled")

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=12, pady=(0, 12))

        def choose(mode):
            result["mode"] = mode
            dialog.destroy()

        ttk.Button(button_frame, text="Overwrite", command=lambda: choose("overwrite")).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="Rename Imported", command=lambda: choose("rename")).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="Skip Existing", command=lambda: choose("skip")).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="Cancel", command=lambda: choose("cancel")).pack(side="right")

        dialog.protocol("WM_DELETE_WINDOW", lambda: choose("cancel"))
        dialog.wait_window()
        return result["mode"]

    def import_presets():
        path = filedialog.askopenfilename(
            title="Import domain presets",
            initialdir=ROOT,
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
            parent=domain_preset_window,
        )

        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            raw_presets = payload.get("domain_presets", payload) if isinstance(payload, dict) else {}
            imported = normalize_domain_presets(raw_presets)

            if not imported:
                messagebox.showwarning("No presets found", "The selected file did not contain any usable domain presets.", parent=domain_preset_window)
                return

            presets = live_presets()
            conflicts = sorted(set(imported.keys()) & set(presets.keys()), key=str.lower)
            conflict_mode = choose_import_conflict_mode(conflicts)

            if conflict_mode == "cancel":
                return

            imported_count = 0
            skipped_count = 0
            renamed_count = 0
            presets = live_presets()
            existing_names = set(presets.keys())

            for name, preset in imported.items():
                target_name = name

                if name in presets:
                    if conflict_mode == "skip":
                        skipped_count += 1
                        continue
                    if conflict_mode == "rename":
                        target_name = make_unique_import_preset_name(name, existing_names)
                        preset = preset.copy()
                        preset["name"] = target_name
                        renamed_count += 1

                presets[target_name] = preset
                existing_names.add(target_name)
                imported_count += 1

            save_domain_presets(show_popup=False)
            refresh_list()

            append_log(
                f"\nImported {imported_count} domain preset(s) from: {path}"
                f" ({renamed_count} renamed, {skipped_count} skipped).\n"
            )
            messagebox.showinfo(
                "Import complete",
                f"Imported {imported_count} domain preset(s).\nRenamed: {renamed_count}\nSkipped: {skipped_count}",
                parent=domain_preset_window,
            )
        except Exception as e:
            messagebox.showerror("Import failed", f"Could not import domain presets:\n\n{e}", parent=domain_preset_window)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=1, sticky="ns")

    ttk.Button(button_frame, text="Save", command=save_current_as_domain_presets).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Import", command=import_presets).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Export Selected", command=lambda: export_presets(selected_only=True)).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Export All", command=lambda: export_presets(selected_only=False)).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Select All", command=lambda: select_all(True)).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Select None", command=lambda: select_all(False)).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Priority Up", command=lambda: adjust_selected_preset_priority(10)).pack(fill="x", pady=(12, 6))
    ttk.Button(button_frame, text="Priority Down", command=lambda: adjust_selected_preset_priority(-10)).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Normalize Priority", command=normalize_preset_priorities_from_order).pack(fill="x", pady=(0, 6))
    ttk.Button(button_frame, text="Close", command=domain_preset_window.destroy).pack(fill="x", pady=(18, 0))

    def on_close_presets():
        global domain_preset_window
        try:
            domain_preset_window.destroy()
        except Exception:
            pass
        domain_preset_window = None

    domain_preset_window.protocol("WM_DELETE_WINDOW", on_close_presets)
    refresh_list()

    try:
        configure_tk_widget_theme(domain_preset_window, get_theme_colors())
    except Exception:
        pass


def open_proxy_options_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Proxy Options")
    dialog.transient(root)
    dialog.grab_set()
    dialog.resizable(False, False)

    local_protocol_var = tk.StringVar(value=normalize_proxy_protocol(proxy_protocol_var.get()))
    local_address_var = tk.StringVar(value=proxy_address_var.get())
    local_port_var = tk.StringVar(value=proxy_port_var.get())
    local_username_var = tk.StringVar(value=proxy_username_var.get())
    local_password_var = tk.StringVar(value=proxy_password_var.get())
    local_no_save_var = tk.BooleanVar(value=proxy_no_save_var.get())

    frame = ttk.Frame(dialog, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(1, weight=1)

    warning = (
        "Warning: Proxy settings can include credentials. If saved, they are stored unencrypted "
        "in gui-settings.json. Proxy credentials may also be visible to local administrators or "
        "process inspection tools while a capture is running."
    )

    ttk.Label(
        frame,
        text=warning,
        wraplength=520,
        justify="left",
    ).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))

    ttk.Label(frame, text="Protocol").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
    protocol_menu = ttk.Combobox(
        frame,
        textvariable=local_protocol_var,
        values=PROXY_PROTOCOL_OPTIONS,
        state="readonly",
        width=12,
    )
    protocol_menu.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Address").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
    address_entry = ttk.Entry(frame, textvariable=local_address_var, width=44)
    address_entry.grid(row=2, column=1, sticky="ew", pady=4)
    ttk.Label(frame, text="example: 127.0.0.1 or proxy.example.com").grid(row=2, column=2, sticky="w", padx=(8, 0), pady=4)

    ttk.Label(frame, text="Port").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
    port_entry = ttk.Entry(frame, textvariable=local_port_var, width=12)
    port_entry.grid(row=3, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Username").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
    username_entry = ttk.Entry(frame, textvariable=local_username_var, width=44)
    username_entry.grid(row=4, column=1, sticky="ew", pady=4)

    ttk.Label(frame, text="Password").grid(row=5, column=0, sticky="w", padx=(0, 8), pady=4)
    password_entry = ttk.Entry(frame, textvariable=local_password_var, width=44, show="*")
    password_entry.grid(row=5, column=1, sticky="ew", pady=4)

    no_save_check = ttk.Checkbutton(
        frame,
        text="Do not save proxy options to settings file; keep them only until the app closes",
        variable=local_no_save_var,
    )
    no_save_check.grid(row=6, column=0, columnspan=3, sticky="w", pady=(10, 8))

    status_var = tk.StringVar(value="")
    ttk.Label(frame, textvariable=status_var, wraplength=520, justify="left").grid(row=7, column=0, columnspan=3, sticky="ew", pady=(0, 10))

    trace_handles = []

    def get_local_proxy_summary():
        protocol = normalize_proxy_protocol(local_protocol_var.get())

        if protocol == "None":
            return "disabled"

        address = local_address_var.get().strip()
        port = normalize_proxy_port(local_port_var.get())
        save_state = "temporary only" if local_no_save_var.get() else "saved in settings"
        target = f"{protocol}://{address}:{port}" if address and port else protocol
        return f"enabled ({target}; {save_state})"

    def update_control_state(*args):
        enabled = normalize_proxy_protocol(local_protocol_var.get()) != "None"
        state = "normal" if enabled else "disabled"

        for widget in (address_entry, port_entry, username_entry, password_entry):
            try:
                widget.configure(state=state)
            except Exception:
                pass

        status_var.set(f"Current proxy: {get_local_proxy_summary()}")

    def clear_proxy():
        local_protocol_var.set("None")
        local_address_var.set("")
        local_port_var.set("")
        local_username_var.set("")
        local_password_var.set("")
        update_control_state()

    def validate_local_proxy():
        protocol = normalize_proxy_protocol(local_protocol_var.get())

        if protocol == "None":
            return True

        port = normalize_proxy_port(local_port_var.get())
        if not local_address_var.get().strip():
            messagebox.showerror("Proxy address required", "Proxy Address is required when proxy is enabled.")
            return False
        if not port:
            messagebox.showerror("Invalid proxy port", "Proxy Port must be a number from 1 to 65535.")
            return False

        try:
            build_proxy_url_from_values(
                protocol,
                local_address_var.get(),
                port,
                local_username_var.get(),
                local_password_var.get(),
            )
        except Exception as e:
            messagebox.showerror("Invalid proxy settings", str(e))
            return False

        local_protocol_var.set(protocol)
        local_port_var.set(port)
        return True

    def commit_local_proxy_to_app():
        proxy_protocol_var.set(normalize_proxy_protocol(local_protocol_var.get()))
        proxy_address_var.set(local_address_var.get().strip())
        proxy_port_var.set(normalize_proxy_port(local_port_var.get()))
        proxy_username_var.set(local_username_var.get().strip())
        proxy_password_var.set(local_password_var.get())
        proxy_no_save_var.set(bool(local_no_save_var.get()))

    def apply_proxy(close_after=False):
        if not validate_local_proxy():
            return False

        commit_local_proxy_to_app()

        saved = save_app_settings(
            show_popup=False,
            changed_setting_label="Proxy Options updated",
        )

        if saved:
            if proxy_no_save_var.get():
                append_log("\nProxy options updated for this app session only. Sensitive proxy fields were not saved to gui-settings.json.\n")
            else:
                append_log("\nProxy options saved as app-level settings. Proxy settings are stored unencrypted in gui-settings.json.\n")

        update_control_state()

        if close_after:
            close_dialog()

        return True

    def remove_traces():
        for variable, trace_id in trace_handles:
            try:
                variable.trace_remove("write", trace_id)
            except Exception:
                pass
        trace_handles.clear()

    def close_dialog():
        remove_traces()
        try:
            dialog.destroy()
        except Exception:
            pass

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=8, column=0, columnspan=3, sticky="e")

    ttk.Button(button_frame, text="Clear", command=clear_proxy).pack(side="left", padx=(0, 6))
    ttk.Button(button_frame, text="Apply", command=lambda: apply_proxy(False)).pack(side="left", padx=(0, 6))
    ttk.Button(button_frame, text="OK", command=lambda: apply_proxy(True)).pack(side="left", padx=(0, 6))
    ttk.Button(button_frame, text="Cancel", command=close_dialog).pack(side="left")

    protocol_menu.bind("<<ComboboxSelected>>", update_control_state)
    for variable in (local_protocol_var, local_address_var, local_port_var, local_username_var, local_password_var, local_no_save_var):
        try:
            trace_id = variable.trace_add("write", update_control_state)
            trace_handles.append((variable, trace_id))
        except Exception:
            pass

    dialog.protocol("WM_DELETE_WINDOW", close_dialog)
    update_control_state()

    try:
        configure_tk_widget_theme(dialog, get_theme_colors())
    except Exception:
        pass

    try:
        dialog.wait_window()
    except Exception:
        pass



def log_app_settings_status(prefix="App settings"):
    append_log(f"{prefix}:\n")
    for line in get_app_settings_summary_lines():
        append_log(f"  - {line}\n")


def save_app_settings(show_popup=False, changed_setting_label=None):
    store = ensure_settings_store()
    store = ensure_app_settings_store(store)
    store["app_settings"] = get_app_settings_dict()
    store["version"] = SETTINGS_SCHEMA_VERSION

    try:
        changed = settings_payload_has_changed(SETTINGS_FILE, store)

        if not changed:
            if show_popup:
                messagebox.showinfo("Settings unchanged", f"No app setting changes detected.\n\n{SETTINGS_FILE}")
            return True

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)

        if changed_setting_label:
            append_log(f"\nApp-level setting changed: {changed_setting_label}\n")
            append_log(f"App settings saved to: {SETTINGS_FILE}\n")
        elif show_popup:
            append_log(f"\nApp settings saved to: {SETTINGS_FILE}\n")

        if show_popup:
            messagebox.showinfo("Settings saved", f"Settings saved to:\n\n{SETTINGS_FILE}")

        return True
    except Exception as e:
        messagebox.showerror("Save failed", f"Could not save app settings:\n\n{e}")
        return False


def update_cookies_file_control_state():
    try:
        state = "normal" if use_cookies_file_var.get() else "disabled"
        cookies_file_entry.configure(state=state)
        cookies_file_browse_button.configure(state=state)
    except Exception:
        # The profile setting can be loaded before the Cookies File row exists during startup.
        pass


def toggle_use_cookies_file_setting():
    update_cookies_file_control_state()
    state = "enabled" if use_cookies_file_var.get() else "disabled"
    saved = save_settings(show_popup=False)
    if saved:
        append_log(f"Profile setting changed: Use Cookies File {state}\n")


def adjust_window_for_vpn_visibility():
    """Keep the top-level window size stable when VPN checking is toggled.

    The VPN panel is shown/hidden inside the existing Capture tab space. The
    Output Log row owns the extra vertical slack, so it expands when the VPN
    panel is hidden and retracts when the VPN panel is visible.
    """
    try:
        root.minsize(APP_WINDOW_MIN_WIDTH, APP_WINDOW_MIN_HEIGHT_WITH_VPN)
        main.rowconfigure(10, weight=0, minsize=URL_ROW_MIN_HEIGHT)
        main.rowconfigure(15, weight=1)
        root.update_idletasks()
    except Exception:
        pass

def update_vpn_section_visibility():
    try:
        if check_vpn_var.get():
            vpn_frame.grid()
        else:
            vpn_frame.grid_remove()
            vpn_status_var.set("VPN: Check disabled")

        adjust_window_for_vpn_visibility()
    except Exception:
        # The app setting can be loaded before the VPN frame exists during startup.
        pass



def toggle_check_vpn_setting():
    update_vpn_section_visibility()
    state = "enabled" if check_vpn_var.get() else "disabled"
    save_app_settings(show_popup=False, changed_setting_label=f"Check VPN {state}")


def toggle_job_persistence_setting():
    state = "enabled" if job_persistence_var.get() else "disabled"
    saved = save_app_settings(show_popup=False, changed_setting_label=f"Job Persistence {state}")
    if saved and job_persistence_var.get():
        save_job_queue_state()
        append_log(f"Job queue state saved to: {JOBS_FILE}\n")


def toggle_url_box_persistence_setting():
    state = "enabled" if url_box_persistence_var.get() else "disabled"
    saved = save_app_settings(show_popup=False, changed_setting_label=f"URL Box Persistence {state}")
    if saved and url_box_persistence_var.get():
        save_url_box_persistence_if_enabled()
        append_log(f"URL box contents saved to: {URL_BOX_PERSISTENCE_FILE}\n")


def toggle_universal_archive_setting():
    state = "enabled" if universal_archive_enabled_var.get() else "disabled"
    saved = save_app_settings(show_popup=False, changed_setting_label=f"Universal Download Archive {state}")
    if saved and universal_archive_enabled_var.get():
        append_log(f"Universal archive file will be used with Archive Mode = Use:\n{UNIVERSAL_ARCHIVE_FILE}\n")


def delete_universal_archive_file():
    if not os.path.isfile(UNIVERSAL_ARCHIVE_FILE):
        messagebox.showinfo(
            "Universal archive not found",
            f"The universal archive file does not exist yet:\n\n{UNIVERSAL_ARCHIVE_FILE}",
        )
        return

    confirm = messagebox.askyesno(
        "Delete universal archive?",
        "Delete the app-level universal download archive?\n\n"
        f"{UNIVERSAL_ARCHIVE_FILE}\n\n"
        "This may allow previously captured media from other cases to be captured again. Case-specific download archives are not deleted.",
    )

    if not confirm:
        return

    try:
        os.remove(UNIVERSAL_ARCHIVE_FILE)
        append_log(f"\nUniversal archive deleted:\n{UNIVERSAL_ARCHIVE_FILE}\n")
        messagebox.showinfo("Universal archive deleted", f"Deleted:\n\n{UNIVERSAL_ARCHIVE_FILE}")
    except Exception as e:
        messagebox.showerror("Delete failed", f"Could not delete the universal archive file:\n\n{UNIVERSAL_ARCHIVE_FILE}\n\n{e}")


def should_pass_universal_archive(archive_mode=None):
    mode = str(archive_mode if archive_mode is not None else archive_mode_var.get()).strip().lower() or "use"
    return bool(universal_archive_enabled_var.get()) and mode == "use"


def delete_selected_cookies_file_on_exit():
    cookies_path = cookies_file_var.get().strip()

    if not use_cookies_file_var.get():
        append_log("\nCookies file use is disabled. Delete cookies on exit was skipped.\n")
        return

    if not delete_cookies_on_exit_var.get():
        append_log("\nDelete cookies on exit is disabled. Cookies file was not deleted.\n")
        return

    if not cookies_path:
        append_log("\nDelete cookies on exit is enabled, but the Cookies File field is blank.\n")
        return

    if not os.path.isfile(cookies_path):
        append_log(f"\nDelete cookies on exit is enabled, but the cookies file was not found:\n{cookies_path}\n")
        return

    try:
        os.remove(cookies_path)
        append_log(f"\nDeleted cookies file on exit:\n{cookies_path}\n")
    except Exception as e:
        append_log(f"\nFailed to delete cookies file on exit:\n{cookies_path}\nError: {e}\n")
        messagebox.showwarning(
            "Cookies file not deleted",
            f"Delete cookies on exit is enabled, but the cookies file could not be deleted:\n\n{cookies_path}\n\n{e}",
        )


def get_settings_store_version(raw):
    if not isinstance(raw, dict):
        return 1

    version = raw.get("version", 1)

    try:
        return int(version)
    except Exception:
        return 1


def normalize_settings_store(raw):
    raw = raw if isinstance(raw, dict) else {}
    source_version = get_settings_store_version(raw)

    store = {
        "version": SETTINGS_SCHEMA_VERSION,
        "loaded_version": source_version,
        "profiles": {},
        "app_settings": {},
        "domain_presets": {},
        "unrecognized_settings": {
            "top_level": {},
            "profiles": {},
            "app_settings": {},
        },
    }

    existing_unrecognized = raw.get("unrecognized_settings", {})
    if isinstance(existing_unrecognized, dict):
        for key in ("top_level", "profiles", "app_settings"):
            if isinstance(existing_unrecognized.get(key), dict):
                store["unrecognized_settings"][key].update(existing_unrecognized[key])

    recognized_top_level = {"version", "profiles", "app_settings", "domain_presets", "unrecognized_settings", "loaded_version"}
    for key, value in raw.items():
        if key not in recognized_top_level:
            store["unrecognized_settings"]["top_level"][key] = value

    if "profiles" in raw and isinstance(raw.get("profiles"), dict):
        profiles = raw.get("profiles", {})
    else:
        # Backward compatibility with older flat settings files.
        profiles = {DEFAULT_PROFILE_NAME: raw}

    for name, profile_settings in profiles.items():
        profile_name = str(name).strip()
        if not profile_name:
            continue

        store["profiles"][profile_name] = merge_profile_settings_with_defaults(
            profile_settings,
            profile_name=profile_name,
            store=store,
        )

    if DEFAULT_PROFILE_NAME not in store["profiles"]:
        store["profiles"][DEFAULT_PROFILE_NAME] = make_default_profile_settings()

    store["app_settings"] = raw.get("app_settings", {}) if isinstance(raw.get("app_settings", {}), dict) else {}
    store["domain_presets"] = normalize_domain_presets(raw.get("domain_presets", {}))
    store = ensure_app_settings_store(store)
    store = ensure_domain_presets_store(store)
    store["version"] = SETTINGS_SCHEMA_VERSION
    store["loaded_version"] = source_version

    return store


def ensure_settings_store():
    global settings_store

    if not isinstance(settings_store, dict) or "profiles" not in settings_store:
        settings_store = {
            "version": SETTINGS_SCHEMA_VERSION,
            "loaded_version": SETTINGS_SCHEMA_VERSION,
            "profiles": {
                DEFAULT_PROFILE_NAME: get_settings_dict(),
            },
            "app_settings": get_app_settings_dict(),
            "domain_presets": {},
            "unrecognized_settings": {
                "top_level": {},
                "profiles": {},
                "app_settings": {},
            },
        }

    if not isinstance(settings_store.get("profiles"), dict):
        settings_store["profiles"] = {}

    if DEFAULT_PROFILE_NAME not in settings_store["profiles"]:
        settings_store["profiles"][DEFAULT_PROFILE_NAME] = get_settings_dict()

    settings_store = ensure_unrecognized_settings_store(settings_store)
    settings_store = ensure_app_settings_store(settings_store)
    settings_store = ensure_domain_presets_store(settings_store)
    settings_store["version"] = SETTINGS_SCHEMA_VERSION
    settings_store.setdefault("loaded_version", SETTINGS_SCHEMA_VERSION)

    return settings_store


def get_profile_names():
    store = ensure_settings_store()
    return sorted(store["profiles"].keys(), key=lambda name: (name != DEFAULT_PROFILE_NAME, name.lower()))


def rebuild_profile_menu():
    global profile_menu

    if profile_menu is None:
        return

    ensure_settings_store()

    profile_menu.delete(0, "end")

    profile_menu.add_command(label="Save Current Settings to Profile...", command=save_current_settings_to_profile)
    profile_menu.add_command(label="Delete Selected Profile...", command=delete_selected_profile)
    profile_menu.add_separator()

    profile_menu.add_command(label="Existing Profiles", state="disabled")

    for profile_name in get_profile_names():
        profile_menu.add_radiobutton(
            label=profile_name,
            variable=selected_profile_var,
            value=profile_name,
            command=lambda name=profile_name: load_profile(name, show_popup=True),
        )


def canonicalize_settings_for_compare(data):
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except Exception:
        return ""


def read_json_for_compare(path):
    if not path or not os.path.isfile(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def settings_payload_has_changed(path, new_payload):
    existing_payload = read_json_for_compare(path)

    if existing_payload is None:
        return True

    return canonicalize_settings_for_compare(existing_payload) != canonicalize_settings_for_compare(new_payload)


def save_settings(show_popup=True, path=None):
    global settings_store

    try:
        settings_path = path or SETTINGS_FILE

        store = ensure_settings_store()

        # Persistent/autosave behavior always writes the current GUI state to
        # the Default profile. Custom profiles are only changed through the
        # Profile menu's explicit save command.
        store["profiles"][DEFAULT_PROFILE_NAME] = get_settings_dict()
        store["app_settings"] = get_app_settings_dict()
        store["version"] = SETTINGS_SCHEMA_VERSION

        changed = settings_payload_has_changed(settings_path, store)

        if not changed:
            if show_popup:
                messagebox.showinfo("Settings unchanged", f"No settings changes detected.\n\n{settings_path}")
            return True

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)

        append_log(f"\nSettings saved to: {settings_path}\n")

        if show_popup:
            messagebox.showinfo("Settings saved", f"Settings saved to:\n\n{settings_path}")

        rebuild_profile_menu()
        return True

    except Exception as e:
        messagebox.showerror("Save failed", f"Could not save settings:\n\n{e}")
        return False


def save_settings_dialog():
    path = filedialog.asksaveasfilename(
        title="Save settings file",
        defaultextension=".json",
        initialfile="gui-settings.json",
        initialdir=ROOT,
        filetypes=[
            ("JSON settings files", "*.json"),
            ("All files", "*.*"),
        ],
    )

    if not path:
        return

    save_settings(show_popup=True, path=path)


def load_settings(show_popup=True, startup=False, path=None):
    global settings_store

    settings_path = path or SETTINGS_FILE

    if not os.path.isfile(settings_path):
        settings_store = {
            "version": SETTINGS_SCHEMA_VERSION,
            "loaded_version": SETTINGS_SCHEMA_VERSION,
            "profiles": {
                DEFAULT_PROFILE_NAME: make_default_profile_settings(),
            },
            "app_settings": APP_SETTINGS_DEFAULTS.copy(),
            "domain_presets": {},
            "unrecognized_settings": {
                "top_level": {},
                "profiles": {},
                "app_settings": {},
            },
        }
        apply_app_settings_dict(settings_store["app_settings"])
        append_log(f"Settings file not found. Using defaults.\nExpected path: {settings_path}\n")
        log_app_settings_status()
        log_domain_presets_status("Loaded domain presets")
        rebuild_profile_menu()
        return False

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        settings_store = normalize_settings_store(raw)
        apply_app_settings_dict(settings_store.get("app_settings", {}))

        # The default profile is always the profile loaded at app startup and
        # when a settings file is loaded.
        apply_settings_dict(settings_store["profiles"][DEFAULT_PROFILE_NAME])
        selected_profile_var.set(DEFAULT_PROFILE_NAME)
        preflight_done_var.set(False)
        update_window_title()

        append_log(f"Settings loaded from: {settings_path}\n")
        loaded_version = settings_store.get("loaded_version", 1)
        append_log(f"Settings file version loaded: {loaded_version}; current schema version: {SETTINGS_SCHEMA_VERSION}\n")
        if loaded_version < SETTINGS_SCHEMA_VERSION:
            append_log("Older settings file detected. Recognized values were imported, newer recognized values were created with defaults, and unrecognized values were preserved under unrecognized_settings.\n")
        elif loaded_version > SETTINGS_SCHEMA_VERSION:
            append_log("Newer settings file detected. Recognized values were imported where possible and unrecognized values were preserved under unrecognized_settings.\n")
        append_log(f"Loaded {len(settings_store['profiles'])} profile(s). Active profile: {DEFAULT_PROFILE_NAME}\n")
        log_app_settings_status("Loaded app settings")
        log_domain_presets_status("Loaded domain presets")

        if show_popup and not startup:
            messagebox.showinfo(
                "Settings loaded",
                f"Settings loaded from:\n\n{settings_path}\n\n"
                f"Loaded {len(settings_store['profiles'])} profile(s). The Default profile was applied.",
            )

        rebuild_profile_menu()
        return True

    except Exception as e:
        settings_store = {
            "version": SETTINGS_SCHEMA_VERSION,
            "loaded_version": SETTINGS_SCHEMA_VERSION,
            "profiles": {
                DEFAULT_PROFILE_NAME: make_default_profile_settings(),
            },
            "app_settings": APP_SETTINGS_DEFAULTS.copy(),
            "domain_presets": {},
            "unrecognized_settings": {
                "top_level": {},
                "profiles": {},
                "app_settings": {},
            },
        }
        apply_app_settings_dict(settings_store["app_settings"])
        append_log(f"Settings file was found but could not be loaded. Using defaults.\nError: {e}\n")
        log_app_settings_status()

        if show_popup and not startup:
            messagebox.showerror("Load failed", f"Could not load settings:\n\n{e}")

        rebuild_profile_menu()
        return False


def load_settings_dialog():
    path = filedialog.askopenfilename(
        title="Load settings file",
        initialdir=ROOT,
        filetypes=[
            ("JSON settings files", "*.json"),
            ("All files", "*.*"),
        ],
    )

    if not path:
        return

    load_settings(show_popup=True, startup=False, path=path)


def load_profile(profile_name, show_popup=True):
    store = ensure_settings_store()

    if profile_name not in store["profiles"]:
        messagebox.showerror("Profile not found", f"The profile does not exist:\n\n{profile_name}")
        rebuild_profile_menu()
        return False

    apply_settings_dict(store["profiles"][profile_name])
    selected_profile_var.set(profile_name)
    preflight_done_var.set(False)
    update_window_title()

    append_log(f"\nProfile loaded: {profile_name}\n")

    if show_popup:
        messagebox.showinfo("Profile loaded", f"Profile loaded:\n\n{profile_name}")

    return True


def save_current_settings_to_profile():
    store = ensure_settings_store()

    profile_name = simpledialog.askstring(
        "Save Profile",
        "Enter a profile name to save the current settings:",
        parent=root,
    )

    if profile_name is None:
        return

    profile_name = profile_name.strip()

    if not profile_name:
        messagebox.showwarning("Invalid profile name", "Profile name cannot be blank.")
        return

    if profile_name in store["profiles"]:
        confirm = messagebox.askyesno(
            "Overwrite profile?",
            f"The profile already exists:\n\n{profile_name}\n\nOverwrite it?",
        )
        if not confirm:
            return

    store["profiles"][profile_name] = get_settings_dict()
    store["app_settings"] = get_app_settings_dict()
    store["version"] = SETTINGS_SCHEMA_VERSION
    selected_profile_var.set(profile_name)
    update_window_title()

    # Saving a custom profile must not refresh or overwrite the Default profile.
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)

        append_log(f"\nProfile saved: {profile_name}\n")
        append_log(f"Settings saved to: {SETTINGS_FILE}\n")
        messagebox.showinfo("Profile saved", f"Profile saved:\n\n{profile_name}")
        rebuild_profile_menu()
    except Exception as e:
        messagebox.showerror("Save failed", f"Could not save profile:\n\n{e}")


def delete_selected_profile():
    store = ensure_settings_store()
    profile_name = selected_profile_var.get().strip() or DEFAULT_PROFILE_NAME

    if profile_name == DEFAULT_PROFILE_NAME:
        messagebox.showwarning("Cannot delete Default", "The Default profile cannot be deleted.")
        return

    if profile_name not in store["profiles"]:
        messagebox.showerror("Profile not found", f"The selected profile does not exist:\n\n{profile_name}")
        rebuild_profile_menu()
        return

    confirm = messagebox.askyesno(
        "Delete profile?",
        f"Delete this profile from the current settings file?\n\n{profile_name}\n\n"
        "This does not delete case files, cookies, media, or logs.",
    )

    if not confirm:
        return

    del store["profiles"][profile_name]
    selected_profile_var.set(DEFAULT_PROFILE_NAME)
    apply_settings_dict(store["profiles"][DEFAULT_PROFILE_NAME])
    preflight_done_var.set(False)
    update_window_title()

    save_settings(show_popup=False)

    append_log(f"\nProfile deleted: {profile_name}\n")
    messagebox.showinfo("Profile deleted", f"Profile deleted:\n\n{profile_name}")
    rebuild_profile_menu()


def delete_settings_file():
    confirm = messagebox.askyesno(
        "Delete settings file?",
        "This will delete the portable settings file:\n\n"
        f"{SETTINGS_FILE}\n\n"
        "All saved profiles in that settings file will be deleted. "
        "The current GUI settings will be reset to defaults.\n\n"
        "Continue?",
    )

    if not confirm:
        return

    try:
        if os.path.isfile(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)
            append_log(f"\nDeleted settings file: {SETTINGS_FILE}\n")
        else:
            append_log(f"\nSettings file was already missing: {SETTINGS_FILE}\n")

        global settings_store
        settings_store = {
            "version": SETTINGS_SCHEMA_VERSION,
            "loaded_version": SETTINGS_SCHEMA_VERSION,
            "profiles": {
                DEFAULT_PROFILE_NAME: make_default_profile_settings(),
            },
            "app_settings": APP_SETTINGS_DEFAULTS.copy(),
            "domain_presets": {},
            "unrecognized_settings": {
                "top_level": {},
                "profiles": {},
                "app_settings": {},
            },
        }

        apply_settings_dict(make_default_profile_settings())
        apply_app_settings_dict(APP_SETTINGS_DEFAULTS.copy())
        urls_text.delete("1.0", "end")
        target_status_var.set("Impersonate targets: Not checked")
        preflight_done_var.set(False)
        selected_profile_var.set(DEFAULT_PROFILE_NAME)
        update_window_title()
        update_case_folder_preview()
        rebuild_profile_menu()

        append_log("Current settings were reset to defaults. Saved custom profiles were removed with the deleted settings file.\n")
        messagebox.showinfo(
            "Settings deleted",
            "The settings file was deleted and the current GUI settings were reset to defaults.",
        )
    except Exception as e:
        messagebox.showerror("Delete failed", f"Could not delete the settings file:\n\n{e}")


def reset_defaults():
    store = ensure_settings_store()

    # Preserve every custom profile. Only reset the GUI fields and the Default
    # profile.
    apply_settings_dict(make_default_profile_settings())
    urls_text.delete("1.0", "end")
    target_status_var.set("Impersonate targets: Not checked")
    preflight_done_var.set(False)
    selected_profile_var.set(DEFAULT_PROFILE_NAME)
    update_window_title()

    apply_app_settings_dict(APP_SETTINGS_DEFAULTS.copy())
    store["profiles"][DEFAULT_PROFILE_NAME] = get_settings_dict()
    store["app_settings"] = get_app_settings_dict()
    save_settings(show_popup=False)

    append_log("\nReset GUI fields to defaults and overwrote only the Default profile. Custom profiles were preserved.\n")
    messagebox.showinfo("Defaults restored", "Defaults restored. Custom profiles were preserved.")


def start_capture():
    global running_process

    effective_concurrency_limit = get_concurrent_capture_limit()

    try:
        preset_decision_urls = get_current_url_lines_for_queue()
        preset_decision_settings, preset_decision_applied = apply_checked_domain_presets_to_settings(
            get_settings_dict(),
            preset_decision_urls,
        )
        effective_concurrency_limit = get_concurrent_capture_limit(preset_decision_settings)
    except Exception:
        preset_decision_applied = []

    queue_has_active_or_pending_jobs = False
    try:
        queue_has_active_or_pending_jobs = (
            job_queue_running
            or bool(get_pending_queue_jobs())
            or bool(get_running_queue_jobs())
        )
    except Exception:
        queue_has_active_or_pending_jobs = bool(job_queue_running)

    if queue_has_active_or_pending_jobs:
        if not job_queue_window_is_open():
            open_job_queue()

        added = add_current_as_job()
        if added:
            append_log("\nStart Capture added the current capture to the existing queue.\n")
            if job_queue_running:
                run_next_queue_job()
            else:
                start_job_queue()
        return

    if effective_concurrency_limit >= 2:
        if not job_queue_window_is_open():
            open_job_queue()
        added = add_current_as_job()
        if added:
            start_job_queue()
        return

    if running_process is not None and running_process.poll() is None:
        messagebox.showwarning("Already running", "A capture process is already running.")
        return

    try:
        validate_inputs()
        capture_urls = get_current_url_lines_for_queue()
        if not capture_urls:
            raise ValueError(describe_current_url_source_problem("starting capture"))

        capture_timestamp = datetime.now()
        pending_playlist_name = consume_url_preview_pending_playlist_name()
        command_settings = get_settings_dict()
        command_settings, applied_domain_presets = apply_checked_domain_presets_to_settings(command_settings, capture_urls)
        capture_domains = sorted({domain for domain in (get_url_domain_key(url) for url in capture_urls) if domain})
        capture_case_template = command_settings.get("case_name", case_name_var.get().strip())
        if str(pending_playlist_name or "").strip():
            capture_case_template = append_playlist_tag_to_case_template(capture_case_template)
        resolved_case_name = safe_case_name(render_case_name_template(
            capture_case_template,
            now=capture_timestamp,
            domains=capture_domains,
            presets=applied_domain_presets,
            playlist=pending_playlist_name,
        ))

        if not resolved_case_name:
            raise ValueError("Case Name is blank after resolving the template.")

        cmd = build_powershell_command_for_job({
            "settings": command_settings,
            "urls": capture_urls,
            "resolved_case_name": resolved_case_name,
        })

        case_folder_for_collision = get_expected_run_paths_for_values(
            command_settings.get("output_root", output_root_var.get().strip()),
            resolved_case_name,
        )["case_folder"]
        if not confirm_case_folder_collision(case_folder_for_collision):
            return
        save_settings(show_popup=False)
    except Exception as e:
        messagebox.showerror("Input error", str(e))
        return

    if check_vpn_var.get() and last_vpn_status != "connected":
        proceed = messagebox.askyesno(
            "VPN not connected",
            "The VPN does not appear to be connected.\n\n"
            "Continue anyway?",
        )
        if not proceed:
            return

    copy_summary_button.config(state="disabled")
    log_box.delete("1.0", "end")
    append_log("Starting capture...\n\n")
    append_log(f"Settings saved to: {SETTINGS_FILE}\n")
    if resolved_case_name != case_name_var.get().strip():
        append_log(f"Resolved case name template: {case_name_var.get().strip()} -> {resolved_case_name}\n")
    if applied_domain_presets:
        append_log(f"Applied active domain preset(s): {', '.join(applied_domain_presets)}\n")
    else:
        loaded_presets, active_presets = get_domain_preset_status()
        if loaded_presets:
            append_log("Applied active domain preset(s): none matched this URL set.\n")
            append_log(f"Active domain preset(s): {', '.join(active_presets) if active_presets else 'none'}\n")
    append_log("\n")

    tool_versions = query_capture_tool_versions_for_log()
    log_capture_tool_versions(tool_versions)

    global last_capture_context
    last_capture_context = {
        "tool_versions": tool_versions,
        "submitted_url_count": len(capture_urls),
        "settings": command_settings,
        "paths": get_expected_run_paths_for_values(
            command_settings.get("output_root", output_root_var.get().strip()),
            resolved_case_name,
        ),
    }

    append_log("Command:\n")
    append_log(format_command_for_log(cmd))
    append_log("\n\n")

    start_button.config(state="disabled")
    start_menu_button.config(state="disabled")
    stop_button.config(state="normal")
    set_status("Running...")

    submitted_url_count = len(capture_urls)

    def worker():
        global running_process

        try:
            running_process = subprocess.Popen(
                cmd,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            universal_skip_records = []
            universal_skip_summary = {}

            if running_process.stdout:
                for line in running_process.stdout:
                    skip_record = parse_universal_archive_skip_output_line(line)
                    if skip_record:
                        universal_skip_records.append(skip_record)
                        root.after(0, append_log, format_universal_archive_skip_record_for_log(skip_record) + "\n")
                        continue

                    skip_summary = parse_universal_archive_skip_summary_line(line)
                    if skip_summary:
                        universal_skip_summary = skip_summary
                        continue

                    root.after(0, append_log, line)

            exit_code = running_process.wait()

            root.after(0, show_run_summary, exit_code, submitted_url_count, universal_skip_records, universal_skip_summary)

            if exit_code == 0:
                root.after(0, set_status, "Done")
                root.after(0, append_log, f"\nProcess completed successfully. Exit code: {exit_code}\n")
            else:
                root.after(0, set_status, f"Finished with exit code {exit_code}")
                root.after(0, append_log, f"\nProcess finished with exit code: {exit_code}\n")

        except Exception as e:
            root.after(0, set_status, "Error")
            root.after(0, append_log, f"\nERROR: {e}\n")

        finally:
            root.after(0, lambda: start_button.config(state="normal"))
            root.after(0, lambda: start_menu_button.config(state="normal"))
            root.after(0, lambda: stop_button.config(state="disabled"))

    threading.Thread(target=worker, daemon=True).start()


def show_run_summary(exit_code, submitted_url_count, universal_skip_records=None, universal_skip_summary=None):
    global last_successful_case_summary

    try:
        paths = last_capture_context.get("paths") or get_expected_run_paths()
    except Exception:
        paths = {}

    append_log("\n========== Run Summary ==========\n")
    append_log(f"Exit code: {exit_code}\n")
    append_log(f"Submitted URLs: {submitted_url_count}\n")

    counts = {}

    if paths:
        append_log(f"Case folder: {paths['case_folder']}\n")
        append_log(f"Media folder: {paths['media_folder']}\n")
        append_log(f"Logs folder: {paths['logs_folder']}\n")
        append_log(f"Manifests folder: {paths['manifests_folder']}\n")
        append_log(f"Download archive: {paths['download_archive']}\n")
        append_universal_archive_skip_summary(universal_skip_records, universal_skip_summary)

        counts = count_case_files(paths["case_folder"])
        append_log(f"Total files found: {counts.get('files', 0)}\n")
        append_log(f"Media files found: {counts.get('media', 0)}\n")
        append_log(f"Metadata JSON files found: {counts.get('metadata', 0)}\n")
        append_log(f"Manifest files found: {counts.get('manifests', 0)}\n")
        append_log(f"Run log files found: {counts.get('logs', 0)}\n")

    append_log("=================================\n")

    if exit_code == 0 and paths:
        versions = last_capture_context.get("tool_versions", {})
        summary_settings = last_capture_context.get("settings", {})
        last_successful_case_summary = build_case_summary_text(
            exit_code,
            submitted_url_count,
            paths,
            versions,
            counts,
            settings=summary_settings,
            universal_skip_records=universal_skip_records,
            universal_skip_summary=universal_skip_summary,
        )
        copy_summary_button.config(state="normal")
        append_log("Case summary is available. Use Copy Case Summary to copy it to the clipboard.\n")
    else:
        last_successful_case_summary = ""
        copy_summary_button.config(state="disabled")



def get_concurrent_capture_limit(settings=None):
    try:
        if isinstance(settings, dict):
            value = settings.get("concurrent_captures", DEFAULTS["concurrent_captures"])
        else:
            value = concurrent_captures_var.get()
        return max(1, min(4, int(str(value).strip())))
    except Exception:
        return 1


def get_concurrent_fragment_limit(settings=None):
    try:
        if isinstance(settings, dict):
            value = settings.get("concurrent_fragments", DEFAULTS["concurrent_fragments"])
        else:
            value = concurrent_fragments_var.get()
        value = int(str(value).strip())
        if value not in {1, 2, 4, 8}:
            return 1
        return value
    except Exception:
        return 1


def get_url_domain_key(url):
    value = str(url or "").strip()
    if not value:
        return ""

    parse_value = value if "://" in value else f"https://{value}"

    try:
        host = urlsplit(parse_value).hostname or ""
    except Exception:
        host = ""

    host = host.lower().strip(".")
    if host.startswith("www."):
        host = host[4:]

    if not host:
        return ""

    parts = host.split(".")
    if len(parts) <= 2:
        return host

    common_second_level = {"co", "com", "org", "net", "ac", "gov", "edu"}
    if len(parts[-1]) == 2 and parts[-2] in common_second_level and len(parts) >= 3:
        return ".".join(parts[-3:])

    return ".".join(parts[-2:])


def get_job_domain_keys(job):
    return sorted({
        domain
        for domain in (get_url_domain_key(url) for url in job.get("urls", []))
        if domain
    })


def find_domain_collisions_for_job(candidate_job, statuses=("pending", "running")):
    candidate_domains = set(get_job_domain_keys(candidate_job))
    collisions = []

    if not candidate_domains:
        return collisions

    for existing in job_queue:
        if existing is candidate_job:
            continue
        if existing.get("status") not in statuses:
            continue

        existing_domains = set(existing.get("domains") or get_job_domain_keys(existing))
        overlap = sorted(candidate_domains & existing_domains)

        if overlap:
            collisions.append({
                "candidate": candidate_job,
                "existing": existing,
                "domains": overlap,
            })

    return collisions


def find_pending_pair_domain_collisions():
    pending = [
        job
        for job in job_queue
        if job.get("status") == "pending" and queue_job_is_in_run_filter(job)
    ]
    collisions = []

    for index, left in enumerate(pending):
        left_domains = set(left.get("domains") or get_job_domain_keys(left))
        if not left_domains:
            continue

        for right in pending[index + 1:]:
            right_domains = set(right.get("domains") or get_job_domain_keys(right))
            overlap = sorted(left_domains & right_domains)

            if overlap:
                collisions.append({
                    "candidate": right,
                    "existing": left,
                    "domains": overlap,
                })

    return collisions


def summarize_domain_collisions(collisions, max_lines=10):
    lines = []

    for item in collisions[:max_lines]:
        candidate = item.get("candidate", {})
        existing = item.get("existing", {})
        domains = ", ".join(item.get("domains", []))
        lines.append(
            f"- {candidate.get('resolved_case_name', 'new job')} conflicts with "
            f"{existing.get('resolved_case_name', 'existing job')} on: {domains}"
        )

    if len(collisions) > max_lines:
        lines.append(f"- ...and {len(collisions) - max_lines} more collision(s).")

    return "\n".join(lines) if lines else "- No collision details available."


def show_domain_collision_dialog(collisions):
    result = {"choice": "cancel"}

    dialog = tk.Toplevel(root)
    dialog.title("Concurrent Domain Collision")
    dialog.geometry("720x420")
    dialog.minsize(620, 340)
    dialog.grab_set()
    dialog.transient(root)

    ttk.Label(
        dialog,
        text=(
            "One or more queued/running jobs use the same URL domain while concurrent captures are enabled.\n\n"
            "Running matching domains at the same time may increase rate-limit or temporary-block risk."
        ),
        wraplength=680,
        justify="left",
    ).pack(fill="x", padx=12, pady=(12, 8))

    text_box = scrolledtext.ScrolledText(dialog, height=10, wrap="word")
    text_box.pack(fill="both", expand=True, padx=12, pady=(0, 8))
    text_box.insert("1.0", summarize_domain_collisions(collisions))
    text_box.configure(state="disabled")

    ttk.Label(
        dialog,
        text=(
            "Continue allows same-domain concurrent jobs. "
            "Queue After Collisions keeps the new/current jobs pending until colliding running jobs finish. "
            "Cancel stops this start/add action."
        ),
        wraplength=680,
        justify="left",
    ).pack(fill="x", padx=12, pady=(0, 8))

    button_frame = ttk.Frame(dialog)
    button_frame.pack(fill="x", padx=12, pady=(0, 12))

    def choose(value):
        result["choice"] = value
        dialog.destroy()

    ttk.Button(button_frame, text="Continue", command=lambda: choose("continue")).pack(side="left", padx=(0, 8))
    ttk.Button(button_frame, text="Queue After Collisions", command=lambda: choose("wait")).pack(side="left", padx=(0, 8))
    ttk.Button(button_frame, text="Cancel", command=lambda: choose("cancel")).pack(side="right")

    dialog.protocol("WM_DELETE_WINDOW", lambda: choose("cancel"))
    dialog.wait_window()
    return result["choice"]


def mark_job_domain_policy(job, choice):
    if choice == "continue":
        job["allow_domain_collision"] = True
    else:
        job["allow_domain_collision"] = False

def get_current_url_lines_for_queue():
    return get_current_url_list_for_tools(use_all_cache=True)


def make_job_id():
    return datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(2)


def get_job_case_folder(job):
    settings = job.get("settings", {})
    output_root = settings.get("output_root", "")
    resolved_case_name = job.get("resolved_case_name") or settings.get("case_name", "")
    return os.path.join(output_root, resolved_case_name) if output_root and resolved_case_name else ""



def job_persistence_is_enabled():
    try:
        return bool(job_persistence_var.get())
    except Exception:
        return bool(APP_SETTINGS_DEFAULTS.get("job_persistence", True))


def serialize_queue_job(job):
    allowed_keys = [
        "job_id",
        "settings_schema_version",
        "status",
        "case_template",
        "resolved_case_name",
        "urls",
        "settings",
        "output_root",
        "created",
        "started",
        "finished",
        "exit_code",
        "completed_urls",
        "summary",
        "applied_domain_presets",
        "playlist_name",
        "domains",
        "allow_domain_collision",
        "checked",
        "paths",
        "tool_versions",
        "interrupted_reason",
        "interrupted_at",
    ]

    serialized = {key: job.get(key) for key in allowed_keys if key in job}
    serialized["settings_schema_version"] = int(job.get("settings_schema_version", SETTINGS_SCHEMA_VERSION) or SETTINGS_SCHEMA_VERSION)
    return serialized


def normalize_loaded_queue_job(raw_job):
    if not isinstance(raw_job, dict):
        return None

    urls = raw_job.get("urls", [])
    if not isinstance(urls, list):
        urls = []

    clean_urls = []
    for url in urls:
        cleaned = clean_extracted_url(str(url or ""))
        if cleaned:
            clean_urls.append(cleaned)

    if not clean_urls:
        return None

    settings = raw_job.get("settings", {})
    if not isinstance(settings, dict):
        settings = {}

    settings = merge_profile_settings_with_defaults(settings)

    raw_status = str(raw_job.get("status") or "pending").lower()
    status = "interrupted" if raw_status == "running" else raw_status
    if status not in {"pending", "completed", "failed", "cancelled", "interrupted"}:
        status = "pending"

    try:
        completed_urls = int(raw_job.get("completed_urls", 0) or 0)
    except Exception:
        completed_urls = 0
    completed_urls = max(0, min(completed_urls, len(clean_urls)))

    try:
        settings_schema_version = int(raw_job.get("settings_schema_version", SETTINGS_SCHEMA_VERSION))
    except Exception:
        settings_schema_version = 0

    job = {
        "job_id": str(raw_job.get("job_id") or make_job_id()),
        "settings_schema_version": settings_schema_version,
        "status": status,
        "case_template": str(raw_job.get("case_template", settings.get("case_name", "")) or ""),
        "resolved_case_name": str(raw_job.get("resolved_case_name", "") or ""),
        "urls": clean_urls,
        "settings": settings,
        "output_root": str(raw_job.get("output_root", settings.get("output_root", "")) or ""),
        "created": str(raw_job.get("created", "") or ""),
        "started": str(raw_job.get("started", "") or ""),
        "finished": str(raw_job.get("finished", "") or ""),
        "exit_code": str(raw_job.get("exit_code", "") or ""),
        "completed_urls": completed_urls,
        "summary": str(raw_job.get("summary", "") or ""),
        "applied_domain_presets": list(raw_job.get("applied_domain_presets", []) or []),
        "playlist_name": str(raw_job.get("playlist_name", "") or ""),
        "domains": list(raw_job.get("domains", []) or []),
        "allow_domain_collision": bool(raw_job.get("allow_domain_collision", False)),
        "checked": bool(raw_job.get("checked", False)),
        "paths": raw_job.get("paths", {}) if isinstance(raw_job.get("paths", {}), dict) else {},
        "tool_versions": raw_job.get("tool_versions", {}) if isinstance(raw_job.get("tool_versions", {}), dict) else {},
        "interrupted_reason": str(raw_job.get("interrupted_reason", "") or ""),
        "interrupted_at": str(raw_job.get("interrupted_at", "") or ""),
    }

    if raw_status == "running":
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job["finished"] = now_text
        job["exit_code"] = "interrupted"
        job["interrupted_at"] = now_text
        job["interrupted_reason"] = "App was closed while this job was marked running."

    if not job["domains"]:
        job["domains"] = get_job_domain_keys(job)

    return job


def describe_job_schema_source(raw_job):
    if not isinstance(raw_job, dict):
        return "unknown job"

    label = str(raw_job.get("resolved_case_name") or raw_job.get("case_template") or raw_job.get("job_id") or "unknown job")
    return label[:120]


def classify_loaded_job_settings_schema(raw_job):
    if not isinstance(raw_job, dict):
        return "missing", None

    if "settings_schema_version" not in raw_job:
        return "missing", None

    try:
        value = int(raw_job.get("settings_schema_version"))
    except Exception:
        return "invalid", raw_job.get("settings_schema_version")

    if value == SETTINGS_SCHEMA_VERSION:
        return "current", value

    if value < SETTINGS_SCHEMA_VERSION:
        return "old", value

    return "newer", value


def append_loaded_job_schema_warning(warnings):
    if not warnings or not any(warnings.get(kind) for kind in ("missing", "invalid", "old", "newer")):
        return

    append_log(
        "\nWARNING: Some persisted queue jobs were loaded with missing or mismatching settings schemas.\n"
    )
    append_log(
        f"Current settings schema: {SETTINGS_SCHEMA_VERSION}. Job settings were merged with current defaults where possible.\n"
    )

    labels = {
        "missing": "Missing settings schema",
        "invalid": "Invalid settings schema",
        "old": "Older settings schema",
        "newer": "Newer settings schema",
    }

    for kind in ("missing", "invalid", "old", "newer"):
        items = warnings.get(kind, [])
        if not items:
            continue

        append_log(f"  {labels[kind]}: {len(items)} job(s)\n")

        for label, value in items[:8]:
            if value is None:
                append_log(f"    - {label}\n")
            else:
                append_log(f"    - {label} (job schema {value})\n")

        if len(items) > 8:
            append_log(f"    ... {len(items) - 8} more\n")


def save_job_queue_state():
    if job_queue_state_loading or not job_persistence_is_enabled():
        return False

    try:
        payload = {
            "type": "yt-dlp-gui-job-queue",
            "version": JOBS_FILE_VERSION,
            "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "jobs": [serialize_queue_job(job) for job in job_queue],
        }

        with open(JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return True
    except Exception as e:
        try:
            append_log(f"\nWARNING: Could not save job queue state: {e}\n")
        except Exception:
            pass
        return False


def load_job_queue_state(startup=False):
    global job_queue, job_queue_state_loading

    if not job_persistence_is_enabled():
        if startup:
            append_log("\nJob persistence is disabled. Queue state was not loaded.\n")
        return False

    if not os.path.isfile(JOBS_FILE):
        if startup:
            append_log("\nNo persisted job queue found.\n")
        return False

    try:
        job_queue_state_loading = True

        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)

        raw_jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
        loaded_jobs = []
        interrupted_count = 0
        schema_warnings = {
            "missing": [],
            "invalid": [],
            "old": [],
            "newer": [],
        }

        for raw_job in raw_jobs:
            job = normalize_loaded_queue_job(raw_job)
            if not job:
                continue

            schema_kind, schema_value = classify_loaded_job_settings_schema(raw_job)
            if schema_kind in schema_warnings:
                schema_warnings[schema_kind].append((describe_job_schema_source(raw_job), schema_value))

            if str(raw_job.get("status", "")).lower() == "running":
                interrupted_count += 1
            loaded_jobs.append(job)

        job_queue = loaded_jobs
        refresh_job_queue_window()

        if startup:
            append_log(f"\nLoaded {len(job_queue)} persisted queue job(s) from: {JOBS_FILE}\n")
            if interrupted_count:
                append_log(f"Marked {interrupted_count} previously running job(s) as interrupted.\n")

        append_loaded_job_schema_warning(schema_warnings)

        return True
    except Exception as e:
        try:
            append_log(f"\nWARNING: Could not load persisted job queue: {e}\n")
        except Exception:
            pass
        return False
    finally:
        job_queue_state_loading = False


def mark_running_queue_jobs_interrupted(reason="Interrupted"):
    changed = False
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for job in job_queue:
        if job.get("status") == "running":
            job["status"] = "interrupted"
            job["finished"] = now_text
            job["exit_code"] = "interrupted"
            job["interrupted_at"] = now_text
            job["interrupted_reason"] = reason
            job["_interruption_requested"] = True
            changed = True

    if changed:
        refresh_job_queue_window()
        save_job_queue_state()

    return changed


def job_queue_window_is_open():
    try:
        return job_queue_window is not None and job_queue_window.winfo_exists()
    except Exception:
        return False


def job_queue_tree_is_available():
    try:
        return (
            job_queue_tree is not None
            and job_queue_window_is_open()
            and job_queue_tree.winfo_exists()
        )
    except Exception:
        return False


def get_queue_job_by_id(job_id):
    for job in job_queue:
        if job.get("job_id") == job_id:
            return job

    return None


def queue_run_filter_is_active():
    return isinstance(job_queue_run_filter_ids, set)


def queue_job_is_in_run_filter(job):
    if not queue_run_filter_is_active():
        return True

    return job.get("job_id") in job_queue_run_filter_ids


def get_checked_runnable_queue_jobs():
    return [
        job
        for job in job_queue
        if job.get("status") in {"pending", "interrupted"} and bool(job.get("checked", False))
    ]


def update_job_queue_selection_marks():
    if not job_queue_tree_is_available():
        return

    try:
        for item_id in job_queue_tree.get_children(""):
            job = get_queue_job_by_id(item_id)
            job_queue_tree.set(item_id, "selected", "☑" if job and bool(job.get("checked", False)) else "☐")
    except Exception:
        pass


def toggle_queue_job_checkmark(job_id):
    job = get_queue_job_by_id(job_id)
    if not job:
        return

    job["checked"] = not bool(job.get("checked", False))
    save_job_queue_state()

    if job_queue_tree_is_available() and job_queue_tree.exists(job_id):
        try:
            job_queue_tree.set(job_id, "selected", "☑" if job["checked"] else "☐")
        except Exception:
            pass


def refresh_job_queue_window():
    if not job_queue_tree_is_available():
        update_job_queue_progress()
        save_job_queue_state()
        return

    try:
        selected = job_queue_tree.selection()
        selected_id = selected[0] if selected else ""
    except Exception:
        selected_id = ""

    for item in job_queue_tree.get_children(""):
        job_queue_tree.delete(item)

    for index, job in enumerate(job_queue, start=1):
        job_queue_tree.insert(
            "",
            "end",
            iid=job["job_id"],
            values=(
                "☑" if bool(job.get("checked", False)) else "☐",
                index,
                job.get("status", "pending"),
                job.get("resolved_case_name", ""),
                len(job.get("urls", [])),
                ", ".join(job.get("domains", []) or get_job_domain_keys(job)),
                ", ".join(job.get("applied_domain_presets", []) or []),
                job.get("output_root", ""),
                job.get("started", ""),
                job.get("finished", ""),
                job.get("exit_code", ""),
            ),
        )

    if selected_id and job_queue_tree.exists(selected_id):
        job_queue_tree.selection_set(selected_id)
    else:
        try:
            job_queue_tree.selection_remove(job_queue_tree.selection())
            job_queue_tree.focus("")
        except Exception:
            pass

    update_job_queue_selection_marks()
    update_job_queue_progress()
    save_job_queue_state()


def update_job_queue_progress():
    progress_available = False
    try:
        progress_available = job_queue_progress_var is not None and job_queue_window_is_open()
    except Exception:
        progress_available = False

    total_urls = sum(len(job.get("urls", [])) for job in job_queue)
    completed_urls = sum(int(job.get("completed_urls", 0) or 0) for job in job_queue)

    if total_urls:
        value = (completed_urls / total_urls) * 100
        status_text = f"Queue: {completed_urls}/{total_urls} URL segment(s) complete"
    else:
        value = 0
        status_text = "Queue is empty."

    if progress_available:
        try:
            job_queue_progress_var.set(value)
        except Exception:
            pass

    if job_queue_status_var and job_queue_window_is_open() and not job_queue_running:
        try:
            job_queue_status_var.set(status_text)
        except Exception:
            pass


def add_urls_to_queue_as_job(urls, resolved_case_name=None, settings=None, case_template=None, playlist_name=None):
    try:
        clean_urls = []
        seen = set()
        for url in urls or []:
            url = clean_extracted_url(url)
            if not url:
                continue
            normalized = normalize_url_for_compare(url)
            if normalized in seen:
                continue
            seen.add(normalized)
            clean_urls.append(url)

        if not clean_urls:
            raise ValueError("No URLs are available to add to the queue.")

        settings = settings.copy() if isinstance(settings, dict) else get_settings_dict()
        settings, applied_presets = apply_checked_domain_presets_to_settings(settings, clean_urls)
        case_template = case_template if case_template is not None else settings.get("case_name", "")
        if str(playlist_name or "").strip():
            case_template = append_playlist_tag_to_case_template(case_template)
        job_domains_for_tags = sorted({domain for domain in (get_url_domain_key(url) for url in clean_urls) if domain})
        resolved_case_name = resolved_case_name or safe_case_name(render_case_name_template(
            case_template,
            now=datetime.now(),
            domains=job_domains_for_tags,
            presets=applied_presets,
            playlist=playlist_name,
        ))

        if not resolved_case_name:
            raise ValueError("Case Name is blank after resolving the template.")

        job = {
            "job_id": make_job_id(),
            "settings_schema_version": SETTINGS_SCHEMA_VERSION,
            "status": "pending",
            "case_template": case_template,
            "resolved_case_name": resolved_case_name,
            "urls": clean_urls,
            "settings": settings,
            "output_root": settings.get("output_root", ""),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "started": "",
            "finished": "",
            "exit_code": "",
            "completed_urls": 0,
            "summary": "",
            "applied_domain_presets": applied_presets,
            "playlist_name": str(playlist_name or ""),
            "checked": False,
        }
        job["domains"] = get_job_domain_keys(job)
        job["allow_domain_collision"] = False

        if get_concurrent_capture_limit() >= 2:
            collisions = find_domain_collisions_for_job(job)
            if collisions:
                choice = show_domain_collision_dialog(collisions)
                if choice == "cancel":
                    return False
                mark_job_domain_policy(job, choice)

        job_queue.append(job)
        refresh_job_queue_window()
        append_log(f"\nAdded queue job: {resolved_case_name} ({len(clean_urls)} URL(s))\n")
        if applied_presets:
            append_log(f"Applied active domain preset(s) to queue job: {', '.join(applied_presets)}\n")
        else:
            loaded_presets, active_presets = get_domain_preset_status()
            if loaded_presets:
                append_log("Applied active domain preset(s) to queue job: none matched this URL set.\n")
                append_log(f"Active domain preset(s): {', '.join(active_presets) if active_presets else 'none'}\n")
        return True
    except Exception as e:
        messagebox.showerror("Add job failed", str(e))
        return False


def describe_current_url_source_problem(action_label="this action"):
    input_paths = parse_input_file_paths()
    existing_paths = get_existing_input_file_paths(input_file_var.get())

    if existing_paths:
        return (
            f"No URLs are available for {action_label}.\n\n"
            "The URL box had no extractable http/https URLs, and the selected Input File entry or entries "
            "were readable but no extractable http/https URLs were found.\n\n"
            f"Input File(s):\n{describe_input_file_paths(existing_paths)}"
        )

    if input_paths:
        return (
            f"No URLs are available for {action_label}.\n\n"
            "The URL box had no extractable http/https URLs, and the selected Input File entry or entries "
            "are missing or invalid.\n\n"
            f"Input File(s):\n{describe_input_file_paths(input_paths)}"
        )

    return (
        f"No URLs are available for {action_label}.\n\n"
        "Add URLs to the URL box or select one or more Input File(s) containing http:// or https:// URLs."
    )


def add_current_as_job(playlist_name=None):
    try:
        validate_inputs()
        urls = get_current_url_lines_for_queue()
        if not urls:
            raise ValueError(describe_current_url_source_problem("adding the current capture to the queue"))
        effective_playlist_name = playlist_name if playlist_name is not None else consume_url_preview_pending_playlist_name()
        return add_urls_to_queue_as_job(urls, playlist_name=effective_playlist_name)
    except Exception as e:
        messagebox.showerror("Add job failed", str(e))
        return False


def add_current_job_and_open_queue():
    if not job_queue_window_is_open():
        open_job_queue()

    add_current_as_job()


def add_current_job_to_queue_and_start():
    if not job_queue_window_is_open():
        open_job_queue()

    added = add_current_as_job()
    if added:
        start_job_queue()


def add_jobs_to_queue_by_domain():
    try:
        validate_inputs()
        urls = get_current_url_lines_for_queue()
        if not urls:
            raise ValueError(describe_current_url_source_problem("adding jobs by domain"))

        settings = get_settings_dict()
        base_case_name = get_resolved_case_name(now=datetime.now())
        template_has_dynamic_domain_tags = any(tag in settings.get("case_name", "") for tag in ("%domains%", "%presets%"))
        groups = {}
        order = []

        for url in urls:
            domain = get_url_domain_key(url) or "unknown"
            if domain not in groups:
                groups[domain] = []
                order.append(domain)
            groups[domain].append(url)

        if not job_queue_window_is_open():
            open_job_queue()

        added_count = 0
        for domain in sorted(order):
            domain_suffix = safe_case_name(domain)
            resolved_name = None if template_has_dynamic_domain_tags else safe_case_name(f"{base_case_name}-{domain_suffix}")
            if add_urls_to_queue_as_job(
                groups[domain],
                resolved_case_name=resolved_name,
                settings=settings,
                case_template=settings.get("case_name", ""),
            ):
                added_count += 1

        append_log(f"\nAdded {added_count} domain-grouped job(s) to the queue.\n")
    except Exception as e:
        messagebox.showerror("Add jobs by domain failed", str(e))


def split_urls_by_count(urls, urls_per_group):
    urls_per_group = int(urls_per_group)

    if urls_per_group <= 0:
        raise ValueError("URLs per group must be greater than zero.")

    return [
        urls[index:index + urls_per_group]
        for index in range(0, len(urls), urls_per_group)
    ]


def split_urls_by_group_count(urls, group_count):
    group_count = int(group_count)

    if group_count <= 0:
        raise ValueError("Number of groups must be greater than zero.")

    group_count = min(group_count, len(urls))
    base_size = len(urls) // group_count
    remainder = len(urls) % group_count

    groups = []
    start_index = 0

    for index in range(group_count):
        size = base_size + (1 if index < remainder else 0)
        end_index = start_index + size
        groups.append(urls[start_index:end_index])
        start_index = end_index

    return [group for group in groups if group]


def normalize_split_queue_mode(value):
    value = str(value or "").strip().lower()
    if value in {"per_group", "group_count"}:
        return value
    return DEFAULTS["split_queue_mode"]


def normalize_positive_int_string(value, default_value):
    try:
        parsed = int(str(value or "").strip())
    except Exception:
        parsed = int(default_value)

    if parsed <= 0:
        parsed = int(default_value)

    return str(parsed)


def get_saved_split_queue_value_for_mode(mode):
    mode = normalize_split_queue_mode(mode)

    if mode == "group_count":
        return normalize_positive_int_string(split_queue_group_count_var.get(), DEFAULTS["split_queue_group_count"])

    return normalize_positive_int_string(split_queue_urls_per_group_var.get(), DEFAULTS["split_queue_urls_per_group"])


def show_split_queue_dialog(url_count):
    result = {"mode": "", "value": None}

    dialog = tk.Toplevel(root)
    dialog.title("Split and Add to Queue")
    dialog.geometry("460x270")
    dialog.minsize(420, 240)
    dialog.transient(root)
    dialog.grab_set()

    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)

    ttk.Label(
        frame,
        text=f"Split {url_count} URL(s) into multiple queue jobs.",
        wraplength=410,
        justify="left",
    ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    mode_var = tk.StringVar(value=normalize_split_queue_mode(split_queue_mode_var.get()))
    value_var = tk.StringVar(value=get_saved_split_queue_value_for_mode(mode_var.get()))

    def set_default_for_mode():
        value_var.set(get_saved_split_queue_value_for_mode(mode_var.get()))

    ttk.Radiobutton(
        frame,
        text="URLs per group",
        variable=mode_var,
        value="per_group",
        command=set_default_for_mode,
    ).grid(row=1, column=0, sticky="w", pady=3)

    ttk.Radiobutton(
        frame,
        text="Number of groups",
        variable=mode_var,
        value="group_count",
        command=set_default_for_mode,
    ).grid(row=2, column=0, sticky="w", pady=3)

    ttk.Label(frame, text="Value").grid(row=3, column=0, sticky="w", pady=(12, 3))
    value_entry = ttk.Entry(frame, textvariable=value_var, width=12)
    value_entry.grid(row=3, column=1, sticky="w", pady=(12, 3))
    value_entry.focus_set()
    value_entry.select_range(0, "end")

    ttk.Label(
        frame,
        text=(
            "URLs are kept in their current order. Each group is added as a separate pending queue job "
            "with a -partXX suffix on the resolved case name."
        ),
        wraplength=410,
        justify="left",
    ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=5, column=0, columnspan=2, sticky="e", pady=(16, 0))

    def accept():
        raw_value = value_var.get().strip()

        try:
            value = int(raw_value)
        except Exception:
            messagebox.showerror("Invalid split value", "Enter a whole number greater than zero.", parent=dialog)
            return

        if value <= 0:
            messagebox.showerror("Invalid split value", "Enter a whole number greater than zero.", parent=dialog)
            return

        if mode_var.get() == "per_group" and value > url_count:
            proceed = messagebox.askyesno(
                "Large group size",
                "The URLs-per-group value is larger than the number of URLs. This will create one queue job.\n\nContinue?",
                parent=dialog,
            )
            if not proceed:
                return

        if mode_var.get() == "group_count" and value > url_count:
            proceed = messagebox.askyesno(
                "More groups than URLs",
                "The requested group count is larger than the number of URLs. The app will create one job per URL.\n\nContinue?",
                parent=dialog,
            )
            if not proceed:
                return

        selected_mode = normalize_split_queue_mode(mode_var.get())

        split_queue_mode_var.set(selected_mode)
        if selected_mode == "per_group":
            split_queue_urls_per_group_var.set(str(value))
        else:
            split_queue_group_count_var.set(str(value))

        try:
            save_settings(show_popup=False)
        except Exception:
            pass

        result["mode"] = selected_mode
        result["value"] = value
        dialog.destroy()

    def cancel():
        result["mode"] = ""
        result["value"] = None
        dialog.destroy()

    ttk.Button(button_frame, text="Split and Add", command=accept).pack(side="left", padx=(0, 6))
    ttk.Button(button_frame, text="Cancel", command=cancel).pack(side="left")

    value_entry.bind("<Return>", lambda event: accept())
    dialog.bind("<Escape>", lambda event: cancel())
    dialog.protocol("WM_DELETE_WINDOW", cancel)

    try:
        configure_tk_widget_theme(dialog, get_theme_colors())
    except Exception:
        pass

    dialog.wait_window()
    return result["mode"], result["value"]


def split_and_add_to_queue():
    try:
        validate_inputs()
        urls = get_current_url_lines_for_queue()
        if not urls:
            raise ValueError(describe_current_url_source_problem("splitting and adding jobs to the queue"))

        mode, value = show_split_queue_dialog(len(urls))

        if not mode or not value:
            return False

        if mode == "per_group":
            groups = split_urls_by_count(urls, value)
            split_label = f"{value} URL(s) per group"
        else:
            groups = split_urls_by_group_count(urls, value)
            split_label = f"{value} requested group(s)"

        if not groups:
            messagebox.showinfo("No groups created", "No URL groups were created.")
            return False

        settings = get_settings_dict()
        base_time = datetime.now()
        base_case_name = get_resolved_case_name(now=base_time)

        if not job_queue_window_is_open():
            open_job_queue()

        added_count = 0

        for index, group_urls in enumerate(groups, start=1):
            resolved_name = safe_case_name(f"{base_case_name}-part{index:02d}")

            if add_urls_to_queue_as_job(
                group_urls,
                resolved_case_name=resolved_name,
                settings=settings,
                case_template=settings.get("case_name", ""),
            ):
                added_count += 1

        append_log(
            f"\nSplit {len(urls)} URL(s) into {added_count} queue job(s) using {split_label}.\n"
        )

        return added_count > 0
    except Exception as e:
        messagebox.showerror("Split and add to queue failed", str(e))
        return False


def get_failed_urls_for_current_context():
    base_urls = get_current_url_list_for_tools(use_all_cache=True)
    base_set = {normalize_url_for_compare(url) for url in base_urls}
    failed_records = get_failed_url_records()

    failed_urls = []
    seen = set()

    for record in failed_records:
        normalized = record.get("normalized", "")
        if base_set and normalized not in base_set:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        failed_urls.append(record["url"])

    return failed_urls


def add_failed_to_queue():
    try:
        failed_urls = get_failed_urls_for_current_context()
        if not failed_urls:
            messagebox.showinfo("No failed URLs", "No failed URLs were found for the current Output Root/current URL set.")
            return False

        if not job_queue_window_is_open():
            open_job_queue()

        return add_urls_to_queue_as_job(failed_urls)
    except Exception as e:
        messagebox.showerror("Add failed URLs failed", str(e))
        return False


def get_selected_queue_job():
    if not job_queue_tree_is_available():
        return None

    selection = job_queue_tree.selection()
    if not selection:
        return None

    job_id = selection[0]
    for job in job_queue:
        if job.get("job_id") == job_id:
            return job

    return None


def copy_text_to_clipboard(value, label="Text"):
    value = str(value or "")

    if not value:
        messagebox.showinfo("Nothing to copy", f"{label} is blank.")
        return False

    root.clipboard_clear()
    root.clipboard_append(value)
    append_log(f"\n{label} copied to clipboard.\n")
    return True


def format_queue_job_details(job):
    if not job:
        return ""

    settings = job.get("settings", {}) if isinstance(job.get("settings", {}), dict) else {}
    urls = job.get("urls", []) or []

    lines = [
        f"Case: {job.get('resolved_case_name', '')}",
        f"Status: {job.get('status', 'pending')}",
        f"URL count: {len(urls)}",
        f"Completed URLs: {job.get('completed_urls', 0)}",
        f"Domains: {', '.join(job.get('domains', []) or get_job_domain_keys(job))}",
        f"Output Root: {settings.get('output_root', job.get('output_root', ''))}",
        f"Started: {job.get('started', '')}",
        f"Finished: {job.get('finished', '')}",
        f"Exit Code: {job.get('exit_code', '')}",
    ]

    if job.get("applied_domain_presets"):
        lines.append(f"Applied Domain Presets: {', '.join(job.get('applied_domain_presets', []))}")

    if job.get("allow_domain_collision"):
        lines.append("Domain Collision: allowed")

    if job.get("summary"):
        lines.append("")
        lines.append("Summary:")
        lines.append(str(job.get("summary", "")).strip())

    lines.append("")
    lines.append("URLs:")
    lines.extend(str(url) for url in urls)

    return "\n".join(lines).strip() + "\n"


def copy_selected_queue_job_details():
    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    copy_text_to_clipboard(format_queue_job_details(job), "Queue job details")


def copy_selected_queue_job_urls():
    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    urls = "\n".join(job.get("urls", []) or []).strip()

    if not urls:
        messagebox.showinfo("No URLs", "The selected queue job does not contain URLs.")
        return

    copy_text_to_clipboard(urls + "\n", "Queue job URLs")


def copy_selected_queue_job_summary():
    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    summary = str(job.get("summary", "") or "").strip()

    if not summary:
        messagebox.showinfo("No summary", "The selected queue job does not have a completed summary.")
        return

    copy_text_to_clipboard(summary + "\n", "Queue job summary")


def copy_selected_queue_case_name():
    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    copy_text_to_clipboard(job.get("resolved_case_name", ""), "Queue job case name")


def copy_selected_queue_domains():
    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    domains = ", ".join(job.get("domains", []) or get_job_domain_keys(job))

    if not domains:
        messagebox.showinfo("No domains", "No domains were detected for the selected queue job.")
        return

    copy_text_to_clipboard(domains, "Queue job domains")


def duplicate_selected_queue_job():
    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    if job.get("status") == "running":
        messagebox.showwarning("Job is running", "A running job cannot be duplicated.")
        return

    settings = (job.get("settings", {}) or {}).copy()
    case_template = job.get("case_template") or job.get("resolved_case_name", "")

    try:
        if case_template:
            resolved_case_name = safe_case_name(render_case_name_template(case_template, now=datetime.now()))
        else:
            resolved_case_name = job.get("resolved_case_name", "")

        if not resolved_case_name:
            resolved_case_name = job.get("resolved_case_name", "")

        duplicate = {
            "job_id": make_job_id(),
            "status": "pending",
            "case_template": case_template,
            "resolved_case_name": resolved_case_name,
            "urls": list(job.get("urls", []) or []),
            "settings": settings,
            "output_root": settings.get("output_root", job.get("output_root", "")),
            "started": "",
            "finished": "",
            "exit_code": "",
            "completed_urls": 0,
            "summary": "",
            "domains": list(job.get("domains", []) or get_job_domain_keys(job)),
            "applied_domain_presets": list(job.get("applied_domain_presets", []) or []),
            "allow_domain_collision": bool(job.get("allow_domain_collision", False)),
            "checked": False,
        }

        job_queue.append(duplicate)
        refresh_job_queue_window()
        append_log(f"\nDuplicated queue job as pending: {resolved_case_name}\n")
    except Exception as e:
        messagebox.showerror("Duplicate job failed", str(e))


def remove_selected_queue_job():
    global job_queue

    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    if job.get("job_id") == job_queue_current_job_id and job_queue_running:
        messagebox.showwarning("Job is running", "The currently running job cannot be removed.")
        return

    if job.get("status") == "running":
        messagebox.showwarning("Job is running", "A running job cannot be removed.")
        return

    job_queue = [item for item in job_queue if item.get("job_id") != job.get("job_id")]
    refresh_job_queue_window()


def clear_completed_queue_jobs():
    global job_queue

    if job_queue_running:
        keep_status = {"pending", "running"}
    else:
        keep_status = {"pending"}

    job_queue = [job for job in job_queue if job.get("status") in keep_status]
    refresh_job_queue_window()


def clear_all_non_active_queue_jobs():
    global job_queue

    active_ids = set()
    if job_queue_current_job_id:
        active_ids.add(job_queue_current_job_id)

    job_queue = [
        job for job in job_queue
        if job.get("status") == "running" or job.get("job_id") in active_ids
    ]

    refresh_job_queue_window()
    append_log("\nCleared all non-active queue jobs.\n")


def copy_completed_queue_job_summaries():
    summaries = []

    for index, job in enumerate(job_queue, start=1):
        if job.get("status") != "completed":
            continue

        summary = job.get("summary", "").strip()
        if not summary:
            continue

        summaries.append(
            "\n".join([
                f"========== Queue Job {index}: {job.get('resolved_case_name', '')} ==========",
                summary,
            ])
        )

    if not summaries:
        messagebox.showinfo("No completed job summaries", "No completed queue job summaries are available.")
        return

    text = "\n\n".join(summaries).strip() + "\n"

    root.clipboard_clear()
    root.clipboard_append(text)
    append_log(f"\nCopied {len(summaries)} completed queue job summary/summaries to clipboard.\n")


def open_selected_queue_case():
    job = get_selected_queue_job()
    if not job:
        messagebox.showinfo("No job selected", "Select a queue job first.")
        return

    case_folder = get_job_case_folder(job)
    if case_folder and os.path.isdir(case_folder):
        os.startfile(case_folder)
    else:
        messagebox.showwarning("Case folder not found", f"The case folder does not exist yet:\n\n{case_folder}")


def pause_queue_after_current():
    global job_queue_pause_after_current

    if not job_queue_running:
        messagebox.showinfo("Queue not running", "The queue is not currently running.")
        return

    job_queue_pause_after_current = True
    if job_queue_status_var and job_queue_window_is_open():
        try:
            job_queue_status_var.set("Queue will pause after the current job.")
        except Exception:
            pass


def stop_current_queue_job():
    global job_queue_pause_after_current

    if not job_queue_running:
        messagebox.showinfo("Queue not running", "The queue is not currently running.")
        return

    job_queue_pause_after_current = True
    stop_capture()

    if job_queue_status_var and job_queue_window_is_open():
        try:
            job_queue_status_var.set("Stop requested for current queue job.")
        except Exception:
            pass


def start_job_queue(selected_only=False):
    global job_queue_running, job_queue_pause_after_current, job_queue_run_filter_ids

    if running_process is not None and running_process.poll() is None and not job_queue_running_processes:
        messagebox.showwarning("Capture already running", "A capture process is already running.")
        return

    if selected_only:
        pending = get_checked_runnable_queue_jobs()
        if not pending:
            messagebox.showinfo("No selected jobs", "Checkmark one or more pending or interrupted jobs first.")
            return

        for job in pending:
            if job.get("status") == "interrupted":
                prepare_queue_job_for_continue(job)

        pending = [job for job in pending if job.get("status") == "pending"]
        if not pending:
            messagebox.showinfo("No remaining URLs", "Selected interrupted jobs had no remaining URLs to continue.")
            save_job_queue_state()
            refresh_job_queue_window()
            return

        job_queue_run_filter_ids = {job.get("job_id") for job in pending}
        save_job_queue_state()
    else:
        pending = [job for job in job_queue if job.get("status") == "pending"]
        job_queue_run_filter_ids = None

    if not pending:
        messagebox.showinfo("No pending jobs", "There are no pending queue jobs to run.")
        return

    if check_vpn_var.get() and last_vpn_status != "connected":
        proceed = messagebox.askyesno(
            "VPN not connected",
            "The VPN does not appear to be connected.\n\n"
            "Start the queue anyway?",
        )
        if not proceed:
            return

    if get_concurrent_capture_limit() >= 2:
        collisions = find_pending_pair_domain_collisions()
        if collisions:
            choice = show_domain_collision_dialog(collisions)
            if choice == "cancel":
                return
            if choice == "continue":
                for item in collisions:
                    item.get("candidate", {})["allow_domain_collision"] = True
                    item.get("existing", {})["allow_domain_collision"] = True

    job_queue_running = True
    job_queue_pause_after_current = False
    append_log("\n========== Job Queue ==========\n")
    if selected_only:
        append_log(f"Starting selected queue jobs: {len(pending)} pending selected job(s).\n")
    else:
        append_log(f"Starting queue with {len(pending)} pending job(s).\n")
    run_next_queue_job()


def start_selected_queue_jobs():
    start_job_queue(selected_only=True)


def restart_selected_queue_jobs():
    selected_jobs = [
        job
        for job in job_queue
        if bool(job.get("checked", False)) and job.get("status") != "running"
    ]

    if not selected_jobs:
        messagebox.showinfo("No selected jobs", "Checkmark one or more non-running jobs first.")
        return

    for job in selected_jobs:
        prepare_queue_job_for_restart(job)

    save_job_queue_state()
    refresh_job_queue_window()
    start_job_queue(selected_only=True)


def continue_selected_interrupted_jobs():
    selected_jobs = [
        job
        for job in job_queue
        if bool(job.get("checked", False)) and job.get("status") == "interrupted"
    ]

    if not selected_jobs:
        messagebox.showinfo("No selected interrupted jobs", "Checkmark one or more interrupted jobs first.")
        return

    for job in selected_jobs:
        prepare_queue_job_for_continue(job)

    save_job_queue_state()
    refresh_job_queue_window()
    start_job_queue(selected_only=True)


def get_running_queue_jobs():
    return [job for job in job_queue if job.get("status") == "running"]


def get_pending_queue_jobs():
    return [
        job
        for job in job_queue
        if job.get("status") == "pending" and queue_job_is_in_run_filter(job)
    ]


def job_collides_with_running_jobs(job):
    if job.get("allow_domain_collision"):
        return False

    job_domains = set(job.get("domains") or get_job_domain_keys(job))
    if not job_domains:
        return False

    for running_job in get_running_queue_jobs():
        running_domains = set(running_job.get("domains") or get_job_domain_keys(running_job))
        if job_domains & running_domains:
            return True

    return False


def update_queue_running_status():
    running_count = len(get_running_queue_jobs())
    pending_count = len(get_pending_queue_jobs())
    total_urls = sum(len(queue_job.get("urls", [])) for queue_job in job_queue)
    completed_urls = sum(int(queue_job.get("completed_urls", 0) or 0) for queue_job in job_queue)

    scope_text = "selected queue" if queue_run_filter_is_active() else "queue"
    text = (
        f"{scope_text.capitalize()} running: {running_count} active, {pending_count} pending, "
        f"{completed_urls}/{total_urls} URL segment(s) complete"
    )

    if job_queue_status_var and job_queue_window_is_open():
        try:
            job_queue_status_var.set(text)
        except Exception:
            pass

    set_status(text)


def run_next_queue_job():
    global job_queue_running, job_queue_current_job_id, job_queue_run_filter_ids

    if not job_queue_running:
        return

    limit = get_concurrent_capture_limit()
    started_any = False

    while len(get_running_queue_jobs()) < limit:
        next_job = None

        for job in job_queue:
            if job.get("status") != "pending":
                continue
            if not queue_job_is_in_run_filter(job):
                continue
            if job_collides_with_running_jobs(job):
                continue
            next_job = job
            break

        if not next_job:
            break

        job_queue_current_job_id = next_job["job_id"]
        run_queue_job(next_job)
        started_any = True

    running_jobs = get_running_queue_jobs()
    pending_jobs = get_pending_queue_jobs()

    if not running_jobs and not pending_jobs:
        job_queue_running = False
        job_queue_current_job_id = None
        job_queue_run_filter_ids = None
        refresh_job_queue_window()
        if job_queue_status_var and job_queue_window_is_open():
            try:
                job_queue_status_var.set("Queue complete.")
            except Exception:
                pass
        append_log("\nJob queue complete.\n")
        set_status("Queue complete")
        start_button.config(state="normal")
        start_menu_button.config(state="normal")
        stop_button.config(state="disabled")
        return

    if not started_any and pending_jobs and running_jobs:
        update_queue_running_status()
        append_log("\nPending queue jobs are waiting for colliding running domain(s) to finish.\n")
    else:
        update_queue_running_status()


def mark_queue_job_url_complete(job_id, url_index=None):
    job = None
    for item in job_queue:
        if item.get("job_id") == job_id:
            job = item
            break

    if not job:
        return

    current = int(job.get("completed_urls", 0) or 0)
    total = len(job.get("urls", []))

    resume_base = int(job.get("_resume_base_completed", 0) or 0)

    if url_index is not None:
        try:
            current = max(current, resume_base + int(url_index))
        except Exception:
            current += 1
    else:
        current += 1

    if total:
        current = min(current, total)

    job["completed_urls"] = current
    save_job_queue_state()
    update_job_queue_progress()

    if job_queue_status_var and job_queue_window_is_open():
        total_urls = sum(len(queue_job.get("urls", [])) for queue_job in job_queue)
        completed_urls = sum(int(queue_job.get("completed_urls", 0) or 0) for queue_job in job_queue)
        try:
            job_queue_status_var.set(f"Queue running: {completed_urls}/{total_urls} URL segment(s) complete")
        except Exception:
            pass


def handle_queue_output_line(job_id, line):
    if line.startswith("GUI_QUEUE_URL_COMPLETE\t"):
        parts = line.strip().split("\t", 3)
        url_index = None
        if len(parts) >= 2:
            try:
                url_index = int(parts[1])
            except Exception:
                url_index = None
        mark_queue_job_url_complete(job_id, url_index=url_index)


def run_queue_job(job):
    global running_process, last_capture_context, job_queue_running_processes

    try:
        validate_queue_job_inputs(job)

        job_case_folder = get_job_case_folder(job)
        if case_folder_is_populated(job_case_folder):
            proceed = messagebox.askyesno(
                "Existing populated case folder",
                "The resolved queue job case folder already exists and contains files or folders:\n\n"
                f"{job_case_folder}\n\n"
                "Starting this queue job may add files to the existing case and reuse its archive/history.\n\n"
                "Continue?",
            )

            if not proceed:
                job["status"] = "cancelled"
                job["finished"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                job["exit_code"] = "cancelled"
                refresh_job_queue_window()
                root.after(0, run_next_queue_job)
                return

        run_urls = get_queue_job_run_urls(job)
        resume_base_completed = int(job.get("_resume_base_completed", 0) or 0)
        cmd = build_powershell_command_for_job(job)
        submitted_url_count = len(run_urls)
        tool_versions = query_capture_tool_versions_for_job(job.get("settings", {}))

        job_paths = get_expected_run_paths_for_values(
            job.get("settings", {}).get("output_root", ""),
            job.get("resolved_case_name", ""),
        )
        job["paths"] = job_paths
        job["tool_versions"] = tool_versions

        last_capture_context = {
            "tool_versions": tool_versions,
            "submitted_url_count": submitted_url_count,
            "settings": job.get("settings", {}),
            "paths": job_paths,
        }

        job["status"] = "running"
        job["started"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job["finished"] = ""
        job["exit_code"] = ""
        if job.get("_run_mode") == "continue":
            job["completed_urls"] = resume_base_completed
        else:
            job["completed_urls"] = 0
        job["_interruption_requested"] = False

        refresh_job_queue_window()
        if job_queue_status_var and job_queue_window_is_open():
            try:
                job_queue_status_var.set(f"Running queue job: {job.get('resolved_case_name', '')}")
            except Exception:
                pass

        append_log("\n========== Queue Job Started ==========\n")
        append_log(f"Job ID: {job['job_id']}\n")
        append_log(f"Case: {job.get('resolved_case_name', '')}\n")
        if job.get("_run_mode") == "continue":
            append_log(f"URLs this run: {submitted_url_count} (continuing from URL {resume_base_completed + 1})\n")
        else:
            append_log(f"URLs: {submitted_url_count}\n")
        if job.get("applied_domain_presets"):
            append_log(f"Applied active domain presets: {', '.join(job.get('applied_domain_presets', []))}\n")
        append_log("\n")
        log_capture_tool_versions(tool_versions)
        append_log("Command:\n")
        append_log(format_command_for_log(cmd))
        append_log("\n\n")

        start_button.config(state="normal")
        start_menu_button.config(state="normal")
        stop_button.config(state="normal")
        copy_summary_button.config(state="disabled")
        set_status(f"Queue running: {job.get('resolved_case_name', '')}")

    except Exception as e:
        job["status"] = "failed"
        job["finished"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job["exit_code"] = "setup error"
        append_log(f"\nQueue job setup failed: {e}\n")
        refresh_job_queue_window()
        root.after(0, run_next_queue_job)
        return

    def worker():
        global running_process

        exit_code = 1

        try:
            process = subprocess.Popen(
                cmd,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            job_queue_running_processes[job["job_id"]] = process
            running_process = process

            universal_skip_records = []
            universal_skip_summary = {}

            if process.stdout:
                for line in process.stdout:
                    skip_record = parse_universal_archive_skip_output_line(line)
                    if skip_record:
                        universal_skip_records.append(skip_record)
                        root.after(0, append_log, format_universal_archive_skip_record_for_log(skip_record) + "\n")
                        continue

                    skip_summary = parse_universal_archive_skip_summary_line(line)
                    if skip_summary:
                        universal_skip_summary = skip_summary
                        continue

                    root.after(0, append_log, line)
                    if line.startswith("GUI_QUEUE_URL_COMPLETE\t"):
                        root.after(0, handle_queue_output_line, job["job_id"], line)

            exit_code = process.wait()

        except Exception as e:
            root.after(0, append_log, f"\nERROR: {e}\n")
            exit_code = 1

        root.after(0, finish_queue_job, job["job_id"], exit_code, submitted_url_count, universal_skip_records, universal_skip_summary)

    threading.Thread(target=worker, daemon=True).start()


def finish_queue_job(job_id, exit_code, submitted_url_count, universal_skip_records=None, universal_skip_summary=None):
    global job_queue_running, job_queue_current_job_id, job_queue_running_processes, last_successful_case_summary, job_queue_run_filter_ids

    job = None
    for item in job_queue:
        if item.get("job_id") == job_id:
            job = item
            break

    if not job:
        return

    job_queue_running_processes.pop(job_id, None)

    job["finished"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job["exit_code"] = exit_code

    if exit_code == 0:
        job["status"] = "completed"
        append_log(f"\nQueue job completed successfully: {job.get('resolved_case_name', '')}\n")
        set_status("Queue job completed")
    elif job.get("_interruption_requested"):
        job["status"] = "interrupted"
        job["exit_code"] = "interrupted"
        job["interrupted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job["interrupted_reason"] = job.get("interrupted_reason") or "Stopped by user."
        append_log(f"\nQueue job interrupted: {job.get('resolved_case_name', '')}\n")
        set_status("Queue job interrupted")
    else:
        job["status"] = "failed"
        append_log(f"\nQueue job failed with exit code {exit_code}: {job.get('resolved_case_name', '')}\n")
        set_status(f"Queue job failed: {exit_code}")

    paths = job.get("paths") or get_expected_run_paths_for_values(
        job.get("settings", {}).get("output_root", ""),
        job.get("resolved_case_name", ""),
    )
    counts = count_case_files(paths.get("case_folder", ""))
    versions = job.get("tool_versions", {})
    summary_settings = job.get("settings", {})

    append_log("\n========== Queue Job Summary ==========")
    append_log(f"\nExit code: {exit_code}\n")
    append_log(f"Submitted URLs: {submitted_url_count}\n")
    append_log(f"Case folder: {paths.get('case_folder', '')}\n")
    append_universal_archive_skip_summary(universal_skip_records, universal_skip_summary)
    append_log(f"Total files found: {counts.get('files', 0)}\n")
    append_log(f"Media files found: {counts.get('media', 0)}\n")
    append_log(f"Metadata JSON files found: {counts.get('metadata', 0)}\n")
    append_log(f"Manifest files found: {counts.get('manifests', 0)}\n")
    append_log("=====================================\n")

    if job.get("status") == "completed":
        job["summary"] = build_case_summary_text(
            exit_code,
            submitted_url_count,
            paths,
            versions,
            counts,
            settings=summary_settings,
            universal_skip_records=universal_skip_records,
            universal_skip_summary=universal_skip_summary,
        )
        last_successful_case_summary = job["summary"]
    else:
        job["summary"] = ""

    job.pop("_run_mode", None)
    job.pop("_resume_base_completed", None)
    job.pop("_interruption_requested", None)

    refresh_job_queue_window()

    if not get_running_queue_jobs():
        start_button.config(state="normal")
        start_menu_button.config(state="normal")
        stop_button.config(state="disabled")

    if job_queue_pause_after_current and not get_running_queue_jobs():
        job_queue_running = False
        job_queue_current_job_id = None
        job_queue_run_filter_ids = None
        if job_queue_status_var and job_queue_window_is_open():
            try:
                job_queue_status_var.set("Queue paused after current job.")
            except Exception:
                pass
        append_log("\nJob queue paused after current job.\n")
        return

    root.after(250, run_next_queue_job)


def open_job_queue(select_tab=True):
    global job_queue_window, job_queue_tree, job_queue_progress_var, job_queue_status_var

    if job_queue_window_is_open():
        if select_tab:
            try:
                app_notebook.select(job_queue_window)
                if job_queue_tree_is_available():
                    job_queue_tree.focus_set()
            except Exception:
                pass
        refresh_job_queue_window()
        return

    try:
        container = job_queue_tab
    except NameError:
        return

    for child in container.winfo_children():
        try:
            child.destroy()
        except Exception:
            pass

    job_queue_window = container
    job_queue_window.columnconfigure(0, weight=1)
    job_queue_window.rowconfigure(0, weight=0)
    job_queue_window.rowconfigure(1, weight=1)
    job_queue_window.rowconfigure(2, weight=0)

    top_bar = ttk.Frame(job_queue_window, padding=(8, 0, 8, 0))
    top_bar.grid(row=0, column=0, sticky="ew")

    ttk.Button(top_bar, text="Add Current as Job", command=add_current_as_job).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Start Queue", command=start_job_queue).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Start Selected", command=start_selected_queue_jobs).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Restart Selected", command=restart_selected_queue_jobs).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Pause After Current", command=pause_queue_after_current).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Stop Current", command=stop_current_queue_job).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Remove Selected", command=remove_selected_queue_job).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Clear Completed", command=clear_completed_queue_jobs).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Clear All", command=clear_all_non_active_queue_jobs).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Copy Jobs Summary", command=copy_completed_queue_job_summaries).pack(side="left", padx=(0, 6))
    ttk.Button(top_bar, text="Open Case", command=open_selected_queue_case).pack(side="left", padx=(0, 6))

    table_frame = ttk.Frame(job_queue_window, padding=(8, 0, 8, 2))
    table_frame.grid(row=1, column=0, sticky="nsew")
    table_frame.columnconfigure(0, weight=1)
    table_frame.rowconfigure(0, weight=1)

    columns = ("selected", "#", "status", "case", "urls", "domains", "presets", "output_root", "started", "finished", "exit")
    job_queue_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
    job_queue_tree.grid(row=0, column=0, sticky="nsew")

    headings = {
        "selected": "Select",
        "#": "#",
        "status": "Status",
        "case": "Case",
        "urls": "URLs",
        "domains": "Domains",
        "presets": "Presets",
        "output_root": "Output Root",
        "started": "Started",
        "finished": "Finished",
        "exit": "Exit",
    }

    widths = {
        "selected": 70,
        "#": 45,
        "status": 110,
        "case": 260,
        "urls": 60,
        "domains": 220,
        "presets": 220,
        "output_root": 420,
        "started": 145,
        "finished": 145,
        "exit": 75,
    }

    for column in columns:
        job_queue_tree.heading(column, text=headings[column])
        anchor = "center" if column == "selected" else "w"
        job_queue_tree.column(column, width=widths[column], minwidth=widths[column], anchor=anchor, stretch=False)

    table_scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=job_queue_tree.yview)
    table_scroll_y.grid(row=0, column=1, sticky="ns")

    table_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=job_queue_tree.xview)
    table_scroll_x.grid(row=1, column=0, sticky="ew")

    job_queue_tree.configure(
        yscrollcommand=table_scroll_y.set,
        xscrollcommand=table_scroll_x.set,
    )

    def clear_job_queue_selection():
        if not job_queue_tree_is_available():
            return

        try:
            job_queue_tree.selection_remove(job_queue_tree.selection())
            job_queue_tree.focus("")
            update_job_queue_selection_marks()
        except Exception:
            pass

    def on_job_queue_left_click(event):
        if not job_queue_tree_is_available():
            return

        row_id = job_queue_tree.identify_row(event.y)
        region = job_queue_tree.identify("region", event.x, event.y)
        column_id = job_queue_tree.identify_column(event.x)

        if not row_id or region not in {"cell", "tree"}:
            clear_job_queue_selection()
            return "break"

        try:
            if column_id == "#1":
                toggle_queue_job_checkmark(row_id)

            job_queue_tree.selection_set(row_id)
            job_queue_tree.focus(row_id)
            update_job_queue_selection_marks()
            return "break"
        except Exception:
            return

    def on_job_queue_double_click(event):
        if not job_queue_tree_is_available():
            return

        row_id = job_queue_tree.identify_row(event.y)
        region = job_queue_tree.identify("region", event.x, event.y)
        column_id = job_queue_tree.identify_column(event.x)

        if not row_id or region not in {"cell", "tree"}:
            clear_job_queue_selection()
            return "break"

        # The checkmark box already toggles on direct click. Avoid toggling twice on a double-click there.
        if column_id == "#1":
            return "break"

        try:
            toggle_queue_job_checkmark(row_id)
            job_queue_tree.selection_set(row_id)
            job_queue_tree.focus(row_id)
            update_job_queue_selection_marks()
            return "break"
        except Exception:
            return

    job_queue_tree.bind("<Button-1>", on_job_queue_left_click)
    job_queue_tree.bind("<Double-1>", on_job_queue_double_click)

    def show_job_queue_context_menu(event):
        if not job_queue_tree_is_available():
            return

        row_id = job_queue_tree.identify_row(event.y)
        region = job_queue_tree.identify("region", event.x, event.y)

        if row_id and region in {"cell", "tree"}:
            job_queue_tree.selection_set(row_id)
            job_queue_tree.focus(row_id)
        else:
            clear_job_queue_selection()

        update_job_queue_selection_marks()
        job = get_selected_queue_job()

        menu = tk.Menu(root, tearoff=0)

        if job:
            job_running = job.get("status") == "running"
            job_has_summary = bool(str(job.get("summary", "") or "").strip())
            case_folder = get_job_case_folder(job)
            case_exists = bool(case_folder and os.path.isdir(case_folder))

            menu.add_command(label="Open Case Folder", command=open_selected_queue_case)
            if not case_exists:
                menu.entryconfig("Open Case Folder", state="disabled")

            menu.add_separator()
            menu.add_command(label="Copy Job Details", command=copy_selected_queue_job_details)
            menu.add_command(label="Copy URLs", command=copy_selected_queue_job_urls)
            menu.add_command(label="Copy Case Name", command=copy_selected_queue_case_name)
            menu.add_command(label="Copy Domains", command=copy_selected_queue_domains)
            menu.add_command(label="Copy Job Summary", command=copy_selected_queue_job_summary)
            if not job_has_summary:
                menu.entryconfig("Copy Job Summary", state="disabled")

            menu.add_separator()
            menu.add_command(label="Duplicate as Pending", command=duplicate_selected_queue_job)
            if job_running:
                menu.entryconfig("Duplicate as Pending", state="disabled")

            menu.add_command(label="Remove Selected", command=remove_selected_queue_job)
            if job_running:
                menu.entryconfig("Remove Selected", state="disabled")
        else:
            menu.add_command(label="No job selected", state="disabled")

        menu.add_separator()
        menu.add_command(label="Add Current as Job", command=add_current_as_job)
        menu.add_command(label="Start Queue", command=start_job_queue)
        if not any(item.get("status") == "pending" for item in job_queue):
            menu.entryconfig("Start Queue", state="disabled")

        menu.add_command(label="Start Selected", command=start_selected_queue_jobs)
        if not any(item.get("status") in {"pending", "interrupted"} and bool(item.get("checked", False)) for item in job_queue):
            menu.entryconfig("Start Selected", state="disabled")

        menu.add_command(label="Continue Selected Interrupted", command=continue_selected_interrupted_jobs)
        if not any(item.get("status") == "interrupted" and bool(item.get("checked", False)) for item in job_queue):
            menu.entryconfig("Continue Selected Interrupted", state="disabled")

        menu.add_command(label="Restart Selected", command=restart_selected_queue_jobs)
        if not any(item.get("status") != "running" and bool(item.get("checked", False)) for item in job_queue):
            menu.entryconfig("Restart Selected", state="disabled")

        menu.add_command(label="Pause After Current", command=pause_queue_after_current)
        menu.add_command(label="Stop Current", command=stop_current_queue_job)
        if not job_queue_running:
            menu.entryconfig("Pause After Current", state="disabled")
            menu.entryconfig("Stop Current", state="disabled")

        menu.add_separator()
        menu.add_command(label="Clear Completed", command=clear_completed_queue_jobs)
        if not any(item.get("status") == "completed" for item in job_queue):
            menu.entryconfig("Clear Completed", state="disabled")

        menu.add_command(label="Clear All Non-Active", command=clear_all_non_active_queue_jobs)
        if not any(item.get("status") != "running" and item.get("job_id") != job_queue_current_job_id for item in job_queue):
            menu.entryconfig("Clear All Non-Active", state="disabled")

        menu.add_command(label="Copy Completed Summaries", command=copy_completed_queue_job_summaries)
        if not any(item.get("status") == "completed" and str(item.get("summary", "") or "").strip() for item in job_queue):
            menu.entryconfig("Copy Completed Summaries", state="disabled")

        try:
            colors = get_theme_colors()
            configure_menu_theme(menu, colors)
        except Exception:
            pass

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    job_queue_tree.bind("<Button-3>", show_job_queue_context_menu)

    bottom = ttk.Frame(job_queue_window, padding=(8, 0, 8, 2))
    bottom.grid(row=2, column=0, sticky="ew")

    job_queue_progress_var = tk.DoubleVar(value=0)
    progress = ttk.Progressbar(bottom, variable=job_queue_progress_var, maximum=100, mode="determinate")
    progress.pack(fill="x", side="top", pady=(0, 6))

    job_queue_status_var = tk.StringVar(value="Queue is empty.")
    ttk.Label(bottom, textvariable=job_queue_status_var).pack(fill="x", side="top")

    if select_tab:
        try:
            app_notebook.select(job_queue_window)
        except Exception:
            pass

    apply_app_theme()
    refresh_job_queue_window()


def stop_capture():
    global running_process, job_queue_pause_after_current

    if job_queue_running_processes:
        job_queue_pause_after_current = True
        try:
            for job in get_running_queue_jobs():
                job["_interruption_requested"] = True
                job["interrupted_reason"] = "Stopped by user."
            save_job_queue_state()
            for process in list(job_queue_running_processes.values()):
                if process is not None and process.poll() is None:
                    process.terminate()
            append_log("\nStop requested. Active queue process(es) terminated. Queue will pause after active job(s) stop.\n")
            set_status("Stopping queue...")
        except Exception as e:
            messagebox.showerror("Stop error", str(e))
        return

    if running_process is not None and running_process.poll() is None:
        try:
            running_process.terminate()
            append_log("\nStop requested. Process terminated.\n")
            set_status("Stopped")
        except Exception as e:
            messagebox.showerror("Stop error", str(e))


def get_selected_vpn_adapter_identifiers():
    selected = vpn_adapter_var.get().strip()

    if not selected:
        return {
            "name": "",
            "description": "",
            "display": "",
        }

    if selected in adapter_display_map:
        return adapter_display_map[selected]

    return {
        "name": selected,
        "description": selected,
        "display": selected,
    }


def check_vpn_status():
    global last_vpn_status

    if not check_vpn_var.get():
        last_vpn_status = "disabled"
        vpn_status_var.set("VPN: Check disabled")
        return

    selected_adapter = get_selected_vpn_adapter_identifiers()
    selected_name = selected_adapter.get("name", "").replace("'", "''")
    selected_description = selected_adapter.get("description", "").replace("'", "''")

    if not selected_name and not selected_description:
        last_vpn_status = "unknown"
        vpn_status_var.set("VPN: No adapter selected")
        messagebox.showwarning("No VPN adapter selected", "Select a VPN adapter first.")
        return

    vpn_status_var.set("VPN: Checking selected adapter...")

    def worker():
        global last_vpn_status

        ps_command = (
            "$adapter = Get-NetAdapter -ErrorAction SilentlyContinue | "
            f"Where-Object {{ $_.Name -eq '{selected_name}' -or $_.InterfaceDescription -eq '{selected_description}' }} | "
            "Select-Object -First 1; "
            "if ($adapter -and $adapter.Status -eq 'Up') { 'UP' } "
            "elseif ($adapter) { 'DOWN' } "
            "else { 'NOT_FOUND' }"
        )

        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            ps_command,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )

            output = (result.stdout or "").strip()

            if output == "UP":
                text = "VPN: Connected"
                last_vpn_status = "connected"
            elif output == "DOWN":
                text = "VPN: Selected adapter found, not connected"
                last_vpn_status = "disconnected"
            elif output == "NOT_FOUND":
                text = "VPN: Selected adapter not found"
                last_vpn_status = "not_found"
            else:
                text = "VPN: Unknown"
                last_vpn_status = "unknown"

        except Exception as e:
            text = f"VPN: Check failed ({e})"
            last_vpn_status = "unknown"

        root.after(0, vpn_status_var.set, text)

    threading.Thread(target=worker, daemon=True).start()


def refresh_network_adapters():
    vpn_status_var.set("VPN: Loading adapters...")

    def worker():
        global adapter_display_map

        ps_command = r"""
Get-NetAdapter -ErrorAction SilentlyContinue |
    Select-Object Name, InterfaceDescription, Status |
    ForEach-Object {
        "ADAPTER`t{0}`t{1}`t{2}" -f $_.Name, $_.InterfaceDescription, $_.Status
    }
"""

        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            ps_command,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )

            new_map = {}
            values = []

            for line in (result.stdout or "").splitlines():
                parts = line.split("\t")
                if len(parts) < 4:
                    continue

                name = parts[1].strip()
                description = parts[2].strip()
                status = parts[3].strip()

                if not name and not description:
                    continue

                # Do not include status in the dropdown display. Status changes
                # between sessions, so including it would make saved settings stale.
                if name and description:
                    display = f"{name} — {description}"
                else:
                    display = name or description

                new_map[display] = {
                    "name": name,
                    "description": description,
                    "status": status,
                    "display": display,
                }

                values.append(display)

            def normalize_saved_adapter_display(value):
                value = value.strip()
                if not value:
                    return ""

                # Backward compatibility for older saved values like:
                # "Name — Description [Up]"
                if value.endswith("]") and " [" in value:
                    value = value.rsplit(" [", 1)[0].strip()

                return value

            def update_ui():
                global adapter_display_map

                adapter_display_map = new_map
                vpn_adapter_menu["values"] = values

                if not values:
                    vpn_adapter_var.set("")
                    vpn_status_var.set("VPN: No adapters found")
                    return

                current = normalize_saved_adapter_display(vpn_adapter_var.get())

                if current in values:
                    vpn_adapter_var.set(current)
                else:
                    vpn_adapter_var.set(values[0])

                vpn_status_var.set(f"VPN: Loaded {len(values)} adapter(s). Select the adapter that represents your VPN.")

            root.after(0, update_ui)

        except Exception as e:
            root.after(0, vpn_status_var.set, f"VPN: Adapter refresh failed ({e})")

    threading.Thread(target=worker, daemon=True).start()



def check_ytdlp_version():
    yt_dlp_path = yt_dlp_path_var.get().strip()

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        yt_dlp_version_status_var.set("yt-dlp: not found")
        append_log("\nyt-dlp version check failed: yt-dlp path is missing or invalid.\n")
        return

    yt_dlp_version_status_var.set("yt-dlp: checking version...")
    append_log(f"\nChecking yt-dlp version: {yt_dlp_path}\n")

    def worker():
        try:
            result = subprocess.run(
                [yt_dlp_path, "--version"],
                cwd=os.path.dirname(os.path.abspath(yt_dlp_path)) or ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )

            output = (result.stdout or result.stderr or "").strip()

            if result.returncode == 0 and output:
                root.after(0, yt_dlp_version_status_var.set, f"yt-dlp: {output}")
                root.after(0, append_log, f"yt-dlp version: {output}\n")
            else:
                root.after(0, yt_dlp_version_status_var.set, "yt-dlp: version check failed")
                root.after(
                    0,
                    append_log,
                    f"yt-dlp version check failed. Exit code: {result.returncode}\n{output}\n",
                )

        except Exception as e:
            root.after(0, yt_dlp_version_status_var.set, "yt-dlp: version check error")
            root.after(0, append_log, f"yt-dlp version check error: {e}\n")

    threading.Thread(target=worker, daemon=True).start()


def normalize_version_for_compare(value):
    value = (value or "").strip()

    if value.lower().startswith("v"):
        value = value[1:]

    parts = []
    for token in re.split(r"[^0-9]+", value):
        if token:
            try:
                parts.append(int(token))
            except Exception:
                pass

    return tuple(parts)


def fetch_latest_app_release():
    req = urllib.request.Request(
        APP_GITHUB_LATEST_API_URL,
        headers={
            "User-Agent": "ytdlp-gui-for-osint",
            "Accept": "application/vnd.github+json",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        release = json.loads(response.read().decode("utf-8"))

    return {
        "tag": release.get("tag_name", "") or release.get("name", ""),
        "name": release.get("name", ""),
        "published": release.get("published_at", ""),
        "body": release.get("body", ""),
        "url": release.get("html_url", APP_RELEASES_LATEST_URL),
    }


def open_about_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("About yt-dlp GUI for OSINT")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    frame = ttk.Frame(dialog, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text=APP_TITLE,
        font=("Segoe UI", 12, "bold"),
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    ttk.Label(
        frame,
        text=f"Version: {APP_VERSION}",
    ).grid(row=1, column=0, sticky="w", pady=(0, 12))

    ttk.Label(
        frame,
        text=(
            "A portable Windows GUI for running an approved yt-dlp capture workflow "
            "for OSINT-style collection and review.\n\n"
            "This app does not bundle yt-dlp, FFmpeg, Deno, or other binaries. "
            "Use official, signed, organization-approved binaries where required."
        ),
        wraplength=520,
        justify="left",
    ).grid(row=2, column=0, sticky="w", pady=(0, 12))

    ttk.Label(
        frame,
        text="Repository:",
    ).grid(row=3, column=0, sticky="w", pady=(0, 2))

    repo_url = "https://github.com/jmashuque/ytdlp-gui-for-osint"
    repo_label = ttk.Label(
        frame,
        text=repo_url,
        cursor="hand2",
        foreground="blue",
    )
    repo_label.grid(row=4, column=0, sticky="w", pady=(0, 14))
    repo_label.bind("<Button-1>", lambda event: webbrowser.open(repo_url))

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=5, column=0, sticky="e")

    ttk.Button(
        button_frame,
        text="Open Repository",
        command=lambda: webbrowser.open(repo_url),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        button_frame,
        text="Close",
        command=dialog.destroy,
    ).pack(side="left")


def open_app_update_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Check for App Updates")
    dialog.geometry("700x460")
    dialog.minsize(640, 420)
    dialog.transient(root)
    dialog.grab_set()

    current_version_var = tk.StringVar(value=f"Current version: {APP_VERSION}")
    latest_version_var = tk.StringVar(value="Latest GitHub release: checking...")
    status_var_local = tk.StringVar(value="Querying latest release from GitHub...")
    latest_release_url_var = tk.StringVar(value=APP_RELEASES_LATEST_URL)

    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(4, weight=1)

    ttk.Label(
        frame,
        text=(
            "This checker only queries the latest GitHub release and opens the release page for manual download. "
            "It does not download, extract, replace, or run files."
        ),
        wraplength=660,
        justify="left",
    ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

    ttk.Label(frame, textvariable=current_version_var).grid(row=1, column=0, sticky="w", pady=3)
    ttk.Label(frame, textvariable=latest_version_var).grid(row=2, column=0, sticky="w", pady=3)
    ttk.Label(frame, textvariable=status_var_local, wraplength=660, justify="left").grid(row=3, column=0, sticky="ew", pady=(6, 8))

    release_notes = scrolledtext.ScrolledText(frame, height=10, wrap="word")
    release_notes.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
    release_notes.insert("1.0", "Release notes will appear here if available.")
    release_notes.config(state="disabled")

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=5, column=0, sticky="e")

    def set_release_notes(text_value):
        release_notes.config(state="normal")
        release_notes.delete("1.0", "end")
        release_notes.insert("1.0", text_value or "No release notes provided.")
        release_notes.config(state="disabled")

    def open_latest_release_page():
        webbrowser.open(latest_release_url_var.get() or APP_RELEASES_LATEST_URL)

    def query_latest_release():
        status_var_local.set("Querying latest release from GitHub...")
        latest_version_var.set("Latest GitHub release: checking...")
        set_release_notes("Querying GitHub...")

        def worker():
            try:
                release = fetch_latest_app_release()
                tag = release.get("tag") or "unknown"
                url = release.get("url") or APP_RELEASES_LATEST_URL
                published = release.get("published") or "unknown"
                body = release.get("body") or "No release notes provided."

                current_tuple = normalize_version_for_compare(APP_VERSION)
                latest_tuple = normalize_version_for_compare(tag)

                if latest_tuple and current_tuple and latest_tuple > current_tuple:
                    status_text = "A newer release appears to be available. Open the release page to manually download the latest ZIP."
                elif latest_tuple and current_tuple and latest_tuple == current_tuple:
                    status_text = "You appear to be on the latest tagged release."
                else:
                    status_text = "Latest release was found. Review the release page to confirm whether an update is needed."

                def update_ui():
                    latest_release_url_var.set(url)
                    latest_version_var.set(f"Latest GitHub release: {tag}    Published: {published}")
                    status_var_local.set(status_text)
                    set_release_notes(body)
                    append_log(
                        "\nChecked app updates from GitHub.\n"
                        f"Current version: {APP_VERSION}\n"
                        f"Latest release: {tag}\n"
                        f"Release page: {url}\n"
                    )

                root.after(0, update_ui)

            except Exception as e:
                error_message = str(e)

                def show_error():
                    latest_version_var.set("Latest GitHub release: unavailable")
                    status_var_local.set(f"Could not query latest GitHub release: {error_message}")
                    set_release_notes("Could not retrieve release notes.")
                    append_log(f"\nFailed to check app updates: {error_message}\n")
                    messagebox.showerror("Update check failed", error_message)

                root.after(0, show_error)

        threading.Thread(target=worker, daemon=True).start()

    ttk.Button(button_frame, text="Recheck", command=query_latest_release).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Open Latest Release Page", command=open_latest_release_page).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side="left", padx=6)

    query_latest_release()


def fetch_ytdlp_nightly_releases(limit=20):
    url = f"https://api.github.com/repos/yt-dlp/yt-dlp-nightly-builds/releases?per_page={limit}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ytdlp-gui-for-osint",
            "Accept": "application/vnd.github+json",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        releases = json.loads(response.read().decode("utf-8"))

    results = []
    for release in releases:
        tag = release.get("tag_name", "")
        published = release.get("published_at", "")
        name = release.get("name", "")

        if tag:
            results.append(
                {
                    "tag": tag,
                    "published": published,
                    "name": name,
                    "display": f"{tag}    {published}",
                }
            )

    return results


def open_ytdlp_update_dialog():
    yt_dlp_path = yt_dlp_path_var.get().strip()

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        yt_dlp_version_status_var.set("yt-dlp: not found")
        messagebox.showerror("yt-dlp not found", "yt-dlp path is missing or invalid.")
        return

    dialog = tk.Toplevel(root)
    dialog.title("Update yt-dlp")
    dialog.geometry("720x560")
    dialog.minsize(680, 520)
    dialog.transient(root)
    dialog.grab_set()

    update_mode_var = tk.StringVar(value="stable")
    nightly_status_var = tk.StringVar(value="Nightly list not loaded.")
    selected_nightly_tag_var = tk.StringVar(value="")
    current_version_var = tk.StringVar(value="Current detected version: checking...")
    nightly_releases = []

    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(5, weight=1)

    warning = (
        "Warning: Organizational ASR or endpoint protection may block very recent nightly builds "
        "because they are new, low-prevalence executable files. Prefer a known-good pinned nightly "
        "or an IT-approved staged release for production use."
    )

    ttk.Label(frame, text=warning, wraplength=670, justify="left").grid(
        row=0,
        column=0,
        columnspan=3,
        sticky="ew",
        pady=(0, 10),
    )

    ttk.Label(
        frame,
        textvariable=current_version_var,
        justify="left",
    ).grid(
        row=1,
        column=0,
        columnspan=3,
        sticky="w",
        pady=(0, 10),
    )

    ttk.Label(frame, text="Update target").grid(row=2, column=0, sticky="nw", pady=4)

    mode_frame = ttk.Frame(frame)
    mode_frame.grid(row=2, column=1, columnspan=2, sticky="ew", pady=4)

    ttk.Radiobutton(
        mode_frame,
        text="Latest stable",
        variable=update_mode_var,
        value="stable",
    ).pack(anchor="w")

    ttk.Radiobutton(
        mode_frame,
        text="Latest nightly",
        variable=update_mode_var,
        value="nightly",
    ).pack(anchor="w")

    ttk.Radiobutton(
        mode_frame,
        text="Selected nightly from list",
        variable=update_mode_var,
        value="selected_nightly",
    ).pack(anchor="w")

    ttk.Button(
        frame,
        text="Query Nightlies from GitHub",
        command=lambda: query_nightlies(),
    ).grid(row=3, column=0, sticky="w", pady=(8, 4))

    ttk.Label(frame, textvariable=nightly_status_var).grid(
        row=3,
        column=1,
        columnspan=2,
        sticky="w",
        pady=(8, 4),
    )

    ttk.Label(frame, text="Available nightlies").grid(row=4, column=0, sticky="nw", pady=4)

    list_frame = ttk.Frame(frame)
    list_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=4)
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)

    nightly_listbox = tk.Listbox(list_frame, height=12)
    nightly_listbox.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=nightly_listbox.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    nightly_listbox.configure(yscrollcommand=scrollbar.set)

    selected_label = ttk.Label(frame, textvariable=selected_nightly_tag_var)
    selected_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=(4, 8))

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=7, column=0, columnspan=3, sticky="e", pady=(8, 0))

    def refresh_current_version_for_dialog():
        append_log(f"\nChecking current yt-dlp version for update dialog: {yt_dlp_path}\n")

        def worker():
            try:
                result = subprocess.run(
                    [yt_dlp_path, "--version"],
                    cwd=os.path.dirname(os.path.abspath(yt_dlp_path)) or ROOT,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                output = (result.stdout or result.stderr or "").strip()

                if result.returncode == 0 and output:
                    root.after(0, current_version_var.set, f"Current detected version: {output}")
                    root.after(0, yt_dlp_version_status_var.set, f"yt-dlp: {output}")
                    root.after(0, append_log, f"Current yt-dlp version: {output}\n")
                else:
                    root.after(0, current_version_var.set, "Current detected version: unable to detect")
                    root.after(0, yt_dlp_version_status_var.set, "yt-dlp: version check failed")
                    root.after(
                        0,
                        append_log,
                        f"Unable to detect current yt-dlp version. Exit code: {result.returncode}\n{output}\n",
                    )

            except Exception as e:
                root.after(0, current_version_var.set, f"Current detected version: error ({e})")
                root.after(0, yt_dlp_version_status_var.set, "yt-dlp: version check error")
                root.after(0, append_log, f"yt-dlp version check error in update dialog: {e}\n")

        threading.Thread(target=worker, daemon=True).start()

    def on_nightly_select(event=None):
        selection = nightly_listbox.curselection()
        if not selection:
            selected_nightly_tag_var.set("")
            return

        index = selection[0]
        if index >= len(nightly_releases):
            selected_nightly_tag_var.set("")
            return

        tag = nightly_releases[index]["tag"]
        selected_nightly_tag_var.set(f"Selected nightly: {tag}")
        update_mode_var.set("selected_nightly")

    nightly_listbox.bind("<<ListboxSelect>>", on_nightly_select)

    def query_nightlies():
        nightly_status_var.set("Querying GitHub for nightly releases...")
        nightly_listbox.delete(0, "end")
        append_log("\nQuerying GitHub for yt-dlp nightly release list...\n")

        def worker():
            nonlocal nightly_releases

            try:
                releases = fetch_ytdlp_nightly_releases(limit=20)

                def update_ui():
                    nonlocal nightly_releases
                    nightly_releases = releases
                    nightly_listbox.delete(0, "end")

                    for item in nightly_releases:
                        nightly_listbox.insert("end", item["display"])

                    nightly_status_var.set(f"Loaded {len(nightly_releases)} nightly release(s).")
                    append_log(f"Loaded {len(nightly_releases)} yt-dlp nightly release(s) from GitHub.\n")

                    if nightly_releases:
                        nightly_listbox.selection_set(0)
                        nightly_listbox.activate(0)
                        on_nightly_select()

                root.after(0, update_ui)

            except Exception as e:
                root.after(0, nightly_status_var.set, "Failed to query GitHub nightlies.")
                root.after(0, append_log, f"Failed to query yt-dlp nightly releases from GitHub: {e}\n")
                root.after(0, messagebox.showerror, "Nightly query failed", str(e))

        threading.Thread(target=worker, daemon=True).start()

    def get_update_target():
        mode = update_mode_var.get()

        if mode == "stable":
            return "stable"

        if mode == "nightly":
            return "nightly"

        selection = nightly_listbox.curselection()
        if not selection:
            raise ValueError("Select a nightly release from the list first.")

        index = selection[0]
        if index >= len(nightly_releases):
            raise ValueError("Selected nightly is invalid. Query the nightly list again.")

        return f"nightly@{nightly_releases[index]['tag']}"

    def begin_update():
        try:
            target = get_update_target()
        except Exception as e:
            messagebox.showerror("Update target missing", str(e))
            return

        confirm = messagebox.askyesno(
            "Update yt-dlp?",
            f"This will run yt-dlp's built-in updater directly:\n\n"
            f"{yt_dlp_path} --update-to {target}\n\n"
            f"{current_version_var.get()}\n\n"
            "Very recent nightlies may be blocked by ASR or endpoint protection.\n\n"
            "Continue?",
        )

        if not confirm:
            return

        dialog.destroy()
        update_ytdlp_direct(target)

    ttk.Button(button_frame, text="Update yt-dlp", command=begin_update).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=6)

    refresh_current_version_for_dialog()



def update_ytdlp_direct(update_target):
    yt_dlp_path = yt_dlp_path_var.get().strip()

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        yt_dlp_version_status_var.set("yt-dlp: not found")
        messagebox.showerror("yt-dlp not found", "yt-dlp path is missing or invalid.")
        return

    append_log(
        "\nStarting direct yt-dlp update...\n"
        f"yt-dlp path: {yt_dlp_path}\n"
        f"Update target: {update_target}\n"
        "Command source: GUI direct subprocess, not the PowerShell capture script.\n\n"
    )

    yt_dlp_version_status_var.set(f"yt-dlp: updating to {update_target}...")
    set_status("Updating yt-dlp...")

    def worker():
        try:
            result = subprocess.Popen(
                [yt_dlp_path, "--update-to", update_target],
                cwd=os.path.dirname(os.path.abspath(yt_dlp_path)) or ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            if result.stdout:
                for line in result.stdout:
                    root.after(0, append_log, line)

            exit_code = result.wait()

            if exit_code == 0:
                root.after(0, append_log, f"\nyt-dlp update completed successfully. Exit code: {exit_code}\n")
                root.after(0, set_status, "yt-dlp update complete")
                root.after(0, messagebox.showinfo, "yt-dlp updated", "yt-dlp update completed successfully.")
                root.after(0, check_ytdlp_version)
            else:
                root.after(0, append_log, f"\nyt-dlp update failed. Exit code: {exit_code}\n")
                root.after(0, set_status, f"yt-dlp update failed with exit code {exit_code}")
                root.after(
                    0,
                    messagebox.showwarning,
                    "yt-dlp update failed",
                    f"yt-dlp exited with code {exit_code}. Review the output log. "
                    "If this was a recent nightly, ASR or endpoint protection may have blocked it.",
                )
                root.after(0, check_ytdlp_version)

        except Exception as e:
            root.after(0, set_status, "yt-dlp update error")
            root.after(0, yt_dlp_version_status_var.set, "yt-dlp: update error")
            root.after(0, append_log, f"\nyt-dlp update error: {e}\n")
            root.after(0, messagebox.showerror, "yt-dlp update error", str(e))

    threading.Thread(target=worker, daemon=True).start()




def update_deno_direct():
    deno_path = resolve_deno_executable_for_gui()
    deno_from_path = shutil.which("deno.exe") or shutil.which("deno")
    deno_resolved = deno_path

    if deno_path == "deno" and deno_from_path:
        deno_resolved = deno_from_path

    if not deno_resolved or (deno_resolved == "deno" and not deno_from_path):
        messagebox.showerror(
            "Deno not found",
            "Deno was not found beside the app or in PATH. Place deno.exe beside the app, beside yt-dlp when required, or make it available in PATH.",
        )
        return

    confirm = messagebox.askyesno(
        "Update Deno?",
        "This will run Deno's built-in updater:\n\n"
        f"{deno_resolved} upgrade\n\n"
        "The latest Deno version may be incompatible with the current yt-dlp workflow or may be blocked by ASR/endpoint protection because it changes a local executable.\n\n"
        "Continue?",
    )

    if not confirm:
        return

    append_log(
        "\nStarting Deno update...\n"
        f"Deno path: {deno_resolved}\n"
        "Command source: GUI direct subprocess, not the PowerShell capture script.\n\n"
    )
    set_status("Updating Deno...")

    def worker():
        try:
            cwd = os.path.dirname(os.path.abspath(deno_resolved)) if os.path.isfile(deno_resolved) else ROOT
            result = subprocess.Popen(
                [deno_resolved, "upgrade"],
                cwd=cwd or ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            if result.stdout:
                for line in result.stdout:
                    root.after(0, append_log, line)

            exit_code = result.wait()

            if exit_code == 0:
                root.after(0, append_log, f"\nDeno update completed successfully. Exit code: {exit_code}\n")
                root.after(0, set_status, "Deno update complete")
                root.after(0, messagebox.showinfo, "Deno updated", "Deno update completed successfully.")
            else:
                root.after(0, append_log, f"\nDeno update failed. Exit code: {exit_code}\n")
                root.after(0, set_status, f"Deno update failed with exit code {exit_code}")
                root.after(
                    0,
                    messagebox.showwarning,
                    "Deno update failed",
                    f"Deno exited with code {exit_code}. Review the output log. "
                    "The update may have been blocked by ASR or endpoint protection.",
                )

        except Exception as e:
            root.after(0, set_status, "Deno update error")
            root.after(0, append_log, f"\nDeno update error: {e}\n")
            root.after(0, messagebox.showerror, "Deno update error", str(e))

    threading.Thread(target=worker, daemon=True).start()



def extract_json_object_from_stdout(stdout_text):
    stdout_text = str(stdout_text or "").strip()

    if not stdout_text:
        raise ValueError("yt-dlp returned no JSON output.")

    try:
        return json.loads(stdout_text)
    except Exception:
        pass

    first = stdout_text.find("{")
    last = stdout_text.rfind("}")

    if first >= 0 and last > first:
        return json.loads(stdout_text[first:last + 1])

    raise ValueError("yt-dlp output did not contain a JSON object.")


def format_preview_duration(value):
    try:
        seconds = int(float(value))
    except Exception:
        return ""

    if seconds < 0:
        return ""

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes}:{seconds:02d}"


def get_playlist_entry_url(entry, playlist_info=None):
    entry = entry if isinstance(entry, dict) else {}
    playlist_info = playlist_info if isinstance(playlist_info, dict) else {}

    for key in ("webpage_url", "original_url", "url"):
        value = str(entry.get(key) or "").strip()
        if value.startswith(("http://", "https://")):
            return value

    entry_id = str(entry.get("id") or "").strip()
    extractor_key = str(entry.get("extractor_key") or playlist_info.get("extractor_key") or "").lower()
    extractor = str(entry.get("extractor") or playlist_info.get("extractor") or "").lower()

    if entry_id and ("youtube" in extractor_key or "youtube" in extractor):
        return f"https://www.youtube.com/watch?v={entry_id}"

    return str(entry.get("url") or "").strip()


def collapse_playlist_indexes(values):
    clean = sorted({
        int(value)
        for value in values
        if str(value).strip().lstrip("-").isdigit() and int(value) > 0
    })

    if not clean:
        return ""

    ranges = []
    start = previous = clean[0]

    for value in clean[1:]:
        if value == previous + 1:
            previous = value
            continue

        ranges.append(f"{start}:{previous}" if start != previous else str(start))
        start = previous = value

    ranges.append(f"{start}:{previous}" if start != previous else str(start))
    return ",".join(ranges)


def get_preview_candidate_urls():
    source_text = get_current_url_source_text()

    if not source_text.strip():
        return []

    analysis = analyze_url_source_text(source_text)
    seen = set()
    urls = []

    for url in analysis.get("valid_urls", []):
        normalized = normalize_url_for_compare(url)
        if normalized in seen:
            continue
        seen.add(normalized)
        urls.append(url)

    return urls


def refresh_playlist_preview_candidate_cache():
    global playlist_preview_candidate_urls, playlist_preview_source_signature

    try:
        urls = get_preview_candidate_urls()
    except Exception:
        urls = []

    signature = "\n".join(urls)
    changed = signature != playlist_preview_source_signature

    playlist_preview_candidate_urls = urls
    playlist_preview_source_signature = signature

    return changed


def show_playlist_preview_placeholder(message=None):
    global playlist_preview_tab_loaded, playlist_preview_loaded_signature

    try:
        tab = playlist_preview_tab
    except NameError:
        return

    for child in tab.winfo_children():
        try:
            child.destroy()
        except Exception:
            pass

    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(0, weight=1)

    frame = ttk.Frame(tab, padding=16)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    content = ttk.Frame(frame)
    content.grid(row=0, column=0)

    ttk.Label(
        content,
        text=message or "URL Preview is waiting for URL box or Input File(s) URLs.",
        anchor="center",
        justify="center",
    ).pack(pady=(0, 8))

    ttk.Button(
        content,
        text="Refresh URL Preview",
        command=lambda: open_playlist_preview_dialog(silent=False, force_reload=True),
    ).pack()

    playlist_preview_tab_loaded = False
    playlist_preview_loaded_signature = ""


def playlist_preview_tab_is_selected():
    try:
        return app_notebook.select() == str(playlist_preview_tab)
    except Exception:
        return False


def schedule_playlist_preview_autoload(delay_ms=400):
    global playlist_preview_reload_after_id

    try:
        if playlist_preview_reload_after_id:
            root.after_cancel(playlist_preview_reload_after_id)
    except Exception:
        pass

    def do_refresh():
        global playlist_preview_reload_after_id, playlist_preview_tab_loaded
        playlist_preview_reload_after_id = None

        changed = refresh_playlist_preview_candidate_cache()

        if changed:
            playlist_preview_tab_loaded = False

        if playlist_preview_tab_is_selected():
            try:
                open_playlist_preview_dialog(silent=True, force_reload=changed)
            except Exception as e:
                try:
                    append_log(f"\nURL Preview auto-load failed: {e}\n")
                except Exception:
                    pass

    try:
        playlist_preview_reload_after_id = root.after(delay_ms, do_refresh)
    except Exception:
        playlist_preview_reload_after_id = None


def handle_playlist_preview_source_changed(event=None):
    try:
        if event is not None and hasattr(event, "widget") and hasattr(event.widget, "edit_modified"):
            if not event.widget.edit_modified():
                return
            event.widget.edit_modified(False)
    except Exception:
        pass

    schedule_playlist_preview_autoload()


def on_notebook_tab_changed(event=None):
    if playlist_preview_tab_is_selected():
        try:
            open_playlist_preview_dialog(silent=True)
        except Exception as e:
            try:
                append_log(f"\nURL Preview tab load failed: {e}\n")
            except Exception:
                pass


def build_playlist_preview_command(url):
    yt_dlp_path = yt_dlp_path_var.get().strip()

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        raise ValueError("yt-dlp path is missing or invalid.")

    cmd = [
        yt_dlp_path,
        "--flat-playlist",
        "--dump-single-json",
        "--no-warnings",
        "--no-progress",
        "--js-runtimes",
        f"deno:{resolve_deno_executable_for_gui()}",
        "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "--add-header",
        "Accept-Language: en-US,en;q=0.9",
    ]

    cookies_file = cookies_file_var.get().strip()
    if use_cookies_file_var.get() and cookies_file:
        cmd += ["--cookies", cookies_file]

    proxy_url = get_proxy_url_for_command()
    if proxy_url:
        cmd += ["--proxy", proxy_url]

    impersonate_target = normalize_impersonate_target(impersonate_var.get())
    if impersonate_target:
        cmd += ["--impersonate", impersonate_target]

    cmd.append(url)
    return cmd



def open_playlist_preview_dialog(silent=False, force_reload=False):
    global playlist_preview_tab_loaded, playlist_preview_loaded_signature

    changed = refresh_playlist_preview_candidate_cache()
    urls = list(playlist_preview_candidate_urls)
    has_preview_urls = bool(urls)
    no_urls_message = (
        "URL Preview is waiting for URL box or Input File(s) URLs."
        if silent else
        "No valid URL text or input file contents were found to preview."
    )

    try:
        dialog = playlist_preview_tab
        if has_preview_urls or not silent:
            app_notebook.select(dialog)
    except NameError:
        if not silent:
            messagebox.showerror("URL Preview unavailable", "URL Preview tab is not available.")
        return

    if playlist_preview_tab_loaded and not force_reload and not changed and playlist_preview_loaded_signature == playlist_preview_source_signature:
        return

    for child in dialog.winfo_children():
        try:
            child.destroy()
        except Exception:
            pass

    dialog.columnconfigure(0, weight=1)
    for row_index in range(0, 9):
        try:
            dialog.rowconfigure(row_index, weight=0)
        except Exception:
            pass
    dialog.rowconfigure(2, weight=2)
    dialog.rowconfigure(3, weight=3)

    stop_event = threading.Event()
    scan_running = {"value": False}
    thumbnail_token = {"value": 0}
    thumbnail_image_holder = {"image": None}
    current_detail_record = {"record": None}
    thumbnail_state_lock = threading.Lock()
    thumbnail_state = {
        "desired_key": "",
        "desired_record": None,
        "worker_running": False,
        # Cooldowns are post-fetch timers. A new thumbnail fetch starts immediately
        # when the relevant timer has already expired; after a real fetch attempt
        # completes, the next-allowed time is moved forward.
        "next_allowed": {"fast": 0.0, "ytdlp": 0.0},
    }

    url_records = [
        {
            "iid": f"url-{index}",
            "number": index,
            "preview": True,
            "include": True,
            "status": "Ready",
            "kind": "Unknown",
            "title": "",
            "uploader": "",
            "duration": "",
            "items": "",
            "thumbnail_status": "Not fetched",
            "thumbnail_url": "",
            "thumbnail_cache_path": "",
            "thumbnail_error": "",
            "url": url,
            "json": {},
            "entries": [],
            "error": "",
        }
        for index, url in enumerate(urls, start=1)
    ]
    url_by_iid = {record["iid"]: record for record in url_records}
    entry_by_iid = {}

    status_var = tk.StringVar(value=(
        f"Loaded {len(urls)} URL(s). Use Preview All/Checked to gather metadata."
        if has_preview_urls else
        f"{no_urls_message} Add URLs in the URL box or select Input File(s) to enable URL Preview."
    ))
    context_title_var = tk.StringVar(value="Select a URL row to view details.")
    thumbnail_status_var = tk.StringVar(value="")
    url_filter_var = tk.StringVar(value="")
    entry_filter_var = tk.StringVar(value="")
    url_count_var = tk.StringVar(value="URLs: 0 shown / 0 total")
    entry_count_var = tk.StringVar(value="Items: 0 shown / 0 total")
    pacing_var = url_preview_pacing_var
    thumbnail_mode_var = url_preview_thumbnail_mode_var
    rate_limit_thumbnails_var = url_preview_rate_limit_thumbnails_var
    cache_mode_var = url_preview_cache_mode_var
    playlist_mode_var = url_preview_playlist_mode_var
    max_playlist_items_var = url_preview_max_playlist_items_var
    timeout_var = url_preview_timeout_var
    options_visible = {"value": False}

    preview_pacing_options = URL_PREVIEW_PACING_OPTIONS
    thumbnail_mode_options = URL_PREVIEW_THUMBNAIL_MODE_OPTIONS
    cache_mode_options = URL_PREVIEW_CACHE_MODE_OPTIONS
    playlist_mode_options = URL_PREVIEW_PLAYLIST_MODE_OPTIONS

    def bool_mark(value):
        return "☑" if bool(value) else "☐"

    def short_text(value, limit=160):
        value = str(value or "").replace("\r", " ").replace("\n", " ").strip()
        return value if len(value) <= limit else value[:limit - 1] + "…"

    def split_filter_terms(value):
        return [term.casefold() for term in re.split(r"\s+", str(value or "").strip()) if term]

    def filter_terms_match(text_value, terms):
        if not terms:
            return True
        haystack = str(text_value or "").casefold()
        return all(term in haystack for term in terms)

    def url_record_filter_text(record):
        record = record or {}
        data = record.get("json") if isinstance(record.get("json"), dict) else {}
        fields = [
            record.get("status", ""), record.get("kind", ""), record.get("title", ""),
            record.get("uploader", ""), record.get("duration", ""), record.get("items", ""),
            record.get("thumbnail_status", ""), record.get("thumbnail_url", ""), record.get("url", ""),
            data.get("extractor", ""), data.get("extractor_key", ""), data.get("id", ""),
            data.get("playlist", ""), data.get("playlist_title", ""), data.get("playlist_id", ""),
        ]
        return " ".join(str(field or "") for field in fields)

    def entry_record_filter_text(entry):
        entry = entry or {}
        data = entry.get("json") if isinstance(entry.get("json"), dict) else {}
        fields = [
            entry.get("index", ""), entry.get("status", ""), entry.get("title", ""),
            entry.get("uploader", ""), entry.get("duration", ""), entry.get("thumbnail_status", ""),
            entry.get("thumbnail_url", ""), entry.get("url", ""), data.get("extractor", ""),
            data.get("extractor_key", ""), data.get("id", ""), data.get("playlist", ""),
            data.get("playlist_title", ""), data.get("playlist_id", ""),
        ]
        return " ".join(str(field or "") for field in fields)

    def url_record_matches_filter(record):
        return filter_terms_match(url_record_filter_text(record), split_filter_terms(url_filter_var.get()))

    def entry_record_matches_filter(entry):
        return filter_terms_match(entry_record_filter_text(entry), split_filter_terms(entry_filter_var.get()))

    def get_preview_timeout_seconds():
        try:
            return max(10, min(900, int(str(timeout_var.get()).strip())))
        except Exception:
            return 120

    def get_max_playlist_items():
        value = str(max_playlist_items_var.get() or "").strip().lower()
        if value in {"", "all", "0"}:
            return 0
        try:
            return max(1, min(5000, int(value)))
        except Exception:
            return 50

    def get_preview_pacing_seconds():
        return preview_pacing_options.get(pacing_var.get(), (0, 5))

    def sleep_before_next_preview_url(current_index, total_count):
        if stop_event.is_set() or current_index >= total_count:
            return

        base_delay, jitter_max = get_preview_pacing_seconds()
        jitter = random.uniform(0, jitter_max) if jitter_max > 0 else 0
        delay = max(0, float(base_delay) + jitter)

        if delay <= 0:
            return

        root.after(0, status_var.set, f"Waiting {delay:.1f}s before next preview URL...")
        append_log(f"URL preview pacing delay before next URL: {delay:.1f}s\n")

        end_time = time.time() + delay
        while time.time() < end_time:
            if stop_event.is_set():
                break
            time.sleep(min(0.25, max(0, end_time - time.time())))

    def detect_preview_backoff_reason(text):
        combined = str(text or "")
        lowered = combined.lower()
        backoff_terms = [
            "http error 429",
            "429 too many requests",
            "too many requests",
            "rate limit",
            "ratelimit",
            "rate-limit",
            "temporarily blocked",
            "try again later",
            "unusual traffic",
            "sign in to confirm",
            "confirm you are not a bot",
            "confirm you're not a bot",
            "captcha",
            "detected unusual",
            "temporarily unavailable due to",
        ]
        for term in backoff_terms:
            if term in lowered:
                return term
        if re.search(r"\b429\b", lowered):
            return "HTTP 429"
        return ""

    def show_preview_backoff_warning(url, reason):
        messagebox.showwarning(
            "Possible rate limit or challenge",
            "URL preview detected a possible rate limit, bot challenge, or temporary block. "
            "The scan was stopped so the source has time to recover.\n\n"
            f"Reason: {reason}\n\nURL:\n{url}",
            parent=dialog,
        )

    def output_root_for_preview_cache():
        root_value = output_root_var.get().strip() or ROOT
        return root_value

    def url_preview_temp_cache_folder_path():
        return os.path.join(output_root_for_preview_cache(), ".gui-cache", "url-preview-pending")

    def url_preview_persistent_cache_folder_path():
        return os.path.join(output_root_for_preview_cache(), ".gui-cache", "url-preview-persistent")

    def url_preview_temp_cache_folder():
        folder = url_preview_temp_cache_folder_path()
        os.makedirs(folder, exist_ok=True)
        return folder

    def url_preview_persistent_cache_folder():
        folder = url_preview_persistent_cache_folder_path()
        os.makedirs(folder, exist_ok=True)
        return folder

    def url_preview_cache_is_persistent():
        return normalize_url_preview_cache_mode(cache_mode_var.get()) == "Reuse cached thumbnails"

    def case_template_needs_playlist_for_preview():
        try:
            return "%playlist%" in str(case_name_var.get() or "").lower()
        except Exception:
            return False

    def resolved_preview_cache_folder_path(playlist_name=None):
        try:
            output_root = output_root_for_preview_cache()
            template = case_name_var.get().strip()
            if playlist_name:
                template = append_playlist_tag_to_case_template(template)
            rendered = render_case_name_template(template, playlist=playlist_name)
            case_name = safe_case_name(rendered)
            if not case_name:
                raise ValueError("blank resolved case name")
            case_folder = os.path.join(output_root, case_name)
            return os.path.join(case_folder, "manifests", ".gui-cache", "url-preview")
        except Exception:
            return url_preview_temp_cache_folder_path()

    def resolved_preview_cache_folder(playlist_name=None):
        folder = resolved_preview_cache_folder_path(playlist_name=playlist_name)
        os.makedirs(folder, exist_ok=True)
        return folder

    def preview_cache_folder(playlist_name=None):
        if url_preview_cache_is_persistent():
            return url_preview_persistent_cache_folder()
        # If the case template contains %playlist% but no playlist value is known yet,
        # use a temporary cache under the output root. It will be moved/copied into
        # the resolved case folder when a playlist-tagged Start/Queue action occurs.
        if case_template_needs_playlist_for_preview() and not str(playlist_name or "").strip():
            return url_preview_temp_cache_folder()
        return resolved_preview_cache_folder(playlist_name=playlist_name)

    def move_preview_cache_to_resolved_case_folder(playlist_name=None):
        if not str(playlist_name or "").strip() and case_template_needs_playlist_for_preview():
            return ""
        source = url_preview_temp_cache_folder()
        target = resolved_preview_cache_folder(playlist_name=playlist_name)
        if os.path.normcase(os.path.abspath(source)) == os.path.normcase(os.path.abspath(target)):
            return target
        if not os.path.isdir(source):
            return target
        try:
            os.makedirs(target, exist_ok=True)
            for name in os.listdir(source):
                src = os.path.join(source, name)
                dst = os.path.join(target, name)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                elif os.path.isfile(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
            source_abs = os.path.abspath(source)
            target_abs = os.path.abspath(target)
            def _rewrite_cache_path(record):
                try:
                    current = str((record or {}).get("thumbnail_cache_path") or "")
                    if current and os.path.abspath(current).startswith(source_abs):
                        record["thumbnail_cache_path"] = target_abs + os.path.abspath(current)[len(source_abs):]
                        update_preview_row(record)
                except Exception:
                    pass
            for preview_record in url_records:
                _rewrite_cache_path(preview_record)
                for preview_entry in preview_record.get("entries") or []:
                    _rewrite_cache_path(preview_entry)

            try:
                shutil.rmtree(source)
                root_cache = os.path.dirname(source)
                if os.path.isdir(root_cache) and not os.listdir(root_cache):
                    os.rmdir(root_cache)
                append_log(f"URL Preview cache copied into resolved case cache and pending cache was cleared: {target}\n")
            except Exception as cleanup_error:
                append_log(f"URL Preview cache copied into resolved case cache, but pending cache cleanup failed: {cleanup_error}\n")
        except Exception as e:
            append_log(f"WARNING: Could not move URL Preview cache into resolved case folder: {e}\n")
        return target

    def clear_url_preview_cache():
        targets = [
            url_preview_temp_cache_folder_path(),
            url_preview_persistent_cache_folder_path(),
            resolved_preview_cache_folder_path(),
        ]

        try:
            playlist_names = set()
            for record in url_records:
                try:
                    playlist_name = playlist_name_for_record(record)
                except Exception:
                    playlist_name = ""
                if playlist_name:
                    playlist_names.add(playlist_name)
            for playlist_name in sorted(playlist_names):
                targets.append(resolved_preview_cache_folder_path(playlist_name=playlist_name))
        except Exception:
            pass

        unique_targets = []
        seen = set()
        for target in targets:
            if not target:
                continue
            try:
                key = os.path.normcase(os.path.abspath(target))
            except Exception:
                key = target
            if key in seen:
                continue
            seen.add(key)
            unique_targets.append(target)

        existing_targets = [target for target in unique_targets if os.path.isdir(target)]
        if not existing_targets:
            messagebox.showinfo("Clear URL Preview Cache", "No URL Preview cache folders were found for the current Output Root/case context.", parent=dialog)
            return

        if not messagebox.askyesno(
            "Clear URL Preview Cache",
            "Clear URL Preview thumbnail/cache folders for the current Output Root and resolved case context?\n\n"
            "This removes only GUI cache folders, not captured media or case manifests.",
            parent=dialog,
        ):
            return

        removed = 0
        failed = []
        for target in existing_targets:
            try:
                shutil.rmtree(target)
                removed += 1
            except Exception as e:
                failed.append(f"{target}: {e}")

        def reset_thumbnail_record(record):
            if not isinstance(record, dict):
                return
            record["thumbnail_cache_path"] = ""
            record["thumbnail_error"] = ""
            if str(record.get("thumbnail_url") or "").strip():
                record["thumbnail_status"] = "URL"
            else:
                record["thumbnail_status"] = "Missing"
            update_preview_row(record)

        for record in url_records:
            reset_thumbnail_record(record)
            for entry in list(record.get("entries") or []):
                reset_thumbnail_record(entry)

        with thumbnail_state_lock:
            thumbnail_state["desired_key"] = ""
            thumbnail_state["desired_record"] = None

        clear_thumbnail("URL Preview cache cleared")
        set_details_text(format_record_details(current_detail_record.get("record")))
        populate_url_tree()
        populate_entry_tree(current_url_record())

        if failed:
            detail = "\n".join(failed[:6])
            messagebox.showwarning("Clear URL Preview Cache", f"Cleared {removed} cache folder(s), but some folders could not be removed:\n\n{detail}", parent=dialog)
        else:
            messagebox.showinfo("Clear URL Preview Cache", f"Cleared {removed} URL Preview cache folder(s).", parent=dialog)
        status_var.set(f"Cleared {removed} URL Preview cache folder(s).")

    def choose_thumbnail_url(info):
        info = info if isinstance(info, dict) else {}
        direct = str(info.get("thumbnail") or "").strip()
        if direct.startswith(("http://", "https://")):
            return direct

        thumbnails = info.get("thumbnails") or []
        if not isinstance(thumbnails, list):
            return ""

        candidates = []
        for thumb in thumbnails:
            if not isinstance(thumb, dict):
                continue
            url = str(thumb.get("url") or "").strip()
            if not url.startswith(("http://", "https://")):
                continue
            try:
                preference = int(thumb.get("preference") or 0)
            except Exception:
                preference = 0
            try:
                area = int(thumb.get("width") or 0) * int(thumb.get("height") or 0)
            except Exception:
                area = 0
            candidates.append((preference, area, url))

        if not candidates:
            return ""
        candidates.sort(reverse=True)
        return candidates[0][2]

    def safe_cache_name(value):
        return hashlib.sha256(str(value or "").encode("utf-8", errors="ignore")).hexdigest()[:32]

    def url_extension_for_cache(url, content_type=""):
        lowered_type = str(content_type or "").lower()
        if "png" in lowered_type:
            return ".png"
        if "webp" in lowered_type:
            return ".webp"
        if "gif" in lowered_type:
            return ".gif"
        if "jpeg" in lowered_type or "jpg" in lowered_type:
            return ".jpg"
        try:
            path = urlsplit(url).path.lower()
            for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"):
                if path.endswith(ext):
                    return ".jpg" if ext == ".jpeg" else ext
        except Exception:
            pass
        return ".img"

    def convert_thumbnail_to_png(source_path, png_path):
        if os.path.isfile(png_path):
            return png_path

        ffmpeg_exe = get_ffmpeg_executable_for_gui()
        if not ffmpeg_exe or not os.path.isfile(ffmpeg_exe):
            ext = os.path.splitext(source_path)[1].lower()
            if ext == ".png":
                shutil.copy2(source_path, png_path)
                return png_path
            raise ValueError("ffmpeg.exe is not configured; thumbnail conversion is unavailable.")

        cmd = [
            ffmpeg_exe,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            source_path,
            "-frames:v",
            "1",
            "-vf",
            "scale=260:-1",
            png_path,
        ]
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(ffmpeg_exe)) or ROOT, capture_output=True, text=True, timeout=45)
        if result.returncode != 0 or not os.path.isfile(png_path):
            detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
            raise ValueError(f"ffmpeg thumbnail conversion failed: {detail}")
        return png_path

    def fetch_thumbnail_fast(record):
        thumb_url = str(record.get("thumbnail_url") or "").strip()
        if not thumb_url:
            raise ValueError("No thumbnail URL was available in metadata.")

        folder = preview_cache_folder()
        base = safe_cache_name(thumb_url)
        png_path = os.path.join(folder, f"{base}.png")
        if os.path.isfile(png_path):
            return png_path

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }
        source_url = str(record.get("url") or record.get("source_url") or "").strip()
        if source_url.startswith(("http://", "https://")):
            headers["Referer"] = source_url

        req = urllib.request.Request(thumb_url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in str(content_type).lower():
                raise ValueError("Thumbnail request returned HTML instead of an image.")
            data = response.read(8 * 1024 * 1024)
            if not data:
                raise ValueError("Thumbnail request returned no data.")

        raw_ext = url_extension_for_cache(thumb_url, content_type)
        raw_path = os.path.join(folder, f"{base}{raw_ext}")
        with open(raw_path, "wb") as f:
            f.write(data)

        return convert_thumbnail_to_png(raw_path, png_path)

    def build_ytdlp_common_metadata_args(url, include_playlist_mode=True):
        yt_dlp_path = yt_dlp_path_var.get().strip()
        if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
            raise ValueError("yt-dlp path is missing or invalid.")

        cmd = [
            yt_dlp_path,
            "--dump-single-json",
            "--skip-download",
            "--ignore-no-formats-error",
            "--no-warnings",
            "--no-progress",
            "--js-runtimes",
            f"deno:{resolve_deno_executable_for_gui()}",
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "--add-header",
            "Accept-Language: en-US,en;q=0.9",
        ]

        if include_playlist_mode:
            max_items = get_max_playlist_items()
            if playlist_mode_var.get() == "Fast playlist scan":
                cmd.append("--flat-playlist")
            elif max_items:
                cmd += ["--playlist-items", f"1:{max_items}"]

        cookies_file = cookies_file_var.get().strip()
        if use_cookies_file_var.get() and cookies_file:
            cmd += ["--cookies", cookies_file]

        proxy_url = get_proxy_url_for_command()
        if proxy_url:
            cmd += ["--proxy", proxy_url]

        impersonate_target = normalize_impersonate_target(impersonate_var.get())
        if impersonate_target:
            cmd += ["--impersonate", impersonate_target]

        cmd.append(url)
        return cmd

    def fetch_thumbnail_ytdlp(record):
        source_url = str(record.get("url") or record.get("source_url") or "").strip()
        if not source_url:
            raise ValueError("No source URL is available for yt-dlp thumbnail fallback.")

        folder = os.path.join(preview_cache_folder(), safe_cache_name(source_url))
        os.makedirs(folder, exist_ok=True)
        png_path = os.path.join(folder, "thumb.png")
        if os.path.isfile(png_path):
            return png_path

        cmd = build_ytdlp_common_metadata_args(source_url, include_playlist_mode=False)
        # Replace JSON-only flags with thumbnail-write flags while preserving cookies/proxy/impersonation/header args.
        cleaned = []
        skip_next = False
        for index, item in enumerate(cmd[:-1]):
            if skip_next:
                skip_next = False
                continue
            if item in {"--dump-single-json", "--ignore-no-formats-error"}:
                continue
            cleaned.append(item)
        cmd = cleaned + [
            "--write-thumbnail",
            "--convert-thumbnails",
            "png",
            "-o",
            os.path.join(folder, "thumb.%(ext)s"),
            source_url,
        ]

        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(yt_dlp_path_var.get().strip())) or ROOT,
            capture_output=True,
            text=True,
            timeout=get_preview_timeout_seconds(),
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
            raise ValueError(f"yt-dlp thumbnail fallback failed: {detail}")

        if os.path.isfile(png_path):
            return png_path

        candidates = []
        for name in os.listdir(folder):
            lowered = name.lower()
            if lowered.startswith("thumb.") and lowered.rsplit(".", 1)[-1] in {"png", "jpg", "jpeg", "webp", "gif", "avif"}:
                candidates.append(os.path.join(folder, name))
        if not candidates:
            raise ValueError("yt-dlp thumbnail fallback did not create a thumbnail file.")

        candidates.sort(key=lambda path: os.path.getmtime(path), reverse=True)
        return convert_thumbnail_to_png(candidates[0], png_path)

    def fetch_thumbnail_hybrid(record):
        mode = thumbnail_mode_var.get()
        if mode == "Off":
            return ""

        errors = []
        try:
            return fetch_thumbnail_fast(record)
        except Exception as e:
            errors.append(str(e))

        if mode == "Reliable":
            try:
                return fetch_thumbnail_ytdlp(record)
            except Exception as e:
                errors.append(str(e))

        raise ValueError("; ".join(error for error in errors if error) or "thumbnail fetch failed")

    def update_url_tree_row(iid):
        try:
            record = url_by_iid.get(iid)
            if not record:
                return
            if not url_record_matches_filter(record):
                if url_tree.exists(iid):
                    url_tree.delete(iid)
                return
            if not url_tree.exists(iid):
                url_tree.insert("", "end", iid=iid, values=("", "", "", "", "", "", "", "", "", "", ""))
            url_tree.item(
                iid,
                values=(
                    bool_mark(record.get("preview")),
                    bool_mark(record.get("include")),
                    record.get("number", ""),
                    record.get("status", ""),
                    record.get("kind", ""),
                    short_text(record.get("title", ""), 90),
                    short_text(record.get("uploader", ""), 55),
                    record.get("duration", ""),
                    record.get("items", ""),
                    record.get("thumbnail_status", ""),
                    record.get("url", ""),
                ),
            )
        except Exception:
            pass

    def update_entry_tree_row(iid):
        try:
            entry = entry_by_iid.get(iid)
            if not entry:
                return
            if not entry_record_matches_filter(entry):
                if entry_tree.exists(iid):
                    entry_tree.delete(iid)
                return
            if not entry_tree.exists(iid):
                entry_tree.insert("", "end", iid=iid, values=("", "", "", "", "", "", "", ""))
            entry_tree.item(
                iid,
                values=(
                    bool_mark(entry.get("include")),
                    entry.get("index", ""),
                    entry.get("status", ""),
                    short_text(entry.get("title", ""), 90),
                    entry.get("duration", ""),
                    entry.get("thumbnail_status", ""),
                    "yes" if entry.get("json") else "",
                    entry.get("url", ""),
                ),
            )
        except Exception:
            pass

    def update_preview_row(record):
        try:
            iid = str((record or {}).get("iid") or "")
            if iid in url_by_iid:
                update_url_tree_row(iid)
            elif iid in entry_by_iid:
                update_entry_tree_row(iid)
        except Exception:
            pass

    def set_record_status(record, status):
        record["status"] = status
        update_url_tree_row(record.get("iid", ""))

    def clear_tree_selection(tree):
        try:
            tree.selection_remove(tree.selection())
            tree.focus("")
        except Exception:
            pass

    def selected_url_records():
        return [url_by_iid[iid] for iid in url_tree.selection() if iid in url_by_iid]

    def current_url_record():
        selected = selected_url_records()
        return selected[0] if selected else None

    def selected_entry_records():
        return [entry_by_iid[iid] for iid in entry_tree.selection() if iid in entry_by_iid]

    def included_entry_records():
        return current_playlist_entries(included_only=True, selected_only=False)

    def unique_valid_top_records(records, require_key=None):
        records_to_use = []
        seen = set()
        for record in records or []:
            if require_key and not record.get(require_key):
                continue
            url = clean_extracted_url(record.get("url", ""))
            if not url_shape_is_valid(url):
                continue
            normalized = normalize_url_for_compare(url)
            if normalized in seen:
                continue
            seen.add(normalized)
            records_to_use.append(record)
        return records_to_use

    def preview_checked_top_records():
        return unique_valid_top_records(url_records, require_key="preview")

    def include_checked_top_records():
        return unique_valid_top_records(url_records, require_key="include")

    def all_top_records():
        return unique_valid_top_records(url_records)

    def visible_top_records():
        return unique_valid_top_records([record for record in url_records if url_record_matches_filter(record)])

    def top_all_action_records():
        return visible_top_records() if url_filter_is_active() else all_top_records()

    def top_records_for_start_or_queue(selected_only=False):
        return include_checked_top_records() if selected_only else top_all_action_records()

    def included_top_records(selected_only=False):
        return top_records_for_start_or_queue(selected_only)

    def included_top_urls(selected_only=False):
        return [clean_extracted_url(record.get("url", "")) for record in included_top_records(selected_only)]

    def record_has_playlist_data(record):
        record = record or {}
        data = record.get("json") if isinstance(record.get("json"), dict) else {}
        kind = str(record.get("kind") or data.get("_type") or data.get("extractor_key") or data.get("extractor") or "").lower()
        if record.get("entries"):
            return True
        if data.get("entries"):
            return True
        if data.get("_type") == "playlist":
            return True
        if data.get("playlist_count") or data.get("n_entries"):
            return True
        return any(token in kind for token in ("playlist", "channel", "tab", "search", "collection"))

    def playlist_name_for_record(record):
        if not record_has_playlist_data(record):
            return ""
        data = record.get("json") if isinstance((record or {}).get("json"), dict) else {}
        return str(
            record.get("title")
            or data.get("playlist_title")
            or data.get("playlist")
            or data.get("title")
            or record.get("id")
            or record.get("url")
            or "preview"
        ).strip()

    def playlist_name_for_records(records):
        records = [record for record in records or [] if record]
        if len(records) != 1:
            return ""
        return playlist_name_for_record(records[0])

    def current_playlist_entries(included_only=True, selected_only=False, visible_only=False):
        record = current_url_record()
        entries = list((record or {}).get("entries", []))
        if selected_only:
            selected_ids = {id(entry) for entry in selected_entry_records()}
            entries = [entry for entry in entries if id(entry) in selected_ids]
        if visible_only:
            entries = [entry for entry in entries if entry_record_matches_filter(entry)]
        if included_only:
            entries = [entry for entry in entries if entry.get("include")]
        return entries

    def url_filter_is_active():
        return bool(str(url_filter_var.get() or "").strip())

    def entry_filter_is_active():
        return bool(str(entry_filter_var.get() or "").strip())

    def urls_from_entries(entries):
        urls_to_use = []
        seen = set()
        for entry in entries or []:
            url = clean_extracted_url(entry.get("url", ""))
            if not url_shape_is_valid(url):
                continue
            normalized = normalize_url_for_compare(url)
            if normalized in seen:
                continue
            seen.add(normalized)
            urls_to_use.append(url)
        return urls_to_use

    def playlist_item_urls_for_top_record(record):
        """Return all usable previewed playlist/context item URLs for a top-level URL row.

        Top-level URL Preview Start/Queue actions should mirror the bottom
        playlist/context item list's All Items behavior once playlist metadata is
        confirmed. That means confirmed playlist rows are expanded to their
        extracted item URLs instead of queueing/capturing only the source URL.
        """
        if not record_has_playlist_data(record):
            return []
        entries = list((record or {}).get("entries") or [])
        return urls_from_entries(entries)

    def top_record_capture_payload(record):
        record = record or {}
        playlist_name = playlist_name_for_record(record)
        playlist_urls = playlist_item_urls_for_top_record(record)
        if playlist_urls:
            return playlist_urls, playlist_name, "playlist/context item URL(s)"
        url = clean_extracted_url(record.get("url", ""))
        if not url_shape_is_valid(url):
            return [], "", "top-level URL"
        return [url], playlist_name, "top-level URL"

    def top_records_capture_payload(records):
        urls_to_use = []
        seen = set()
        playlist_names = []
        expanded_count = 0
        source_count = 0
        for record in records or []:
            record_urls, playlist_name, payload_type = top_record_capture_payload(record)
            if not record_urls:
                continue
            if playlist_name and playlist_name not in playlist_names:
                playlist_names.append(playlist_name)
            if payload_type.startswith("playlist"):
                expanded_count += 1
            else:
                source_count += 1
            for url in record_urls:
                normalized = normalize_url_for_compare(url)
                if normalized in seen:
                    continue
                seen.add(normalized)
                urls_to_use.append(url)
        playlist_name = playlist_names[0] if len(playlist_names) == 1 else ""
        return urls_to_use, playlist_name, expanded_count, source_count

    def copy_text_to_clipboard(text_value, description):
        text_value = str(text_value or "").strip()
        if not text_value:
            messagebox.showwarning("Nothing to copy", f"No {description} were available to copy.", parent=dialog)
            return
        root.clipboard_clear()
        root.clipboard_append(text_value)
        root.update()
        append_log(f"\nCopied {description} to clipboard.\n")

    def copy_selected_preview_urls():
        urls_to_copy = [record.get("url", "") for record in selected_url_records() if record.get("url")]
        copy_text_to_clipboard("\n".join(urls_to_copy), "selected URL(s)")

    def copy_selected_record_json():
        record = highlighted_url_record() or current_url_record()
        if not record or not record.get("json"):
            messagebox.showwarning("No JSON", "Right-click or select a previewed URL row first.", parent=dialog)
            return
        copy_text_to_clipboard(json.dumps(record.get("json"), indent=2, ensure_ascii=False), "highlighted URL JSON")

    def export_record_json(record, description):
        if not record or not record.get("json"):
            messagebox.showwarning("No JSON", f"No JSON is available for the {description}.", parent=dialog)
            return
        safe_title = safe_case_name(record.get("title") or record.get("id") or description or "url-preview")[:80] or "url-preview"
        initial_file = f"{safe_title}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            title=f"Export {description} JSON",
            defaultextension=".json",
            initialdir=preview_cache_folder(playlist_name=playlist_name_for_record(record) if record_has_playlist_data(record) else None),
            initialfile=initial_file,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=dialog,
        )
        if not path:
            return
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            payload = {
                "app": APP_TITLE,
                "app_version": APP_VERSION,
                "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": description,
                "url": record.get("url") or record.get("source_url") or "",
                "title": record.get("title", ""),
                "json": record.get("json") or {},
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.write("\n")
            append_log(f"\nExported highlighted URL Preview JSON: {path}\n")
            messagebox.showinfo("Export complete", f"Exported JSON to:\n\n{path}", parent=dialog)
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export JSON:\n\n{e}", parent=dialog)

    def export_highlighted_url_json():
        record, _url = highlighted_url_value()
        export_record_json(record, "highlighted URL")

    def export_highlighted_entry_json():
        entry, _url = highlighted_entry_value()
        export_record_json(entry, "highlighted playlist/context item")

    entry_context_iid = {"value": ""}

    def highlighted_entry_record():
        iid = str(entry_context_iid.get("value") or "")
        if iid in entry_by_iid:
            return entry_by_iid[iid]
        focused = str(entry_tree.focus() or "")
        if focused in entry_by_iid:
            return entry_by_iid[focused]
        selected = selected_entry_records()
        return selected[0] if selected else None

    def highlighted_entry_value():
        entry = highlighted_entry_record()
        url = clean_extracted_url((entry or {}).get("url", ""))
        return entry, url

    def copy_highlighted_entry_json():
        entry, _url = highlighted_entry_value()
        if not entry:
            messagebox.showwarning("No playlist item", "Right-click a playlist/context item row first.", parent=dialog)
            return
        copy_text_to_clipboard(json.dumps(entry.get("json") or {}, indent=2, ensure_ascii=False), "highlighted playlist item JSON")

    def open_highlighted_entry_url():
        entry, url = highlighted_entry_value()
        if not entry or not url_shape_is_valid(url):
            messagebox.showwarning("No item URL", "Right-click a playlist/context item row first.", parent=dialog)
            return
        try:
            webbrowser.open(url)
            append_log(f"\nOpened URL Preview playlist/context item URL: {url}\n")
        except Exception as e:
            messagebox.showerror("Open URL failed", str(e), parent=dialog)

    def start_highlighted_entry():
        entry, url = highlighted_entry_value()
        if not entry or not url_shape_is_valid(url):
            messagebox.showwarning("No item URL", "Right-click a playlist/context item row first.", parent=dialog)
            return
        start_urls_now([url], "highlighted playlist/context item URL", playlist_name=get_current_playlist_name())

    def queue_highlighted_entry():
        entry, url = highlighted_entry_value()
        if not entry or not url_shape_is_valid(url):
            messagebox.showwarning("No item URL", "Right-click a playlist/context item row first.", parent=dialog)
            return
        queue_urls([url], "highlighted playlist/context item URL", playlist_name=get_current_playlist_name())

    def toggle_highlighted_entry_include():
        iid = str(entry_context_iid.get("value") or entry_tree.focus() or "")
        if iid in entry_by_iid:
            toggle_entry_include(iid)

    def set_url_preview_flags(records, key, value):
        for record in records:
            record[key] = bool(value)
            update_url_tree_row(record.get("iid", ""))

    def set_all_url_preview_flags(key, value):
        set_url_preview_flags(url_records, key, value)

    def invert_url_preview_flags(key):
        for record in url_records:
            record[key] = not bool(record.get(key))
            update_url_tree_row(record.get("iid", ""))

    def set_selected_url_preview_flags(key, value):
        records = selected_url_records()
        if not records:
            messagebox.showwarning("No URL selection", "Select one or more URL rows first.", parent=dialog)
            return
        set_url_preview_flags(records, key, value)

    def toggle_url_flag(iid, key):
        record = url_by_iid.get(iid)
        if not record:
            return
        record[key] = not bool(record.get(key))
        update_url_tree_row(iid)

    def set_all_current_item_includes(value):
        for entry in current_playlist_entries(included_only=False):
            entry["include"] = bool(value)
        for iid in entry_tree.get_children():
            update_entry_tree_row(iid)

    def invert_current_item_includes():
        for entry in current_playlist_entries(included_only=False):
            entry["include"] = not bool(entry.get("include"))
        for iid in entry_tree.get_children():
            update_entry_tree_row(iid)

    def toggle_entry_include(iid):
        entry = entry_by_iid.get(iid)
        if not entry:
            return
        entry["include"] = not bool(entry.get("include"))
        update_entry_tree_row(iid)

    def start_urls_now(urls_to_start, description, playlist_name=None):
        if not urls_to_start:
            messagebox.showwarning("No URLs", f"No usable {description} are available to start.", parent=dialog)
            return
        if playlist_name:
            move_preview_cache_to_resolved_case_folder(playlist_name=playlist_name)
        set_url_box_urls(urls_to_start)
        set_url_preview_pending_playlist_name(playlist_name)
        append_log(f"\nURL Preview set URL box to {len(urls_to_start)} {description} and started capture.\n")
        if playlist_name:
            append_log(f"URL Preview playlist tag value: {playlist_name}\n")
        try:
            app_notebook.select(main)
        except Exception:
            pass
        start_capture()

    def queue_urls(urls_to_queue, description, playlist_name=None):
        if not urls_to_queue:
            messagebox.showwarning("No URLs", f"No usable {description} are available to queue.", parent=dialog)
            return
        if playlist_name:
            move_preview_cache_to_resolved_case_folder(playlist_name=playlist_name)
        if not job_queue_window_is_open():
            open_job_queue()
        if add_urls_to_queue_as_job(urls_to_queue, playlist_name=playlist_name):
            append_log(f"\nQueued {len(urls_to_queue)} {description} from URL Preview.\n")

    def playlist_name_for_any_record(records):
        for record in records or []:
            name = playlist_name_for_record(record)
            if name:
                return name
        return ""

    def start_top_urls(selected_only, description):
        records = included_top_records(selected_only)
        urls_to_start, playlist_name, expanded_count, source_count = top_records_capture_payload(records)
        if expanded_count:
            description = f"expanded playlist/context item URL(s) from {expanded_count} top-level row(s)"
            if source_count:
                description += f" plus {source_count} source URL(s)"
        start_urls_now(urls_to_start, description, playlist_name=playlist_name)

    def queue_top_urls(selected_only, description):
        records = included_top_records(selected_only)
        if not records:
            messagebox.showwarning("No URLs", f"No usable {description} are available to queue.", parent=dialog)
            return
        if not job_queue_window_is_open():
            open_job_queue()

        queued_count = 0
        queued_url_count = 0
        expanded_jobs = 0
        for record in records:
            urls_to_queue, playlist_name, expanded_count, _source_count = top_records_capture_payload([record])
            if not urls_to_queue:
                continue
            if playlist_name:
                move_preview_cache_to_resolved_case_folder(playlist_name=playlist_name)
            if add_urls_to_queue_as_job(urls_to_queue, playlist_name=playlist_name):
                queued_count += 1
                queued_url_count += len(urls_to_queue)
                if expanded_count:
                    expanded_jobs += 1
                if playlist_name:
                    append_log(f"URL Preview playlist tag value for queued job: {playlist_name}\n")

        if queued_count:
            detail = f" ({queued_url_count} URL(s) total"
            if expanded_jobs:
                detail += f"; {expanded_jobs} playlist/context row(s) expanded to item URLs"
            detail += ")"
            append_log(f"\nQueued {queued_count} separate job(s) from URL Preview {description}{detail}.\n")
        else:
            messagebox.showwarning("No jobs queued", f"No {description} could be queued.", parent=dialog)

    url_context_iid = {"value": ""}

    def highlighted_url_record():
        iid = str(url_context_iid.get("value") or "")
        if iid in url_by_iid:
            return url_by_iid[iid]
        focused = str(url_tree.focus() or "")
        if focused in url_by_iid:
            return url_by_iid[focused]
        selected = selected_url_records()
        return selected[0] if selected else None

    def highlighted_url_value():
        record = highlighted_url_record()
        url = clean_extracted_url((record or {}).get("url", ""))
        return record, url

    def preview_highlighted_url():
        record, url = highlighted_url_value()
        if not record or not url_shape_is_valid(url):
            messagebox.showwarning("No URL", "Right-click a URL row first.", parent=dialog)
            return
        start_preview(explicit_records=[record])

    def start_highlighted_url():
        record, url = highlighted_url_value()
        if not record or not url_shape_is_valid(url):
            messagebox.showwarning("No URL", "Right-click a URL row first.", parent=dialog)
            return
        urls_to_start, playlist_name, expanded_count, _source_count = top_records_capture_payload([record])
        description = "highlighted playlist/context item URL(s)" if expanded_count else "highlighted top-level URL"
        start_urls_now(urls_to_start, description, playlist_name=playlist_name)

    def queue_highlighted_url():
        record, url = highlighted_url_value()
        if not record or not url_shape_is_valid(url):
            messagebox.showwarning("No URL", "Right-click a URL row first.", parent=dialog)
            return
        urls_to_queue, playlist_name, expanded_count, _source_count = top_records_capture_payload([record])
        description = "highlighted playlist/context item URL(s)" if expanded_count else "highlighted top-level URL"
        queue_urls(urls_to_queue, description, playlist_name=playlist_name)

    def open_highlighted_url():
        record, url = highlighted_url_value()
        if not record or not url_shape_is_valid(url):
            messagebox.showwarning("No URL", "Right-click a URL row first.", parent=dialog)
            return
        try:
            webbrowser.open(url)
            append_log(f"\nOpened URL from URL Preview: {url}\n")
        except Exception as e:
            messagebox.showerror("Open URL failed", str(e), parent=dialog)

    def get_current_playlist_name():
        record = current_url_record() or {}
        return str(record.get("title") or record.get("id") or record.get("url") or "preview").strip()

    def set_url_box_from_current_items(append=False):
        urls_to_use = urls_from_entries(current_playlist_entries(included_only=True, selected_only=False))
        if not urls_to_use:
            messagebox.showwarning("No item URLs", "No included playlist item URLs are available.", parent=dialog)
            return
        if append:
            append_text_to_urls_box("\n".join(urls_to_use))
            append_log(f"\nAppended {len(urls_to_use)} URL Preview playlist item URL(s) to the URL box.\n")
        else:
            set_url_box_urls(urls_to_use)
            append_log(f"\nReplaced URL box with {len(urls_to_use)} URL Preview playlist item URL(s).\n")

    def set_playlist_items_from_current_selection():
        entries = current_playlist_entries(included_only=True, selected_only=False)
        if not entries:
            messagebox.showwarning("No included items", "Include one or more playlist item rows first.", parent=dialog)
            return
        indexes = [entry.get("index") for entry in entries]
        item_value = collapse_playlist_indexes(indexes)
        if not item_value:
            messagebox.showwarning("No usable indexes", "The included playlist items did not expose usable playlist indexes.", parent=dialog)
            return
        source_scope_var.set("include_playlist")
        playlist_items_enabled_var.set(True)
        playlist_items_var.set(item_value)
        update_playlist_metadata_visibility()
        update_capture_options_summary()
        save_settings(show_popup=False)
        append_log(f"\nSet Playlist Items from URL Preview included items: {item_value}\n")
        messagebox.showinfo("Playlist Items set", f"Playlist Items was set to:\n\n{item_value}", parent=dialog)

    def export_preview_json():
        if not url_records:
            messagebox.showwarning("No preview data", "No URL preview data is available to export.", parent=dialog)
            return
        initial_file = f"url-preview-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            title="Export URL Preview JSON",
            defaultextension=".json",
            initialdir=preview_cache_folder(),
            initialfile=initial_file,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=dialog,
        )
        if not path:
            return
        payload = {
            "app": APP_TITLE,
            "app_version": APP_VERSION,
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_url_count": len(url_records),
            "preview_mode": "yt-dlp --dump-single-json --skip-download",
            "thumbnail_mode": thumbnail_mode_var.get(),
            "cache_mode": cache_mode_var.get(),
            "playlist_mode": playlist_mode_var.get(),
            "urls": [
                {
                    "source_url": record.get("url", ""),
                    "preview": bool(record.get("preview")),
                    "include": bool(record.get("include")),
                    "status": record.get("status", ""),
                    "type": record.get("kind", ""),
                    "title": record.get("title", ""),
                    "uploader": record.get("uploader", ""),
                    "duration": record.get("duration", ""),
                    "items": record.get("items", ""),
                    "thumbnail_url": record.get("thumbnail_url", ""),
                    "thumbnail_cache_path": record.get("thumbnail_cache_path", ""),
                    "error": record.get("error", ""),
                    "json": record.get("json", {}),
                    "entries": record.get("entries", []),
                }
                for record in url_records
            ],
        }
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.write("\n")
            append_log(f"\nExported URL preview JSON: {path}\n")
            messagebox.showinfo("Export complete", f"URL preview JSON was exported to:\n\n{path}", parent=dialog)
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export URL preview JSON:\n\n{e}", parent=dialog)

    def normalized_info_record(record, data):
        data = data if isinstance(data, dict) else {}
        entries_raw = data.get("entries") if isinstance(data.get("entries"), list) else []
        is_playlist = data.get("_type") == "playlist" or bool(entries_raw)
        kind = "Playlist" if is_playlist else str(data.get("extractor_key") or data.get("extractor") or "URL").strip()
        title = str(data.get("title") or data.get("playlist_title") or "").strip()
        uploader = str(data.get("uploader") or data.get("channel") or data.get("creator") or "").strip()
        duration = format_preview_duration(data.get("duration"))
        thumb_url = choose_thumbnail_url(data)

        entries = []
        for item_index, entry in enumerate(entries_raw, start=1):
            entry = entry if isinstance(entry, dict) else {}
            playlist_index = entry.get("playlist_index") or entry.get("n_entries") or item_index
            entry_thumb = choose_thumbnail_url(entry)
            entry_url = get_playlist_entry_url(entry, data)
            entries.append({
                "include": True,
                "index": playlist_index,
                "status": "Ready",
                "kind": "Playlist Item",
                "title": str(entry.get("title") or "").strip(),
                "uploader": str(entry.get("uploader") or entry.get("channel") or "").strip(),
                "id": str(entry.get("id") or "").strip(),
                "duration": format_preview_duration(entry.get("duration")),
                "items": "",
                "url": entry_url,
                "source_url": entry_url,
                "thumbnail_url": entry_thumb,
                "thumbnail_status": "URL" if entry_thumb else "Missing",
                "thumbnail_cache_path": "",
                "thumbnail_error": "",
                "error": "",
                "json": entry,
            })

        record.update({
            "status": "Previewed",
            "kind": kind or "URL",
            "title": title,
            "uploader": uploader,
            "duration": duration,
            "items": len(entries) if is_playlist else "",
            "thumbnail_url": thumb_url,
            "thumbnail_status": "URL" if thumb_url else "Missing",
            "json": data,
            "entries": entries,
            "error": "",
        })

    def add_preview_error(record, status, detail):
        record.update({
            "status": status,
            "kind": "Error" if status in {"Failed", "Error", "Backoff"} else record.get("kind", "Unknown"),
            "error": str(detail or "").strip(),
        })
        update_url_tree_row(record.get("iid", ""))

    def records_for_preview(selected_only=False):
        return preview_checked_top_records() if selected_only else top_all_action_records()

    def warn_if_many_preview_urls(count):
        if count <= 10:
            return True
        return messagebox.askyesno(
            "Preview many URLs?",
            f"You are about to query {count} URL(s) for metadata preview. This can trigger source rate limits, account challenges, or IP throttling.\n\nContinue?",
            parent=dialog,
        )

    def scan_worker(scan_records):
        total_count = len(scan_records)
        for index, record in enumerate(scan_records, start=1):
            if stop_event.is_set():
                break
            url = record.get("url", "")
            root.after(0, set_record_status, record, "Scanning")
            root.after(0, status_var.set, f"Previewing {index}/{total_count}: {url[:140]}")
            try:
                cmd = build_ytdlp_common_metadata_args(url, include_playlist_mode=True)
                append_log(f"\nURL Preview metadata scan {index}/{total_count}:\n{format_command_for_log(cmd)}\n")
                result = subprocess.run(
                    cmd,
                    cwd=os.path.dirname(os.path.abspath(yt_dlp_path_var.get().strip())) or ROOT,
                    capture_output=True,
                    text=True,
                    timeout=get_preview_timeout_seconds(),
                )
                combined_output = "\n".join(part for part in [result.stdout, result.stderr] if part)
                backoff_reason = detect_preview_backoff_reason(combined_output)
                if backoff_reason:
                    root.after(0, add_preview_error, record, "Backoff", backoff_reason)
                    root.after(0, show_preview_backoff_warning, url, backoff_reason)
                    stop_event.set()
                    break
                if result.returncode != 0:
                    detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
                    root.after(0, add_preview_error, record, "Failed", detail)
                    sleep_before_next_preview_url(index, total_count)
                    continue
                data = extract_json_object_from_stdout(result.stdout)
                root.after(0, normalized_info_record, record, data)
                root.after(0, update_url_tree_row, record.get("iid", ""))
            except Exception as e:
                message_text = str(e)
                backoff_reason = detect_preview_backoff_reason(message_text)
                if backoff_reason:
                    root.after(0, add_preview_error, record, "Backoff", backoff_reason)
                    root.after(0, show_preview_backoff_warning, url, backoff_reason)
                    stop_event.set()
                    break
                root.after(0, add_preview_error, record, "Error", message_text)
            sleep_before_next_preview_url(index, total_count)

        def finish():
            if not dialog.winfo_exists():
                return
            set_buttons_scanning(False)
            update_action_states()
            selected = current_url_record()
            if selected:
                show_context_for_record(selected)
            previewed_count = len([record for record in url_records if record.get("json")])
            if stop_event.is_set():
                status_var.set(f"URL preview stopped. {previewed_count}/{len(url_records)} URL(s) have metadata.")
            else:
                status_var.set(f"URL preview complete. {previewed_count}/{len(url_records)} URL(s) have metadata.")
            append_log(f"\nURL preview finished. {previewed_count}/{len(url_records)} URL(s) have metadata.\n")

        root.after(0, finish)

    def start_preview(selected_only=False, explicit_records=None):
        if scan_running["value"]:
            return
        if not has_preview_urls:
            return
        try:
            yt_dlp_path = yt_dlp_path_var.get().strip()
            if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
                raise ValueError("yt-dlp path is missing or invalid.")
        except Exception as e:
            messagebox.showerror("yt-dlp not found", str(e), parent=dialog)
            return
        scan_records = unique_valid_top_records(explicit_records) if explicit_records is not None else records_for_preview(selected_only=selected_only)
        if not scan_records:
            messagebox.showwarning(
                "No URLs selected",
                "Use Preview Checked with checked Preview rows, or right-click a highlighted row and choose Preview Highlighted URL.",
                parent=dialog,
            )
            return
        if not warn_if_many_preview_urls(len(scan_records)):
            return
        for record in scan_records:
            record["status"] = "Queued"
            update_url_tree_row(record.get("iid", ""))
        stop_event.clear()
        set_buttons_scanning(True)
        append_log(
            f"\nStarting URL preview for {len(scan_records)} URL(s). "
            f"Pacing: {pacing_var.get()}; thumbnail mode: {thumbnail_mode_var.get()}; playlist mode: {playlist_mode_var.get()}.\n"
        )
        threading.Thread(target=lambda: scan_worker(scan_records), daemon=True).start()

    def stop_preview():
        stop_event.set()
        status_var.set("Stopping URL preview after current URL...")

    def top_all_action_label(base_text):
        return base_text.replace("All", "Visible") if url_filter_is_active() else base_text

    def top_all_action_description():
        return "visible usable top-level URL(s)" if url_filter_is_active() else "all usable top-level URL(s)"

    def playlist_all_item_label(base_text):
        return base_text.replace("All Items", "Visible Items") if entry_filter_is_active() else base_text

    def playlist_all_item_description():
        return "visible playlist item URL(s)" if entry_filter_is_active() else "playlist item URL(s)"

    def all_action_playlist_entries():
        return current_playlist_entries(False, False, visible_only=entry_filter_is_active())

    def update_context_sensitive_action_labels():
        try:
            preview_all_button.configure(text=top_all_action_label("Preview All"))
            start_all_button.configure(text=top_all_action_label("Start All"))
            queue_all_button.configure(text=top_all_action_label("Queue All"))
        except Exception:
            pass
        try:
            playlist_start_all_button.configure(text=playlist_all_item_label("Start All Items"))
            playlist_queue_all_button.configure(text=playlist_all_item_label("Queue All Items"))
        except Exception:
            pass

    def set_buttons_scanning(is_scanning):
        scan_running["value"] = is_scanning
        try:
            preview_all_button.configure(state="disabled" if is_scanning or not has_preview_urls else "normal")
            preview_selected_button.configure(state="disabled" if is_scanning or not has_preview_urls else "normal")
            stop_button.configure(state="normal" if is_scanning else "disabled")
        except Exception:
            pass

    def update_action_states():
        enabled_state = "normal" if has_preview_urls and not scan_running["value"] else "disabled"
        for widget in action_buttons:
            try:
                widget.configure(state=enabled_state)
            except Exception:
                pass
        try:
            stop_button.configure(state="normal" if scan_running["value"] else "disabled")
        except Exception:
            pass
        if not has_preview_urls:
            for tree in (url_tree, entry_tree):
                try:
                    tree.configure(selectmode="none")
                    tree.state(["disabled"])
                except Exception:
                    pass
        else:
            for tree in (url_tree, entry_tree):
                try:
                    tree.configure(selectmode="extended")
                    tree.state(["!disabled"])
                except Exception:
                    pass

    def update_url_filter_count_label():
        total = len(url_records)
        shown = sum(1 for record in url_records if url_record_matches_filter(record))
        url_count_var.set(f"URLs: {shown} shown / {total} total")

        update_context_sensitive_action_labels()

        if scan_running.get("value"):
            return

        if total and shown == 0 and url_filter_is_active():
            status_var.set("No URL rows match the current filter.")
        elif has_preview_urls:
            status_var.set(f"Loaded {total} URL(s). Use Preview All/Checked to gather metadata.")
        else:
            status_var.set(f"{no_urls_message} Add URLs in the URL box or select Input File(s) to enable URL Preview.")

    def update_entry_filter_count_label(record=None):
        record = record or current_url_record()
        entries = list((record or {}).get("entries", []))
        total = len(entries)
        shown = sum(1 for entry in entries if entry_record_matches_filter(entry))
        entry_count_var.set(f"Items: {shown} shown / {total} total")

        update_context_sensitive_action_labels()

        if total and shown == 0 and entry_filter_is_active():
            context_title_var.set("No playlist/context items match the current filter.")
        elif record and total:
            context_title_var.set(f"Playlist/context items: {record.get('title') or record.get('url')} ({shown} shown / {total} item(s))")

    def populate_url_tree():
        for item in url_tree.get_children():
            url_tree.delete(item)
        for record in url_records:
            update_url_tree_row(record["iid"])
        update_url_filter_count_label()

    def populate_entry_tree(record):
        entry_by_iid.clear()
        for item in entry_tree.get_children():
            entry_tree.delete(item)
        entries = list((record or {}).get("entries", []))
        for index, entry in enumerate(entries):
            iid = f"{record.get('iid', 'url')}:entry-{index}"
            entry["iid"] = iid
            entry_by_iid[iid] = entry
            update_entry_tree_row(iid)
        update_entry_filter_count_label(record)

    def set_details_text(text_value):
        details_text.configure(state="normal")
        details_text.delete("1.0", "end")
        details_text.insert("1.0", str(text_value or ""))
        details_text.configure(state="disabled")

    def format_record_details(record):
        if not record:
            return "Select a URL row to view details."
        lines = [
            f"Status: {record.get('status', '')}",
            f"Type: {record.get('kind', '')}",
            f"Index: {record.get('index', '')}",
            f"Title: {record.get('title', '')}",
            f"Uploader/channel: {record.get('uploader', '')}",
            f"Duration: {record.get('duration', '')}",
            f"Items: {record.get('items', '')}",
            f"Extractor: {(record.get('json') or {}).get('extractor_key') or (record.get('json') or {}).get('extractor') or ''}",
            f"ID: {(record.get('json') or {}).get('id') or record.get('id') or ''}",
            f"URL: {record.get('url', '')}",
            f"Webpage URL: {(record.get('json') or {}).get('webpage_url') or record.get('url', '')}",
            f"Original URL: {(record.get('json') or {}).get('original_url') or record.get('url', '')}",
            f"Availability: {(record.get('json') or {}).get('availability') or ''}",
            f"Live status: {(record.get('json') or {}).get('live_status') or ''}",
            f"Upload date: {(record.get('json') or {}).get('upload_date') or ''}",
            f"Playlist: {(record.get('json') or {}).get('playlist') or (record.get('json') or {}).get('playlist_title') or ''}",
            f"Playlist ID: {(record.get('json') or {}).get('playlist_id') or ''}",
            f"Playlist index: {(record.get('json') or {}).get('playlist_index') or ''}",
            f"Thumbnail URL: {record.get('thumbnail_url', '')}",
            f"Thumbnail cache: {record.get('thumbnail_cache_path', '')}",
        ]
        if record.get("error"):
            lines.extend(["", f"Error/notes: {record.get('error')}"])
        return "\n".join(lines)

    def set_thumbnail_status(text=""):
        try:
            thumbnail_status_var.set(str(text or ""))
        except Exception:
            pass

    def clear_thumbnail(text="No thumbnail loaded", status_text=""):
        thumbnail_image_holder["image"] = None
        try:
            thumbnail_label.configure(image="", text=text)
        except Exception:
            pass
        set_thumbnail_status(status_text)

    def thumbnail_record_key(record):
        if not record:
            return ""
        mode = normalize_url_preview_thumbnail_mode(thumbnail_mode_var.get())
        thumb_url = str(record.get("thumbnail_url") or "").strip()
        source_url = clean_extracted_url(record.get("url") or record.get("source_url") or "")
        if not thumb_url and not source_url:
            return ""
        return hashlib.sha256(f"{mode}\n{thumb_url}\n{source_url}".encode("utf-8", errors="ignore")).hexdigest()

    def thumbnail_record_label(record):
        return short_text((record or {}).get("title") or (record or {}).get("url") or "thumbnail", 80)

    def thumbnail_rate_limit_enabled():
        try:
            return bool(rate_limit_thumbnails_var.get())
        except Exception:
            return True

    def thumbnail_cooldown_delay(fetch_kind):
        if not thumbnail_rate_limit_enabled():
            return 0.0
        if fetch_kind == "ytdlp":
            return 10.0 + random.uniform(0, 10.0)
        return 5.0 + random.uniform(0, 5.0)

    def thumbnail_cooldown_remaining(fetch_kind):
        if not thumbnail_rate_limit_enabled():
            return 0.0
        now = time.time()
        with thumbnail_state_lock:
            next_allowed = thumbnail_state.get("next_allowed") or {}
            allowed_at = float(next_allowed.get(fetch_kind) or 0.0)
        return max(0.0, allowed_at - now)

    def mark_thumbnail_fetch_attempt_completed(fetch_kind):
        if not thumbnail_rate_limit_enabled():
            with thumbnail_state_lock:
                next_allowed = thumbnail_state.setdefault("next_allowed", {"fast": 0.0, "ytdlp": 0.0})
                next_allowed[fetch_kind] = 0.0
            return 0.0

        delay = thumbnail_cooldown_delay(fetch_kind)
        with thumbnail_state_lock:
            next_allowed = thumbnail_state.setdefault("next_allowed", {"fast": 0.0, "ytdlp": 0.0})
            next_allowed[fetch_kind] = time.time() + delay
        return delay

    def thumbnail_desired_key():
        with thumbnail_state_lock:
            return thumbnail_state.get("desired_key", "")

    def load_thumbnail_image(record, png_path):
        if not record or not png_path or not os.path.isfile(png_path):
            clear_thumbnail("Thumbnail unavailable")
            return
        try:
            image = tk.PhotoImage(file=png_path)
            thumbnail_image_holder["image"] = image
            thumbnail_label.configure(image=image, text="")
            set_thumbnail_status("Thumbnail loaded from cache." if record.get("thumbnail_status") == "Cached" else "Thumbnail loaded.")
            record["thumbnail_cache_path"] = png_path
            record["thumbnail_status"] = "Cached"
            update_preview_row(record)
            if current_detail_record.get("record") is record:
                set_details_text(format_record_details(record))
        except Exception as e:
            record["thumbnail_error"] = str(e)
            record["thumbnail_status"] = "Display failed"
            update_preview_row(record)
            clear_thumbnail("Thumbnail display failed", "Thumbnail display failed.")

    def apply_thumbnail_fetch_result(record, key, path, error=""):
        if path:
            record["thumbnail_cache_path"] = path
            record["thumbnail_status"] = "Cached"
            record["thumbnail_error"] = ""
        else:
            record["thumbnail_error"] = error
            record["thumbnail_status"] = "Fetch failed"
        update_preview_row(record)

        if thumbnail_desired_key() != key or current_detail_record.get("record") is not record:
            return

        if path:
            load_thumbnail_image(record, path)
        else:
            clear_thumbnail("Thumbnail fetch failed", "Thumbnail fetch failed.")
            set_details_text(format_record_details(record) + (f"\n\nThumbnail error: {error}" if error else ""))

    def cached_fast_thumbnail_path(record):
        thumb_url = str((record or {}).get("thumbnail_url") or "").strip()
        if not thumb_url:
            return ""
        png_path = os.path.join(preview_cache_folder(), f"{safe_cache_name(thumb_url)}.png")
        return png_path if os.path.isfile(png_path) else ""

    def cached_ytdlp_thumbnail_path(record):
        source_url = str((record or {}).get("url") or (record or {}).get("source_url") or "").strip()
        if not source_url:
            return ""
        png_path = os.path.join(preview_cache_folder(), safe_cache_name(source_url), "thumb.png")
        return png_path if os.path.isfile(png_path) else ""

    def wait_thumbnail_cooldown(fetch_kind, key, record):
        if not thumbnail_rate_limit_enabled():
            return thumbnail_desired_key() == key

        label = "yt-dlp thumbnail fallback" if fetch_kind == "ytdlp" else "thumbnail fetch"
        while True:
            remaining = thumbnail_cooldown_remaining(fetch_kind)
            if remaining <= 0:
                break
            with thumbnail_state_lock:
                visible_record = thumbnail_state.get("desired_record")
            if visible_record and current_detail_record.get("record") is visible_record:
                root.after(0, set_thumbnail_status, f"Rate-limited {label}; fetching in {remaining:.1f}s...")
                root.after(0, lambda r=remaining, l=label: thumbnail_label.configure(image="", text=f"Rate-limited {l}\n{r:.1f}s"))
            time.sleep(min(0.25, max(0.0, remaining)))

        return thumbnail_desired_key() == key

    def fetch_thumbnail_for_record_with_rate_limits(record, key):
        mode = thumbnail_mode_var.get()
        errors = []
        has_thumbnail_url = bool(str(record.get("thumbnail_url") or "").strip())
        has_source_url = bool(clean_extracted_url(record.get("url") or record.get("source_url") or ""))

        if mode == "Off":
            return "", "Thumbnail fetching is off."
        if not has_thumbnail_url and mode != "Reliable":
            return "", "No thumbnail URL was available in metadata."
        if not has_thumbnail_url and not has_source_url:
            return "", "No thumbnail source URL was available."

        if has_thumbnail_url:
            cached_path = cached_fast_thumbnail_path(record)
            if cached_path:
                return cached_path, ""
            if not wait_thumbnail_cooldown("fast", key, record):
                return "", "superseded"
            did_attempt = False
            try:
                root.after(0, set_thumbnail_status, "Fetching thumbnail from metadata URL...")
                did_attempt = True
                path = fetch_thumbnail_fast(record)
                return path, ""
            except Exception as e:
                errors.append(str(e))
            finally:
                if did_attempt:
                    mark_thumbnail_fetch_attempt_completed("fast")

        if mode == "Reliable":
            cached_path = cached_ytdlp_thumbnail_path(record)
            if cached_path:
                return cached_path, ""
            if not wait_thumbnail_cooldown("ytdlp", key, record):
                return "", "superseded"
            did_attempt = False
            try:
                root.after(0, set_thumbnail_status, "Fetching thumbnail with yt-dlp fallback...")
                did_attempt = True
                path = fetch_thumbnail_ytdlp(record)
                return path, ""
            except Exception as e:
                errors.append(str(e))
            finally:
                if did_attempt:
                    mark_thumbnail_fetch_attempt_completed("ytdlp")

        return "", "; ".join(error for error in errors if error) or "thumbnail fetch failed"

    def thumbnail_worker_loop():
        try:
            while True:
                with thumbnail_state_lock:
                    record = thumbnail_state.get("desired_record")
                    key = thumbnail_state.get("desired_key", "")
                if not record or not key:
                    return

                cached_path = record.get("thumbnail_cache_path")
                if cached_path and os.path.isfile(cached_path):
                    root.after(0, load_thumbnail_image, record, cached_path)
                    return

                if thumbnail_mode_var.get() == "Off":
                    if thumbnail_desired_key() == key and current_detail_record.get("record") is record:
                        root.after(0, clear_thumbnail, "Thumbnail fetching is off", "")
                    return

                record["thumbnail_status"] = "Fetching"
                root.after(0, update_preview_row, record)
                if thumbnail_desired_key() == key and current_detail_record.get("record") is record:
                    root.after(0, clear_thumbnail, "Preparing thumbnail fetch...", "")

                path, error = fetch_thumbnail_for_record_with_rate_limits(record, key)

                if error == "superseded" or thumbnail_desired_key() != key:
                    continue

                if path:
                    record["thumbnail_cache_path"] = path
                    record["thumbnail_status"] = "Cached"
                    record["thumbnail_error"] = ""
                else:
                    record["thumbnail_status"] = "Fetch failed"
                    record["thumbnail_error"] = error
                root.after(0, apply_thumbnail_fetch_result, record, key, path, error)
                return
        finally:
            restart_needed = False
            with thumbnail_state_lock:
                thumbnail_state["worker_running"] = False
                record = thumbnail_state.get("desired_record")
                key = thumbnail_state.get("desired_key", "")
                if record and key:
                    cached = record.get("thumbnail_cache_path") and os.path.isfile(record.get("thumbnail_cache_path"))
                    if not cached and record.get("thumbnail_status") in {"Waiting", "Fetching"}:
                        restart_needed = True
            if restart_needed:
                root.after(0, ensure_thumbnail_worker)

    def ensure_thumbnail_worker():
        with thumbnail_state_lock:
            if thumbnail_state.get("worker_running"):
                return
            thumbnail_state["worker_running"] = True
        threading.Thread(target=thumbnail_worker_loop, daemon=True).start()

    def begin_thumbnail_fetch(record):
        mode = thumbnail_mode_var.get()
        if mode == "Off":
            with thumbnail_state_lock:
                thumbnail_state["desired_key"] = ""
                thumbnail_state["desired_record"] = None
            clear_thumbnail("Thumbnail fetching is off")
            return
        if not record:
            with thumbnail_state_lock:
                thumbnail_state["desired_key"] = ""
                thumbnail_state["desired_record"] = None
            clear_thumbnail("No thumbnail loaded")
            return

        key = thumbnail_record_key(record)
        has_thumbnail_url = bool(str(record.get("thumbnail_url") or "").strip())
        has_source_url = bool(clean_extracted_url(record.get("url") or record.get("source_url") or ""))
        if not has_thumbnail_url and mode != "Reliable":
            clear_thumbnail("No thumbnail URL")
            set_thumbnail_status("No thumbnail URL available for Fast mode.")
            return
        if not has_thumbnail_url and not has_source_url:
            clear_thumbnail("No thumbnail source URL")
            set_thumbnail_status("No thumbnail source URL available.")
            return
        if record.get("thumbnail_cache_path") and os.path.isfile(record.get("thumbnail_cache_path")):
            with thumbnail_state_lock:
                thumbnail_state["desired_key"] = key
                thumbnail_state["desired_record"] = record
            load_thumbnail_image(record, record.get("thumbnail_cache_path"))
            return

        with thumbnail_state_lock:
            same_target = thumbnail_state.get("desired_key") == key and thumbnail_state.get("desired_record") is record
            worker_running = bool(thumbnail_state.get("worker_running"))
            thumbnail_state["desired_key"] = key
            thumbnail_state["desired_record"] = record
        if same_target and worker_running:
            return

        record["thumbnail_status"] = "Fetching"
        update_preview_row(record)
        clear_thumbnail("Fetching thumbnail...")
        ensure_thumbnail_worker()

    def show_context_for_record(record):
        context_title_var.set("Select a URL row to view details.")
        current_detail_record["record"] = record
        details_frame.grid_remove()
        playlist_frame.grid_remove()
        clear_thumbnail()
        set_details_text("")
        populate_entry_tree(None)

        if not record:
            details_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
            details_frame.tkraise()
            set_details_text("Select a URL row to view details.")
            return

        entries = record.get("entries") or []
        if entries:
            context_title_var.set(f"Playlist/context items: {record.get('title') or record.get('url')} ({len(entries)} item(s))")
            populate_entry_tree(record)
            # Explicit columnspan=1 is important because the non-playlist state
            # uses columnspan=2. Without resetting it, Tk can retain the old
            # span and draw the details notebook underneath/over the playlist list.
            details_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=(0, 8))
            playlist_frame.grid(row=1, column=1, columnspan=1, sticky="nsew")
            details_frame.tkraise()
            playlist_frame.tkraise()
            set_details_text(format_record_details(record))
            begin_thumbnail_fetch(record)
        else:
            context_title_var.set(f"URL details: {record.get('title') or record.get('url')}")
            details_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
            details_frame.tkraise()
            set_details_text(format_record_details(record))
            begin_thumbnail_fetch(record)

    def show_context_for_entry(entry):
        if not entry:
            return
        current_detail_record["record"] = entry
        context_title_var.set(f"Playlist item details: {entry.get('title') or entry.get('url')}")
        set_details_text(format_record_details(entry))
        begin_thumbnail_fetch(entry)

    def on_url_tree_select(event=None):
        show_context_for_record(current_url_record())

    def on_entry_tree_select(event=None):
        entries = selected_entry_records()
        if entries:
            show_context_for_entry(entries[0])

    def on_url_tree_click(event):
        if not has_preview_urls:
            return "break"
        try:
            item_id = url_tree.identify_row(event.y)
            region = url_tree.identify("region", event.x, event.y)
            column_id = url_tree.identify_column(event.x)
            if not item_id or region not in {"cell", "tree"}:
                clear_tree_selection(url_tree)
                show_context_for_record(None)
                return "break"
            if column_id == "#1":
                toggle_url_flag(item_id, "preview")
                url_tree.selection_set(item_id)
                url_tree.focus(item_id)
                show_context_for_record(url_by_iid.get(item_id))
                return "break"
            if column_id == "#2":
                toggle_url_flag(item_id, "include")
                url_tree.selection_set(item_id)
                url_tree.focus(item_id)
                show_context_for_record(url_by_iid.get(item_id))
                return "break"
            return None
        except Exception:
            return

    def on_url_tree_double_click(event):
        if not has_preview_urls:
            return "break"
        try:
            item_id = url_tree.identify_row(event.y)
            column_id = url_tree.identify_column(event.x)
            if not item_id:
                return "break"
            if column_id not in {"#1", "#2"}:
                toggle_url_flag(item_id, "preview")
            url_tree.selection_set(item_id)
            url_tree.focus(item_id)
            show_context_for_record(url_by_iid.get(item_id))
            return "break"
        except Exception:
            return

    def on_entry_tree_click(event):
        if not has_preview_urls:
            return "break"
        try:
            item_id = entry_tree.identify_row(event.y)
            region = entry_tree.identify("region", event.x, event.y)
            column_id = entry_tree.identify_column(event.x)
            if not item_id or region not in {"cell", "tree"}:
                clear_tree_selection(entry_tree)
                return "break"
            if column_id == "#1":
                toggle_entry_include(item_id)
                entry_tree.selection_set(item_id)
                entry_tree.focus(item_id)
                show_context_for_entry(entry_by_iid.get(item_id))
                return "break"
            return None
        except Exception:
            return

    def on_entry_tree_double_click(event):
        if not has_preview_urls:
            return "break"
        try:
            item_id = entry_tree.identify_row(event.y)
            if not item_id:
                return "break"
            toggle_entry_include(item_id)
            entry_tree.selection_set(item_id)
            entry_tree.focus(item_id)
            show_context_for_entry(entry_by_iid.get(item_id))
            return "break"
        except Exception:
            return

    def show_tree_context_menu(event, tree, menu, context_holder=None):
        if not has_preview_urls:
            return "break"
        try:
            iid = tree.identify_row(event.y)
            if context_holder is not None:
                context_holder["value"] = iid or ""
            if iid:
                tree.selection_set(iid)
                tree.focus(iid)
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return "break"

    def toggle_options_panel():
        options_visible["value"] = not options_visible["value"]
        if options_visible["value"]:
            options_panel.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 6))
            options_panel.tkraise()
            options_button.configure(text="Preview Options ▴")
        else:
            options_panel.grid_remove()
            options_button.configure(text="Preview Options ▾")

    def pack_preview_button(widget):
        widget.pack(side="left", padx=(0, 6), pady=2)
        return widget

    header = ttk.Frame(dialog, padding=(12, 12, 12, 4))
    header.grid(row=0, column=0, sticky="ew")
    header.columnconfigure(0, weight=1)
    ttk.Label(header, textvariable=status_var).grid(row=0, column=0, sticky="w")

    url_action_frame = ttk.LabelFrame(dialog, text="URL Preview Actions", padding=8)
    url_action_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
    action_buttons = []
    preview_all_button = pack_preview_button(ttk.Button(url_action_frame, text="Preview All", command=lambda: start_preview(False)))
    action_buttons.append(preview_all_button)
    preview_selected_button = pack_preview_button(ttk.Button(url_action_frame, text="Preview Checked", command=lambda: start_preview(True)))
    action_buttons.append(preview_selected_button)
    stop_button = pack_preview_button(ttk.Button(url_action_frame, text="Stop", command=stop_preview, state="disabled"))
    start_all_button = pack_preview_button(ttk.Button(url_action_frame, text="Start All", command=lambda: start_top_urls(False, top_all_action_description())))
    action_buttons.append(start_all_button)
    start_selected_button = pack_preview_button(ttk.Button(url_action_frame, text="Start Included", command=lambda: start_top_urls(True, "included top-level URL(s)")))
    action_buttons.append(start_selected_button)
    queue_all_button = pack_preview_button(ttk.Button(url_action_frame, text="Queue All", command=lambda: queue_top_urls(False, top_all_action_description())))
    action_buttons.append(queue_all_button)
    queue_selected_button = pack_preview_button(ttk.Button(url_action_frame, text="Queue Included", command=lambda: queue_top_urls(True, "included top-level URL(s)")))
    action_buttons.append(queue_selected_button)
    export_button = pack_preview_button(ttk.Button(url_action_frame, text="Export JSON", command=export_preview_json))
    action_buttons.append(export_button)

    url_frame = ttk.LabelFrame(dialog, text="URLs", padding=8)
    url_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))
    url_frame.columnconfigure(0, weight=1)
    url_frame.rowconfigure(1, weight=1)

    url_filter_frame = ttk.Frame(url_frame)
    url_filter_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
    url_filter_frame.columnconfigure(1, weight=1)
    ttk.Label(url_filter_frame, text="Filter URLs").grid(row=0, column=0, sticky="w", padx=(0, 6))
    ttk.Entry(url_filter_frame, textvariable=url_filter_var).grid(row=0, column=1, sticky="ew", padx=(0, 6))
    ttk.Button(url_filter_frame, text="Clear", command=lambda: url_filter_var.set("")).grid(row=0, column=2, sticky="e")
    ttk.Label(url_filter_frame, textvariable=url_count_var).grid(row=0, column=3, sticky="e", padx=(8, 0))

    url_tree = ttk.Treeview(
        url_frame,
        columns=("preview", "include", "number", "status", "type", "title", "uploader", "duration", "items", "thumb", "url"),
        show="headings",
        selectmode="extended",
        height=9,
    )
    for col, label in (
        ("preview", "Preview"), ("include", "Include"), ("number", "#"), ("status", "Status"),
        ("type", "Type"), ("title", "Title"), ("uploader", "Uploader"), ("duration", "Duration"),
        ("items", "Items"), ("thumb", "Thumbnail"), ("url", "URL"),
    ):
        url_tree.heading(col, text=label)
    url_tree.column("preview", width=70, anchor="center", stretch=False)
    url_tree.column("include", width=70, anchor="center", stretch=False)
    url_tree.column("number", width=45, anchor="e", stretch=False)
    url_tree.column("status", width=110, stretch=False)
    url_tree.column("type", width=100, stretch=False)
    url_tree.column("title", width=250)
    url_tree.column("uploader", width=150)
    url_tree.column("duration", width=85, stretch=False)
    url_tree.column("items", width=65, anchor="e", stretch=False)
    url_tree.column("thumb", width=95, stretch=False)
    url_tree.column("url", width=430)
    url_tree.grid(row=1, column=0, sticky="nsew")
    url_scroll_y = ttk.Scrollbar(url_frame, orient="vertical", command=url_tree.yview)
    url_scroll_y.grid(row=1, column=1, sticky="ns")
    url_scroll_x = ttk.Scrollbar(url_frame, orient="horizontal", command=url_tree.xview)
    url_scroll_x.grid(row=2, column=0, sticky="ew")
    url_tree.configure(yscrollcommand=url_scroll_y.set, xscrollcommand=url_scroll_x.set)
    url_tree.bind("<<TreeviewSelect>>", on_url_tree_select)
    url_tree.bind("<Button-1>", on_url_tree_click)
    url_tree.bind("<Double-1>", on_url_tree_double_click)
    url_filter_var.trace_add("write", lambda *args: populate_url_tree())
    populate_url_tree()

    bottom_outer = ttk.LabelFrame(dialog, text="Selected URL Context", padding=8)
    bottom_outer.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 8))
    bottom_outer.columnconfigure(0, weight=1, minsize=320)
    bottom_outer.columnconfigure(1, weight=2)
    bottom_outer.rowconfigure(1, weight=1)

    bottom_header = ttk.Frame(bottom_outer)
    bottom_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
    bottom_header.columnconfigure(0, weight=1)
    ttk.Label(bottom_header, textvariable=context_title_var).grid(row=0, column=0, sticky="w")

    options_panel = ttk.Frame(dialog, padding=8)
    options_panel.columnconfigure(7, weight=1)
    ttk.Label(options_panel, text="Preview pacing").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=2)
    ttk.Combobox(options_panel, textvariable=pacing_var, values=list(preview_pacing_options.keys()), state="readonly", width=28).grid(row=0, column=1, sticky="w", padx=(0, 12), pady=2)
    ttk.Label(options_panel, text="Thumbnails").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=2)
    ttk.Combobox(options_panel, textvariable=thumbnail_mode_var, values=thumbnail_mode_options, state="readonly", width=12).grid(row=0, column=3, sticky="w", padx=(0, 12), pady=2)
    ttk.Label(options_panel, text="Playlist mode").grid(row=0, column=4, sticky="w", padx=(0, 6), pady=2)
    ttk.Combobox(options_panel, textvariable=playlist_mode_var, values=playlist_mode_options, state="readonly", width=22).grid(row=0, column=5, sticky="w", padx=(0, 12), pady=2)
    ttk.Label(options_panel, text="Max items").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=2)
    ttk.Entry(options_panel, textvariable=max_playlist_items_var, width=8).grid(row=1, column=1, sticky="w", padx=(0, 12), pady=2)
    ttk.Label(options_panel, text="Timeout sec").grid(row=1, column=2, sticky="w", padx=(0, 6), pady=2)
    ttk.Entry(options_panel, textvariable=timeout_var, width=8).grid(row=1, column=3, sticky="w", padx=(0, 12), pady=2)
    ttk.Checkbutton(
        options_panel,
        text="Rate limit thumbnails",
        variable=rate_limit_thumbnails_var,
    ).grid(row=1, column=4, columnspan=2, sticky="w", padx=(0, 12), pady=2)
    ttk.Label(options_panel, text="Cache mode").grid(row=2, column=0, sticky="w", padx=(0, 6), pady=2)
    ttk.Combobox(options_panel, textvariable=cache_mode_var, values=cache_mode_options, state="readonly", width=24).grid(row=2, column=1, columnspan=3, sticky="w", padx=(0, 12), pady=2)
    ttk.Button(options_panel, text="Clear URL Preview Cache", command=clear_url_preview_cache).grid(row=2, column=4, columnspan=2, sticky="w", padx=(0, 12), pady=2)
    options_panel.grid_remove()

    preview_options_bar = ttk.Frame(dialog)
    preview_options_bar.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 8))
    preview_options_bar.columnconfigure(1, weight=1)
    options_button = ttk.Button(preview_options_bar, text="Preview Options ▾", command=toggle_options_panel)
    options_button.grid(row=0, column=0, sticky="w", padx=(0, 8))

    details_frame = ttk.Frame(bottom_outer)
    details_frame.columnconfigure(0, weight=1)
    details_frame.rowconfigure(0, weight=1)

    details_notebook = ttk.Notebook(details_frame)
    details_notebook.grid(row=0, column=0, sticky="nsew")

    thumbnail_tab = ttk.Frame(details_notebook, padding=8)
    thumbnail_tab.columnconfigure(0, weight=1)
    thumbnail_tab.rowconfigure(0, weight=1)
    thumbnail_tab.rowconfigure(1, weight=0)
    thumbnail_label = ttk.Label(thumbnail_tab, text="No thumbnail loaded", anchor="center", justify="center", width=32)
    thumbnail_label.grid(row=0, column=0, sticky="nsew")
    ttk.Label(thumbnail_tab, textvariable=thumbnail_status_var, anchor="center", justify="center", wraplength=260).grid(row=1, column=0, sticky="ew", pady=(8, 0))

    metadata_tab = ttk.Frame(details_notebook, padding=8)
    metadata_tab.columnconfigure(0, weight=1)
    metadata_tab.rowconfigure(0, weight=1)
    details_text = tk.Text(metadata_tab, height=9, wrap="none", state="disabled")
    details_text.grid(row=0, column=0, sticky="nsew")
    details_scroll_y = ttk.Scrollbar(metadata_tab, orient="vertical", command=details_text.yview)
    details_scroll_y.grid(row=0, column=1, sticky="ns")
    details_scroll_x = ttk.Scrollbar(metadata_tab, orient="horizontal", command=details_text.xview)
    details_scroll_x.grid(row=1, column=0, sticky="ew")
    details_text.configure(yscrollcommand=details_scroll_y.set, xscrollcommand=details_scroll_x.set)

    details_notebook.add(thumbnail_tab, text="Thumbnail")
    details_notebook.add(metadata_tab, text="Metadata")

    playlist_frame = ttk.Frame(bottom_outer)
    playlist_frame.columnconfigure(0, weight=1)
    playlist_frame.rowconfigure(1, weight=1)
    playlist_action_frame = ttk.LabelFrame(playlist_frame, text="Playlist Item Actions", padding=8)
    playlist_action_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
    playlist_action_frame.columnconfigure(1, weight=1)

    def scroll_playlist_action_buttons(direction):
        try:
            bbox = playlist_action_canvas.bbox("all")
            if not bbox:
                return
            content_width = max(1, bbox[2] - bbox[0])
            view_width = max(1, playlist_action_canvas.winfo_width())
            if content_width <= view_width:
                playlist_action_canvas.xview_moveto(0)
                return
            current_left = playlist_action_canvas.canvasx(0)
            new_left = max(0, min(content_width - view_width, current_left + (direction * 180)))
            playlist_action_canvas.xview_moveto(new_left / content_width)
        except Exception:
            try:
                playlist_action_canvas.xview_scroll(direction * 3, "units")
            except Exception:
                pass

    def update_playlist_action_scroll_region(_event=None):
        try:
            playlist_action_canvas.configure(scrollregion=playlist_action_canvas.bbox("all"))
        except Exception:
            pass

    playlist_action_left = ttk.Button(
        playlist_action_frame,
        text="◀",
        width=3,
        command=lambda: scroll_playlist_action_buttons(-1),
    )
    playlist_action_left.grid(row=0, column=0, sticky="w", padx=(0, 6))

    try:
        playlist_action_canvas_bg = dialog.cget("background")
    except Exception:
        playlist_action_canvas_bg = None
    playlist_action_canvas_kwargs = {"height": 36, "highlightthickness": 0, "borderwidth": 0}
    if playlist_action_canvas_bg:
        playlist_action_canvas_kwargs["background"] = playlist_action_canvas_bg
    playlist_action_canvas = tk.Canvas(playlist_action_frame, **playlist_action_canvas_kwargs)
    playlist_action_canvas.grid(row=0, column=1, sticky="ew")

    playlist_action_button_frame = ttk.Frame(playlist_action_canvas)
    playlist_action_window = playlist_action_canvas.create_window(
        (0, 0),
        window=playlist_action_button_frame,
        anchor="nw",
    )
    playlist_action_button_frame.bind("<Configure>", update_playlist_action_scroll_region)
    playlist_action_canvas.bind(
        "<Configure>",
        lambda event: (
            playlist_action_canvas.itemconfigure(playlist_action_window, height=event.height),
            update_playlist_action_scroll_region(),
        ),
    )

    playlist_action_right = ttk.Button(
        playlist_action_frame,
        text="▶",
        width=3,
        command=lambda: scroll_playlist_action_buttons(1),
    )
    playlist_action_right.grid(row=0, column=2, sticky="e", padx=(6, 0))

    def pack_playlist_action_button(widget):
        widget.pack(side="left", padx=(0, 6), pady=2)
        return widget

    playlist_start_all_button = pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Start All Items", command=lambda: start_urls_now(urls_from_entries(all_action_playlist_entries()), playlist_all_item_description(), playlist_name=get_current_playlist_name())))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Start Included Items", command=lambda: start_urls_now(urls_from_entries(included_entry_records()), "included playlist item URL(s)", playlist_name=get_current_playlist_name())))
    playlist_queue_all_button = pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Queue All Items", command=lambda: queue_urls(urls_from_entries(all_action_playlist_entries()), playlist_all_item_description(), playlist_name=get_current_playlist_name())))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Queue Included Items", command=lambda: queue_urls(urls_from_entries(included_entry_records()), "included playlist item URL(s)", playlist_name=get_current_playlist_name())))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Copy Included URLs", command=lambda: copy_text_to_clipboard("\n".join(urls_from_entries(current_playlist_entries(True, False))), "included playlist item URL(s)")))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Load Included URLs", command=lambda: set_url_box_from_current_items(False)))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Append Included URLs", command=lambda: set_url_box_from_current_items(True)))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Set Playlist Items", command=set_playlist_items_from_current_selection))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Include All", command=lambda: set_all_current_item_includes(True)))
    pack_playlist_action_button(ttk.Button(playlist_action_button_frame, text="Exclude All", command=lambda: set_all_current_item_includes(False)))

    entry_frame = ttk.LabelFrame(playlist_frame, text="Playlist / Context URLs", padding=8)
    entry_frame.grid(row=1, column=0, sticky="nsew")
    entry_frame.columnconfigure(0, weight=1)
    entry_frame.rowconfigure(1, weight=1)

    entry_filter_frame = ttk.Frame(entry_frame)
    entry_filter_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
    entry_filter_frame.columnconfigure(1, weight=1)
    ttk.Label(entry_filter_frame, text="Filter items").grid(row=0, column=0, sticky="w", padx=(0, 6))
    ttk.Entry(entry_filter_frame, textvariable=entry_filter_var).grid(row=0, column=1, sticky="ew", padx=(0, 6))
    ttk.Button(entry_filter_frame, text="Clear", command=lambda: entry_filter_var.set("")).grid(row=0, column=2, sticky="e")
    ttk.Label(entry_filter_frame, textvariable=entry_count_var).grid(row=0, column=3, sticky="e", padx=(8, 0))

    entry_tree = ttk.Treeview(
        entry_frame,
        columns=("include", "index", "status", "title", "duration", "thumb", "json", "url"),
        show="headings",
        selectmode="extended",
        height=8,
    )
    for col, label in (
        ("include", "Include"), ("index", "Index"), ("status", "Status"), ("title", "Title"),
        ("duration", "Duration"), ("thumb", "Thumbnail"), ("json", "JSON"), ("url", "URL"),
    ):
        entry_tree.heading(col, text=label)
    entry_tree.column("include", width=70, anchor="center", stretch=False)
    entry_tree.column("index", width=70, anchor="e", stretch=False)
    entry_tree.column("status", width=90, stretch=False)
    entry_tree.column("title", width=260)
    entry_tree.column("duration", width=90, stretch=False)
    entry_tree.column("thumb", width=95, stretch=False)
    entry_tree.column("json", width=60, anchor="center", stretch=False)
    entry_tree.column("url", width=380)
    entry_tree.grid(row=1, column=0, sticky="nsew")
    entry_scroll_y = ttk.Scrollbar(entry_frame, orient="vertical", command=entry_tree.yview)
    entry_scroll_y.grid(row=1, column=1, sticky="ns")
    entry_scroll_x = ttk.Scrollbar(entry_frame, orient="horizontal", command=entry_tree.xview)
    entry_scroll_x.grid(row=2, column=0, sticky="ew")
    entry_tree.configure(yscrollcommand=entry_scroll_y.set, xscrollcommand=entry_scroll_x.set)
    entry_tree.bind("<<TreeviewSelect>>", on_entry_tree_select)
    entry_tree.bind("<Button-1>", on_entry_tree_click)
    entry_tree.bind("<Double-1>", on_entry_tree_double_click)
    entry_filter_var.trace_add("write", lambda *args: populate_entry_tree(current_url_record()))

    details_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
    details_frame.tkraise()
    playlist_frame.grid_remove()
    show_context_for_record(None)

    url_context_menu = tk.Menu(dialog, tearoff=False)
    url_context_menu.add_command(label="Toggle Preview for Highlighted Row", command=lambda: toggle_url_flag(url_context_iid.get("value") or url_tree.focus(), "preview"))
    url_context_menu.add_command(label="Toggle Include for Highlighted Row", command=lambda: toggle_url_flag(url_context_iid.get("value") or url_tree.focus(), "include"))
    url_context_menu.add_separator()
    url_context_menu.add_command(label="Preview Highlighted URL", command=preview_highlighted_url)
    url_context_menu.add_command(label="Start Highlighted URL", command=start_highlighted_url)
    url_context_menu.add_command(label="Queue Highlighted URL", command=queue_highlighted_url)
    url_context_menu.add_command(label="Open Highlighted URL", command=open_highlighted_url)
    url_context_menu.add_separator()
    url_context_menu.add_command(label="Copy Highlighted URL", command=lambda: copy_text_to_clipboard(highlighted_url_value()[1], "highlighted URL"))
    url_context_menu.add_command(label="Copy Highlighted JSON", command=copy_selected_record_json)
    url_context_menu.add_command(label="Export Highlighted JSON...", command=export_highlighted_url_json)
    url_context_menu.add_separator()
    url_context_menu.add_command(label="Preview All On", command=lambda: set_all_url_preview_flags("preview", True))
    url_context_menu.add_command(label="Preview All Off", command=lambda: set_all_url_preview_flags("preview", False))
    url_context_menu.add_command(label="Include All", command=lambda: set_all_url_preview_flags("include", True))
    url_context_menu.add_command(label="Exclude All", command=lambda: set_all_url_preview_flags("include", False))

    entry_context_menu = tk.Menu(dialog, tearoff=False)
    entry_context_menu.add_command(label="Toggle Include for Highlighted Item", command=toggle_highlighted_entry_include)
    entry_context_menu.add_command(label="Include All Items", command=lambda: set_all_current_item_includes(True))
    entry_context_menu.add_command(label="Exclude All Items", command=lambda: set_all_current_item_includes(False))
    entry_context_menu.add_command(label="Invert Item Includes", command=invert_current_item_includes)
    entry_context_menu.add_separator()
    entry_context_menu.add_command(label="Start Highlighted Item", command=start_highlighted_entry)
    entry_context_menu.add_command(label="Queue Highlighted Item", command=queue_highlighted_entry)
    entry_context_menu.add_command(label="Open Highlighted Item URL", command=open_highlighted_entry_url)
    entry_context_menu.add_command(label="Copy Highlighted Item JSON", command=copy_highlighted_entry_json)
    entry_context_menu.add_command(label="Export Highlighted Item JSON...", command=export_highlighted_entry_json)
    entry_context_menu.add_command(label="Copy Included Item URL(s)", command=lambda: copy_text_to_clipboard("\n".join(urls_from_entries(included_entry_records())), "included playlist item URL(s)"))
    entry_context_menu.add_separator()
    entry_context_menu.add_command(label="Start Included Items", command=lambda: start_urls_now(urls_from_entries(included_entry_records()), "included playlist item URL(s)", playlist_name=get_current_playlist_name()))
    entry_context_menu.add_command(label="Queue Included Items", command=lambda: queue_urls(urls_from_entries(included_entry_records()), "included playlist item URL(s)", playlist_name=get_current_playlist_name()))

    url_tree.bind("<Button-3>", lambda event: show_tree_context_menu(event, url_tree, url_context_menu, url_context_iid))
    entry_tree.bind("<Button-3>", lambda event: show_tree_context_menu(event, entry_tree, entry_context_menu, entry_context_iid))

    extra_action_frame = ttk.Frame(url_action_frame)
    extra_action_frame.pack(side="left", padx=(6, 0))
    pack_preview_button(ttk.Button(extra_action_frame, text="Preview ✓ All", command=lambda: set_all_url_preview_flags("preview", True)))
    pack_preview_button(ttk.Button(extra_action_frame, text="Preview ☐ All", command=lambda: set_all_url_preview_flags("preview", False)))
    pack_preview_button(ttk.Button(extra_action_frame, text="Include ✓ All", command=lambda: set_all_url_preview_flags("include", True)))
    pack_preview_button(ttk.Button(extra_action_frame, text="Include ☐ All", command=lambda: set_all_url_preview_flags("include", False)))

    try:
        configure_tk_widget_theme(dialog, get_theme_colors())
    except Exception:
        pass

    update_action_states()
    if has_preview_urls:
        status_var.set(f"Loaded {len(urls)} URL(s). Use Preview All/Checked to gather metadata; Include checkmarks control Start/Queue Included actions.")
    else:
        status_var.set(f"{no_urls_message} Add URLs in the URL box or select Input File(s) to enable URL Preview.")

    playlist_preview_tab_loaded = True
    playlist_preview_loaded_signature = playlist_preview_source_signature

def check_impersonate_targets():
    yt_dlp_path = yt_dlp_path_var.get().strip()

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        messagebox.showerror("yt-dlp not found", "yt-dlp path is missing or invalid.")
        return

    target_status_var.set("Impersonate targets: Checking...")

    def worker():
        cmd = [
            yt_dlp_path,
            "--list-impersonate-targets",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )

            combined_output = "\n".join(
                part for part in [result.stdout, result.stderr] if part
            )

            if show_all_impersonate_targets_var.get():
                targets = parse_all_impersonate_targets(combined_output)
                target_label = "target(s)"
                log_title = "Available impersonate targets"
            else:
                targets = parse_windows_impersonate_targets(combined_output)
                target_label = "Windows target(s)"
                log_title = "Available Windows impersonate targets"

            values = DEFAULT_IMPERSONATE_TARGETS.copy()
            for target in targets:
                if is_valid_impersonate_target_label(target) and target not in values:
                    values.append(target)

            root.after(0, update_impersonate_menu, values)
            root.after(0, target_status_var.set, f"Impersonate targets: Found {len(values) - 1} {target_label}")
            root.after(0, append_log, f"\n{log_title}:\n" + "\n".join(values) + "\n")

        except Exception as e:
            root.after(0, target_status_var.set, "Impersonate targets: Check failed")
            root.after(0, messagebox.showerror, "Impersonate check failed", str(e))

    threading.Thread(target=worker, daemon=True).start()


def is_valid_impersonate_target_label(value):
    value = (value or "").strip()

    if not value:
        return False

    lowered = value.lower()

    # Filter yt-dlp status/log lines such as [info], [debug], [warning], etc.
    if lowered.startswith("["):
        return False

    target_token = normalize_impersonate_target(value)

    if not target_token:
        return False

    if target_token.startswith("["):
        return False

    if target_token in {"target", "client", "source", "os", "none"}:
        return False

    browser_prefixes = (
        "chrome",
        "edge",
        "firefox",
        "brave",
        "opera",
        "vivaldi",
        "safari",
    )

    return target_token.startswith(browser_prefixes)


def parse_windows_impersonate_targets(output):
    targets = []
    seen = set()

    browser_prefixes = (
        "chrome",
        "edge",
        "firefox",
        "brave",
        "opera",
        "vivaldi",
    )

    for raw_line in output.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        lowered = line.lower()

        if lowered.startswith("["):
            continue

        if "client" in lowered and "os" in lowered:
            continue

        if "target" in lowered and "source" in lowered:
            continue

        if set(line) <= {"-", " ", "\t"}:
            continue

        parts = line.split()
        if not parts:
            continue

        candidate = parts[0].strip().lower()

        if not candidate.startswith(browser_prefixes):
            continue

        if "windows" not in lowered and "win" not in lowered:
            continue

        if candidate not in seen:
            seen.add(candidate)
            targets.append(candidate)

    return targets


def parse_all_impersonate_targets(output):
    targets = []
    seen = set()

    browser_prefixes = (
        "chrome",
        "edge",
        "firefox",
        "brave",
        "opera",
        "vivaldi",
        "safari",
    )

    os_tokens = (
        "windows",
        "win",
        "macos",
        "mac",
        "linux",
        "ubuntu",
        "android",
        "ios",
        "iphone",
        "ipad",
    )

    for raw_line in output.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        lowered = line.lower()

        # Skip yt-dlp log/info/debug lines. These are not impersonation targets.
        if lowered.startswith("["):
            continue

        if "client" in lowered and "os" in lowered:
            continue

        if "target" in lowered and "source" in lowered:
            continue

        if set(line) <= {"-", " ", "\t"}:
            continue

        parts = line.split()
        if not parts:
            continue

        candidate = parts[0].strip().lower()

        if candidate.startswith("["):
            continue

        if not candidate.startswith(browser_prefixes):
            continue

        os_value = ""

        for part in parts[1:]:
            clean_part = part.strip().strip("|").strip(",").strip().lower()
            if any(token in clean_part for token in os_tokens):
                os_value = clean_part
                break

        display = f"{candidate} ({os_value})" if os_value else candidate

        # De-duplicate by the display label so the same target can be shown
        # separately for different OS values if yt-dlp reports it that way.
        if display not in seen:
            seen.add(display)
            targets.append(display)

    return targets


def update_impersonate_menu(values):
    clean_values = []

    for value in values:
        if value == "None" or is_valid_impersonate_target_label(value):
            if value not in clean_values:
                clean_values.append(value)

    if "None" not in clean_values:
        clean_values.insert(0, "None")

    impersonate_menu["values"] = clean_values

    current = impersonate_var.get()
    if current not in clean_values:
        impersonate_var.set("None")


def export_browser_cookies_dialog():
    yt_dlp_path = yt_dlp_path_var.get().strip()

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        messagebox.showerror("yt-dlp not found", "yt-dlp path is missing or invalid.")
        return

    dialog = tk.Toplevel(root)
    dialog.title("Export Browser Cookies")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    browser_var = tk.StringVar(value="chrome")
    output_cookie_var = tk.StringVar(value=os.path.join(ROOT, "cookies.txt"))
    update_main_cookie_path_var = tk.BooleanVar(value=True)

    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Browser").grid(row=0, column=0, sticky="w", pady=4)
    browser_menu = ttk.Combobox(
        frame,
        textvariable=browser_var,
        values=BROWSER_COOKIE_OPTIONS,
        state="readonly",
        width=30,
    )
    browser_menu.grid(row=0, column=1, columnspan=2, sticky="ew", padx=6, pady=4)

    ttk.Label(frame, text="Output cookies file").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=output_cookie_var, width=55).grid(
        row=1,
        column=1,
        sticky="ew",
        padx=6,
        pady=4,
    )

    def browse_cookie_output():
        path = filedialog.asksaveasfilename(
            title="Save cookies file",
            defaultextension=".txt",
            initialfile="cookies.txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if path:
            output_cookie_var.set(path)

    ttk.Button(frame, text="Browse...", command=browse_cookie_output).grid(
        row=1,
        column=2,
        sticky="e",
        pady=4,
    )

    ttk.Checkbutton(
        frame,
        text="Update main Cookies File field after export",
        variable=update_main_cookie_path_var,
    ).grid(
        row=2,
        column=0,
        columnspan=3,
        sticky="w",
        pady=(8, 4),
    )

    note = (
        "This uses yt-dlp's built-in --cookies-from-browser method.\n"
        "Cookies files can function like logged-in browser sessions. Do not share them unencrypted.\n"
        "Run this as the same Windows user that is signed into the browser.\n"
        "Close the browser first if the export fails due to locked profile files.\n\n"
        "Warning: browser cookie export does not work reliably on every site. "
        "The output log may show site-specific errors or warnings even when a cookies file is created.\n\n"
        "The reference URL is hardcoded to https://example.com/ for generic browser-cookie export. "
        "yt-dlp is run with --simulate and --no-playlist."
    )

    ttk.Label(frame, text=note, justify="left").grid(
        row=3,
        column=0,
        columnspan=3,
        sticky="w",
        pady=(8, 8),
    )

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=4, column=0, columnspan=3, sticky="e", pady=(8, 0))

    def begin_export():
        browser = browser_var.get().strip()
        output_cookie_file = output_cookie_var.get().strip()
        update_main_cookie_path = update_main_cookie_path_var.get()

        if not browser:
            messagebox.showerror("Missing browser", "Choose a browser.")
            return

        if not output_cookie_file:
            messagebox.showerror("Missing output file", "Choose an output cookies file.")
            return

        dialog.destroy()
        export_browser_cookies(browser, output_cookie_file, update_main_cookie_path)

    ttk.Button(button_frame, text="Export", command=begin_export).pack(side="left", padx=6)
    ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=6)

    frame.columnconfigure(1, weight=1)
    dialog.update_idletasks()

    x = root.winfo_x() + (root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")


def output_says_cookies_exported(output_text):
    text = output_text.lower()

    patterns = [
        "extracting cookies from",
        "extracted cookies from",
        "exporting cookies",
        "cookies from browser",
        "extracting cookies",
    ]

    if any(pattern in text for pattern in patterns):
        return True

    if "extracted" in text and "cookies" in text:
        return True

    if "cookie" in text and ("saved" in text or "written" in text or "exported" in text):
        return True

    return False


def export_browser_cookies(browser, output_cookie_file, update_main_cookie_path=True):
    yt_dlp_path = yt_dlp_path_var.get().strip()
    reference_url = "https://example.com/"

    append_log(
        "\nStarting browser cookie export...\n"
        f"Browser: {browser}\n"
        f"Reference URL: {reference_url}\n"
        f"Output file: {output_cookie_file}\n"
        f"Update main Cookies File field: {update_main_cookie_path}\n\n"
    )

    set_status("Exporting browser cookies...")

    def worker():
        cmd = [
            yt_dlp_path,
            "--cookies-from-browser",
            browser,
            "--cookies",
            output_cookie_file,
            "--skip-download",
            "--simulate",
            "--no-playlist",
            "--ignore-errors",
            reference_url,
        ]

        try:
            result = subprocess.Popen(
                cmd,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            output_lines = []

            if result.stdout:
                for line in result.stdout:
                    output_lines.append(line)
                    root.after(0, append_log, line)

            exit_code = result.wait()
            combined_output = "".join(output_lines)

            cookies_file_exists = (
                os.path.isfile(output_cookie_file)
                and os.path.getsize(output_cookie_file) > 0
            )

            yt_dlp_says_cookies_exported = output_says_cookies_exported(combined_output)
            cookies_exported = cookies_file_exists or yt_dlp_says_cookies_exported

            if cookies_exported:
                if cookies_file_exists and update_main_cookie_path:
                    root.after(0, cookies_file_var.set, output_cookie_file)
                    root.after(0, save_settings, False)

                if exit_code == 0:
                    root.after(0, set_status, "Browser cookies exported")
                    root.after(
                        0,
                        messagebox.showinfo,
                        "Cookies exported",
                        f"Cookies exported to:\n\n{output_cookie_file}\n\n"
                        + (
                            "The Cookies File field has been updated."
                            if cookies_file_exists and update_main_cookie_path
                            else "The Cookies File field was not changed."
                        ),
                    )
                else:
                    root.after(0, set_status, f"Browser cookies exported; yt-dlp exited with code {exit_code}")
                    root.after(
                        0,
                        append_log,
                        f"\nCookie export appears successful, but yt-dlp exited with code {exit_code} "
                        "while processing the reference URL. Suppressing warning dialog because cookies were exported.\n",
                    )

                    if cookies_file_exists and update_main_cookie_path:
                        root.after(
                            0,
                            append_log,
                            f"Main Cookies File field updated to: {output_cookie_file}\n",
                        )
                    elif not update_main_cookie_path:
                        root.after(
                            0,
                            append_log,
                            "Main Cookies File field was not changed because the export dialog checkbox was unchecked.\n",
                        )
            else:
                root.after(0, set_status, f"Cookie export failed with exit code {exit_code}")
                root.after(
                    0,
                    messagebox.showwarning,
                    "Cookie export failed",
                    f"yt-dlp exited with code {exit_code}, and no non-empty cookies file was created. Review the output log.",
                )

        except Exception as e:
            root.after(0, set_status, "Cookie export error")
            root.after(0, messagebox.showerror, "Cookie export error", str(e))

    threading.Thread(target=worker, daemon=True).start()



def parse_download_speed_limit_to_bytes(value):
    value = str(value or "").strip()

    if not value or value.lower() == "disabled":
        return None

    cleaned = value.strip().lower()
    cleaned = cleaned.replace("/sec", "/s")
    cleaned = cleaned.replace("per second", "/s")
    cleaned = cleaned.replace("bytes", "b")
    cleaned = cleaned.replace("byte", "b")
    cleaned = cleaned.replace(" ", "")

    match = re.fullmatch(r"(\d+(?:\.\d+)?)(kib/s|mib/s|gib/s|kib|mib|gib|ki|mi|gi|kb/s|mb/s|gb/s|kb|mb|gb|k|m|g|b/s|b)?", cleaned)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2) or "b"

    multiplier_map = {
        "b": 1,
        "b/s": 1,
        "k": 1024,
        "kb": 1024,
        "kb/s": 1024,
        "ki": 1024,
        "kib": 1024,
        "kib/s": 1024,
        "m": 1024 ** 2,
        "mb": 1024 ** 2,
        "mb/s": 1024 ** 2,
        "mi": 1024 ** 2,
        "mib": 1024 ** 2,
        "mib/s": 1024 ** 2,
        "g": 1024 ** 3,
        "gb": 1024 ** 3,
        "gb/s": 1024 ** 3,
        "gi": 1024 ** 3,
        "gib": 1024 ** 3,
        "gib/s": 1024 ** 3,
    }

    multiplier = multiplier_map.get(unit)
    if not multiplier:
        return None

    bytes_value = int(round(number * multiplier))

    if bytes_value < DOWNLOAD_SPEED_MIN_BYTES or bytes_value > DOWNLOAD_SPEED_MAX_BYTES:
        return None

    return bytes_value


def format_download_speed_limit_bytes(bytes_value):
    try:
        bytes_value = int(bytes_value)
    except Exception:
        bytes_value = DOWNLOAD_SPEED_DEFAULT_BYTES

    bytes_value = max(DOWNLOAD_SPEED_MIN_BYTES, min(DOWNLOAD_SPEED_MAX_BYTES, bytes_value))

    if bytes_value >= 1024 ** 3:
        value = bytes_value / (1024 ** 3)
        unit = "GiB/s"
    elif bytes_value >= 1024 ** 2:
        value = bytes_value / (1024 ** 2)
        unit = "MiB/s"
    else:
        value = bytes_value / 1024
        unit = "KiB/s"

    if abs(value - round(value)) < 0.005:
        number = str(int(round(value)))
    else:
        number = f"{value:.2f}".rstrip("0").rstrip(".")

    return f"{number} {unit}"


def normalize_download_speed_limit_value(value):
    if str(value or "").strip().lower() == "disabled":
        return "disabled"

    bytes_value = parse_download_speed_limit_to_bytes(value)
    if bytes_value is None:
        return ""

    return format_download_speed_limit_bytes(bytes_value)


def download_speed_limit_to_ytdlp_value(value):
    if str(value or "").strip().lower() == "disabled":
        return "disabled"

    bytes_value = parse_download_speed_limit_to_bytes(value)
    if bytes_value is None:
        return ""

    return str(int(bytes_value))


def parse_binary_size_to_bytes(value, min_bytes=1024, max_bytes=1024 ** 3):
    value = str(value or "").strip()

    if not value or value.lower() == "disabled":
        return None

    cleaned = value.strip().lower()
    cleaned = cleaned.replace("bytes", "b").replace("byte", "b")
    cleaned = cleaned.replace(" ", "")

    match = re.fullmatch(r"(\d+(?:\.\d+)?)(kib|mib|gib|ki|mi|gi|kb|mb|gb|k|m|g|b)?", cleaned)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2) or "b"
    multiplier_map = {
        "b": 1,
        "k": 1024, "kb": 1024, "ki": 1024, "kib": 1024,
        "m": 1024 ** 2, "mb": 1024 ** 2, "mi": 1024 ** 2, "mib": 1024 ** 2,
        "g": 1024 ** 3, "gb": 1024 ** 3, "gi": 1024 ** 3, "gib": 1024 ** 3,
    }

    multiplier = multiplier_map.get(unit)
    if not multiplier:
        return None

    bytes_value = int(round(number * multiplier))
    if bytes_value < min_bytes or bytes_value > max_bytes:
        return None

    return bytes_value


def format_binary_size(bytes_value):
    try:
        bytes_value = int(bytes_value)
    except Exception:
        bytes_value = 10 * 1024 ** 2

    if bytes_value >= 1024 ** 3:
        value = bytes_value / (1024 ** 3)
        unit = "GiB"
    elif bytes_value >= 1024 ** 2:
        value = bytes_value / (1024 ** 2)
        unit = "MiB"
    else:
        value = bytes_value / 1024
        unit = "KiB"

    if abs(value - round(value)) < 0.005:
        number = str(int(round(value)))
    else:
        number = f"{value:.2f}".rstrip("0").rstrip(".")

    return f"{number} {unit}"


def normalize_binary_size_value(value, default_value="10 MiB"):
    bytes_value = parse_binary_size_to_bytes(value)
    if bytes_value is None:
        bytes_value = parse_binary_size_to_bytes(default_value) or (10 * 1024 ** 2)

    return format_binary_size(bytes_value)


def binary_size_to_ytdlp_value(value):
    bytes_value = parse_binary_size_to_bytes(value)
    if bytes_value is None:
        return ""

    return str(int(bytes_value))


def normalize_retry_behavior(value):
    value = str(value or "").strip().lower()
    if value in {"light", "normal", "aggressive"}:
        return value
    return "normal"


def normalize_format_strategy(value):
    value = str(value or "").strip().lower()
    if value in {"best", "prefer_mp4", "strict_mp4", "audio_only", "low_bandwidth"}:
        return value
    return "best"


def normalize_playlist_order(value):
    value = str(value or "").strip().lower()
    if value in {"normal", "reverse", "random"}:
        return value
    return "normal"


def script_playlist_order(value):
    return {
        "normal": "Normal",
        "reverse": "Reverse",
        "random": "Random",
    }.get(normalize_playlist_order(value), "Normal")


def normalize_optional_positive_int_string(value):
    value = str(value or "").strip()

    if not value:
        return ""

    if not value.isdigit():
        return ""

    parsed = int(value)
    if parsed <= 0:
        return ""

    return str(parsed)


def normalize_playlist_items(value):
    value = re.sub(r"\s+", "", str(value or ""))

    if not value:
        return ""

    if re.fullmatch(r"[0-9,:\-]+", value):
        return value

    return ""


def normalize_gui_cache_mode(value):
    value = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")

    if value in {"off", "after_each_url", "after_run"}:
        return value

    if value in {"after_each", "each_url"}:
        return "after_each_url"

    return "after_run"


def display_gui_cache_mode(value):
    return {
        "off": "Off",
        "after_each_url": "After each URL",
        "after_run": "After run",
    }.get(normalize_gui_cache_mode(value), "After run")


def normalize_manifest_mode(value):
    value = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")

    if value in {"full", "run_only"}:
        return value

    if value in {"this_run", "run"}:
        return "run_only"

    return "full"


def display_manifest_mode(value):
    return {
        "full": "Full",
        "run_only": "This run",
    }.get(normalize_manifest_mode(value), "Full")


def script_gui_cache_mode(value):
    return {
        "off": "Off",
        "after_each_url": "AfterEachUrl",
        "after_run": "AfterRun",
    }.get(normalize_gui_cache_mode(value), "AfterRun")


def script_manifest_mode(value):
    return {
        "full": "Full",
        "run_only": "RunOnly",
    }.get(normalize_manifest_mode(value), "Full")


def download_speed_bytes_to_slider(bytes_value):
    try:
        bytes_value = int(bytes_value)
    except Exception:
        bytes_value = DOWNLOAD_SPEED_DEFAULT_BYTES

    bytes_value = max(DOWNLOAD_SPEED_MIN_BYTES, min(DOWNLOAD_SPEED_MAX_BYTES, bytes_value))
    min_log = math.log(DOWNLOAD_SPEED_MIN_BYTES)
    max_log = math.log(DOWNLOAD_SPEED_MAX_BYTES)
    value_log = math.log(bytes_value)
    ratio = (value_log - min_log) / (max_log - min_log)
    return max(0, min(DOWNLOAD_SPEED_SLIDER_MAX, ratio * DOWNLOAD_SPEED_SLIDER_MAX))


def download_speed_slider_to_bytes(slider_value):
    try:
        slider_value = float(slider_value)
    except Exception:
        slider_value = download_speed_bytes_to_slider(DOWNLOAD_SPEED_DEFAULT_BYTES)

    ratio = max(0.0, min(float(DOWNLOAD_SPEED_SLIDER_MAX), slider_value)) / float(DOWNLOAD_SPEED_SLIDER_MAX)
    min_log = math.log(DOWNLOAD_SPEED_MIN_BYTES)
    max_log = math.log(DOWNLOAD_SPEED_MAX_BYTES)
    bytes_value = int(round(math.exp(min_log + ratio * (max_log - min_log))))

    # Keep the stored value readable and stable by rounding to the nearest KiB.
    bytes_value = int(round(bytes_value / 1024.0) * 1024)
    return max(DOWNLOAD_SPEED_MIN_BYTES, min(DOWNLOAD_SPEED_MAX_BYTES, bytes_value))


download_speed_limit_syncing = False


def set_download_speed_limit_control_state():
    try:
        state = "normal" if download_speed_limit_enabled_var.get() else "disabled"
        download_speed_slider.configure(state=state)
        download_speed_entry.configure(state=state)
    except Exception:
        pass


def sync_download_speed_limit_controls_from_var(show_errors=False):
    global download_speed_limit_syncing

    if download_speed_limit_syncing:
        return

    raw_value = download_speed_limit_var.get().strip()
    bytes_value = parse_download_speed_limit_to_bytes(raw_value)

    download_speed_limit_syncing = True
    try:
        if raw_value.lower() == "disabled" or not raw_value:
            # Backward compatibility for older saved values. Keep a usable last value
            # instead of leaving the textbox as "disabled".
            download_speed_limit_enabled_var.set(False)
            bytes_value = DOWNLOAD_SPEED_DEFAULT_BYTES
            download_speed_limit_var.set(format_download_speed_limit_bytes(bytes_value))
            download_speed_slider_var.set(download_speed_bytes_to_slider(bytes_value))
        elif bytes_value is None:
            if show_errors:
                messagebox.showerror(
                    "Invalid speed limit",
                    "Enter a value from 1 KiB/s to 1 GiB/s, such as 750 KiB/s, 2 MiB/s, or 0.5 GiB/s.",
                )
            bytes_value = DOWNLOAD_SPEED_DEFAULT_BYTES
            download_speed_limit_enabled_var.set(False)
            download_speed_limit_var.set(format_download_speed_limit_bytes(bytes_value))
            download_speed_slider_var.set(download_speed_bytes_to_slider(bytes_value))
        else:
            download_speed_limit_var.set(format_download_speed_limit_bytes(bytes_value))
            download_speed_slider_var.set(download_speed_bytes_to_slider(bytes_value))
    finally:
        download_speed_limit_syncing = False

    set_download_speed_limit_control_state()
    update_capture_options_summary()


def on_download_speed_limit_enabled_changed():
    global download_speed_limit_syncing

    download_speed_limit_syncing = True
    try:
        bytes_value = parse_download_speed_limit_to_bytes(download_speed_limit_var.get())
        if bytes_value is None:
            bytes_value = DOWNLOAD_SPEED_DEFAULT_BYTES

        download_speed_limit_var.set(format_download_speed_limit_bytes(bytes_value))
        download_speed_slider_var.set(download_speed_bytes_to_slider(bytes_value))
    finally:
        download_speed_limit_syncing = False

    set_download_speed_limit_control_state()
    update_capture_options_summary()


def on_download_speed_slider_changed(value=None):
    global download_speed_limit_syncing

    if download_speed_limit_syncing or not download_speed_limit_enabled_var.get():
        return

    bytes_value = download_speed_slider_to_bytes(value if value is not None else download_speed_slider_var.get())

    download_speed_limit_syncing = True
    try:
        download_speed_limit_var.set(format_download_speed_limit_bytes(bytes_value))
    finally:
        download_speed_limit_syncing = False

    update_capture_options_summary()


def on_download_speed_entry_commit(event=None):
    sync_download_speed_limit_controls_from_var(show_errors=True)



def update_throttled_rate_state(*args):
    try:
        state = "normal" if throttle_detection_enabled_var.get() else "disabled"
        throttled_rate_entry.configure(state=state)
    except Exception:
        pass


def update_http_chunk_size_state(*args):
    try:
        state = "normal" if http_chunk_size_enabled_var.get() else "disabled"
        http_chunk_size_entry.configure(state=state)
    except Exception:
        pass


def on_throttled_rate_commit(event=None):
    normalized = normalize_download_speed_limit_value(throttled_rate_var.get())
    if not normalized or normalized == "disabled":
        messagebox.showerror("Invalid throttled rate", "Enter a value from 1 KiB/s to 1 GiB/s.")
        throttled_rate_var.set(DEFAULTS["throttled_rate"])
    else:
        throttled_rate_var.set(normalized)
    update_capture_options_summary()


def on_http_chunk_size_commit(event=None):
    normalized = normalize_binary_size_value(http_chunk_size_var.get(), DEFAULTS["http_chunk_size"])
    http_chunk_size_var.set(normalized)
    update_capture_options_summary()


def update_capture_options_summary(*args):
    try:
        capture_mode = normalize_capture_mode(capture_mode_var.get())

        if capture_mode == "metadata_only":
            mode = "Metadata only"
        elif capture_mode == "media_only":
            mode = "Media only"
        elif capture_mode == "media_embedded":
            mode = "Media + embedded"
        else:
            mode = "Media + sidecars"

        include_playlist = source_scope_var.get() == "include_playlist"
        scope = "Include playlist" if include_playlist else "Single item"

        playlist_bits = []
        if include_playlist:
            if playlist_items_enabled_var.get():
                playlist_items = normalize_playlist_items(playlist_items_var.get())
                playlist_bits.append(f"items {playlist_items}" if playlist_items else "items invalid")

            if playlist_order_enabled_var.get():
                playlist_order = normalize_playlist_order(playlist_order_var.get())
                playlist_bits.append(f"order {playlist_order}")

            if max_playlist_items_enabled_var.get():
                max_playlist_items = normalize_optional_positive_int_string(max_playlist_items_var.get())
                playlist_bits.append(f"max {max_playlist_items}" if max_playlist_items else "max invalid")

            if break_on_existing_var.get():
                playlist_bits.append("break existing")

            if skip_playlist_after_errors_enabled_var.get():
                skip_errors = normalize_optional_positive_int_string(skip_playlist_after_errors_var.get())
                playlist_bits.append(f"skip after {skip_errors} errors" if skip_errors else "skip errors invalid")

        playlist_text = f"playlist {'; '.join(playlist_bits)}" if playlist_bits else ("playlist all" if include_playlist else "playlist off")

        archive_names = {
            "use": "case archive",
            "ignore": "ignore archive",
            "force": "force re-capture",
        }
        archive_text = archive_names.get(archive_mode_var.get(), "case archive")

        rate_names = {
            "none": "none",
            "fast": "fast",
            "normal": "normal",
            "cautious": "cautious",
        }
        rate_text = rate_names.get(rate_limit_var.get(), "normal")
        format_names = {
            "best": "best",
            "prefer_mp4": "prefer MP4",
            "strict_mp4": "strict MP4",
            "audio_only": "audio only",
            "low_bandwidth": "low bandwidth",
        }
        format_text = format_names.get(format_strategy_var.get(), "best")
        rate_text = f"{rate_text}; {format_text}"
        speed_limit = normalize_download_speed_limit_value(download_speed_limit_var.get())
        if download_speed_limit_enabled_var.get():
            speed_text = f"speed {speed_limit or 'invalid'}"
        else:
            speed_text = "speed unlimited"
        concurrency_text = f"{get_concurrent_capture_limit()} queue concurrent"
        fragments_text = f"{get_concurrent_fragment_limit()} fragment worker"
        if get_concurrent_fragment_limit() != 1:
            fragments_text += "s"
        resolution_text = "best" if max_resolution_var.get() == "best" else f"max {max_resolution_var.get()}p"
        cache_names = {
            "off": "cache off",
            "after_each_url": "cache each URL",
            "after_run": "cache after run",
        }
        manifest_names = {
            "full": "full manifest",
            "run_only": "run manifest",
        }
        cache_text = cache_names.get(normalize_gui_cache_mode(gui_cache_mode_var.get()), "cache after run")
        manifest_text = manifest_names.get(normalize_manifest_mode(manifest_mode_var.get()), "full manifest")
        retry_text = f"retry {normalize_retry_behavior(retry_behavior_var.get())}"
        throttle_text = f"throttle {throttled_rate_var.get()}" if throttle_detection_enabled_var.get() else "throttle off"
        chunk_text = f"chunk {http_chunk_size_var.get()}" if http_chunk_size_enabled_var.get() else "chunks auto"
        failure_text = "stop on fail" if failure_handling_var.get() == "stop" else "continue on fail"

        artifacts = []

        if write_info_json_var.get():
            artifacts.append("JSON")
        if write_source_link_var.get():
            artifacts.append("link")
        if write_description_var.get():
            artifacts.append("description")
        if write_thumbnail_var.get():
            artifacts.append("thumbnail")
        if write_subs_var.get():
            artifacts.append("subs")
        if write_auto_subs_var.get():
            artifacts.append("auto-subs")
        if write_comments_var.get():
            artifacts.append("comments")
        if prefer_mp4_var.get():
            artifacts.append("MP4")
        if save_playlist_metadata_var.get() and source_scope_var.get() == "include_playlist":
            artifacts.append("playlist metadata")
        if generate_url_shortcuts_var.get():
            artifacts.append("URL shortcuts")
        if keep_partials_var.get():
            artifacts.append("partials")

        embeds = []
        if embed_metadata_var.get():
            embeds.append("metadata")
        if embed_thumbnail_var.get():
            embeds.append("thumbnail")
        if embed_subs_var.get():
            embeds.append("subs")
        if embed_chapters_var.get():
            embeds.append("chapters")
        if embed_info_json_var.get():
            embeds.append("info JSON")

        date_filters = []
        if date_after_enabled_var.get():
            date_filters.append("after")
        if date_before_enabled_var.get():
            date_filters.append("before")

        if date_filters:
            artifacts.append("date " + "/".join(date_filters))

        if capture_mode == "media_only":
            artifact_text = "metadata options ignored"
        elif capture_mode == "media_embedded":
            embed_text = ", ".join(embeds) if embeds else "no embeds selected"
            artifact_text = f"sidecars ignored; embeds: {embed_text}"
        elif capture_mode == "metadata_only":
            sidecar_text = ", ".join(artifacts) if artifacts else "no sidecars"
            artifact_text = f"{sidecar_text}; embeds ignored"
        else:
            sidecar_text = ", ".join(artifacts) if artifacts else "no sidecars"
            embed_text = ", ".join(embeds) if embeds else "embeds off"
            artifact_text = f"{sidecar_text}; embeds: {embed_text}"

        capture_options_summary_var.set(f"{mode}; {scope}; {playlist_text}; {archive_text}; {resolution_text}; {cache_text}; {manifest_text}; {rate_text}; {speed_text}; {retry_text}; {throttle_text}; {chunk_text}; {concurrency_text}; {fragments_text}; {failure_text}; {artifact_text}")

        try:
            update_metadata_options_state()
            update_playlist_options_state()
        except Exception:
            pass
    except Exception:
        pass


def hide_capture_options_panel(save=False):
    try:
        if capture_options_panel.winfo_ismapped():
            capture_options_panel.grid_remove()
    except Exception:
        pass

    capture_options_button.config(text="Capture Options ▾")

    if save:
        update_capture_options_summary()
        save_settings(show_popup=False)


def hide_metadata_options_panel(save=False):
    try:
        if metadata_options_panel.winfo_ismapped():
            metadata_options_panel.grid_remove()
    except Exception:
        pass

    metadata_options_button.config(text="Metadata Options ▾")

    if save:
        update_capture_options_summary()
        save_settings(show_popup=False)


def hide_advanced_options_panel(save=False):
    try:
        if advanced_options_panel.winfo_ismapped():
            advanced_options_panel.grid_remove()
    except Exception:
        pass

    advanced_options_button.config(text="Advanced Options ▾")

    if save:
        update_capture_options_summary()
        save_settings(show_popup=False)


def hide_pacing_options_panel(save=False):
    try:
        if pacing_options_panel.winfo_ismapped():
            pacing_options_panel.grid_remove()
    except Exception:
        pass

    pacing_options_button.config(text="Pacing Options ▾")

    if save:
        update_capture_options_summary()
        save_settings(show_popup=False)


def toggle_capture_options_panel():
    if capture_options_panel.winfo_ismapped():
        hide_capture_options_panel(save=True)
        return

    hide_metadata_options_panel(save=True)
    hide_advanced_options_panel(save=True)
    hide_pacing_options_panel(save=True)
    update_capture_options_summary()
    capture_options_panel.grid(
        row=8,
        column=0,
        columnspan=4,
        rowspan=8,
        sticky="nsew",
        padx=0,
        pady=(8, 0),
    )
    capture_options_panel.tkraise()
    capture_options_button.config(text="Capture Options ▴")


def close_capture_options_panel():
    hide_capture_options_panel(save=True)


def toggle_metadata_options_panel():
    if metadata_options_panel.winfo_ismapped():
        hide_metadata_options_panel(save=True)
        return

    hide_capture_options_panel(save=True)
    hide_advanced_options_panel(save=True)
    hide_pacing_options_panel(save=True)
    update_capture_options_summary()
    metadata_options_panel.grid(
        row=8,
        column=0,
        columnspan=4,
        rowspan=8,
        sticky="nsew",
        padx=0,
        pady=(8, 0),
    )
    metadata_options_panel.tkraise()
    metadata_options_button.config(text="Metadata Options ▴")


def close_metadata_options_panel():
    hide_metadata_options_panel(save=True)


def update_metadata_options_state():
    try:
        capture_mode = normalize_capture_mode(capture_mode_var.get())
        sidecars_enabled = capture_mode in {"media", "metadata_only"}
        embeds_enabled = capture_mode in {"media", "media_embedded"}

        sidecar_state = "normal" if sidecars_enabled else "disabled"
        embed_state = "normal" if embeds_enabled else "disabled"

        for widget in globals().get("sidecar_option_widgets", []):
            try:
                widget.configure(state=sidecar_state)
            except Exception:
                pass

        for widget in globals().get("embed_option_widgets", []):
            try:
                widget.configure(state=embed_state)
            except Exception:
                pass

        try:
            playlist_metadata_check.configure(state=sidecar_state)
        except Exception:
            pass
    except Exception:
        pass


def update_playlist_options_state():
    try:
        playlist_enabled = source_scope_var.get() == "include_playlist"

        for item in globals().get("playlist_option_widgets", []):
            try:
                if len(item) == 2:
                    widget, widget_type = item
                    controlling_var = None
                else:
                    widget, widget_type, controlling_var = item

                control_enabled = playlist_enabled
                if controlling_var is not None:
                    control_enabled = playlist_enabled and bool(controlling_var.get())

                if widget_type == "combo":
                    widget.configure(state="readonly" if control_enabled else "disabled")
                else:
                    widget.configure(state="normal" if control_enabled else "disabled")
            except Exception:
                pass
    except Exception:
        pass


def update_playlist_metadata_visibility(*args):
    try:
        sidecars_enabled = normalize_capture_mode(capture_mode_var.get()) in {"media", "metadata_only"}

        if source_scope_var.get() == "include_playlist":
            playlist_metadata_check.grid()
            playlist_metadata_check.configure(state="normal" if sidecars_enabled else "disabled")
        else:
            save_playlist_metadata_var.set(False)
            playlist_metadata_check.grid_remove()
    except Exception:
        pass

    update_playlist_options_state()
    update_capture_options_summary()


def toggle_advanced_options_panel():
    if advanced_options_panel.winfo_ismapped():
        hide_advanced_options_panel(save=True)
        return

    hide_capture_options_panel(save=True)
    hide_metadata_options_panel(save=True)
    hide_pacing_options_panel(save=True)
    update_capture_options_summary()
    advanced_options_panel.grid(
        row=8,
        column=0,
        columnspan=4,
        rowspan=8,
        sticky="nsew",
        padx=0,
        pady=(8, 0),
    )
    advanced_options_panel.tkraise()
    advanced_options_button.config(text="Advanced Options ▴")


def close_advanced_options_panel():
    hide_advanced_options_panel(save=True)


def toggle_pacing_options_panel():
    if pacing_options_panel.winfo_ismapped():
        hide_pacing_options_panel(save=True)
        return

    hide_capture_options_panel(save=True)
    hide_metadata_options_panel(save=True)
    hide_advanced_options_panel(save=True)
    update_capture_options_summary()
    pacing_options_panel.grid(
        row=8,
        column=0,
        columnspan=4,
        rowspan=8,
        sticky="nsew",
        padx=0,
        pady=(8, 0),
    )
    pacing_options_panel.tkraise()
    pacing_options_button.config(text="Pacing Options ▴")


def close_pacing_options_panel():
    hide_pacing_options_panel(save=True)


def clear_match_keywords():
    match_keywords_var.set("")
    update_capture_options_summary()


def clear_reject_keywords():
    reject_keywords_var.set("")
    update_capture_options_summary()



def get_ffmpeg_executable_for_gui():
    ffmpeg_folder = ffmpeg_folder_var.get().strip()

    if ffmpeg_folder:
        candidate = os.path.join(ffmpeg_folder, "ffmpeg.exe")
        if os.path.isfile(candidate):
            return candidate

    found = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
    return found or ""


def get_gui_thumbnail_cache_folder_for_path(path):
    output_root = output_root_var.get().strip()
    current = os.path.abspath(path)

    try:
        output_root_abs = os.path.abspath(output_root)
    except Exception:
        output_root_abs = ""

    case_root = ""

    if output_root_abs and os.path.commonpath([output_root_abs, current]) == output_root_abs:
        rel = os.path.relpath(current, output_root_abs)
        first_part = rel.split(os.sep)[0]
        if first_part and first_part not in (".", ".."):
            case_root = os.path.join(output_root_abs, first_part)

    if not case_root:
        case_root = os.path.dirname(current)

    return os.path.join(case_root, ".gui-cache", "thumbnails")


def get_gui_cache_file_stem(path):
    try:
        stat_info = os.stat(path)
        # Match PowerShell FileInfo.LastWriteTimeUtc.Ticks: 100 ns ticks since 0001-01-01 UTC.
        dotnet_ticks = 621355968000000000 + int(stat_info.st_mtime_ns / 100)
        fingerprint = f"{os.path.abspath(path).lower()}|{stat_info.st_size}|{dotnet_ticks}"
    except Exception:
        fingerprint = os.path.abspath(path).lower()

    return hashlib.sha256(fingerprint.encode("utf-8", errors="ignore")).hexdigest().upper()


def get_gui_thumbnail_path(video_path):
    cache_folder = get_gui_thumbnail_cache_folder_for_path(video_path)
    thumb_name = get_gui_cache_file_stem(video_path) + ".png"
    return os.path.join(cache_folder, thumb_name)


def generate_gui_thumbnail(video_path):
    return generate_gui_thumbnail_with_exe(video_path, get_ffmpeg_executable_for_gui())


def get_ffprobe_executable_for_gui():
    ffmpeg_folder = ffmpeg_folder_var.get().strip()

    if ffmpeg_folder:
        candidate = os.path.join(ffmpeg_folder, "ffprobe.exe")
        if os.path.isfile(candidate):
            return candidate

    found = shutil.which("ffprobe.exe") or shutil.which("ffprobe")
    return found or ""


def get_gui_metadata_path(media_path):
    cache_folder = get_gui_thumbnail_cache_folder_for_path(media_path)
    metadata_folder = os.path.join(os.path.dirname(cache_folder), "metadata")
    metadata_name = get_gui_cache_file_stem(media_path) + ".ffprobe.json"
    return os.path.join(metadata_folder, metadata_name)


def load_or_generate_media_info(media_path):
    return load_or_generate_media_info_with_exe(media_path, get_ffprobe_executable_for_gui())


def load_or_generate_media_info_with_exe(media_path, ffprobe_exe):
    metadata_path = get_gui_metadata_path(media_path)

    if os.path.isfile(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    if not ffprobe_exe:
        return {}

    try:
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

        cmd = [
            ffprobe_exe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            media_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return {}

        info = json.loads(result.stdout)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)

        return info

    except Exception:
        return {}


def generate_gui_thumbnail_with_exe(video_path, ffmpeg_exe):
    thumb_path = get_gui_thumbnail_path(video_path)

    if os.path.isfile(thumb_path):
        return thumb_path

    if not ffmpeg_exe:
        return ""

    try:
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)

        cmd = [
            ffmpeg_exe,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            "00:00:03",
            "-i",
            video_path,
            "-frames:v",
            "1",
            "-vf",
            "scale=320:-1",
            thumb_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45,
        )

        if result.returncode == 0 and os.path.isfile(thumb_path):
            return thumb_path

        if os.path.isfile(thumb_path):
            try:
                os.remove(thumb_path)
            except Exception:
                pass

        return ""

    except Exception:
        return ""


def format_seconds_for_display(value):
    try:
        total_seconds = int(float(value))
    except Exception:
        return ""

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes}:{seconds:02d}"


def format_bytes_for_display(value):
    try:
        size = float(value)
    except Exception:
        return ""

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"

    return f"{size:.1f} {units[unit_index]}"


def format_bitrate_for_display(value):
    try:
        bitrate = float(value)
    except Exception:
        return ""

    if bitrate >= 1_000_000:
        return f"{bitrate / 1_000_000:.2f} Mbps"

    if bitrate >= 1_000:
        return f"{bitrate / 1_000:.0f} kbps"

    return f"{bitrate:.0f} bps"


def get_streams_by_type(info, stream_type):
    streams = info.get("streams", []) if isinstance(info, dict) else []
    return [stream for stream in streams if stream.get("codec_type") == stream_type]


def get_media_info_summary(info, file_path):
    if not info:
        return {
            "card": "Media info unavailable",
            "tooltip": f"{os.path.basename(file_path)}\n\nMedia information unavailable.\nFFprobe may be missing or unable to read this file.",
        }

    format_info = info.get("format", {}) if isinstance(info, dict) else {}
    video_streams = get_streams_by_type(info, "video")
    audio_streams = get_streams_by_type(info, "audio")

    duration = format_seconds_for_display(format_info.get("duration"))
    size = format_bytes_for_display(format_info.get("size"))
    bitrate = format_bitrate_for_display(format_info.get("bit_rate"))

    card_lines = []

    if video_streams:
        video = video_streams[0]
        width = video.get("width")
        height = video.get("height")
        codec = video.get("codec_name", "video")

        if width and height:
            card_lines.append(f"{width}x{height}")

        if codec:
            card_lines.append(str(codec))

    elif audio_streams:
        audio = audio_streams[0]
        codec = audio.get("codec_name", "audio")
        card_lines.append(str(codec))

    if duration:
        card_lines.append(duration)

    if size:
        card_lines.append(size)

    if not card_lines:
        card_lines.append("Media file")

    tooltip_lines = [
        os.path.basename(file_path),
        "",
    ]

    if duration:
        tooltip_lines.append(f"Duration: {duration}")
    if size:
        tooltip_lines.append(f"Size: {size}")
    if bitrate:
        tooltip_lines.append(f"Overall bitrate: {bitrate}")

    if video_streams:
        video = video_streams[0]
        width = video.get("width")
        height = video.get("height")
        codec = video.get("codec_name", "")
        profile = video.get("profile", "")
        pix_fmt = video.get("pix_fmt", "")

        fps = ""
        rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
        if rate and "/" in rate:
            try:
                num, den = rate.split("/", 1)
                den = float(den)
                if den:
                    fps_value = float(num) / den
                    if fps_value > 0:
                        fps = f"{fps_value:.2f} fps"
            except Exception:
                pass

        tooltip_lines.append("")
        tooltip_lines.append("Video:")
        if width and height:
            tooltip_lines.append(f"  Resolution: {width}x{height}")
        if codec:
            tooltip_lines.append(f"  Codec: {codec}")
        if profile:
            tooltip_lines.append(f"  Profile: {profile}")
        if fps:
            tooltip_lines.append(f"  Frame rate: {fps}")
        if pix_fmt:
            tooltip_lines.append(f"  Pixel format: {pix_fmt}")

    if audio_streams:
        audio = audio_streams[0]
        codec = audio.get("codec_name", "")
        channels = audio.get("channels", "")
        channel_layout = audio.get("channel_layout", "")
        sample_rate = audio.get("sample_rate", "")

        tooltip_lines.append("")
        tooltip_lines.append("Audio:")
        if codec:
            tooltip_lines.append(f"  Codec: {codec}")
        if channels:
            tooltip_lines.append(f"  Channels: {channels}")
        if channel_layout:
            tooltip_lines.append(f"  Layout: {channel_layout}")
        if sample_rate:
            tooltip_lines.append(f"  Sample rate: {sample_rate} Hz")

    try:
        rel_path = os.path.relpath(file_path, output_root_var.get().strip())
    except Exception:
        rel_path = file_path

    tooltip_lines.append("")
    tooltip_lines.append(f"Path: {rel_path}")

    return {
        "card": " | ".join(card_lines),
        "tooltip": "\n".join(tooltip_lines),
    }


class Tooltip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.after_id = None
        self.window = None

        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        self.cancel()
        self.after_id = self.widget.after(self.delay, self.show)

    def cancel(self):
        if self.after_id:
            try:
                self.widget.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def show(self):
        if self.window or not self.text:
            return

        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        except Exception:
            x = 100
            y = 100

        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(
            self.window,
            text=self.text,
            justify="left",
            relief="solid",
            borderwidth=1,
            padding=8,
            wraplength=520,
        )
        label.pack()

    def hide(self, event=None):
        self.cancel()

        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None


class TreeviewHoverTooltip:
    def __init__(self, tree, text_provider, delay=500, wraplength=620):
        self.tree = tree
        self.text_provider = text_provider
        self.delay = delay
        self.wraplength = wraplength
        self.after_id = None
        self.window = None
        self.current_item = ""
        self.current_text = ""
        self.last_event = None

        tree.bind("<Motion>", self.on_motion, add="+")
        tree.bind("<Leave>", self.hide, add="+")
        tree.bind("<ButtonPress>", self.hide, add="+")
        tree.bind("<MouseWheel>", self.hide, add="+")

    def on_motion(self, event):
        item = self.tree.identify_row(event.y)
        self.last_event = event

        if item != self.current_item:
            self.current_item = item
            self.current_text = ""
            self.hide()

            if item:
                text = self.text_provider(item)
                if text:
                    self.current_text = text
                    self.after_id = self.tree.after(self.delay, self.show)

    def cancel(self):
        if self.after_id:
            try:
                self.tree.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def show(self):
        self.cancel()

        if self.window or not self.current_text:
            return

        try:
            event = self.last_event
            x = event.x_root + 18
            y = event.y_root + 18
        except Exception:
            x = self.tree.winfo_rootx() + 20
            y = self.tree.winfo_rooty() + 40

        self.window = tk.Toplevel(self.tree)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(
            self.window,
            text=self.current_text,
            justify="left",
            relief="solid",
            borderwidth=1,
            padding=8,
            wraplength=self.wraplength,
        )
        label.pack()

    def hide(self, event=None):
        self.cancel()
        self.current_item = ""
        self.current_text = ""

        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None


def is_browser_media_file(path):
    return os.path.splitext(path)[1].lower() in {
        ".mp4",
        ".mkv",
        ".webm",
        ".mov",
        ".avi",
        ".m4v",
        ".mp3",
        ".m4a",
        ".opus",
        ".wav",
        ".aac",
        ".flac",
    }


def is_browser_video_file(path):
    return os.path.splitext(path)[1].lower() in {
        ".mp4",
        ".mkv",
        ".webm",
        ".mov",
        ".avi",
        ".m4v",
    }


def enqueue_case_browser_ui(callback):
    try:
        case_browser_result_queue.put(callback)
    except Exception:
        pass


def process_case_browser_result_queue():
    global case_browser_result_poller_running

    case_browser_result_poller_running = True

    try:
        while True:
            callback = case_browser_result_queue.get_nowait()
            try:
                callback()
            except Exception as e:
                try:
                    append_log(f"\nCase Browser UI update failed: {e}\n")
                except Exception:
                    pass
    except queue.Empty:
        pass
    except Exception as e:
        try:
            append_log(f"\nCase Browser result queue failed: {e}\n")
        except Exception:
            pass

    try:
        root.after(100, process_case_browser_result_queue)
    except Exception:
        case_browser_result_poller_running = False


def start_case_browser_result_poller():
    global case_browser_result_poller_running

    if case_browser_result_poller_running:
        return

    try:
        root.after(100, process_case_browser_result_queue)
        case_browser_result_poller_running = True
    except Exception:
        case_browser_result_poller_running = False


def show_case_browser_placeholder(message):
    try:
        for child in case_browser_tab.winfo_children():
            child.destroy()

        frame = ttk.Frame(case_browser_tab, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        ttk.Label(
            frame,
            text=message,
            anchor="center",
            justify="center",
        ).grid(row=0, column=0, sticky="ew")
    except Exception:
        pass


def schedule_case_browser_autoload(delay_ms=500):
    global case_browser_reload_after_id

    try:
        if case_browser_reload_after_id:
            root.after_cancel(case_browser_reload_after_id)
    except Exception:
        pass

    def do_reload():
        global case_browser_reload_after_id
        case_browser_reload_after_id = None
        try:
            open_case_browser(select_tab=False, silent=True)
        except Exception as e:
            append_log(f"\nCase Browser auto-load failed: {e}\n")

    try:
        case_browser_reload_after_id = root.after(delay_ms, do_reload)
    except Exception:
        case_browser_reload_after_id = None


def on_output_root_changed(*args):
    update_case_folder_preview(*args)
    schedule_case_browser_autoload()


def open_case_browser(select_tab=True, silent=False):
    global case_browser_active_token

    output_root = output_root_var.get().strip()
    load_token = object()
    case_browser_active_token = load_token

    if not output_root:
        if silent:
            show_case_browser_placeholder("Case Browser is waiting for an Output Root.")
        else:
            messagebox.showwarning("Output root missing", "Output Root is blank.")
        return

    if not os.path.isdir(output_root):
        if silent:
            show_case_browser_placeholder(f"Output Root does not exist:\n\n{output_root}")
        else:
            messagebox.showwarning("Output root not found", f"Output Root does not exist:\n\n{output_root}")
        return

    try:
        browser = case_browser_tab
    except NameError:
        return

    for child in browser.winfo_children():
        try:
            child.destroy()
        except Exception:
            pass

    browser_file_map = {}
    tree_path_map = {}
    image_refs = []
    file_render_generation = {"value": 0}

    if select_tab:
        try:
            app_notebook.select(browser)
        except Exception:
            pass

    top_bar = ttk.Frame(browser, padding=(8, 4, 8, 4))
    top_bar.pack(fill="x")

    ttk.Label(top_bar, text=f"Output Root: {output_root}").pack(side="left", fill="x", expand=True)

    paned = ttk.PanedWindow(browser, orient="horizontal")
    paned.pack(fill="both", expand=True, padx=8, pady=(0, 4))

    tree_frame = ttk.Frame(paned)
    tree_frame.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)

    tree = ttk.Treeview(tree_frame, show="tree")
    tree.grid(row=0, column=0, sticky="nsew")

    tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree_scroll.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=tree_scroll.set)

    paned.add(tree_frame, weight=1)

    right_frame = ttk.Frame(paned)
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(2, weight=1)

    browser_status_var = tk.StringVar(value="Select a folder to view captured files.")
    browser_filter_var = case_browser_filter_var
    browser_sort_var = case_browser_sort_var
    browser_current_only_var = case_browser_current_only_var
    browser_icon_scale_var = case_browser_icon_scale_var
    browser_search_var = tk.StringVar(value="")
    browser_search_after_id = {"value": None}

    def save_case_browser_preferences():
        save_app_settings(show_popup=False)

    def refresh_browser_view():
        save_case_browser_preferences()
        try:
            render_files(get_selected_browser_folder())
        except NameError:
            # During window construction, render_files/get_selected_browser_folder are defined later.
            pass

    def schedule_browser_search_refresh(*args):
        try:
            if browser_search_after_id["value"]:
                root.after_cancel(browser_search_after_id["value"])
        except Exception:
            pass
        browser_search_after_id["value"] = root.after(250, refresh_browser_view)

    def get_browser_icon_geometry():
        scale = browser_icon_scale_var.get()

        if scale == "Small":
            return {
                "thumb_w": 120,
                "thumb_h": 76,
                "card_w": 170,
                "wrap": 150,
                "label_chars": 22,
                "font_big": 12,
                "font_small": 8,
            }

        if scale == "Large":
            return {
                "thumb_w": 220,
                "thumb_h": 138,
                "card_w": 300,
                "wrap": 280,
                "label_chars": 42,
                "font_big": 18,
                "font_small": 10,
            }

        return {
            "thumb_w": 160,
            "thumb_h": 100,
            "card_w": 230,
            "wrap": 210,
            "label_chars": 30,
            "font_big": 14,
            "font_small": 9,
        }

    def wrap_case_browser_card_text(value, max_chars):
        text = str(value or "").strip()

        if not text:
            return ""

        parts = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                parts.append("")
                continue

            wrapped = textwrap.wrap(
                line,
                width=max(8, int(max_chars)),
                break_long_words=True,
                break_on_hyphens=True,
            )
            parts.extend(wrapped or [line])

        return "\n".join(parts)

    case_browser_layout_columns = {"value": 0}
    case_browser_reflow_after_id = {"value": None}

    def get_case_browser_canvas_width():
        try:
            width = int(canvas.winfo_width())
        except Exception:
            width = 0

        if width <= 1:
            try:
                width = int(right_frame.winfo_width()) - 24
            except Exception:
                width = 0

        return max(1, width)

    def get_dynamic_browser_columns(geometry=None, canvas_width=None):
        geometry = geometry or get_browser_icon_geometry()
        available_width = int(canvas_width or get_case_browser_canvas_width())

        # padx=10 on each side of every card plus a small safety margin avoids
        # the final card nudging past the right edge and forcing horizontal overflow.
        card_pitch = max(1, int(geometry["card_w"]) + 24)
        usable_width = max(1, available_width - 12)

        return max(1, usable_width // card_pitch)

    def schedule_case_browser_reflow_if_needed(event=None):
        try:
            geometry = get_browser_icon_geometry()
            new_columns = get_dynamic_browser_columns(geometry, getattr(event, "width", None))
        except Exception:
            return

        if not case_browser_layout_columns["value"] or new_columns == case_browser_layout_columns["value"]:
            try:
                canvas.configure(scrollregion=canvas.bbox("all"))
            except Exception:
                pass
            return

        try:
            if case_browser_reflow_after_id["value"]:
                root.after_cancel(case_browser_reflow_after_id["value"])
        except Exception:
            pass

        def do_reflow():
            case_browser_reflow_after_id["value"] = None
            try:
                render_files(get_selected_browser_folder())
            except Exception:
                pass

        case_browser_reflow_after_id["value"] = root.after(200, do_reflow)

    ttk.Label(right_frame, textvariable=browser_status_var).grid(row=0, column=0, sticky="ew", pady=(0, 6))

    browser_controls = ttk.Frame(right_frame)
    browser_controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    browser_controls.columnconfigure(5, weight=1)
    browser_controls.columnconfigure(1, weight=1)

    ttk.Label(browser_controls, text="Filter").grid(row=0, column=0, sticky="w", padx=(0, 4))
    filter_menu = ttk.Combobox(
        browser_controls,
        textvariable=browser_filter_var,
        values=["All", "Media", "Video", "Audio", "Metadata/JSON", "Logs/Text", "Subtitles", "Images", "URL shortcuts"],
        state="readonly",
        width=16,
    )
    filter_menu.grid(row=0, column=1, sticky="w", padx=(0, 8))

    ttk.Label(browser_controls, text="Sort").grid(row=0, column=2, sticky="w", padx=(0, 4))
    sort_menu = ttk.Combobox(
        browser_controls,
        textvariable=browser_sort_var,
        values=["Name", "Domain", "Type", "Size", "Newest", "Oldest"],
        state="readonly",
        width=10,
    )
    sort_menu.grid(row=0, column=3, sticky="w", padx=(0, 8))

    ttk.Checkbutton(
        browser_controls,
        text="Current folder only",
        variable=browser_current_only_var,
        command=refresh_browser_view,
    ).grid(row=0, column=4, sticky="w", padx=(0, 8))

    ttk.Label(browser_controls, text="Icon scale").grid(row=0, column=5, sticky="e", padx=(8, 4))
    scale_menu = ttk.Combobox(
        browser_controls,
        textvariable=browser_icon_scale_var,
        values=["Small", "Medium", "Large"],
        state="readonly",
        width=9,
    )
    scale_menu.grid(row=0, column=6, sticky="e")

    ttk.Label(browser_controls, text="Search").grid(row=1, column=0, sticky="w", padx=(0, 4), pady=(6, 0))
    browser_search_entry = ttk.Entry(browser_controls, textvariable=browser_search_var)
    browser_search_entry.grid(row=1, column=1, columnspan=5, sticky="ew", padx=(0, 8), pady=(6, 0))
    ttk.Button(browser_controls, text="Clear", command=lambda: browser_search_var.set("")).grid(row=1, column=6, sticky="e", pady=(6, 0))
    browser_search_var.trace_add("write", schedule_browser_search_refresh)

    canvas = tk.Canvas(right_frame, highlightthickness=0)
    canvas.grid(row=2, column=0, sticky="nsew")

    y_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
    y_scroll.grid(row=2, column=1, sticky="ns")

    x_scroll = ttk.Scrollbar(right_frame, orient="horizontal", command=canvas.xview)
    x_scroll.grid(row=3, column=0, sticky="ew")

    canvas.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    content_frame = ttk.Frame(canvas)
    content_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def configure_content(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def configure_canvas(event):
        # Keep the file-card surface aligned to the visible pane width. The
        # column count is recalculated separately, so the content should not
        # force horizontal scrolling just because the window was narrowed.
        try:
            canvas.itemconfigure(content_window, width=max(1, event.width))
        except Exception:
            pass

        canvas.configure(scrollregion=canvas.bbox("all"))
        schedule_case_browser_reflow_if_needed(event)

    content_frame.bind("<Configure>", configure_content)
    canvas.bind("<Configure>", configure_canvas)

    paned.add(right_frame, weight=4)

    case_browser_ignored_folder_names = {".gui-cache", "__pycache__"}
    case_browser_ignored_file_names = {".ds_store", "desktop.ini", "thumbs.db"}

    def build_folder_tree_snapshot(folder_path, max_depth=4, depth=0):
        if depth > max_depth:
            return []

        try:
            entries = [
                entry for entry in os.scandir(folder_path)
                if entry.is_dir() and entry.name.lower() not in case_browser_ignored_folder_names
            ]
        except Exception:
            entries = []

        if depth == 0:
            entries = [
                entry for entry in entries
                if case_folder_is_populated(entry.path)
            ]

        entries.sort(key=lambda entry: entry.name.lower())
        nodes = []

        for entry in entries:
            nodes.append({
                "name": entry.name,
                "path": entry.path,
                "children": build_folder_tree_snapshot(entry.path, max_depth=max_depth, depth=depth + 1),
            })

        return nodes

    def insert_folder_snapshot_batched(parent_id, nodes, on_done=None, batch_size=CASE_BROWSER_TREE_BATCH_SIZE):
        stack = [{"parent": parent_id, "nodes": list(nodes or []), "index": 0}]

        def process_batch():
            inserted_count = 0

            try:
                while stack and inserted_count < batch_size:
                    frame = stack[-1]

                    if frame["index"] >= len(frame["nodes"]):
                        stack.pop()
                        continue

                    node = frame["nodes"][frame["index"]]
                    frame["index"] += 1

                    item_id = tree.insert(frame["parent"], "end", text=node["name"], open=False)
                    tree_path_map[item_id] = node["path"]
                    children = node.get("children", [])

                    if children:
                        stack.append({"parent": item_id, "nodes": list(children), "index": 0})

                    inserted_count += 1

                if stack:
                    root.after(1, process_batch)
                elif on_done:
                    on_done()
            except Exception as e:
                append_log(f"\nCase Browser tree render failed: {e}\n")
                if on_done:
                    on_done()

        process_batch()

    root_id = ""

    def open_selected_file(path):
        if os.path.isfile(path):
            os.startfile(path)

    def open_containing_folder(path):
        folder = os.path.dirname(path)
        if os.path.isdir(folder):
            os.startfile(folder)

    def copy_text_to_clipboard(value, label="Text"):
        root.clipboard_clear()
        root.clipboard_append(value)
        append_log(f"\n{label} copied to clipboard.\n")

    def find_related_file(path, extensions):
        base, _ = os.path.splitext(path)
        for extension in extensions:
            candidate = base + extension
            if os.path.isfile(candidate):
                return candidate
        return ""

    def open_related_metadata(path):
        related = find_related_file(path, [".info.json", ".json"])
        if related:
            os.startfile(related)
        else:
            messagebox.showinfo("No related metadata", "No related metadata JSON file was found beside this item.")

    def open_related_source_link(path):
        related = find_related_file(path, [".url", ".webloc"])
        if related:
            os.startfile(related)
        else:
            messagebox.showinfo("No related source link", "No related URL shortcut was found beside this item.")

    def show_file_context_menu(event, path, folder_path):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="Open", command=lambda: open_selected_file(path))
        menu.add_command(label="Open Containing Folder", command=lambda: open_containing_folder(path))
        menu.add_separator()
        menu.add_command(label="Open Related Metadata JSON", command=lambda: open_related_metadata(path))
        menu.add_command(label="Open Related Source Link", command=lambda: open_related_source_link(path))
        menu.add_separator()
        menu.add_command(label="Copy Full Path", command=lambda: copy_text_to_clipboard(path, "Full path"))
        menu.add_command(label="Copy File Name", command=lambda: copy_text_to_clipboard(os.path.basename(path), "File name"))
        try:
            rel_path = os.path.relpath(path, folder_path)
        except Exception:
            rel_path = path
        menu.add_command(label="Copy Relative Path", command=lambda: copy_text_to_clipboard(rel_path, "Relative path"))

        try:
            colors = get_theme_colors()
            configure_menu_theme(menu, colors)
        except Exception:
            pass

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def make_placeholder(parent, extension, width=160, height=100, font_big=14, font_small=9):
        placeholder = tk.Canvas(parent, width=width, height=height, highlightthickness=1, relief="ridge")
        placeholder.create_rectangle(0, 0, width, height)
        placeholder.create_text(width // 2, height // 2 - 8, text=(extension or "FILE").upper(), font=("Segoe UI", font_big, "bold"))
        placeholder.create_text(width // 2, height // 2 + 18, text="No preview", font=("Segoe UI", font_small))
        return placeholder

    def clear_content():
        for child in content_frame.winfo_children():
            child.destroy()
        image_refs.clear()

    def get_browser_sort_domain(path, folder_path):
        try:
            parts = [
                part.lower()
                for part in os.path.relpath(path, output_root).split(os.sep)
                if part and part not in {".", ".."}
            ]
        except Exception:
            parts = []

        if "media" in parts:
            media_index = parts.index("media")
            if media_index + 1 < len(parts):
                return parts[media_index + 1]

        try:
            rel_parts = [
                part.lower()
                for part in os.path.relpath(path, folder_path).split(os.sep)
                if part and part not in {".", ".."}
            ]
            if len(rel_parts) > 1:
                return rel_parts[0]
        except Exception:
            pass

        basename = os.path.basename(path).lower()
        domain_match = re.search(r"([a-z0-9-]+\.(?:com|net|org|ca|io|co|tv|me|info|biz|edu|gov|uk|au))", basename)
        if domain_match:
            return domain_match.group(1)

        return "unknown"

    def file_matches_browser_filter_value(path, selected_filter):
        ext = os.path.splitext(path)[1].lower()

        if selected_filter == "All":
            return is_browser_media_file(path) or ext in {".json", ".txt", ".description", ".url", ".webloc", ".srt", ".vtt", ".png", ".jpg", ".jpeg", ".webp", ".log", ".csv"}

        if selected_filter == "Media":
            return is_browser_media_file(path)

        if selected_filter == "Video":
            return is_browser_video_file(path)

        if selected_filter == "Audio":
            return ext in {".mp3", ".m4a", ".opus", ".wav", ".aac", ".flac"}

        if selected_filter == "Metadata/JSON":
            return ext in {".json", ".csv"}

        if selected_filter == "Logs/Text":
            return ext in {".log", ".txt", ".description"}

        if selected_filter == "Subtitles":
            return ext in {".srt", ".vtt"}

        if selected_filter == "Images":
            return ext in {".png", ".jpg", ".jpeg", ".webp"}

        if selected_filter == "URL shortcuts":
            return ext in {".url", ".webloc"}

        return True

    def list_display_files(folder_path, selected_filter, current_only, sort_mode, search_query=""):
        display_files = []
        total_after_type_filter = 0
        search_terms = [term.casefold() for term in re.split(r"\s+", str(search_query or "").strip()) if term]

        def file_matches_browser_search(path):
            if not search_terms:
                return True
            try:
                rel_folder = os.path.relpath(path, folder_path)
            except Exception:
                rel_folder = path
            try:
                rel_output = os.path.relpath(path, output_root)
            except Exception:
                rel_output = path
            fields = [
                os.path.basename(path),
                os.path.splitext(path)[1],
                rel_folder,
                rel_output,
                get_browser_sort_domain(path, folder_path),
            ]
            haystack = " ".join(str(field or "") for field in fields).casefold()
            return all(term in haystack for term in search_terms)

        if current_only:
            try:
                names = os.listdir(folder_path)
            except Exception:
                names = []

            for name in names:
                path = os.path.join(folder_path, name)
                if os.path.isfile(path) and file_matches_browser_filter_value(path, selected_filter):
                    total_after_type_filter += 1
                    if file_matches_browser_search(path):
                        display_files.append(path)
        else:
            for root_dir, dir_names, file_names in os.walk(folder_path):
                dir_names[:] = [
                    name for name in dir_names
                    if name.lower() not in {".gui-cache", "__pycache__"}
                ]

                for file_name in file_names:
                    path = os.path.join(root_dir, file_name)
                    if file_matches_browser_filter_value(path, selected_filter):
                        total_after_type_filter += 1
                        if file_matches_browser_search(path):
                            display_files.append(path)

        if sort_mode == "Domain":
            display_files.sort(key=lambda p: (get_browser_sort_domain(p, folder_path), not is_browser_media_file(p), os.path.basename(p).lower()))
        elif sort_mode == "Type":
            display_files.sort(key=lambda p: (os.path.splitext(p)[1].lower(), os.path.basename(p).lower()))
        elif sort_mode == "Size":
            display_files.sort(key=lambda p: (-(os.path.getsize(p) if os.path.isfile(p) else 0), os.path.basename(p).lower()))
        elif sort_mode == "Newest":
            display_files.sort(key=lambda p: (-(os.path.getmtime(p) if os.path.isfile(p) else 0), os.path.basename(p).lower()))
        elif sort_mode == "Oldest":
            display_files.sort(key=lambda p: ((os.path.getmtime(p) if os.path.isfile(p) else 0), os.path.basename(p).lower()))
        else:
            display_files.sort(key=lambda p: (not is_browser_media_file(p), os.path.basename(p).lower()))

        return display_files, total_after_type_filter

    def render_file_cards(folder_path, files, total_count=None, search_query="", selected_filter="All"):
        clear_content()
        render_generation = file_render_generation["value"]
        total_count = len(files) if total_count is None else total_count
        browser_status_var.set(f"{folder_path} - {len(files)} shown / {total_count} file(s)")

        if not files:
            if str(search_query or "").strip():
                message = "No files match the current Case Browser search/filter."
            elif selected_filter != "All":
                message = f"No files match the current Case Browser filter: {selected_filter}."
            elif os.path.normcase(os.path.abspath(folder_path)) == os.path.normcase(os.path.abspath(output_root)):
                message = "No captured case files found. Preview-only cache folders are hidden."
            else:
                message = "No media or sidecar files found in this folder."
            ttk.Label(content_frame, text=message).grid(row=0, column=0, sticky="w", padx=12, pady=12)
            return

        geometry = get_browser_icon_geometry()
        columns = get_dynamic_browser_columns(geometry)
        case_browser_layout_columns["value"] = columns
        thumb_w = geometry["thumb_w"]
        thumb_h = geometry["thumb_h"]
        wrap = geometry["wrap"]
        label_chars = geometry["label_chars"]
        card_w = geometry["card_w"]

        card_entries = {}
        media_paths = []
        index_state = {"index": 0}

        try:
            for column_index in range(max(1, columns + 1)):
                content_frame.columnconfigure(column_index, weight=0)
            for column_index in range(columns):
                content_frame.columnconfigure(column_index, weight=1, uniform="case_file_cards")
        except Exception:
            pass

        def create_file_card(index, path):
            row = index // columns
            column = index % columns

            card = ttk.Frame(content_frame, padding=10, relief="ridge")
            card.grid(row=row, column=column, sticky="new", padx=10, pady=10)
            card.columnconfigure(0, weight=1, minsize=card_w)

            ext = os.path.splitext(path)[1].lower().lstrip(".")
            file_name = os.path.basename(path)
            tooltip_text = f"{file_name}\n\nDouble-click to open. Right-click for actions."

            thumb = make_placeholder(
                card,
                ext or "file",
                width=thumb_w,
                height=thumb_h,
                font_big=geometry["font_big"],
                font_small=geometry["font_small"],
            )
            thumb.grid(row=0, column=0, pady=(0, 6))

            name_label = ttk.Label(
                card,
                text=wrap_case_browser_card_text(file_name, label_chars),
                wraplength=wrap,
                justify="center",
                anchor="center",
            )
            name_label.grid(row=1, column=0, sticky="ew")

            info_label = None
            rel_row = 2
            if is_browser_media_file(path):
                info_label = ttk.Label(
                    card,
                    text="Media info loading...",
                    wraplength=wrap,
                    justify="center",
                    anchor="center",
                )
                info_label.grid(row=2, column=0, sticky="ew")
                rel_row = 3
                media_paths.append(path)

            try:
                rel_path = os.path.relpath(path, folder_path)
            except Exception:
                rel_path = path

            type_label = ttk.Label(
                card,
                text=wrap_case_browser_card_text(rel_path, label_chars),
                wraplength=wrap,
                justify="center",
                anchor="center",
            )
            type_label.grid(row=rel_row, column=0, sticky="ew")

            widgets = [card, thumb, name_label, type_label]
            if info_label:
                widgets.append(info_label)

            tooltips = []
            for widget in widgets:
                widget.bind("<Double-Button-1>", lambda event, p=path: open_selected_file(p))
                widget.bind("<Button-3>", lambda event, p=path, fp=folder_path: show_file_context_menu(event, p, fp))
                widget.bind("<Button-2>", lambda event, p=path, fp=folder_path: show_file_context_menu(event, p, fp))
                tooltips.append(Tooltip(widget, tooltip_text))

            card_entries[path] = {
                "thumb": thumb,
                "info_label": info_label,
                "tooltips": tooltips,
            }

        def render_next_card_batch():
            if case_browser_active_token is not load_token or render_generation != file_render_generation["value"]:
                return

            start_index = index_state["index"]
            end_index = min(len(files), start_index + CASE_BROWSER_CARD_BATCH_SIZE)

            for index in range(start_index, end_index):
                create_file_card(index, files[index])

            index_state["index"] = end_index
            configure_content()

            if end_index < len(files):
                browser_status_var.set(f"{folder_path} - rendering {end_index}/{len(files)} file card(s)")
                root.after(1, render_next_card_batch)
            else:
                browser_status_var.set(f"{folder_path} - {len(files)} file(s)")
                start_media_asset_worker()

        def update_media_card(path, media_info, thumb_path):
            if case_browser_active_token is not load_token or render_generation != file_render_generation["value"]:
                return

            entry = card_entries.get(path)
            if not entry:
                return

            tooltip_text = f"{os.path.basename(path)}\n\nDouble-click to open. Right-click for actions."
            info_label = entry.get("info_label")

            if info_label:
                info_summary = get_media_info_summary(media_info, path)
                info_label.configure(text=wrap_case_browser_card_text(info_summary["card"], label_chars))
                tooltip_text = info_summary["tooltip"] + "\n\nDouble-click to open. Right-click for actions."

            if thumb_path and os.path.isfile(thumb_path):
                thumb = entry.get("thumb")
                if thumb:
                    try:
                        image = tk.PhotoImage(file=thumb_path)
                        if image.width() > thumb_w or image.height() > thumb_h:
                            factor = max(1, int(max(image.width() / thumb_w, image.height() / thumb_h)))
                            image = image.subsample(factor, factor)
                        image_refs.append(image)
                        thumb.delete("all")
                        thumb.create_image(thumb_w // 2, thumb_h // 2, image=image, anchor="center")
                    except Exception:
                        pass

            for tooltip in entry.get("tooltips", []):
                try:
                    tooltip.text = tooltip_text
                except Exception:
                    pass

        def start_media_asset_worker():
            if not media_paths:
                return

            ffprobe_exe = get_ffprobe_executable_for_gui()
            ffmpeg_exe = get_ffmpeg_executable_for_gui()

            def worker():
                for path in list(media_paths):
                    if case_browser_active_token is not load_token:
                        return

                    try:
                        media_info = load_or_generate_media_info_with_exe(path, ffprobe_exe) if is_browser_media_file(path) else {}
                    except Exception:
                        media_info = {}

                    try:
                        thumb_path = generate_gui_thumbnail_with_exe(path, ffmpeg_exe) if is_browser_video_file(path) else ""
                    except Exception:
                        thumb_path = ""

                    def apply_result(p=path, info=media_info, thumbnail=thumb_path):
                        update_media_card(p, info, thumbnail)

                    enqueue_case_browser_ui(apply_result)

            threading.Thread(target=worker, daemon=True).start()

        render_next_card_batch()


    def render_files(folder_path):
        if not folder_path or not os.path.isdir(folder_path):
            clear_content()
            browser_status_var.set("Selected folder is missing or invalid.")
            ttk.Label(content_frame, text="Selected folder is missing or invalid.").grid(row=0, column=0, sticky="w", padx=12, pady=12)
            return

        file_render_generation["value"] += 1
        generation = file_render_generation["value"]
        selected_filter = browser_filter_var.get()
        current_only = bool(browser_current_only_var.get())
        sort_mode = browser_sort_var.get()
        search_query = browser_search_var.get()

        clear_content()
        browser_status_var.set(f"Loading files from: {folder_path}")
        ttk.Label(content_frame, text="Loading files...").grid(row=0, column=0, sticky="w", padx=12, pady=12)

        def worker():
            try:
                files, total_count = list_display_files(folder_path, selected_filter, current_only, sort_mode, search_query)
                error = ""
            except Exception as e:
                files = []
                error = str(e)

            def apply_result():
                if case_browser_active_token is not load_token or generation != file_render_generation["value"]:
                    return

                if error:
                    clear_content()
                    browser_status_var.set(f"Could not list files for: {folder_path}")
                    ttk.Label(content_frame, text=f"Could not list files:\n\n{error}").grid(row=0, column=0, sticky="w", padx=12, pady=12)
                    return

                render_file_cards(folder_path, files, total_count=total_count, search_query=search_query, selected_filter=selected_filter)

            enqueue_case_browser_ui(apply_result)

        threading.Thread(target=worker, daemon=True).start()


    def on_tree_select(event=None):
        selection = tree.selection()
        if not selection:
            return

        selected_id = selection[0]
        folder_path = tree_path_map.get(selected_id)

        if folder_path and os.path.isdir(folder_path):
            # Single-click should both expand the selected folder and show its contents.
            try:
                tree.item(selected_id, open=True)
            except Exception:
                pass

            render_files(folder_path)

    def get_selected_browser_folder():
        selection = tree.selection()
        if not selection:
            return output_root

        selected_id = selection[0]
        folder_path = tree_path_map.get(selected_id)

        if folder_path and os.path.isdir(folder_path):
            return folder_path

        return output_root

    def open_selected_browser_folder():
        folder_path = get_selected_browser_folder()

        if os.path.isdir(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showwarning("Folder not found", f"The selected folder does not exist:\n\n{folder_path}")

    def get_case_root_for_browser_folder(folder_path):
        try:
            output_root_abs = os.path.abspath(output_root)
            folder_abs = os.path.abspath(folder_path)

            if os.path.normcase(folder_abs) == os.path.normcase(output_root_abs):
                return ""

            if os.path.commonpath([output_root_abs, folder_abs]) == output_root_abs:
                rel = os.path.relpath(folder_abs, output_root_abs)
                first_part = rel.split(os.sep)[0]
                if first_part and first_part not in {".", ".."}:
                    return os.path.join(output_root_abs, first_part)
        except Exception:
            pass

        return ""

    def find_latest_manifest(case_root):
        candidates = []
        search_roots = [
            os.path.join(case_root, "manifests"),
            case_root,
        ]

        for search_root in search_roots:
            if not os.path.isdir(search_root):
                continue

            for root_dir, dir_names, file_names in os.walk(search_root):
                for file_name in file_names:
                    lowered = file_name.lower()
                    if lowered.startswith("sha256-manifest") and lowered.endswith(".csv"):
                        path = os.path.join(root_dir, file_name)
                        candidates.append(path)

        if not candidates:
            return ""

        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return candidates[0]

    def verify_case_files():
        folder_path = get_selected_browser_folder()
        case_root = get_case_root_for_browser_folder(folder_path)

        if not case_root:
            messagebox.showwarning(
                "Select a case folder",
                "Select a case folder or a folder inside a case before verifying case files.\n\n"
                "The Output Root itself cannot be verified.",
            )
            return

        manifest_path = find_latest_manifest(case_root)

        if not manifest_path:
            messagebox.showwarning(
                "No manifest found",
                f"No SHA256 manifest was found for:\n\n{case_root}",
            )
            return

        ok_count = 0
        missing = []
        changed = []
        manifest_paths = set()

        try:
            with open(manifest_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    path = row.get("Path", "")
                    expected_hash = (row.get("Hash", "") or "").upper()

                    if not path:
                        continue

                    abs_path = os.path.abspath(path)

                    if is_case_verification_ignored_path(abs_path):
                        continue

                    manifest_paths.add(abs_path)

                    if not os.path.isfile(abs_path):
                        missing.append(path)
                        continue

                    try:
                        h = hashlib.sha256()
                        with open(abs_path, "rb") as input_file_obj:
                            for chunk in iter(lambda: input_file_obj.read(1024 * 1024), b""):
                                h.update(chunk)
                        actual_hash = h.hexdigest().upper()
                    except Exception:
                        changed.append(path)
                        continue

                    if actual_hash == expected_hash:
                        ok_count += 1
                    else:
                        changed.append(path)

            untracked_count = 0
            for root_dir, dir_names, file_names in os.walk(case_root):
                dir_names[:] = [name for name in dir_names if name.lower() not in {"__pycache__", ".gui-cache", "manifests"}]
                for file_name in file_names:
                    path = os.path.abspath(os.path.join(root_dir, file_name))
                    if is_case_verification_ignored_path(path):
                        continue
                    if path == os.path.abspath(manifest_path):
                        continue
                    if path not in manifest_paths:
                        untracked_count += 1

            summary = (
                f"Manifest:\n{manifest_path}\n\n"
                f"Verified unchanged: {ok_count}\n"
                f"Missing: {len(missing)}\n"
                f"Changed/unreadable: {len(changed)}\n"
                f"New/untracked since manifest: {untracked_count}\n"
                f"Ignored folders: .gui-cache, manifests\n"
            )

            append_log("\nCase file verification:\n" + summary + "\n")
            messagebox.showinfo("Case file verification", summary)

        except Exception as e:
            messagebox.showerror("Verification failed", f"Could not verify case files:\n\n{e}")

    def find_tree_item_by_path(target_path):
        try:
            target_abs = os.path.normcase(os.path.abspath(target_path))
        except Exception:
            return ""

        for item_id, folder_path in tree_path_map.items():
            try:
                if os.path.normcase(os.path.abspath(folder_path)) == target_abs:
                    return item_id
            except Exception:
                continue

        return ""

    def refresh_tree():
        nonlocal root_id

        try:
            previously_selected_folder = get_selected_browser_folder()
        except Exception:
            previously_selected_folder = output_root

        for item in tree.get_children(""):
            tree.delete(item)

        tree_path_map.clear()
        root_id = tree.insert("", "end", text=os.path.basename(os.path.abspath(output_root)) or output_root, open=True)
        tree_path_map[root_id] = output_root
        browser_status_var.set(f"Loading case folders from: {output_root}")
        clear_content()
        ttk.Label(content_frame, text="Loading case folders...").grid(row=0, column=0, sticky="w", padx=12, pady=12)

        def worker():
            try:
                nodes = build_folder_tree_snapshot(output_root)
                error = ""
            except Exception as e:
                nodes = []
                error = str(e)

            def apply_result():
                if case_browser_active_token is not load_token:
                    return

                if error:
                    append_log(f"\nCase Browser folder scan failed: {error}\n")

                try:
                    for child in tree.get_children(root_id):
                        tree.delete(child)
                except Exception:
                    return

                def finish_tree_render():
                    if case_browser_active_token is not load_token:
                        return

                    selected_item = find_tree_item_by_path(previously_selected_folder) or root_id
                    selected_folder = tree_path_map.get(selected_item, output_root)

                    try:
                        tree.selection_set(selected_item)
                        tree.focus(selected_item)
                        tree.see(selected_item)
                    except Exception:
                        pass

                    render_files(selected_folder)

                insert_folder_snapshot_batched(root_id, nodes, on_done=finish_tree_render)

            enqueue_case_browser_ui(apply_result)

        threading.Thread(target=worker, daemon=True).start()

    tree.bind("<<TreeviewSelect>>", on_tree_select)
    filter_menu.bind("<<ComboboxSelected>>", lambda event: refresh_browser_view())
    sort_menu.bind("<<ComboboxSelected>>", lambda event: refresh_browser_view())
    scale_menu.bind("<<ComboboxSelected>>", lambda event: (case_browser_layout_columns.update({"value": 0}), refresh_browser_view()))

    ttk.Button(top_bar, text="Refresh", command=refresh_tree).pack(side="right", padx=(6, 0))
    ttk.Button(top_bar, text="Verify Case Files", command=verify_case_files).pack(side="right", padx=(6, 0))
    ttk.Button(top_bar, text="Open Folder", command=open_selected_browser_folder).pack(side="right", padx=(6, 0))
    ttk.Button(top_bar, text="Open Output Root", command=lambda: os.startfile(output_root)).pack(side="right", padx=(6, 0))

    refresh_tree()


def on_close():
    global temp_url_file

    if job_queue_running:
        if not messagebox.askyesno(
            "Job queue running",
            "The job queue is still running. Stop the current job and exit?",
        ):
            return

        for job in get_running_queue_jobs():
            job["_interruption_requested"] = True
            job["interrupted_reason"] = "App closed while job was running."
        stop_capture()
        mark_running_queue_jobs_interrupted("App closed while job was running.")

    try:
        save_url_box_persistence_if_enabled()
        save_settings(show_popup=False)
        save_job_queue_state()
    except Exception:
        pass

    if running_process is not None and running_process.poll() is None:
        if not messagebox.askyesno("Capture running", "A capture is still running. Stop it and exit?"):
            return

        try:
            running_process.terminate()
        except Exception:
            pass

    if temp_url_file and os.path.isfile(temp_url_file):
        try:
            os.remove(temp_url_file)
        except Exception:
            pass

    delete_selected_cookies_file_on_exit()

    root.destroy()


root = tk.Tk()
try:
    ORIGINAL_TTK_THEME = ttk.Style(root).theme_use()
except Exception:
    ORIGINAL_TTK_THEME = ""
root.title(f"{APP_TITLE} - Profile: {DEFAULT_PROFILE_NAME}")
root.geometry(f"{APP_WINDOW_WIDTH}x{APP_WINDOW_HEIGHT_WITH_VPN}")
root.minsize(APP_WINDOW_MIN_WIDTH, APP_WINDOW_MIN_HEIGHT_WITH_VPN)

script_path_var = tk.StringVar(value=DEFAULTS["script_path"])
yt_dlp_path_var = tk.StringVar(value=DEFAULTS["yt_dlp_path"])
input_file_var = tk.StringVar(value=DEFAULTS["input_file"])
case_name_var = tk.StringVar(value=DEFAULTS["case_name"])
case_folder_preview_var = tk.StringVar(value="")
cookies_file_var = tk.StringVar(value=DEFAULTS["cookies_file"])
output_root_var = tk.StringVar(value=DEFAULTS["output_root"])
ffmpeg_folder_var = tk.StringVar(value=DEFAULTS["ffmpeg_folder"])
impersonate_var = tk.StringVar(value=DEFAULTS["impersonate_target"])
prefer_mp4_var = tk.BooleanVar(value=DEFAULTS["prefer_mp4"])
format_strategy_var = tk.StringVar(value=DEFAULTS["format_strategy"])
vpn_adapter_var = tk.StringVar(value=DEFAULTS["vpn_adapter_name"])
vpn_status_var = tk.StringVar(value="VPN: Not checked")
target_status_var = tk.StringVar(value="Impersonate targets: Not checked")
split_queue_mode_var = tk.StringVar(value=DEFAULTS["split_queue_mode"])
split_queue_urls_per_group_var = tk.StringVar(value=DEFAULTS["split_queue_urls_per_group"])
split_queue_group_count_var = tk.StringVar(value=DEFAULTS["split_queue_group_count"])
url_preview_pacing_var = tk.StringVar(value=DEFAULTS["url_preview_pacing"])
url_preview_thumbnail_mode_var = tk.StringVar(value=DEFAULTS["url_preview_thumbnail_mode"])
url_preview_rate_limit_thumbnails_var = tk.BooleanVar(value=DEFAULTS["url_preview_rate_limit_thumbnails"])
url_preview_cache_mode_var = tk.StringVar(value=DEFAULTS["url_preview_cache_mode"])
url_preview_playlist_mode_var = tk.StringVar(value=DEFAULTS["url_preview_playlist_mode"])
url_preview_max_playlist_items_var = tk.StringVar(value=DEFAULTS["url_preview_max_playlist_items"])
url_preview_timeout_var = tk.StringVar(value=DEFAULTS["url_preview_timeout"])
status_var = tk.StringVar(value="Ready")
yt_dlp_version_status_var = tk.StringVar(value="yt-dlp: not checked")
preflight_done_var = tk.BooleanVar(value=False)
delete_cookies_on_exit_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["delete_cookies_on_exit"])
check_vpn_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["check_vpn"])
use_cookies_file_var = tk.BooleanVar(value=DEFAULTS["use_cookies_file"])
dark_mode_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["dark_mode"])
case_browser_filter_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["case_browser_filter"])
case_browser_sort_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["case_browser_sort"])
case_browser_current_only_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["case_browser_current_only"])
case_browser_icon_scale_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["case_browser_icon_scale"])
job_persistence_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["job_persistence"])
url_box_persistence_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["url_box_persistence"])
universal_archive_enabled_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["universal_archive_enabled"])
proxy_protocol_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["proxy_protocol"])
proxy_address_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["proxy_address"])
proxy_port_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["proxy_port"])
proxy_username_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["proxy_username"])
proxy_password_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["proxy_password"])
proxy_no_save_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["proxy_no_save"])
selected_profile_var = tk.StringVar(value=DEFAULT_PROFILE_NAME)
capture_options_summary_var = tk.StringVar(value="")
capture_mode_var = tk.StringVar(value=DEFAULTS["capture_mode"])
source_scope_var = tk.StringVar(value=DEFAULTS["source_scope"])
playlist_items_enabled_var = tk.BooleanVar(value=DEFAULTS["playlist_items_enabled"])
playlist_items_var = tk.StringVar(value=DEFAULTS["playlist_items"])
playlist_order_enabled_var = tk.BooleanVar(value=DEFAULTS["playlist_order_enabled"])
playlist_order_var = tk.StringVar(value=DEFAULTS["playlist_order"])
max_playlist_items_enabled_var = tk.BooleanVar(value=DEFAULTS["max_playlist_items_enabled"])
max_playlist_items_var = tk.StringVar(value=DEFAULTS["max_playlist_items"])
break_on_existing_var = tk.BooleanVar(value=DEFAULTS["break_on_existing"])
skip_playlist_after_errors_enabled_var = tk.BooleanVar(value=DEFAULTS["skip_playlist_after_errors_enabled"])
skip_playlist_after_errors_var = tk.StringVar(value=DEFAULTS["skip_playlist_after_errors"])
archive_mode_var = tk.StringVar(value=DEFAULTS["archive_mode"])
max_resolution_var = tk.StringVar(value=DEFAULTS["max_resolution"])
gui_cache_mode_var = tk.StringVar(value=display_gui_cache_mode(DEFAULTS["gui_cache_mode"]))
manifest_mode_var = tk.StringVar(value=display_manifest_mode(DEFAULTS["manifest_mode"]))
save_playlist_metadata_var = tk.BooleanVar(value=DEFAULTS["save_playlist_metadata"])
generate_url_shortcuts_var = tk.BooleanVar(value=DEFAULTS["generate_url_shortcuts"])
match_keywords_var = tk.StringVar(value=DEFAULTS["match_keywords"])
reject_keywords_var = tk.StringVar(value=DEFAULTS["reject_keywords"])
failure_handling_var = tk.StringVar(value=DEFAULTS["failure_handling"])
show_all_impersonate_targets_var = tk.BooleanVar(value=DEFAULTS["show_all_impersonate_targets"])
date_after_enabled_var = tk.BooleanVar(value=DEFAULTS["date_after_enabled"])
date_after_year_var = tk.StringVar(value=DEFAULTS["date_after_year"])
date_after_month_var = tk.StringVar(value=DEFAULTS["date_after_month"])
date_after_day_var = tk.StringVar(value=DEFAULTS["date_after_day"])
date_before_enabled_var = tk.BooleanVar(value=DEFAULTS["date_before_enabled"])
date_before_year_var = tk.StringVar(value=DEFAULTS["date_before_year"])
date_before_month_var = tk.StringVar(value=DEFAULTS["date_before_month"])
date_before_day_var = tk.StringVar(value=DEFAULTS["date_before_day"])
rate_limit_var = tk.StringVar(value=DEFAULTS["rate_limit"])
download_speed_limit_var = tk.StringVar(value=normalize_download_speed_limit_value(DEFAULTS["download_speed_limit"]) or "1 MiB/s")
download_speed_limit_enabled_var = tk.BooleanVar(value=bool(DEFAULTS["download_speed_limit_enabled"]))
download_speed_slider_var = tk.DoubleVar(value=download_speed_bytes_to_slider(parse_download_speed_limit_to_bytes(download_speed_limit_var.get()) or DOWNLOAD_SPEED_DEFAULT_BYTES))
retry_behavior_var = tk.StringVar(value=DEFAULTS["retry_behavior"])
throttle_detection_enabled_var = tk.BooleanVar(value=DEFAULTS["throttle_detection_enabled"])
throttled_rate_var = tk.StringVar(value=DEFAULTS["throttled_rate"])
http_chunk_size_enabled_var = tk.BooleanVar(value=DEFAULTS["http_chunk_size_enabled"])
http_chunk_size_var = tk.StringVar(value=DEFAULTS["http_chunk_size"])
concurrent_captures_var = tk.StringVar(value=DEFAULTS["concurrent_captures"])
concurrent_fragments_var = tk.StringVar(value=DEFAULTS["concurrent_fragments"])
keep_partials_var = tk.BooleanVar(value=DEFAULTS["keep_partials"])
write_info_json_var = tk.BooleanVar(value=DEFAULTS["write_info_json"])
write_source_link_var = tk.BooleanVar(value=DEFAULTS["write_source_link"])
write_description_var = tk.BooleanVar(value=DEFAULTS["write_description"])
write_thumbnail_var = tk.BooleanVar(value=DEFAULTS["write_thumbnail"])
write_subs_var = tk.BooleanVar(value=DEFAULTS["write_subs"])
write_auto_subs_var = tk.BooleanVar(value=DEFAULTS["write_auto_subs"])
write_comments_var = tk.BooleanVar(value=DEFAULTS["write_comments"])
embed_metadata_var = tk.BooleanVar(value=DEFAULTS["embed_metadata"])
embed_thumbnail_var = tk.BooleanVar(value=DEFAULTS["embed_thumbnail"])
embed_subs_var = tk.BooleanVar(value=DEFAULTS["embed_subs"])
embed_chapters_var = tk.BooleanVar(value=DEFAULTS["embed_chapters"])
embed_info_json_var = tk.BooleanVar(value=DEFAULTS["embed_info_json"])


for option_var in [
    prefer_mp4_var,
    format_strategy_var,
    capture_mode_var,
    source_scope_var,
    playlist_items_enabled_var,
    playlist_items_var,
    playlist_order_enabled_var,
    playlist_order_var,
    max_playlist_items_enabled_var,
    max_playlist_items_var,
    break_on_existing_var,
    skip_playlist_after_errors_enabled_var,
    skip_playlist_after_errors_var,
    archive_mode_var,
    max_resolution_var,
    save_playlist_metadata_var,
    generate_url_shortcuts_var,
    match_keywords_var,
    reject_keywords_var,
    failure_handling_var,
    show_all_impersonate_targets_var,
    date_after_enabled_var,
    date_after_year_var,
    date_after_month_var,
    date_after_day_var,
    date_before_enabled_var,
    date_before_year_var,
    date_before_month_var,
    date_before_day_var,
    rate_limit_var,
    download_speed_limit_var,
    download_speed_limit_enabled_var,
    retry_behavior_var,
    throttle_detection_enabled_var,
    throttled_rate_var,
    http_chunk_size_enabled_var,
    http_chunk_size_var,
    concurrent_captures_var,
    concurrent_fragments_var,
    keep_partials_var,
    write_info_json_var,
    write_source_link_var,
    write_description_var,
    write_thumbnail_var,
    write_subs_var,
    write_auto_subs_var,
    write_comments_var,
    embed_metadata_var,
    embed_thumbnail_var,
    embed_subs_var,
    embed_chapters_var,
    embed_info_json_var,
]:
    option_var.trace_add("write", update_capture_options_summary)

source_scope_var.trace_add("write", update_playlist_metadata_visibility)
update_capture_options_summary()

app_notebook = ttk.Notebook(root, style="Bottom.TNotebook")
app_notebook.pack(fill="both", expand=True)

main = ttk.Frame(app_notebook, padding=12)
job_queue_tab = ttk.Frame(app_notebook, padding=0)
playlist_preview_tab = ttk.Frame(app_notebook, padding=0)
case_browser_tab = ttk.Frame(app_notebook, padding=0)

app_notebook.add(main, text="Capture")
app_notebook.add(job_queue_tab, text="Job Queue")
app_notebook.add(playlist_preview_tab, text="URL Preview")
app_notebook.add(case_browser_tab, text="Case Browser")

job_queue_tab.columnconfigure(0, weight=1)
job_queue_tab.rowconfigure(0, weight=0)
job_queue_tab.rowconfigure(1, weight=1)
job_queue_tab.rowconfigure(2, weight=0)

playlist_preview_tab.columnconfigure(0, weight=1)
playlist_preview_tab.rowconfigure(0, weight=1)

playlist_preview_placeholder = ttk.Frame(playlist_preview_tab, padding=16)
playlist_preview_placeholder.grid(row=0, column=0, sticky="nsew")
playlist_preview_placeholder.columnconfigure(0, weight=1)
playlist_preview_placeholder.rowconfigure(0, weight=1)

playlist_preview_placeholder_content = ttk.Frame(playlist_preview_placeholder)
playlist_preview_placeholder_content.grid(row=0, column=0)

ttk.Label(
    playlist_preview_placeholder_content,
    text="URL Preview will automatically load current URL box or selected Input File(s) contents when this tab is selected.",
    anchor="center",
    justify="center",
).pack()

case_browser_tab.columnconfigure(0, weight=1)
case_browser_tab.rowconfigure(0, weight=1)

case_browser_placeholder = ttk.Frame(case_browser_tab, padding=16)
case_browser_placeholder.grid(row=0, column=0, sticky="nsew")
case_browser_placeholder.columnconfigure(0, weight=1)
case_browser_placeholder.rowconfigure(0, weight=1)

ttk.Label(
    case_browser_placeholder,
    text="Case Browser will load automatically from the current Output Root.",
    anchor="center",
).grid(row=0, column=0, sticky="ew")

app_notebook.bind("<<NotebookTabChanged>>", on_notebook_tab_changed)

main.columnconfigure(1, weight=1)
main.columnconfigure(3, weight=0)
main.rowconfigure(10, weight=0, minsize=URL_ROW_MIN_HEIGHT)
main.rowconfigure(15, weight=1)


def add_file_row(row, label, var):
    ttk.Label(main, text=label).grid(row=row, column=0, sticky="w", pady=3)

    row_frame = ttk.Frame(main)
    row_frame.grid(row=row, column=1, columnspan=3, sticky="ew", padx=6, pady=3)
    row_frame.columnconfigure(0, weight=1)

    ttk.Entry(row_frame, textvariable=var).grid(row=0, column=0, sticky="ew", padx=(0, 6))
    ttk.Button(row_frame, text="Browse...", command=lambda: browse_file(var, label)).grid(row=0, column=1, sticky="e")


def add_folder_row(row, label, var):
    ttk.Label(main, text=label).grid(row=row, column=0, sticky="w", pady=3)

    row_frame = ttk.Frame(main)
    row_frame.grid(row=row, column=1, columnspan=3, sticky="ew", padx=6, pady=3)
    row_frame.columnconfigure(0, weight=1)

    ttk.Entry(row_frame, textvariable=var).grid(row=0, column=0, sticky="ew", padx=(0, 6))
    ttk.Button(row_frame, text="Browse...", command=lambda: browse_folder(var, label)).grid(row=0, column=1, sticky="e")


# Menu bar keeps less-used actions out of the main workflow.
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open Output Folder", command=open_output_folder)
file_menu.add_command(label="Open Current Case Folder", command=open_current_case_folder)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=on_close)

capture_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Capture", menu=capture_menu)
capture_menu.add_command(label="Preflight Check", command=run_preflight_check)
capture_menu.add_command(label="Start Capture", command=start_capture)
capture_menu.add_command(label="Stop Capture", command=stop_capture)
capture_menu.add_separator()
capture_menu.add_command(label="Delete Current Case Folder", command=delete_current_case_folder)

cookies_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Cookies", menu=cookies_menu)
cookies_menu.add_command(label="Export Browser Cookies", command=export_browser_cookies_dialog)
cookies_menu.add_command(label="Encrypt Cookies for Storage", command=encrypt_cookies_dialog)
cookies_menu.add_command(label="Decrypt Cookies from Storage", command=decrypt_cookies_dialog)

tools_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Tools", menu=tools_menu)
tools_menu.add_command(label="Proxy Options", command=open_proxy_options_dialog)
tools_menu.add_command(label="Update Deno", command=update_deno_direct)
tools_menu.add_command(label="Domain Presets", command=open_domain_presets_window)
profile_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Profile", menu=profile_menu)

settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Save Settings As...", command=save_settings_dialog)
settings_menu.add_command(label="Load Settings...", command=load_settings_dialog)
settings_menu.add_separator()
settings_menu.add_checkbutton(
    label="Delete Cookies on Exit",
    variable=delete_cookies_on_exit_var,
    command=lambda: save_app_settings(
        show_popup=False,
        changed_setting_label=f"Delete Cookies on Exit {'enabled' if delete_cookies_on_exit_var.get() else 'disabled'}",
    ),
)
settings_menu.add_checkbutton(
    label="Check VPN",
    variable=check_vpn_var,
    command=toggle_check_vpn_setting,
)
settings_menu.add_checkbutton(
    label="Dark Mode",
    variable=dark_mode_var,
    command=toggle_dark_mode_setting,
)
settings_menu.add_checkbutton(
    label="Job Persistence",
    variable=job_persistence_var,
    command=toggle_job_persistence_setting,
)
settings_menu.add_checkbutton(
    label="URL Box Persistence",
    variable=url_box_persistence_var,
    command=toggle_url_box_persistence_setting,
)
settings_menu.add_separator()
settings_menu.add_checkbutton(
    label="Universal Download Archive",
    variable=universal_archive_enabled_var,
    command=toggle_universal_archive_setting,
)
settings_menu.add_command(label="Delete Universal Archive File...", command=delete_universal_archive_file)
settings_menu.add_separator()
settings_menu.add_command(label="Reset Defaults", command=reset_defaults)
settings_menu.add_separator()
settings_menu.add_command(label="Save Default Portable Settings", command=lambda: save_settings(show_popup=True))
settings_menu.add_separator()
settings_menu.add_command(label="Delete Settings File...", command=delete_settings_file)

help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Check for Updates", command=open_app_update_dialog)
help_menu.add_command(label="About", command=open_about_dialog)

add_file_row(0, "Script Path", script_path_var)

ttk.Label(main, text="yt-dlp Path").grid(row=1, column=0, sticky="nw", pady=3)
yt_dlp_path_frame = ttk.Frame(main)
yt_dlp_path_frame.grid(row=1, column=1, columnspan=3, sticky="ew", padx=6, pady=3)
yt_dlp_path_frame.columnconfigure(0, weight=1)

ttk.Entry(yt_dlp_path_frame, textvariable=yt_dlp_path_var).grid(
    row=0,
    column=0,
    sticky="ew",
    padx=(0, 6),
    pady=(0, 4),
)
ttk.Button(
    yt_dlp_path_frame,
    text="Browse...",
    command=lambda: browse_file(yt_dlp_path_var, "yt-dlp Path"),
).grid(row=0, column=1, sticky="e", pady=(0, 4))

yt_dlp_tools_frame = ttk.Frame(yt_dlp_path_frame)
yt_dlp_tools_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
yt_dlp_tools_frame.columnconfigure(2, weight=1)

ttk.Button(
    yt_dlp_tools_frame,
    text="Check yt-dlp Version",
    command=check_ytdlp_version,
).grid(row=0, column=0, sticky="w", padx=(0, 6))

ttk.Button(
    yt_dlp_tools_frame,
    text="Update yt-dlp",
    command=open_ytdlp_update_dialog,
).grid(row=0, column=1, sticky="w", padx=(0, 10))

ttk.Label(
    yt_dlp_tools_frame,
    textvariable=yt_dlp_version_status_var,
).grid(row=0, column=2, sticky="w")

add_file_row(2, "Input File(s)", input_file_var)

ttk.Label(main, text="Case Name").grid(row=3, column=0, sticky="nw", pady=(6, 3))
case_name_frame = ttk.Frame(main)
case_name_frame.grid(row=3, column=1, columnspan=3, sticky="ew", padx=6, pady=3)
case_name_frame.columnconfigure(0, weight=1)

case_name_entry = ttk.Entry(case_name_frame, textvariable=case_name_var)
case_name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

case_folder_preview_label = ttk.Label(
    case_name_frame,
    textvariable=case_folder_preview_var,
    wraplength=760,
    justify="left",
)
case_folder_preview_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(3, 0))

case_tag_menu_button = ttk.Menubutton(case_name_frame, text="Insert Tag")
case_tag_menu = tk.Menu(case_tag_menu_button, tearoff=0)
case_tag_menu_button["menu"] = case_tag_menu

case_name_tag_items = [
    "%date%",
    "%time%",
    "%datetime%",
    "%utcdatetime%",
    "%domains%",
    "%presets%",
    "%playlist%",
    "%year%",
    "%month%",
    "%day%",
    "%hour%",
    "%minute%",
    "%second%",
]

for tag in case_name_tag_items:
    case_tag_menu.add_command(
        label=tag,
        command=lambda value=tag: insert_case_name_tag(value),
    )


case_tag_menu_button.grid(row=0, column=1, sticky="e", padx=(0, 6))
ttk.Button(case_name_frame, text="Open", command=open_current_case_folder).grid(row=0, column=2, sticky="e")

ttk.Label(main, text="Cookies File").grid(row=4, column=0, sticky="w", pady=3)

cookies_file_frame = ttk.Frame(main)
cookies_file_frame.grid(row=4, column=1, columnspan=3, sticky="ew", padx=6, pady=3)
cookies_file_frame.columnconfigure(0, weight=1)

cookies_file_entry = ttk.Entry(cookies_file_frame, textvariable=cookies_file_var)
cookies_file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

cookies_file_browse_button = ttk.Button(
    cookies_file_frame,
    text="Browse...",
    command=lambda: browse_file(cookies_file_var, "Cookies File"),
)
cookies_file_browse_button.grid(row=0, column=1, sticky="e", padx=(0, 6))

cookies_file_use_check = ttk.Checkbutton(
    cookies_file_frame,
    text="Use",
    variable=use_cookies_file_var,
    command=toggle_use_cookies_file_setting,
)
cookies_file_use_check.grid(row=0, column=2, sticky="e")

update_cookies_file_control_state()

add_folder_row(5, "Output Root", output_root_var)
add_folder_row(6, "FFmpeg Folder", ffmpeg_folder_var)

options_frame = ttk.Frame(main)
options_frame.grid(row=7, column=0, columnspan=4, sticky="ew", padx=0, pady=5)
options_frame.columnconfigure(4, weight=1)

capture_options_button = ttk.Button(
    options_frame,
    text="Capture Options ▾",
    command=toggle_capture_options_panel,
)
capture_options_button.grid(row=0, column=0, sticky="w", padx=(0, 8))

metadata_options_button = ttk.Button(
    options_frame,
    text="Metadata Options ▾",
    command=toggle_metadata_options_panel,
)
metadata_options_button.grid(row=0, column=1, sticky="w", padx=(0, 8))

pacing_options_button = ttk.Button(
    options_frame,
    text="Pacing Options ▾",
    command=toggle_pacing_options_panel,
)
pacing_options_button.grid(row=0, column=2, sticky="w", padx=(0, 8))

advanced_options_button = ttk.Button(
    options_frame,
    text="Advanced Options ▾",
    command=toggle_advanced_options_panel,
)
advanced_options_button.grid(row=0, column=3, sticky="w", padx=(0, 10))

capture_options_summary_label = ttk.Label(
    options_frame,
    textvariable=capture_options_summary_var,
    wraplength=700,
    justify="left",
)
capture_options_summary_label.grid(row=0, column=4, sticky="ew")

def update_capture_options_summary_wrap(event=None):
    try:
        width = max(
            360,
            options_frame.winfo_width()
            - capture_options_button.winfo_width()
            - metadata_options_button.winfo_width()
            - pacing_options_button.winfo_width()
            - advanced_options_button.winfo_width()
            - 78,
        )
        capture_options_summary_label.configure(wraplength=width)
    except Exception:
        pass


options_frame.bind("<Configure>", update_capture_options_summary_wrap)

vpn_frame = ttk.LabelFrame(main, text="VPN Status", padding=8)
vpn_frame.grid(row=8, column=0, columnspan=4, sticky="ew", pady=(8, 6))
vpn_frame.columnconfigure(1, weight=1)

ttk.Label(vpn_frame, text="VPN Adapter").grid(row=0, column=0, sticky="w", padx=(0, 8))

vpn_adapter_menu = ttk.Combobox(
    vpn_frame,
    textvariable=vpn_adapter_var,
    values=[],
    state="readonly",
)
vpn_adapter_menu.grid(row=0, column=1, sticky="ew", padx=(0, 8))
vpn_adapter_menu.bind("<<ComboboxSelected>>", lambda event: save_settings(show_popup=False))

ttk.Button(
    vpn_frame,
    text="Refresh Adapters",
    command=refresh_network_adapters,
).grid(row=0, column=2, sticky="e", padx=(0, 8))

ttk.Button(
    vpn_frame,
    text="Check VPN",
    command=check_vpn_status,
).grid(row=0, column=3, sticky="e")

ttk.Label(vpn_frame, textvariable=vpn_status_var).grid(
    row=1,
    column=0,
    columnspan=4,
    sticky="w",
    pady=(6, 0),
)

update_vpn_section_visibility()

ttk.Label(
    main,
    text="Paste URLs below, one per line. If this box is used, it overrides the Input File(s) field.",
).grid(row=9, column=0, columnspan=4, sticky="w", pady=(10, 3))

urls_text = scrolledtext.ScrolledText(main, height=8, wrap="word")
urls_text.grid(row=10, column=0, columnspan=3, sticky="nsew", pady=(0, 8))
urls_text.bind("<<Modified>>", handle_playlist_preview_source_changed)
urls_text.edit_modified(False)

url_button_frame = ttk.Frame(main)
url_button_frame.grid(row=10, column=3, sticky="n", padx=(8, 0), pady=(0, 8))

for index, (label, command) in enumerate((
    ("Load", load_urls_from_input_file),
    ("Append", append_urls_from_input_file),
    ("Save", save_urls_to_input_file),
    ("Clear", clear_urls),
    ("Strip", strip_url_extra_ampersand_tags),
    ("Copy", copy_urls_from_box),
)):
    ttk.Button(
        url_button_frame,
        text=label,
        command=command,
        width=8,
    ).grid(row=index, column=0, sticky="ew", pady=(0 if index == 0 else 6, 0), padx=(0, 6))

failed_url_toggle_button = ttk.Button(
    url_button_frame,
    text="Failed",
    command=toggle_failed_url_view,
    width=10,
)
failed_url_toggle_button.grid(row=0, column=1, sticky="ew")

for index, (label, command) in enumerate((
    ("Group", group_urls_by_tld),
    ("Statistics", show_url_statistics),
    ("Normalize", normalize_urls_in_box),
    ("Duplicates", remove_duplicate_urls_from_box),
    ("Validate", validate_urls_in_box),
), start=1):
    ttk.Button(
        url_button_frame,
        text=label,
        command=command,
        width=10,
    ).grid(row=index, column=1, sticky="ew", pady=(6, 0))

def show_start_capture_menu():
    try:
        start_capture_menu.tk_popup(
            start_menu_button.winfo_rootx(),
            start_menu_button.winfo_rooty() + start_menu_button.winfo_height(),
        )
    finally:
        try:
            start_capture_menu.grab_release()
        except Exception:
            pass


workflow_frame = ttk.Frame(main)
workflow_frame.grid(row=11, column=0, columnspan=4, sticky="ew", pady=(8, 12))
workflow_frame.columnconfigure(0, weight=1)
workflow_frame.columnconfigure(1, weight=0)
workflow_frame.columnconfigure(2, weight=1)
workflow_frame.columnconfigure(3, weight=1)
workflow_frame.columnconfigure(4, weight=1)

main_action_button_style = {
    "font": ("Segoe UI", 10, "bold"),
    "padx": 10,
    "pady": 5,
    "relief": "raised",
    "borderwidth": 2,
}

preflight_button = tk.Button(
    workflow_frame,
    text="✓ Preflight Check",
    command=run_preflight_check,
    fg="#003366",
    activeforeground="#003366",
    **main_action_button_style,
)
preflight_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

preflight_check_box = ttk.Checkbutton(
    workflow_frame,
    text="Preflight passed",
    variable=preflight_done_var,
    state="disabled",
)
preflight_check_box.grid(row=0, column=1, sticky="w", padx=(0, 8))

start_capture_split_frame = tk.Frame(workflow_frame, borderwidth=0, highlightthickness=0)
start_capture_split_frame.grid(row=0, column=2, sticky="ew", padx=(0, 8))
start_capture_split_frame.columnconfigure(0, weight=1)
start_capture_split_frame.columnconfigure(1, weight=0)

start_button = tk.Button(
    start_capture_split_frame,
    text="▶ Start Capture",
    command=start_capture,
    fg="green",
    **main_action_button_style,
)
start_button.grid(row=0, column=0, sticky="ew")

start_menu_button = tk.Button(
    start_capture_split_frame,
    text="▼",
    command=show_start_capture_menu,
    fg="green",
    font=("Segoe UI", 9, "bold"),
    padx=6,
    pady=5,
    relief="raised",
    borderwidth=2,
)
start_menu_button.grid(row=0, column=1, sticky="ns", padx=(2, 0))

start_capture_menu = tk.Menu(root, tearoff=0)
start_capture_menu.add_command(label="Add Job to Queue", command=add_current_job_and_open_queue)
start_capture_menu.add_command(label="Add Job to Queue and Start", command=add_current_job_to_queue_and_start)
start_capture_menu.add_command(label="Split and Add to Queue", command=split_and_add_to_queue)
start_capture_menu.add_command(label="Add Jobs to Queue by Domain", command=add_jobs_to_queue_by_domain)
start_capture_menu.add_command(label="Add Failed to Queue", command=add_failed_to_queue)

stop_button = tk.Button(
    workflow_frame,
    text="■ Stop",
    command=stop_capture,
    fg="red",
    state="disabled",
    **main_action_button_style,
)
stop_button.grid(row=0, column=3, sticky="ew", padx=(0, 8))

copy_summary_button = tk.Button(
    workflow_frame,
    text="📋 Copy Case Summary",
    command=copy_case_summary,
    fg="#8A6500",
    activeforeground="#8A6500",
    state="disabled",
    **main_action_button_style,
)
copy_summary_button.grid(row=0, column=4, sticky="ew")

ttk.Label(main, textvariable=status_var).grid(row=12, column=0, columnspan=4, sticky="w", pady=(0, 6))

ttk.Label(main, text="Output Log").grid(row=13, column=0, columnspan=4, sticky="w")

log_box = scrolledtext.ScrolledText(main, height=14, wrap="word")
log_box.grid(row=15, column=0, columnspan=4, sticky="nsew")

if FRESH_STARTUP_MESSAGES:
    log_box.insert("end", "\n".join(FRESH_STARTUP_MESSAGES) + "\n")
    log_box.see("end")

capture_options_panel = ttk.LabelFrame(main, text="Capture Options", padding=12)
capture_options_panel.columnconfigure(0, weight=1)
capture_options_panel.columnconfigure(1, weight=1)
capture_options_panel.columnconfigure(2, weight=1)
capture_options_panel.rowconfigure(5, weight=1)

ttk.Label(
    capture_options_panel,
    text="These options are passed to the underlying yt-dlp capture script. Defaults prioritize OSINT-friendly sidecar metadata while keeping the workflow simple.",
    wraplength=980,
    justify="left",
).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))

mode_frame = ttk.LabelFrame(capture_options_panel, text="Capture Mode", padding=8)
mode_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
ttk.Radiobutton(
    mode_frame,
    text="Download media and selected sidecars",
    variable=capture_mode_var,
    value="media",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    mode_frame,
    text="Media + embedded metadata; ignore sidecars",
    variable=capture_mode_var,
    value="media_embedded",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    mode_frame,
    text="Media only; ignore metadata options",
    variable=capture_mode_var,
    value="media_only",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    mode_frame,
    text="Metadata/artifacts only; do not download media",
    variable=capture_mode_var,
    value="metadata_only",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)

scope_frame = ttk.LabelFrame(capture_options_panel, text="Source Scope", padding=8)
scope_frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=(0, 8))
ttk.Radiobutton(
    scope_frame,
    text="Single item only",
    variable=source_scope_var,
    value="single",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    scope_frame,
    text="Include playlist / multi-item source",
    variable=source_scope_var,
    value="include_playlist",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)

format_frame = ttk.LabelFrame(capture_options_panel, text="Format", padding=8)
format_frame.grid(row=1, column=2, sticky="nsew", padx=(8, 0), pady=(0, 8))
format_frame.columnconfigure(1, weight=1)

ttk.Label(format_frame, text="Strategy").grid(row=0, column=0, sticky="w", pady=2)
format_strategy_menu = ttk.Combobox(
    format_frame,
    textvariable=format_strategy_var,
    values=["best", "prefer_mp4", "strict_mp4", "audio_only", "low_bandwidth"],
    state="readonly",
    width=18,
)
format_strategy_menu.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=2)
format_strategy_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())

ttk.Label(format_frame, text="Max resolution").grid(row=1, column=0, sticky="w", pady=(6, 2))
max_resolution_menu = ttk.Combobox(
    format_frame,
    textvariable=max_resolution_var,
    values=["best", "2160", "1440", "1080", "720", "480"],
    state="readonly",
    width=10,
)
max_resolution_menu.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=(6, 2))
max_resolution_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())

ttk.Checkbutton(
    format_frame,
    text="Generate Windows .url shortcuts",
    variable=generate_url_shortcuts_var,
    command=update_capture_options_summary,
).grid(row=2, column=0, columnspan=2, sticky="w", pady=2)


archive_frame = ttk.LabelFrame(capture_options_panel, text="Archive Mode", padding=8)
archive_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
ttk.Radiobutton(
    archive_frame,
    text="Use case download archive",
    variable=archive_mode_var,
    value="use",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    archive_frame,
    text="Ignore archive for this run",
    variable=archive_mode_var,
    value="ignore",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    archive_frame,
    text="Force re-capture",
    variable=archive_mode_var,
    value="force",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)

date_outer_frame = ttk.LabelFrame(capture_options_panel, text="Date Filters", padding=8)
date_outer_frame.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=8, pady=(0, 8))

playlist_frame = ttk.LabelFrame(capture_options_panel, text="Playlist Options", padding=8)
playlist_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 8))
playlist_frame.columnconfigure(1, weight=1)
playlist_frame.columnconfigure(3, weight=0)
playlist_frame.columnconfigure(5, weight=0)

playlist_option_widgets = []

playlist_items_check = ttk.Checkbutton(
    playlist_frame,
    text="Items",
    variable=playlist_items_enabled_var,
    command=update_capture_options_summary,
)
playlist_items_check.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)
playlist_option_widgets.append((playlist_items_check, "check", None))

playlist_items_entry = ttk.Entry(playlist_frame, textvariable=playlist_items_var, width=28)
playlist_items_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=3)
playlist_option_widgets.append((playlist_items_entry, "entry", playlist_items_enabled_var))

playlist_order_check = ttk.Checkbutton(
    playlist_frame,
    text="Order",
    variable=playlist_order_enabled_var,
    command=update_capture_options_summary,
)
playlist_order_check.grid(row=0, column=2, sticky="w", padx=(0, 8), pady=3)
playlist_option_widgets.append((playlist_order_check, "check", None))

playlist_order_menu = ttk.Combobox(
    playlist_frame,
    textvariable=playlist_order_var,
    values=["normal", "reverse", "random"],
    state="readonly",
    width=10,
)
playlist_order_menu.grid(row=0, column=3, sticky="w", padx=(0, 12), pady=3)
playlist_order_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())
playlist_option_widgets.append((playlist_order_menu, "combo", playlist_order_enabled_var))

max_playlist_items_check = ttk.Checkbutton(
    playlist_frame,
    text="Max items",
    variable=max_playlist_items_enabled_var,
    command=update_capture_options_summary,
)
max_playlist_items_check.grid(row=0, column=4, sticky="w", padx=(0, 8), pady=3)
playlist_option_widgets.append((max_playlist_items_check, "check", None))

max_playlist_items_entry = ttk.Entry(playlist_frame, textvariable=max_playlist_items_var, width=8)
max_playlist_items_entry.grid(row=0, column=5, sticky="w", pady=3)
playlist_option_widgets.append((max_playlist_items_entry, "entry", max_playlist_items_enabled_var))

break_on_existing_check = ttk.Checkbutton(
    playlist_frame,
    text="Stop when archived item is found",
    variable=break_on_existing_var,
    command=update_capture_options_summary,
)
break_on_existing_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=3)
playlist_option_widgets.append((break_on_existing_check, "check", None))

skip_playlist_after_errors_check = ttk.Checkbutton(
    playlist_frame,
    text="Skip after failed items",
    variable=skip_playlist_after_errors_enabled_var,
    command=update_capture_options_summary,
)
skip_playlist_after_errors_check.grid(row=1, column=2, sticky="w", padx=(0, 8), pady=3)
playlist_option_widgets.append((skip_playlist_after_errors_check, "check", None))

skip_playlist_after_errors_entry = ttk.Entry(playlist_frame, textvariable=skip_playlist_after_errors_var, width=8)
skip_playlist_after_errors_entry.grid(row=1, column=3, sticky="w", padx=(0, 12), pady=3)
playlist_option_widgets.append((skip_playlist_after_errors_entry, "entry", skip_playlist_after_errors_enabled_var))

ttk.Label(
    playlist_frame,
    text="Enabled only for playlist/multi-item sources. Check an option to pass that playlist flag. Saved values are preserved when unchecked.",
    wraplength=900,
    justify="left",
).grid(row=2, column=0, columnspan=6, sticky="w", pady=(6, 0))

output_record_frame = ttk.LabelFrame(capture_options_panel, text="Output Records", padding=8)
output_record_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 8))
output_record_frame.columnconfigure(1, weight=1)
output_record_frame.columnconfigure(3, weight=1)

ttk.Label(output_record_frame, text="Case Browser cache").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)
gui_cache_mode_menu = ttk.Combobox(
    output_record_frame,
    textvariable=gui_cache_mode_var,
    values=["After run", "After each URL", "Off"],
    state="readonly",
    width=18,
)
gui_cache_mode_menu.grid(row=0, column=1, sticky="w", pady=3)
gui_cache_mode_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())

ttk.Label(output_record_frame, text="File manifest").grid(row=0, column=2, sticky="w", padx=(16, 8), pady=3)
manifest_mode_menu = ttk.Combobox(
    output_record_frame,
    textvariable=manifest_mode_var,
    values=["Full", "This run"],
    state="readonly",
    width=12,
)
manifest_mode_menu.grid(row=0, column=3, sticky="w", pady=3)
manifest_mode_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())

ttk.Label(
    output_record_frame,
    text="Cache controls when Case Browser thumbnails/details are prepared. Manifest controls whether all case files or only this run's files are hashed.",
    wraplength=900,
    justify="left",
).grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

date_filter_frame = ttk.Frame(date_outer_frame)
date_filter_frame.grid(row=0, column=0, columnspan=6, sticky="ew")

current_year = datetime.now().year
year_values = [str(year) for year in range(CAPTURE_DATE_MIN.year, current_year + 1)]

ttk.Checkbutton(
    date_filter_frame,
    text="Date after",
    variable=date_after_enabled_var,
    command=update_date_filter_states,
).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=2)

date_after_year_menu = ttk.Combobox(
    date_filter_frame,
    textvariable=date_after_year_var,
    values=year_values,
    width=6,
    state="disabled",
)
date_after_year_menu.grid(row=0, column=1, padx=2, pady=2)

date_after_month_menu = ttk.Combobox(
    date_filter_frame,
    textvariable=date_after_month_var,
    values=get_allowed_month_values(datetime.now().year),
    width=4,
    state="disabled",
)
date_after_month_menu.grid(row=0, column=2, padx=2, pady=2)

date_after_day_menu = ttk.Combobox(
    date_filter_frame,
    textvariable=date_after_day_var,
    values=get_allowed_day_values(datetime.now().year, datetime.now().month),
    width=4,
    state="disabled",
)
date_after_day_menu.grid(row=0, column=3, padx=2, pady=2)

ttk.Checkbutton(
    date_filter_frame,
    text="Date before",
    variable=date_before_enabled_var,
    command=update_date_filter_states,
).grid(row=1, column=0, sticky="w", padx=(0, 6), pady=2)

date_before_year_menu = ttk.Combobox(
    date_filter_frame,
    textvariable=date_before_year_var,
    values=year_values,
    width=6,
    state="disabled",
)
date_before_year_menu.grid(row=1, column=1, padx=2, pady=2)

date_before_month_menu = ttk.Combobox(
    date_filter_frame,
    textvariable=date_before_month_var,
    values=get_allowed_month_values(datetime.now().year),
    width=4,
    state="disabled",
)
date_before_month_menu.grid(row=1, column=2, padx=2, pady=2)

date_before_day_menu = ttk.Combobox(
    date_filter_frame,
    textvariable=date_before_day_var,
    values=get_allowed_day_values(datetime.now().year, datetime.now().month),
    width=4,
    state="disabled",
)
date_before_day_menu.grid(row=1, column=3, padx=2, pady=2)

for widget, prefix in (
    (date_after_year_menu, "after"),
    (date_after_month_menu, "after"),
    (date_after_day_menu, "after"),
    (date_before_year_menu, "before"),
    (date_before_month_menu, "before"),
    (date_before_day_menu, "before"),
):
    widget.bind("<<ComboboxSelected>>", lambda event, p=prefix: on_date_filter_combo_changed(p))

ttk.Label(
    date_filter_frame,
    text="Year / Month / Day - allowed range: Jan 01, 2000 through today",
).grid(row=2, column=1, columnspan=5, sticky="w", padx=2, pady=(2, 0))

update_date_filter_states()
update_playlist_options_state()


capture_button_frame = ttk.Frame(capture_options_panel)
capture_button_frame.grid(row=5, column=0, columnspan=3, sticky="ne", pady=(8, 0))

ttk.Button(
    capture_button_frame,
    text="Close Capture Options",
    command=close_capture_options_panel,
).pack(side="left", padx=6)

capture_options_panel.grid_remove()

metadata_options_panel = ttk.LabelFrame(main, text="Metadata Options", padding=12)
metadata_options_panel.columnconfigure(0, weight=1)
metadata_options_panel.columnconfigure(1, weight=1)
metadata_options_panel.columnconfigure(2, weight=1)
metadata_options_panel.rowconfigure(4, weight=1)

ttk.Label(
    metadata_options_panel,
    text="Sidecar options create separate files. Embed options modify the final media container and apply in Media + sidecars or Media + Embedded mode.",
    wraplength=980,
    justify="left",
).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))

artifact_frame = ttk.LabelFrame(metadata_options_panel, text="Sidecar Artifacts", padding=8)
artifact_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
artifact_frame.columnconfigure(0, weight=1)
artifact_frame.columnconfigure(1, weight=1)
artifact_frame.columnconfigure(2, weight=1)
artifact_frame.columnconfigure(3, weight=1)

artifact_options = [
    ("Save metadata JSON", write_info_json_var, 0, 0),
    ("Save source link", write_source_link_var, 0, 1),
    ("Save description", write_description_var, 0, 2),
    ("Save thumbnail", write_thumbnail_var, 0, 3),
    ("Save subtitles", write_subs_var, 1, 0),
    ("Save automatic subtitles", write_auto_subs_var, 1, 1),
    ("Save comments when supported", write_comments_var, 1, 2),
]

sidecar_option_widgets = []

for label_text, variable, row_index, column_index in artifact_options:
    widget = ttk.Checkbutton(
        artifact_frame,
        text=label_text,
        variable=variable,
        command=update_capture_options_summary,
    )
    widget.grid(row=row_index, column=column_index, sticky="w", padx=4, pady=3)
    sidecar_option_widgets.append(widget)

playlist_metadata_check = ttk.Checkbutton(
    artifact_frame,
    text="Save playlist metadata",
    variable=save_playlist_metadata_var,
    command=update_capture_options_summary,
)
playlist_metadata_check.grid(row=1, column=3, sticky="w", padx=4, pady=3)

ttk.Label(
    artifact_frame,
    text="Sidecar files remain separate from the final media file and are easier to inspect, hash, compare, and preserve independently.",
    wraplength=900,
    justify="left",
).grid(row=2, column=0, columnspan=4, sticky="ew", padx=4, pady=(6, 0))

embed_frame = ttk.LabelFrame(metadata_options_panel, text="Embed Options", padding=8)
embed_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 8))
embed_frame.columnconfigure(0, weight=1)
embed_frame.columnconfigure(1, weight=1)
embed_frame.columnconfigure(2, weight=1)

embed_option_widgets = []

embed_options = [
    ("Embed metadata into media file", embed_metadata_var, 0, 0),
    ("Embed thumbnail as cover art", embed_thumbnail_var, 0, 1),
    ("Embed subtitles into media file", embed_subs_var, 0, 2),
    ("Embed chapter markers", embed_chapters_var, 1, 0),
    ("Embed info JSON into MKV/MKA", embed_info_json_var, 1, 1),
]

for label_text, variable, row_index, column_index in embed_options:
    widget = ttk.Checkbutton(
        embed_frame,
        text=label_text,
        variable=variable,
        command=update_capture_options_summary,
    )
    widget.grid(row=row_index, column=column_index, sticky="w", padx=4, pady=3)
    embed_option_widgets.append(widget)

ttk.Label(
    embed_frame,
    text="Embedding applies in Media + sidecars or Media + Embedded mode. Media + Embedded ignores sidecar files. Some embed options depend on output format, available metadata, and FFmpeg/mutagen support.",
    wraplength=900,
    justify="left",
).grid(row=2, column=0, columnspan=3, sticky="ew", padx=4, pady=(6, 0))

metadata_button_frame = ttk.Frame(metadata_options_panel)
metadata_button_frame.grid(row=4, column=0, columnspan=3, sticky="ne", pady=(8, 0))

ttk.Button(
    metadata_button_frame,
    text="Close Metadata Options",
    command=close_metadata_options_panel,
).pack(side="left", padx=6)

metadata_options_panel.grid_remove()
update_playlist_metadata_visibility()
update_metadata_options_state()

advanced_options_panel = ttk.LabelFrame(main, text="Advanced Options", padding=12)
advanced_options_panel.columnconfigure(0, weight=1)
advanced_options_panel.columnconfigure(1, weight=1)
advanced_options_panel.columnconfigure(2, weight=1)

ttk.Label(
    advanced_options_panel,
    text="Advanced controls for filtering, impersonation, failure behavior, and queue concurrency.",
    wraplength=980,
    justify="left",
).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))

keyword_frame = ttk.LabelFrame(advanced_options_panel, text="Match / Reject Keywords", padding=8)
keyword_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
keyword_frame.columnconfigure(1, weight=1)

ttk.Label(keyword_frame, text="Only capture titles matching").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)
ttk.Entry(keyword_frame, textvariable=match_keywords_var).grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=3)
ttk.Button(keyword_frame, text="Clear", command=clear_match_keywords).grid(row=0, column=2, sticky="e", pady=3)

ttk.Label(keyword_frame, text="Reject titles matching").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=3)
ttk.Entry(keyword_frame, textvariable=reject_keywords_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=3)
ttk.Button(keyword_frame, text="Clear", command=clear_reject_keywords).grid(row=1, column=2, sticky="e", pady=3)

ttk.Label(
    keyword_frame,
    text="Enter one or more keywords separated by commas. The script builds a safe case-insensitive title filter.",
    wraplength=900,
    justify="left",
).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

impersonate_frame = ttk.LabelFrame(advanced_options_panel, text="Impersonate Target", padding=8)
impersonate_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 8))
impersonate_frame.columnconfigure(1, weight=1)

ttk.Label(impersonate_frame, text="Target").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)

impersonate_menu_box = ttk.Combobox(
    impersonate_frame,
    textvariable=impersonate_var,
    values=DEFAULT_IMPERSONATE_TARGETS,
    state="readonly",
)
impersonate_menu_box.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=3)

check_targets_button = ttk.Button(
    impersonate_frame,
    text="Check Targets",
    command=check_impersonate_targets,
)
check_targets_button.grid(row=0, column=2, sticky="e", pady=3)

impersonate_menu = impersonate_menu_box

ttk.Label(
    impersonate_frame,
    textvariable=target_status_var,
).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

ttk.Checkbutton(
    impersonate_frame,
    text="Show all targets",
    variable=show_all_impersonate_targets_var,
    command=lambda: target_status_var.set("Impersonate targets: Not checked"),
).grid(row=1, column=2, sticky="e", pady=(6, 0))

failure_rate_options_row = ttk.Frame(advanced_options_panel)
failure_rate_options_row.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 8))
failure_rate_options_row.columnconfigure(0, weight=1, uniform="advanced_half")
failure_rate_options_row.columnconfigure(1, weight=1, uniform="advanced_half")
failure_rate_options_row.rowconfigure(0, weight=1)

failure_frame = ttk.LabelFrame(failure_rate_options_row, text="Failure Handling", padding=8)
failure_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
ttk.Radiobutton(
    failure_frame,
    text="Continue after failed URL",
    variable=failure_handling_var,
    value="continue",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    failure_frame,
    text="Stop on first failed URL",
    variable=failure_handling_var,
    value="stop",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)

rate_options = [
    ("None - 0 sec baseline, jitter up to 5 sec", "none", 0, 0),
    ("Fast - 15 sec baseline, jitter up to 30 sec", "fast", 0, 1),
    ("Normal - 30 sec baseline, jitter up to 60 sec", "normal", 1, 0),
    ("Cautious - 60 sec baseline, jitter up to 120 sec", "cautious", 1, 1),
]

concurrency_frame = ttk.LabelFrame(failure_rate_options_row, text="Concurrent Captures", padding=8)
concurrency_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
concurrency_frame.columnconfigure(1, weight=1)

ttk.Label(concurrency_frame, text="Maximum active queue jobs").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)
concurrency_menu = ttk.Combobox(
    concurrency_frame,
    textvariable=concurrent_captures_var,
    values=["1", "2", "3", "4"],
    state="readonly",
    width=8,
)
concurrency_menu.grid(row=0, column=1, sticky="w", pady=3)
concurrency_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())

ttk.Label(
    concurrency_frame,
    text="Values above 1 use the Job Queue and check for matching URL domains before concurrent runs.",
    wraplength=360,
    justify="left",
).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

advanced_button_frame = ttk.Frame(advanced_options_panel)
advanced_button_frame.grid(row=4, column=0, columnspan=3, sticky="e", pady=(8, 0))

ttk.Button(
    advanced_button_frame,
    text="Close Advanced Options",
    command=close_advanced_options_panel,
).pack(side="left", padx=6)

advanced_options_panel.grid_remove()

pacing_options_panel = ttk.LabelFrame(main, text="Pacing Options", padding=12)
pacing_options_panel.columnconfigure(0, weight=1)
pacing_options_panel.columnconfigure(1, weight=1)
pacing_options_panel.columnconfigure(2, weight=1)

ttk.Label(
    pacing_options_panel,
    text="Controls for request pacing, retries, throttle detection, transfer limits, fragments, and HTTP chunking.",
    wraplength=980,
    justify="left",
).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))

pacing_top_row = ttk.Frame(pacing_options_panel)
pacing_top_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
pacing_top_row.columnconfigure(0, weight=1)
pacing_top_row.columnconfigure(1, weight=1)

pacing_rate_frame = ttk.LabelFrame(pacing_top_row, text="Request Rate Limit", padding=8)
pacing_rate_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
pacing_rate_frame.columnconfigure(0, weight=1)
pacing_rate_frame.columnconfigure(1, weight=1)

for label_text, value, row_index, column_index in rate_options:
    ttk.Radiobutton(
        pacing_rate_frame,
        text=label_text,
        variable=rate_limit_var,
        value=value,
        command=update_capture_options_summary,
    ).grid(row=row_index, column=column_index, sticky="w", padx=(0, 8), pady=2)

retry_frame = ttk.LabelFrame(pacing_top_row, text="Retry Behaviour", padding=8)
retry_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
retry_frame.columnconfigure(1, weight=1)

ttk.Label(retry_frame, text="Retry profile").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)
retry_behavior_menu = ttk.Combobox(
    retry_frame,
    textvariable=retry_behavior_var,
    values=["light", "normal", "aggressive"],
    state="readonly",
    width=14,
)
retry_behavior_menu.grid(row=0, column=1, sticky="w", pady=3)
retry_behavior_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())

ttk.Label(
    retry_frame,
    text="Light reduces retries; Aggressive raises retries and retry sleep windows for unstable sources.",
    wraplength=430,
    justify="left",
).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

download_speed_frame = ttk.LabelFrame(pacing_options_panel, text="Download Speed Limit", padding=8)
download_speed_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 8))
download_speed_frame.columnconfigure(1, weight=1)

download_speed_use_check = ttk.Checkbutton(
    download_speed_frame,
    text="Use limit",
    variable=download_speed_limit_enabled_var,
    command=on_download_speed_limit_enabled_changed,
)
download_speed_use_check.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)

download_speed_slider = ttk.Scale(
    download_speed_frame,
    from_=0,
    to=DOWNLOAD_SPEED_SLIDER_MAX,
    variable=download_speed_slider_var,
    command=on_download_speed_slider_changed,
)
download_speed_slider.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=3)

download_speed_entry = ttk.Entry(
    download_speed_frame,
    textvariable=download_speed_limit_var,
    width=16,
)
download_speed_entry.grid(row=0, column=2, sticky="e", pady=3)
download_speed_entry.bind("<Return>", on_download_speed_entry_commit)
download_speed_entry.bind("<FocusOut>", on_download_speed_entry_commit)

ttk.Label(
    download_speed_frame,
    text="Range: 1 KiB/s to 1 GiB/s. The slider increases logarithmically; edit the value directly for precision.",
    wraplength=720,
    justify="left",
).grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

sync_download_speed_limit_controls_from_var(show_errors=False)

pacing_bottom_row = ttk.Frame(pacing_options_panel)
pacing_bottom_row.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 8))
pacing_bottom_row.columnconfigure(0, weight=1)
pacing_bottom_row.columnconfigure(1, weight=1)
pacing_bottom_row.columnconfigure(2, weight=1)

throttle_frame = ttk.LabelFrame(pacing_bottom_row, text="Throttle Detection", padding=8)
throttle_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
throttle_frame.columnconfigure(1, weight=1)

ttk.Checkbutton(
    throttle_frame,
    text="Use throttled-rate detection",
    variable=throttle_detection_enabled_var,
    command=lambda: (update_throttled_rate_state(), update_capture_options_summary()),
).grid(row=0, column=0, columnspan=2, sticky="w", pady=3)

ttk.Label(throttle_frame, text="Threshold").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=3)
throttled_rate_entry = ttk.Entry(throttle_frame, textvariable=throttled_rate_var, width=14)
throttled_rate_entry.grid(row=1, column=1, sticky="w", pady=3)
throttled_rate_entry.bind("<Return>", on_throttled_rate_commit)
throttled_rate_entry.bind("<FocusOut>", on_throttled_rate_commit)
update_throttled_rate_state()

http_chunk_frame = ttk.LabelFrame(pacing_bottom_row, text="HTTP Chunks", padding=8)
http_chunk_frame.grid(row=0, column=1, sticky="nsew", padx=6)
http_chunk_frame.columnconfigure(1, weight=1)

ttk.Checkbutton(
    http_chunk_frame,
    text="Use HTTP chunk size",
    variable=http_chunk_size_enabled_var,
    command=lambda: (update_http_chunk_size_state(), update_capture_options_summary()),
).grid(row=0, column=0, columnspan=2, sticky="w", pady=3)

ttk.Label(http_chunk_frame, text="Chunk size").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=3)
http_chunk_size_entry = ttk.Entry(http_chunk_frame, textvariable=http_chunk_size_var, width=14)
http_chunk_size_entry.grid(row=1, column=1, sticky="w", pady=3)
http_chunk_size_entry.bind("<Return>", on_http_chunk_size_commit)
http_chunk_size_entry.bind("<FocusOut>", on_http_chunk_size_commit)
update_http_chunk_size_state()

fragments_frame = ttk.LabelFrame(pacing_bottom_row, text="Concurrent Fragments", padding=8)
fragments_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
fragments_frame.columnconfigure(1, weight=1)

ttk.Label(fragments_frame, text="Fragment workers per URL").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=3)
fragments_menu = ttk.Combobox(
    fragments_frame,
    textvariable=concurrent_fragments_var,
    values=["1", "2", "4", "8"],
    state="readonly",
    width=8,
)
fragments_menu.grid(row=0, column=1, sticky="w", pady=3)
fragments_menu.bind("<<ComboboxSelected>>", lambda event: update_capture_options_summary())

pacing_button_frame = ttk.Frame(pacing_options_panel)
pacing_button_frame.grid(row=4, column=0, columnspan=3, sticky="e", pady=(8, 0))

ttk.Button(
    pacing_button_frame,
    text="Close Pacing Options",
    command=close_pacing_options_panel,
).pack(side="left", padx=6)

pacing_options_panel.grid_remove()

case_name_var.trace_add("write", update_case_folder_preview)
input_file_var.trace_add("write", handle_input_file_var_changed)
output_root_var.trace_add("write", on_output_root_changed)
update_case_folder_preview()

root.protocol("WM_DELETE_WINDOW", on_close)

try:
    app_notebook.select(main)
except Exception:
    pass

def deferred_job_queue_startup():
    global job_queue_state_loading

    try:
        job_queue_state_loading = True
        open_job_queue(select_tab=False)
    finally:
        job_queue_state_loading = False

    load_job_queue_state(startup=True)
    refresh_job_queue_window()

load_settings(show_popup=False, startup=True)
initialize_url_box_from_persistence_and_input_files()
start_case_browser_result_poller()
schedule_case_browser_autoload(delay_ms=400)
schedule_playlist_preview_autoload(delay_ms=500)
apply_app_theme()
update_window_title()
if check_vpn_var.get():
    root.after(300, refresh_network_adapters)
else:
    vpn_status_var.set("VPN: Check disabled")

root.after(150, deferred_job_queue_startup)

root.mainloop()
