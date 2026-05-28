import base64
import calendar
import csv
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import urllib.request
import webbrowser
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog


APP_TITLE = "yt-dlp GUI for OSINT"
APP_VERSION = "v0.2026.0528"
APP_RELEASES_LATEST_URL = "https://github.com/jmashuque/ytdlp-gui-for-osint/releases/latest"
APP_GITHUB_LATEST_API_URL = "https://api.github.com/repos/jmashuque/ytdlp-gui-for-osint/releases/latest"
SETTINGS_SCHEMA_VERSION = 6
CAPTURE_DATE_MIN = datetime(2000, 1, 1)

ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(ROOT, "gui-settings.json")
DEFAULT_PROFILE_NAME = "Default"

DEFAULTS = {
    "script_path": os.path.join(ROOT, "script.ps1"),
    "yt_dlp_path": os.path.join(ROOT, "yt-dlp.exe"),
    "input_file": os.path.join(ROOT, "urls.txt"),
    "case_name": "Case-%date%",
    "cookies_file": os.path.join(ROOT, "cookies.txt"),
    "output_root": os.path.join(ROOT, "Investigations"),
    "ffmpeg_folder": ROOT,
    "impersonate_target": "None",
    "prefer_mp4": False,
    "capture_mode": "media",
    "source_scope": "single",
    "archive_mode": "use",
    "max_resolution": "best",
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
    "keep_partials": False,
    "write_info_json": True,
    "write_source_link": True,
    "write_description": False,
    "write_thumbnail": False,
    "write_subs": False,
    "write_auto_subs": False,
    "write_comments": False,
    "vpn_adapter_name": "",
}

APP_SETTINGS_DEFAULTS = {
    "delete_cookies_on_exit": False,
    "check_vpn": True,
    "dark_mode": False,
    "case_browser_filter": "All",
    "case_browser_sort": "Name",
    "case_browser_current_only": False,
    "case_browser_icon_scale": "Medium",
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
case_browser_images = []
case_browser_file_map = {}
last_capture_context = {}
last_successful_case_summary = ""


def browse_file(var, title="Select file"):
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


def get_case_template_values(now=None):
    now = now or datetime.now()

    return {
        "%date%": now.strftime("%Y-%m-%d"),
        "%time%": now.strftime("%H-%M-%S"),
        "%datetime%": now.strftime("%Y-%m-%d_%H-%M-%S"),
        "%year%": now.strftime("%Y"),
        "%month%": now.strftime("%m"),
        "%day%": now.strftime("%d"),
        "%hour%": now.strftime("%H"),
        "%minute%": now.strftime("%M"),
        "%second%": now.strftime("%S"),
    }


def render_case_name_template(template, now=None):
    rendered = str(template or "").strip()

    for tag, value in get_case_template_values(now).items():
        rendered = rendered.replace(tag, value)

    return rendered


def get_resolved_case_name(now=None):
    template = case_name_var.get().strip()
    rendered = render_case_name_template(template, now=now)
    return safe_case_name(rendered)


def insert_case_name_tag(tag):
    try:
        case_name_entry.insert("insert", tag)
        case_name_entry.focus_set()
    except Exception:
        current = case_name_var.get()
        case_name_var.set(f"{current}{tag}")


def get_current_case_folder(now=None):
    output_root = output_root_var.get().strip()
    case_name = get_resolved_case_name(now=now)

    if not output_root:
        raise ValueError("Output Root is blank.")

    if not case_name:
        raise ValueError("Case Name is blank after resolving the template.")

    return os.path.join(output_root, case_name)


def case_folder_is_populated(case_folder):
    if not os.path.isdir(case_folder):
        return False

    try:
        with os.scandir(case_folder) as entries:
            for entry in entries:
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
            case_folder_preview_var.set(f"Resolved case folder: {case_folder}  [existing populated folder]")
        elif os.path.isdir(case_folder):
            case_folder_preview_var.set(f"Resolved case folder: {case_folder}  [folder exists]")
        else:
            case_folder_preview_var.set(f"Resolved case folder: {case_folder}")
    except Exception as e:
        try:
            case_folder_preview_var.set(f"Resolved case folder: unavailable ({e})")
        except Exception:
            pass


def confirm_case_folder_collision():
    try:
        case_folder = get_current_case_folder()
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
        dir_names[:] = [name for name in dir_names if name.lower() not in {"__pycache__"}]

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


def build_case_summary_text(exit_code, submitted_url_count, paths, versions, counts):
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
        "",
        "Counts:",
        f"  Total files: {counts.get('files', 0)}",
        f"  Media files: {counts.get('media', 0)}",
        f"  Metadata JSON files: {counts.get('metadata', 0)}",
        f"  Log files: {counts.get('logs', 0)}",
        f"  Manifest files: {counts.get('manifests', 0)}",
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
        f"  Profile: {selected_profile_var.get()}",
        f"  Case name template: {case_name_var.get()}",
        f"  Resolved case name: {os.path.basename(paths.get('case_folder', ''))}",
        f"  Capture mode: {capture_mode_var.get()}",
        f"  Source scope: {source_scope_var.get()}",
        f"  Archive mode: {archive_mode_var.get()}",
        f"  Max resolution: {max_resolution_var.get()}",
        f"  Failure handling: {failure_handling_var.get()}",
        f"  Rate limit: {rate_limit_var.get()}",
        f"  Impersonate target: {impersonate_var.get()}",
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


def create_url_input_file():
    global temp_url_file

    pasted = urls_text.get("1.0", "end").strip()

    if not pasted:
        return input_file_var.get().strip()

    lines = []
    for line in pasted.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)

    if not lines:
        raise ValueError("The pasted URL box does not contain any usable URLs.")

    fd, path = tempfile.mkstemp(prefix="yt-dlp-gui-urls-", suffix=".txt", text=True)
    os.close(fd)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")

    temp_url_file = path
    return path


def count_submitted_urls():
    pasted = urls_text.get("1.0", "end").strip()

    if pasted:
        return len([
            line for line in pasted.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ])

    input_file = input_file_var.get().strip()
    if os.path.isfile(input_file):
        try:
            with open(input_file, "r", encoding="utf-8-sig") as f:
                return len([
                    line for line in f.read().splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ])
        except Exception:
            return "Unknown"

    return 0


def load_urls_from_input_file():
    path = input_file_var.get().strip()

    if not path or not os.path.isfile(path):
        messagebox.showerror("Input file not found", "Input File is missing or invalid.")
        return

    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()

        urls_text.delete("1.0", "end")
        urls_text.insert("1.0", content)
        append_log(f"\nLoaded URLs from input file: {path}\n")
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="cp1252") as f:
                content = f.read()

            urls_text.delete("1.0", "end")
            urls_text.insert("1.0", content)
            append_log(f"\nLoaded URLs from input file using cp1252 fallback: {path}\n")
        except Exception as e:
            messagebox.showerror("Read error", f"Could not read input file:\n\n{e}")
    except Exception as e:
        messagebox.showerror("Read error", f"Could not read input file:\n\n{e}")


def save_urls_to_file():
    content = urls_text.get("1.0", "end").strip()

    if not content:
        messagebox.showwarning("No URLs", "The URL box is empty.")
        return

    default_name = f"{safe_case_name(case_name_var.get().strip() or 'urls')}_urls.txt"

    path = filedialog.asksaveasfilename(
        title="Save URLs to file",
        defaultextension=".txt",
        initialfile=default_name,
        filetypes=[
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )

    if not path:
        return

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            f.write("\n")

        input_file_var.set(path)
        append_log(f"\nSaved URLs to file: {path}\n")
        messagebox.showinfo("Saved", f"URLs saved to:\n\n{path}")
    except Exception as e:
        messagebox.showerror("Save failed", f"Could not save URLs:\n\n{e}")


def clear_urls():
    urls_text.delete("1.0", "end")
    append_log("\nCleared pasted URL box.\n")


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
    input_file = input_file_var.get().strip()
    cookies_file = cookies_file_var.get().strip()
    output_root = output_root_var.get().strip()
    ffmpeg_folder = ffmpeg_folder_var.get().strip()

    pasted_urls = urls_text.get("1.0", "end").strip()

    if not script_path or not os.path.isfile(script_path):
        raise ValueError("PowerShell script path is missing or invalid.")

    if not yt_dlp_path or not os.path.isfile(yt_dlp_path):
        raise ValueError("yt-dlp path is missing or invalid.")

    if not pasted_urls:
        if not input_file or not os.path.isfile(input_file):
            raise ValueError("Input file is missing or invalid, and no URLs were pasted.")

    if cookies_file and not os.path.isfile(cookies_file):
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
    if cookies_file:
        cmd += ["-CookiesFile", cookies_file]

    ffmpeg_folder = ffmpeg_folder_var.get().strip()
    if ffmpeg_folder:
        cmd += ["-FFmpegFolder", ffmpeg_folder]

    impersonate_target = normalize_impersonate_target(impersonate_var.get())
    if impersonate_target:
        cmd += ["-ImpersonateTarget", impersonate_target]

    if prefer_mp4_var.get():
        cmd += ["-PreferMp4"]

    if capture_mode_var.get() == "metadata_only":
        cmd += ["-MetadataOnly"]

    if source_scope_var.get() == "include_playlist":
        cmd += ["-IncludePlaylist"]

    archive_mode = archive_mode_var.get().strip() or "use"
    if archive_mode == "ignore":
        cmd += ["-ArchiveMode", "Ignore"]
    elif archive_mode == "force":
        cmd += ["-ArchiveMode", "Force"]
    else:
        cmd += ["-ArchiveMode", "Use"]

    max_resolution = max_resolution_var.get().strip() or "best"
    if max_resolution != "best":
        cmd += ["-MaxResolution", max_resolution]

    if save_playlist_metadata_var.get():
        cmd += ["-SavePlaylistMetadata"]

    if generate_url_shortcuts_var.get():
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
    if rate_limit == "fast":
        cmd += ["-RateLimit", "Fast"]
    elif rate_limit == "cautious":
        cmd += ["-RateLimit", "Cautious"]
    else:
        cmd += ["-RateLimit", "Normal"]

    if keep_partials_var.get():
        cmd += ["-KeepPartials"]

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
    input_file = input_file_var.get().strip()
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
        add_check("Input file exists", os.path.isfile(input_file), input_file)

    if cookies_file:
        add_check("Cookies file exists", os.path.isfile(cookies_file), cookies_file)
    else:
        add_check("Cookies file", True, "Not specified")

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


def get_settings_dict():
    return {
        "script_path": script_path_var.get(),
        "yt_dlp_path": yt_dlp_path_var.get(),
        "input_file": input_file_var.get(),
        "case_name": case_name_var.get(),
        "cookies_file": cookies_file_var.get(),
        "output_root": output_root_var.get(),
        "ffmpeg_folder": ffmpeg_folder_var.get(),
        "impersonate_target": impersonate_var.get(),
        "prefer_mp4": prefer_mp4_var.get(),
        "capture_mode": capture_mode_var.get(),
        "source_scope": source_scope_var.get(),
        "archive_mode": archive_mode_var.get(),
        "max_resolution": max_resolution_var.get(),
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
        "keep_partials": keep_partials_var.get(),
        "write_info_json": write_info_json_var.get(),
        "write_source_link": write_source_link_var.get(),
        "write_description": write_description_var.get(),
        "write_thumbnail": write_thumbnail_var.get(),
        "write_subs": write_subs_var.get(),
        "write_auto_subs": write_auto_subs_var.get(),
        "write_comments": write_comments_var.get(),
        "vpn_adapter_name": vpn_adapter_var.get(),
    }


def apply_settings_dict(settings):
    script_path_var.set(settings.get("script_path", DEFAULTS["script_path"]))
    yt_dlp_path_var.set(settings.get("yt_dlp_path", DEFAULTS["yt_dlp_path"]))
    input_file_var.set(settings.get("input_file", DEFAULTS["input_file"]))
    case_name_var.set(settings.get("case_name", DEFAULTS["case_name"]))
    cookies_file_var.set(settings.get("cookies_file", DEFAULTS["cookies_file"]))
    output_root_var.set(settings.get("output_root", DEFAULTS["output_root"]))
    ffmpeg_folder_var.set(settings.get("ffmpeg_folder", DEFAULTS["ffmpeg_folder"]))
    impersonate_var.set(settings.get("impersonate_target", DEFAULTS["impersonate_target"]))
    prefer_mp4_var.set(bool(settings.get("prefer_mp4", DEFAULTS["prefer_mp4"])))
    capture_mode_var.set(settings.get("capture_mode", DEFAULTS["capture_mode"]))
    source_scope_var.set(settings.get("source_scope", DEFAULTS["source_scope"]))
    archive_mode_var.set(settings.get("archive_mode", DEFAULTS["archive_mode"]))
    max_resolution_var.set(settings.get("max_resolution", DEFAULTS["max_resolution"]))
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
    keep_partials_var.set(bool(settings.get("keep_partials", DEFAULTS["keep_partials"])))
    write_info_json_var.set(bool(settings.get("write_info_json", DEFAULTS["write_info_json"])))
    write_source_link_var.set(bool(settings.get("write_source_link", DEFAULTS["write_source_link"])))
    write_description_var.set(bool(settings.get("write_description", DEFAULTS["write_description"])))
    write_thumbnail_var.set(bool(settings.get("write_thumbnail", DEFAULTS["write_thumbnail"])))
    write_subs_var.set(bool(settings.get("write_subs", DEFAULTS["write_subs"])))
    write_auto_subs_var.set(bool(settings.get("write_auto_subs", DEFAULTS["write_auto_subs"])))
    write_comments_var.set(bool(settings.get("write_comments", DEFAULTS["write_comments"])))
    vpn_adapter_var.set(settings.get("vpn_adapter_name", DEFAULTS["vpn_adapter_name"]))
    update_capture_options_summary()


def make_default_profile_settings():
    return DEFAULTS.copy()


def get_app_settings_dict():
    return {
        "delete_cookies_on_exit": delete_cookies_on_exit_var.get(),
        "check_vpn": check_vpn_var.get(),
        "dark_mode": dark_mode_var.get(),
        "case_browser_filter": case_browser_filter_var.get(),
        "case_browser_sort": case_browser_sort_var.get(),
        "case_browser_current_only": case_browser_current_only_var.get(),
        "case_browser_icon_scale": case_browser_icon_scale_var.get(),
    }


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
    update_vpn_section_visibility()


def get_app_settings_summary_lines():
    delete_state = "enabled" if delete_cookies_on_exit_var.get() else "disabled"
    vpn_state = "enabled" if check_vpn_var.get() else "disabled"
    return [
        f"Delete cookies on exit: {delete_state}",
        f"Check VPN: {vpn_state}",
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


def update_vpn_tools_menu_state():
    try:
        state = "normal" if check_vpn_var.get() else "disabled"
        tools_menu.entryconfig("Refresh VPN Adapters", state=state)
        tools_menu.entryconfig("Check VPN", state=state)
    except Exception:
        # The app setting can be loaded before the Tools menu exists during startup.
        pass


def update_vpn_section_visibility():
    try:
        if check_vpn_var.get():
            vpn_frame.grid()
        else:
            vpn_frame.grid_remove()
            vpn_status_var.set("VPN: Check disabled")
    except Exception:
        # The app setting can be loaded before the VPN frame exists during startup.
        pass

    update_vpn_tools_menu_state()


def toggle_check_vpn_setting():
    update_vpn_section_visibility()
    state = "enabled" if check_vpn_var.get() else "disabled"
    save_app_settings(show_popup=False, changed_setting_label=f"Check VPN {state}")


def delete_selected_cookies_file_on_exit():
    cookies_path = cookies_file_var.get().strip()

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

    recognized_top_level = {"version", "profiles", "app_settings", "unrecognized_settings", "loaded_version"}
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
    store = ensure_app_settings_store(store)
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

    profile_menu.add_command(
        label="Load Default Profile",
        command=lambda: load_profile(DEFAULT_PROFILE_NAME, show_popup=True),
    )

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
            "unrecognized_settings": {
                "top_level": {},
                "profiles": {},
                "app_settings": {},
            },
        }
        apply_app_settings_dict(settings_store["app_settings"])
        append_log(f"Settings file not found. Using defaults.\nExpected path: {settings_path}\n")
        log_app_settings_status()
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

    if running_process is not None and running_process.poll() is None:
        messagebox.showwarning("Already running", "A capture process is already running.")
        return

    try:
        validate_inputs()
        cmd = build_powershell_command()
        if not confirm_case_folder_collision():
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
    append_log(f"Settings saved to: {SETTINGS_FILE}\n\n")

    tool_versions = query_capture_tool_versions_for_log()
    log_capture_tool_versions(tool_versions)

    global last_capture_context
    last_capture_context = {
        "tool_versions": tool_versions,
        "submitted_url_count": count_submitted_urls(),
    }

    append_log("Command:\n")
    append_log(" ".join(f'"{part}"' if " " in part else part for part in cmd))
    append_log("\n\n")

    start_button.config(state="disabled")
    stop_button.config(state="normal")
    set_status("Running...")

    submitted_url_count = count_submitted_urls()

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

            if running_process.stdout:
                for line in running_process.stdout:
                    root.after(0, append_log, line)

            exit_code = running_process.wait()

            root.after(0, show_run_summary, exit_code, submitted_url_count)

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
            root.after(0, lambda: stop_button.config(state="disabled"))

    threading.Thread(target=worker, daemon=True).start()


def show_run_summary(exit_code, submitted_url_count):
    global last_successful_case_summary

    try:
        paths = get_expected_run_paths()
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

        counts = count_case_files(paths["case_folder"])
        append_log(f"Total files found: {counts.get('files', 0)}\n")
        append_log(f"Media files found: {counts.get('media', 0)}\n")
        append_log(f"Metadata JSON files found: {counts.get('metadata', 0)}\n")
        append_log(f"Manifest files found: {counts.get('manifests', 0)}\n")
        append_log(f"Run log files found: {counts.get('logs', 0)}\n")

    append_log("=================================\n")

    if exit_code == 0 and paths:
        versions = last_capture_context.get("tool_versions", {})
        last_successful_case_summary = build_case_summary_text(
            exit_code,
            submitted_url_count,
            paths,
            versions,
            counts,
        )
        copy_summary_button.config(state="normal")
        append_log("Case summary is available. Use Copy Case Summary to copy it to the clipboard.\n")
    else:
        last_successful_case_summary = ""
        copy_summary_button.config(state="disabled")

def stop_capture():
    global running_process

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

                latest_release_url_var.set(url)

                current_tuple = normalize_version_for_compare(APP_VERSION)
                latest_tuple = normalize_version_for_compare(tag)

                if latest_tuple and current_tuple and latest_tuple > current_tuple:
                    status_text = "A newer release appears to be available. Open the release page to manually download the latest ZIP."
                elif latest_tuple and current_tuple and latest_tuple == current_tuple:
                    status_text = "You appear to be on the latest tagged release."
                else:
                    status_text = "Latest release was found. Review the release page to confirm whether an update is needed."

                def update_ui():
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


def fetch_ytdlp_nightly_releases(limit=30):
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
                releases = fetch_ytdlp_nightly_releases(limit=30)

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
        "The reference URL is hardcoded to a single YouTube video and yt-dlp is run with "
        "--simulate and --no-playlist to avoid processing homepage feeds or playlists."
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
    reference_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

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



def update_capture_options_summary(*args):
    try:
        mode = "Metadata only" if capture_mode_var.get() == "metadata_only" else "Media + artifacts"
        scope = "Include playlist" if source_scope_var.get() == "include_playlist" else "Single item"

        archive_names = {
            "use": "case archive",
            "ignore": "ignore archive",
            "force": "force re-capture",
        }
        archive_text = archive_names.get(archive_mode_var.get(), "case archive")

        rate_names = {
            "fast": "fast",
            "normal": "normal",
            "cautious": "cautious",
        }
        rate_text = rate_names.get(rate_limit_var.get(), "normal")
        resolution_text = "best" if max_resolution_var.get() == "best" else f"max {max_resolution_var.get()}p"
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

        date_filters = []
        if date_after_enabled_var.get():
            date_filters.append("after")
        if date_before_enabled_var.get():
            date_filters.append("before")

        if date_filters:
            artifacts.append("date " + "/".join(date_filters))

        artifact_text = ", ".join(artifacts) if artifacts else "no sidecars"
        capture_options_summary_var.set(f"{mode}; {scope}; {archive_text}; {resolution_text}; {rate_text}; {failure_text}; {artifact_text}")
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


def toggle_capture_options_panel():
    if capture_options_panel.winfo_ismapped():
        hide_capture_options_panel(save=True)
        return

    hide_advanced_options_panel(save=True)
    update_capture_options_summary()
    capture_options_panel.grid(
        row=10,
        column=0,
        columnspan=3,
        rowspan=8,
        sticky="nsew",
        padx=0,
        pady=(8, 0),
    )
    capture_options_panel.tkraise()
    capture_options_button.config(text="Capture Options ▴")


def close_capture_options_panel():
    hide_capture_options_panel(save=True)


def update_playlist_metadata_visibility(*args):
    try:
        if source_scope_var.get() == "include_playlist":
            playlist_metadata_check.grid()
        else:
            save_playlist_metadata_var.set(False)
            playlist_metadata_check.grid_remove()
    except Exception:
        pass

    update_capture_options_summary()


def toggle_advanced_options_panel():
    if advanced_options_panel.winfo_ismapped():
        hide_advanced_options_panel(save=True)
        return

    hide_capture_options_panel(save=True)
    update_capture_options_summary()
    advanced_options_panel.grid(
        row=10,
        column=0,
        columnspan=3,
        rowspan=8,
        sticky="nsew",
        padx=0,
        pady=(8, 0),
    )
    advanced_options_panel.tkraise()
    advanced_options_button.config(text="Advanced Options ▴")


def close_advanced_options_panel():
    hide_advanced_options_panel(save=True)


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


def get_gui_thumbnail_path(video_path):
    cache_folder = get_gui_thumbnail_cache_folder_for_path(video_path)
    try:
        file_hash = hashlib.sha256()
        with open(video_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                file_hash.update(chunk)
        thumb_name = f"{file_hash.hexdigest().upper()}.png"
    except Exception:
        thumb_name = hashlib.sha256(os.path.abspath(video_path).encode("utf-8", errors="ignore")).hexdigest().upper() + ".png"

    return os.path.join(cache_folder, thumb_name)


def generate_gui_thumbnail(video_path):
    thumb_path = get_gui_thumbnail_path(video_path)

    if os.path.isfile(thumb_path):
        return thumb_path

    ffmpeg_exe = get_ffmpeg_executable_for_gui()
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

    try:
        file_hash = hashlib.sha256()
        with open(media_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                file_hash.update(chunk)
        metadata_name = f"{file_hash.hexdigest().upper()}.ffprobe.json"
    except Exception:
        metadata_name = hashlib.sha256(os.path.abspath(media_path).encode("utf-8", errors="ignore")).hexdigest().upper() + ".ffprobe.json"

    return os.path.join(metadata_folder, metadata_name)


def load_or_generate_media_info(media_path):
    metadata_path = get_gui_metadata_path(media_path)

    if os.path.isfile(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    ffprobe_exe = get_ffprobe_executable_for_gui()
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


def open_case_browser():
    output_root = output_root_var.get().strip()

    if not output_root:
        messagebox.showwarning("Output root missing", "Output Root is blank.")
        return

    if not os.path.isdir(output_root):
        messagebox.showwarning("Output root not found", f"Output Root does not exist:\n\n{output_root}")
        return

    browser = tk.Toplevel(root)
    browser.title("Case Browser")
    browser.geometry("1100x720")
    browser.minsize(900, 560)
    browser.transient(root)

    browser_file_map = {}
    tree_path_map = {}
    image_refs = []

    top_bar = ttk.Frame(browser, padding=8)
    top_bar.pack(fill="x")

    ttk.Label(top_bar, text=f"Output Root: {output_root}").pack(side="left", fill="x", expand=True)

    paned = ttk.PanedWindow(browser, orient="horizontal")
    paned.pack(fill="both", expand=True, padx=8, pady=(0, 8))

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

    def save_case_browser_preferences():
        save_app_settings(show_popup=False)

    def refresh_browser_view():
        save_case_browser_preferences()
        try:
            render_files(get_selected_browser_folder())
        except NameError:
            # During window construction, render_files/get_selected_browser_folder are defined later.
            pass

    def get_browser_icon_geometry():
        scale = browser_icon_scale_var.get()

        if scale == "Small":
            return {
                "thumb_w": 120,
                "thumb_h": 76,
                "card_w": 150,
                "wrap": 130,
                "label_width": 20,
                "columns": 6,
                "font_big": 12,
                "font_small": 8,
            }

        if scale == "Large":
            return {
                "thumb_w": 220,
                "thumb_h": 138,
                "card_w": 260,
                "wrap": 230,
                "label_width": 34,
                "columns": 3,
                "font_big": 18,
                "font_small": 10,
            }

        return {
            "thumb_w": 160,
            "thumb_h": 100,
            "card_w": 200,
            "wrap": 170,
            "label_width": 24,
            "columns": 4,
            "font_big": 14,
            "font_small": 9,
        }

    ttk.Label(right_frame, textvariable=browser_status_var).grid(row=0, column=0, sticky="ew", pady=(0, 6))

    browser_controls = ttk.Frame(right_frame)
    browser_controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    browser_controls.columnconfigure(5, weight=1)

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
        values=["Name", "Type", "Size", "Newest", "Oldest"],
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
        # Keep the content frame at its natural requested width so horizontal scrolling works.
        canvas.configure(scrollregion=canvas.bbox("all"))

    content_frame.bind("<Configure>", configure_content)
    canvas.bind("<Configure>", configure_canvas)

    paned.add(right_frame, weight=4)

    def insert_folder(parent_id, folder_path, max_depth=4, depth=0):
        if depth > max_depth:
            return

        try:
            entries = [
                entry for entry in os.scandir(folder_path)
                if entry.is_dir() and entry.name.lower() not in {".gui-cache", "__pycache__"}
            ]
        except Exception:
            entries = []

        entries.sort(key=lambda entry: entry.name.lower())

        for entry in entries:
            item_id = tree.insert(parent_id, "end", text=entry.name, open=False)
            tree_path_map[item_id] = entry.path
            insert_folder(item_id, entry.path, max_depth=max_depth, depth=depth + 1)

    root_id = tree.insert("", "end", text=os.path.basename(os.path.abspath(output_root)) or output_root, open=True)
    tree_path_map[root_id] = output_root
    insert_folder(root_id, output_root)

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
        menu = tk.Menu(browser, tearoff=0)
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

    def file_matches_browser_filter(path):
        ext = os.path.splitext(path)[1].lower()
        selected_filter = browser_filter_var.get()

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

    def list_display_files(folder_path):
        display_files = []

        if browser_current_only_var.get():
            try:
                names = os.listdir(folder_path)
            except Exception:
                names = []

            for name in names:
                path = os.path.join(folder_path, name)
                if os.path.isfile(path) and file_matches_browser_filter(path):
                    display_files.append(path)
        else:
            for root_dir, dir_names, file_names in os.walk(folder_path):
                dir_names[:] = [
                    name for name in dir_names
                    if name.lower() not in {".gui-cache", "__pycache__"}
                ]

                for file_name in file_names:
                    path = os.path.join(root_dir, file_name)
                    if file_matches_browser_filter(path):
                        display_files.append(path)

        sort_mode = browser_sort_var.get()

        if sort_mode == "Type":
            display_files.sort(key=lambda p: (os.path.splitext(p)[1].lower(), os.path.basename(p).lower()))
        elif sort_mode == "Size":
            display_files.sort(key=lambda p: (-(os.path.getsize(p) if os.path.isfile(p) else 0), os.path.basename(p).lower()))
        elif sort_mode == "Newest":
            display_files.sort(key=lambda p: (-(os.path.getmtime(p) if os.path.isfile(p) else 0), os.path.basename(p).lower()))
        elif sort_mode == "Oldest":
            display_files.sort(key=lambda p: ((os.path.getmtime(p) if os.path.isfile(p) else 0), os.path.basename(p).lower()))
        else:
            display_files.sort(key=lambda p: (not is_browser_media_file(p), os.path.basename(p).lower()))

        return display_files

    def render_files(folder_path):
        clear_content()

        files = list_display_files(folder_path)
        browser_status_var.set(f"{folder_path} - {len(files)} file(s)")

        if not files:
            ttk.Label(content_frame, text="No media or sidecar files found in this folder.").grid(row=0, column=0, sticky="w", padx=12, pady=12)
            return

        geometry = get_browser_icon_geometry()
        columns = geometry["columns"]
        thumb_w = geometry["thumb_w"]
        thumb_h = geometry["thumb_h"]
        wrap = geometry["wrap"]
        label_width = geometry["label_width"]

        for index, path in enumerate(files):
            row = index // columns
            column = index % columns

            card = ttk.Frame(content_frame, padding=10, relief="ridge")
            card.grid(row=row, column=column, sticky="n", padx=10, pady=10)

            ext = os.path.splitext(path)[1].lower().lstrip(".")
            thumb_loaded = False
            info_summary = None
            tooltip_text = f"{os.path.basename(path)}\n\nDouble-click to open. Right-click for actions."

            if is_browser_media_file(path):
                media_info = load_or_generate_media_info(path)
                info_summary = get_media_info_summary(media_info, path)
                tooltip_text = info_summary["tooltip"] + "\n\nDouble-click to open."

            if is_browser_video_file(path):
                thumb_path = generate_gui_thumbnail(path)
                if thumb_path and os.path.isfile(thumb_path):
                    try:
                        image = tk.PhotoImage(file=thumb_path)
                        if image.width() > thumb_w or image.height() > thumb_h:
                            factor = max(1, int(max(image.width() / thumb_w, image.height() / thumb_h)))
                            image = image.subsample(factor, factor)
                        image_refs.append(image)
                        thumb = tk.Canvas(card, width=thumb_w, height=thumb_h, highlightthickness=1, relief="ridge")
                        thumb.create_image(thumb_w // 2, thumb_h // 2, image=image, anchor="center")
                        thumb_loaded = True
                    except Exception:
                        thumb_loaded = False

            if not thumb_loaded:
                thumb = make_placeholder(
                    card,
                    ext or "file",
                    width=thumb_w,
                    height=thumb_h,
                    font_big=geometry["font_big"],
                    font_small=geometry["font_small"],
                )

            thumb.grid(row=0, column=0, pady=(0, 6))

            name_label = ttk.Label(card, text=os.path.basename(path), width=label_width, wraplength=wrap, justify="center")
            name_label.grid(row=1, column=0)

            if info_summary:
                info_label = ttk.Label(card, text=info_summary["card"], width=label_width, wraplength=wrap, justify="center")
                info_label.grid(row=2, column=0)
                rel_row = 3
            else:
                info_label = None
                rel_row = 2

            try:
                rel_path = os.path.relpath(path, folder_path)
            except Exception:
                rel_path = path

            type_label = ttk.Label(card, text=rel_path, width=label_width, wraplength=wrap, justify="center")
            type_label.grid(row=rel_row, column=0)

            widgets = [card, thumb, name_label, type_label]
            if info_label:
                widgets.append(info_label)

            for widget in widgets:
                widget.bind("<Double-Button-1>", lambda event, p=path: open_selected_file(p))
                widget.bind("<Button-3>", lambda event, p=path, fp=folder_path: show_file_context_menu(event, p, fp))
                widget.bind("<Button-2>", lambda event, p=path, fp=folder_path: show_file_context_menu(event, p, fp))
                Tooltip(widget, tooltip_text)

        configure_content()


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
            if os.path.commonpath([output_root_abs, folder_abs]) == output_root_abs:
                rel = os.path.relpath(folder_abs, output_root_abs)
                first_part = rel.split(os.sep)[0]
                if first_part and first_part not in {".", ".."}:
                    return os.path.join(output_root_abs, first_part)
        except Exception:
            pass

        return folder_path

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

                    manifest_paths.add(os.path.abspath(path))

                    if not os.path.isfile(path):
                        missing.append(path)
                        continue

                    try:
                        h = hashlib.sha256()
                        with open(path, "rb") as input_file_obj:
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
                dir_names[:] = [name for name in dir_names if name.lower() not in {"__pycache__"}]
                for file_name in file_names:
                    path = os.path.abspath(os.path.join(root_dir, file_name))
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
            )

            append_log("\nCase file verification:\n" + summary + "\n")
            messagebox.showinfo("Case file verification", summary)

        except Exception as e:
            messagebox.showerror("Verification failed", f"Could not verify case files:\n\n{e}")

    def refresh_tree():
        for item in tree.get_children(""):
            tree.delete(item)

        tree_path_map.clear()
        root_item = tree.insert("", "end", text=os.path.basename(os.path.abspath(output_root)) or output_root, open=True)
        tree_path_map[root_item] = output_root
        insert_folder(root_item, output_root)
        clear_content()
        browser_status_var.set("Case tree refreshed. Select a folder to view captured files.")

    tree.bind("<<TreeviewSelect>>", on_tree_select)
    filter_menu.bind("<<ComboboxSelected>>", lambda event: refresh_browser_view())
    sort_menu.bind("<<ComboboxSelected>>", lambda event: refresh_browser_view())
    scale_menu.bind("<<ComboboxSelected>>", lambda event: refresh_browser_view())

    ttk.Button(top_bar, text="Refresh", command=refresh_tree).pack(side="right", padx=(6, 0))
    ttk.Button(top_bar, text="Verify Case Files", command=verify_case_files).pack(side="right", padx=(6, 0))
    ttk.Button(top_bar, text="Open Folder", command=open_selected_browser_folder).pack(side="right", padx=(6, 0))
    ttk.Button(top_bar, text="Open Output Root", command=lambda: os.startfile(output_root)).pack(side="right", padx=(6, 0))

    tree.selection_set(root_id)
    tree.focus(root_id)
    render_files(output_root)


def on_close():
    global temp_url_file

    try:
        save_settings(show_popup=False)
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
root.geometry("1180x900")
root.minsize(1050, 780)

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
vpn_adapter_var = tk.StringVar(value=DEFAULTS["vpn_adapter_name"])
vpn_status_var = tk.StringVar(value="VPN: Not checked")
target_status_var = tk.StringVar(value="Impersonate targets: Not checked")
status_var = tk.StringVar(value="Ready")
yt_dlp_version_status_var = tk.StringVar(value="yt-dlp: not checked")
preflight_done_var = tk.BooleanVar(value=False)
delete_cookies_on_exit_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["delete_cookies_on_exit"])
check_vpn_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["check_vpn"])
dark_mode_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["dark_mode"])
case_browser_filter_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["case_browser_filter"])
case_browser_sort_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["case_browser_sort"])
case_browser_current_only_var = tk.BooleanVar(value=APP_SETTINGS_DEFAULTS["case_browser_current_only"])
case_browser_icon_scale_var = tk.StringVar(value=APP_SETTINGS_DEFAULTS["case_browser_icon_scale"])
selected_profile_var = tk.StringVar(value=DEFAULT_PROFILE_NAME)
capture_options_summary_var = tk.StringVar(value="")
capture_mode_var = tk.StringVar(value=DEFAULTS["capture_mode"])
source_scope_var = tk.StringVar(value=DEFAULTS["source_scope"])
archive_mode_var = tk.StringVar(value=DEFAULTS["archive_mode"])
max_resolution_var = tk.StringVar(value=DEFAULTS["max_resolution"])
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
keep_partials_var = tk.BooleanVar(value=DEFAULTS["keep_partials"])
write_info_json_var = tk.BooleanVar(value=DEFAULTS["write_info_json"])
write_source_link_var = tk.BooleanVar(value=DEFAULTS["write_source_link"])
write_description_var = tk.BooleanVar(value=DEFAULTS["write_description"])
write_thumbnail_var = tk.BooleanVar(value=DEFAULTS["write_thumbnail"])
write_subs_var = tk.BooleanVar(value=DEFAULTS["write_subs"])
write_auto_subs_var = tk.BooleanVar(value=DEFAULTS["write_auto_subs"])
write_comments_var = tk.BooleanVar(value=DEFAULTS["write_comments"])


for option_var in [
    prefer_mp4_var,
    capture_mode_var,
    source_scope_var,
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
    keep_partials_var,
    write_info_json_var,
    write_source_link_var,
    write_description_var,
    write_thumbnail_var,
    write_subs_var,
    write_auto_subs_var,
    write_comments_var,
]:
    option_var.trace_add("write", update_capture_options_summary)

source_scope_var.trace_add("write", update_playlist_metadata_visibility)
update_capture_options_summary()

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

main.columnconfigure(1, weight=1)
main.rowconfigure(12, weight=1)
main.rowconfigure(17, weight=2)


def add_file_row(row, label, var):
    ttk.Label(main, text=label).grid(row=row, column=0, sticky="w", pady=3)
    ttk.Entry(main, textvariable=var).grid(row=row, column=1, sticky="ew", padx=6, pady=3)
    ttk.Button(main, text="Browse...", command=lambda: browse_file(var, label)).grid(row=row, column=2, sticky="e", pady=3)


def add_folder_row(row, label, var):
    ttk.Label(main, text=label).grid(row=row, column=0, sticky="w", pady=3)
    ttk.Entry(main, textvariable=var).grid(row=row, column=1, sticky="ew", padx=6, pady=3)
    ttk.Button(main, text="Browse...", command=lambda: browse_folder(var, label)).grid(row=row, column=2, sticky="e", pady=3)


# Menu bar keeps less-used actions out of the main workflow.
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Load URLs From Input File", command=load_urls_from_input_file)
file_menu.add_command(label="Save URLs To File", command=save_urls_to_file)
file_menu.add_command(label="Clear URL Box", command=clear_urls)
file_menu.add_separator()
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
tools_menu.add_command(label="Open Case Browser", command=open_case_browser)
tools_menu.add_separator()
tools_menu.add_command(label="Check Impersonate Targets", command=check_impersonate_targets)
tools_menu.add_separator()
tools_menu.add_command(label="Refresh VPN Adapters", command=refresh_network_adapters)
tools_menu.add_command(label="Check VPN", command=check_vpn_status)
update_vpn_tools_menu_state()

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
yt_dlp_path_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=6, pady=3)
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

add_file_row(2, "Input File", input_file_var)

ttk.Label(main, text="Case Name").grid(row=3, column=0, sticky="nw", pady=(6, 3))
case_name_frame = ttk.Frame(main)
case_name_frame.grid(row=3, column=1, columnspan=2, sticky="ew", padx=6, pady=3)
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
    ("%date%", "Date, e.g. 2026-05-27"),
    ("%time%", "Time, e.g. 14-30-05"),
    ("%datetime%", "Date and time, e.g. 2026-05-27_14-30-05"),
    ("%year%", "Year"),
    ("%month%", "Month"),
    ("%day%", "Day"),
    ("%hour%", "Hour"),
    ("%minute%", "Minute"),
    ("%second%", "Second"),
]

for tag, description in case_name_tag_items:
    case_tag_menu.add_command(
        label=f"{tag}    {description}",
        command=lambda value=tag: insert_case_name_tag(value),
    )

case_tag_menu_button.grid(row=0, column=1, sticky="e", padx=(0, 6))
ttk.Button(case_name_frame, text="Open", command=open_current_case_folder).grid(row=0, column=2, sticky="e")

add_file_row(4, "Cookies File", cookies_file_var)
add_folder_row(5, "Output Root", output_root_var)
add_folder_row(6, "FFmpeg Folder", ffmpeg_folder_var)

ttk.Label(main, text="Impersonate Target").grid(row=7, column=0, sticky="w", pady=3)
impersonate_frame = ttk.Frame(main)
impersonate_frame.grid(row=7, column=1, columnspan=2, sticky="ew", padx=6, pady=3)
impersonate_frame.columnconfigure(0, weight=1)

impersonate_menu_box = ttk.Combobox(
    impersonate_frame,
    textvariable=impersonate_var,
    values=DEFAULT_IMPERSONATE_TARGETS,
    state="readonly",
)
impersonate_menu_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))

check_targets_button = ttk.Button(
    impersonate_frame,
    text="Check Targets",
    command=check_impersonate_targets,
)
check_targets_button.grid(row=0, column=1, sticky="e")

impersonate_menu = impersonate_menu_box

impersonate_status_frame = ttk.Frame(main)
impersonate_status_frame.grid(row=8, column=1, columnspan=2, sticky="ew", padx=6, pady=(0, 4))
impersonate_status_frame.columnconfigure(0, weight=1)

ttk.Label(
    impersonate_status_frame,
    textvariable=target_status_var,
).grid(row=0, column=0, sticky="w")

ttk.Checkbutton(
    impersonate_status_frame,
    text="Show all targets",
    variable=show_all_impersonate_targets_var,
    command=lambda: target_status_var.set("Impersonate targets: Not checked"),
).grid(row=0, column=1, sticky="e")

options_frame = ttk.Frame(main)
options_frame.grid(row=9, column=1, columnspan=2, sticky="ew", padx=6, pady=5)
options_frame.columnconfigure(2, weight=1)

capture_options_button = ttk.Button(
    options_frame,
    text="Capture Options ▾",
    command=toggle_capture_options_panel,
)
capture_options_button.grid(row=0, column=0, sticky="w", padx=(0, 8))

advanced_options_button = ttk.Button(
    options_frame,
    text="Advanced Options ▾",
    command=toggle_advanced_options_panel,
)
advanced_options_button.grid(row=0, column=1, sticky="w", padx=(0, 10))

ttk.Label(
    options_frame,
    textvariable=capture_options_summary_var,
).grid(row=0, column=2, sticky="w")

vpn_frame = ttk.LabelFrame(main, text="VPN Status", padding=8)
vpn_frame.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(8, 6))
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
    text="Paste URLs below, one per line. If this box is used, it overrides the Input File field. URL load/save/clear actions are in the File menu.",
).grid(row=11, column=0, columnspan=3, sticky="w", pady=(10, 3))

urls_text = scrolledtext.ScrolledText(main, height=7, wrap="word")
urls_text.grid(row=12, column=0, columnspan=3, sticky="nsew", pady=(0, 8))

workflow_frame = ttk.Frame(main)
workflow_frame.grid(row=13, column=0, columnspan=3, sticky="ew", pady=(8, 12))
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
    text="Preflight run",
    variable=preflight_done_var,
    state="disabled",
)
preflight_check_box.grid(row=0, column=1, sticky="w", padx=(0, 8))

start_button = tk.Button(
    workflow_frame,
    text="▶ Start Capture",
    command=start_capture,
    fg="green",
    **main_action_button_style,
)
start_button.grid(row=0, column=2, sticky="ew", padx=(0, 8))

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

ttk.Label(main, textvariable=status_var).grid(row=14, column=0, columnspan=3, sticky="w", pady=(0, 6))

ttk.Label(main, text="Output Log").grid(row=15, column=0, columnspan=3, sticky="w")

log_box = scrolledtext.ScrolledText(main, height=14, wrap="word")
log_box.grid(row=17, column=0, columnspan=3, sticky="nsew")

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
    text="Download media and selected artifacts",
    variable=capture_mode_var,
    value="media",
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
ttk.Checkbutton(
    format_frame,
    text="Prefer MP4-compatible streams and merge to MP4",
    variable=prefer_mp4_var,
    command=update_capture_options_summary,
).grid(row=0, column=0, columnspan=2, sticky="w", pady=2)

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


artifact_frame = ttk.LabelFrame(capture_options_panel, text="Sidecar Artifacts", padding=8)
artifact_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 8))
artifact_frame.columnconfigure(0, weight=1)
artifact_frame.columnconfigure(1, weight=1)
artifact_frame.columnconfigure(2, weight=1)

artifact_options = [
    ("Save metadata JSON", write_info_json_var, 0, 0),
    ("Save source link", write_source_link_var, 0, 1),
    ("Save description", write_description_var, 0, 2),
    ("Save thumbnail", write_thumbnail_var, 1, 0),
    ("Save subtitles", write_subs_var, 1, 1),
    ("Save automatic subtitles", write_auto_subs_var, 1, 2),
    ("Save comments when supported", write_comments_var, 2, 0),
]

for label_text, variable, row_index, column_index in artifact_options:
    ttk.Checkbutton(
        artifact_frame,
        text=label_text,
        variable=variable,
        command=update_capture_options_summary,
    ).grid(row=row_index, column=column_index, sticky="w", padx=4, pady=3)

playlist_metadata_check = ttk.Checkbutton(
    artifact_frame,
    text="Save playlist metadata",
    variable=save_playlist_metadata_var,
    command=update_capture_options_summary,
)
playlist_metadata_check.grid(row=2, column=1, sticky="w", padx=4, pady=3)
update_playlist_metadata_visibility()

ttk.Label(
    capture_options_panel,
    text="Note: comments, subtitles, thumbnails, date filtering, and metadata availability depend on the source and yt-dlp extractor support.",
    wraplength=980,
    justify="left",
).grid(row=4, column=0, columnspan=3, sticky="ew", pady=(4, 12))

panel_button_frame = ttk.Frame(capture_options_panel)
panel_button_frame.grid(row=6, column=0, columnspan=3, sticky="e")

ttk.Button(
    panel_button_frame,
    text="Close Capture Options",
    command=close_capture_options_panel,
).pack(side="left", padx=6)

capture_options_panel.grid_remove()

advanced_options_panel = ttk.LabelFrame(main, text="Advanced Options", padding=12)
advanced_options_panel.columnconfigure(0, weight=1)
advanced_options_panel.columnconfigure(1, weight=1)
advanced_options_panel.columnconfigure(2, weight=1)

ttk.Label(
    advanced_options_panel,
    text="Advanced controls for filtering, failure behavior, and request pacing.",
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

failure_frame = ttk.LabelFrame(advanced_options_panel, text="Failure Handling", padding=8)
failure_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
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

rate_frame = ttk.LabelFrame(advanced_options_panel, text="Rate Limit", padding=8)
rate_frame.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=(8, 0), pady=(0, 8))
ttk.Radiobutton(
    rate_frame,
    text="Fast - 15 sec baseline, jitter up to 30 sec",
    variable=rate_limit_var,
    value="fast",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    rate_frame,
    text="Normal - 30 sec baseline, jitter up to 60 sec",
    variable=rate_limit_var,
    value="normal",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)
ttk.Radiobutton(
    rate_frame,
    text="Cautious - 60 sec baseline, jitter up to 120 sec",
    variable=rate_limit_var,
    value="cautious",
    command=update_capture_options_summary,
).pack(anchor="w", pady=2)

advanced_button_frame = ttk.Frame(advanced_options_panel)
advanced_button_frame.grid(row=3, column=0, columnspan=3, sticky="e", pady=(8, 0))

ttk.Button(
    advanced_button_frame,
    text="Close Advanced Options",
    command=close_advanced_options_panel,
).pack(side="left", padx=6)

advanced_options_panel.grid_remove()

case_name_var.trace_add("write", update_case_folder_preview)
output_root_var.trace_add("write", update_case_folder_preview)
update_case_folder_preview()

root.protocol("WM_DELETE_WINDOW", on_close)

load_settings(show_popup=False, startup=True)
apply_app_theme()
update_window_title()
if check_vpn_var.get():
    refresh_network_adapters()
else:
    vpn_status_var.set("VPN: Check disabled")

root.mainloop()
