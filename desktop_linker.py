#!/usr/bin/env python3
"""
Desktop Linker - Create desktop shortcuts on Linux
Dependencies: python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib, Gdk

import os
import stat
import glob
import shutil
import locale
import subprocess
from pathlib import Path


# ─────────────────────────────────────────────
#  Translations
# ─────────────────────────────────────────────

TRANSLATIONS = {
    "en": {
        "app_title":            "Desktop Linker",
        "tab_files":            "File / Folder",
        "tab_apps":             "Applications",
        "drop_hint":            "Drag a file or folder here\nor use the buttons below",
        "no_path":              "No path selected",
        "select_file_folder":   "Select a file or folder",
        "btn_choose_file":      "Choose File",
        "btn_choose_folder":    "Choose Folder",
        "shortcut_name":        "Shortcut name",
        "configure_shortcut":   "Configure shortcut",
        "custom_icon":          "Custom icon (optional)",
        "no_icon":              "No custom icon – default will be used",
        "btn_choose_icon":      "Choose Icon",
        "btn_clear_icon":       "Clear icon",
        "btn_create_file":      "Create Shortcut",
        "btn_create_app":       "Create App Shortcut",
        "search_placeholder":   "Search apps…",
        "unknown_app":          "Unknown",
        "dialog_file_title":    "Select File",
        "dialog_folder_title":  "Select Folder",
        "dialog_icon_title":    "Select Icon",
        "filter_images":        "Images (PNG, SVG, XPM)",
        "toast_created":        "Shortcut created: {}",
        "toast_error":          "Error: {}",
        "toast_no_file":        "Please select a file or folder first!",
        "toast_no_app":         "Please select an app from the list first!",
        "lang_button_tooltip":  "Switch to German",
        "about_app":            "Create desktop shortcuts for files, folders and applications.",
        "about_version":        "Version",
        "about_developer":      "Developer",
    },
    "de": {
        "app_title":            "Desktop Linker",
        "tab_files":            "Datei / Ordner",
        "tab_apps":             "Anwendungen",
        "drop_hint":            "Datei oder Ordner hierher ziehen\noder Button nutzen",
        "no_path":              "Kein Pfad gewählt",
        "select_file_folder":   "Datei oder Ordner auswählen",
        "btn_choose_file":      "Datei wählen",
        "btn_choose_folder":    "Ordner wählen",
        "shortcut_name":        "Name der Verknüpfung",
        "configure_shortcut":   "Verknüpfung konfigurieren",
        "custom_icon":          "Eigenes Icon (optional)",
        "no_icon":              "Kein eigenes Icon – Standard wird verwendet",
        "btn_choose_icon":      "Icon wählen",
        "btn_clear_icon":       "Icon zurücksetzen",
        "btn_create_file":      "Verknüpfung erstellen",
        "btn_create_app":       "App-Verknüpfung erstellen",
        "search_placeholder":   "App suchen …",
        "unknown_app":          "Unbekannt",
        "dialog_file_title":    "Datei auswählen",
        "dialog_folder_title":  "Ordner auswählen",
        "dialog_icon_title":    "Icon auswählen",
        "filter_images":        "Bilder (PNG, SVG, XPM)",
        "toast_created":        "Verknüpfung erstellt: {}",
        "toast_error":          "Fehler: {}",
        "toast_no_file":        "Bitte erst eine Datei oder einen Ordner auswählen!",
        "toast_no_app":         "Bitte erst eine App aus der Liste auswählen!",
        "lang_button_tooltip":  "Auf Englisch wechseln",
        "about_app":            "Erstellt Desktop-Verknüpfungen für Dateien, Ordner und Anwendungen.",
        "about_version":        "Version",
        "about_developer":      "Entwickler",
    },
    "ar": {
        "app_title":            "Desktop Linker",
        "tab_files":            "ملف / مجلد",
        "tab_apps":             "التطبيقات",
        "drop_hint":            "اسحب ملف او مجلد هنا\nاو استخدم اﻷزرار في اﻷسفل",
        "no_path":              "لم يتم تحديد الموقع",
        "select_file_folder":   "اختر ملفاً او مجلداً",
        "btn_choose_file":      "اختر الملف",
        "btn_choose_folder":    "اختر المجلد",
        "shortcut_name":        "اسم اﻷختصار",
        "configure_shortcut":   "التعديل على اﻷختصار",
        "custom_icon":          "ايقونة مخصصة (اختياري)",
        "no_icon":              "لم يتم اختيار ايقونة مخصصة - سوف تستخدم ايقونة افتراضية",
        "btn_choose_icon":      "اختر ايقونة",
        "btn_clear_icon":       "ازالة اﻷيقونة",
        "btn_create_file":      "صنع الاختصار",
        "btn_create_app":       "صنع اختصار لتطبيق",
        "search_placeholder":   "ابحث التطبيقات...",
        "unknown_app":          "غير معرف",
        "dialog_file_title":    "اختر الملف",
        "dialog_folder_title":  "اختر المجلد",
        "dialog_icon_title":    "اختر اﻷيقونة",
        "filter_images":        "(PNG, SVG, XPM) الصور",
        "toast_created":        "تم صنع اﻷختصار: {}",
        "toast_error":          "خطا: {}",
        "toast_no_file":        "الرجاء اختر ملف او مجلد اولاً!",
        "toast_no_app":         "الرجاء اختر تطبيقاً من القائمة املاً!",
        "lang_button_tooltip":  "التحويل الى الانجليزية",
        "about_app":            "صنع اختصارات للتطبيقات, والملفات, والمجلدات في سطح المكتب",
        "about_version":        "اﻷصدار",
        "about_developer":      "صانع البرنامج",
    },
}

APP_VERSION = "1.0.0"
APP_DEVELOPER = "aumuck"


def detect_language():
    """Detect system language, fall back to English."""
    try:
        lang = locale.getlocale()[0] or ""
        if lang.startswith("de"):
            return "de"
        elif lang.startswith("ar"):
            return "ar"
    except Exception:
        pass
    return "en"


class I18n:
    """Simple translation helper."""
    def __init__(self, lang=None):
        self.lang = lang or detect_language()

    def t(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]).get(key, key)

    def switch(self):
        self.lang = "de" if self.lang == "en" else "en"


# ─────────────────────────────────────────────
#  Backend helpers
# ─────────────────────────────────────────────

def get_desktop_dir():
    """Get desktop path via XDG or fallback."""
    try:
        result = subprocess.run(
            ["xdg-user-dir", "DESKTOP"],
            capture_output=True, text=True
        )
        path = result.stdout.strip()
        if path:
            return Path(path)
    except Exception:
        pass
    return Path.home() / "Desktop"


def find_installed_apps():
    """Find all installed .desktop files."""
    search_dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        str(Path.home() / ".local/share/applications"),
        "/var/lib/snapd/desktop/applications",
        "/var/lib/flatpak/exports/share/applications",
        str(Path.home() / ".local/share/flatpak/exports/share/applications"),
    ]
    apps = []
    seen = set()
    for d in search_dirs:
        for f in glob.glob(os.path.join(d, "*.desktop")):
            info = parse_desktop_file(f)
            if info and info.get("Name") and info.get("Name") not in seen:
                if info.get("NoDisplay", "false").lower() != "true":
                    seen.add(info["Name"])
                    info["_path"] = f
                    apps.append(info)
    apps.sort(key=lambda x: x["Name"].lower())
    return apps


def parse_desktop_file(path):
    """Parse a .desktop file into a dict."""
    info = {}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            in_section = False
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_section = True
                    continue
                if line.startswith("[") and line != "[Desktop Entry]":
                    in_section = False
                if in_section and "=" in line and not line.startswith("#"):
                    key, _, val = line.partition("=")
                    info[key.strip()] = val.strip()
    except Exception:
        pass
    return info


def unique_path(base_path):
    """Return a path that doesn't exist yet by appending a counter."""
    p = base_path
    counter = 1
    while p.exists():
        p = base_path.parent / f"{base_path.stem}_{counter}{base_path.suffix}"
        counter += 1
    return p


def create_file_shortcut(target_path, icon_path=None, custom_name=None):
    """Create a .desktop shortcut for a file or folder."""
    desktop_dir = get_desktop_dir()
    desktop_dir.mkdir(parents=True, exist_ok=True)

    target = Path(target_path)
    name = custom_name or target.name

    shortcut_path = unique_path(desktop_dir / f"{name}.desktop")

    if icon_path:
        icon_line = f"Icon={icon_path}"
    elif target.is_dir():
        icon_line = "Icon=folder"
    else:
        suffix = target.suffix.lower()
        mime_icons = {
            ".pdf":  "application-pdf",
            ".png":  "image-x-generic",
            ".jpg":  "image-x-generic",
            ".jpeg": "image-x-generic",
            ".mp3":  "audio-x-generic",
            ".ogg":  "audio-x-generic",
            ".flac": "audio-x-generic",
            ".mp4":  "video-x-generic",
            ".mkv":  "video-x-generic",
            ".sh":   "text-x-script",
        }
        icon_line = f"Icon={mime_icons.get(suffix, 'text-x-generic')}"

    content = (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        f"Name={name}\n"
        f"Exec=xdg-open \"{target}\"\n"
        f"{icon_line}\n"
        "Terminal=false\n"
    )
    shortcut_path.write_text(content, encoding="utf-8")
    os.chmod(shortcut_path, os.stat(shortcut_path).st_mode | stat.S_IEXEC)
    return str(shortcut_path)


def create_app_shortcut(desktop_file_path, icon_path=None, custom_name=None):
    """Copy an app .desktop file to the desktop."""
    desktop_dir = get_desktop_dir()
    desktop_dir.mkdir(parents=True, exist_ok=True)

    info = parse_desktop_file(desktop_file_path)
    name = custom_name or info.get("Name", Path(desktop_file_path).stem)

    shortcut_path = unique_path(desktop_dir / f"{name}.desktop")
    shutil.copy2(desktop_file_path, shortcut_path)

    if icon_path:
        lines = shortcut_path.read_text(encoding="utf-8").splitlines()
        new_lines = []
        replaced = False
        for line in lines:
            if line.startswith("Icon="):
                new_lines.append(f"Icon={icon_path}")
                replaced = True
            else:
                new_lines.append(line)
        if not replaced:
            new_lines.append(f"Icon={icon_path}")
        shortcut_path.write_text("\n".join(new_lines), encoding="utf-8")

    os.chmod(shortcut_path, os.stat(shortcut_path).st_mode | stat.S_IEXEC)
    return str(shortcut_path)


# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────

class DesktopLinkerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.desktoplinker")
        self.i18n = I18n()
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app, i18n=self.i18n)
        self.win.present()


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, i18n, **kwargs):
        super().__init__(**kwargs)
        self.i18n = i18n
        self.selected_icon_path = None
        self.file_target_path = None
        self.selected_app_info = None
        self.apps_list = find_installed_apps()

        self.set_default_size(700, 680)
        self._build_ui()

    def t(self, key):
        return self.i18n.t(key)

    def _build_ui(self):
        self.set_title(self.t("app_title"))

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # ── Header ──
        header = Adw.HeaderBar()
        header.add_css_class("flat")

        # Language toggle button
        self.lang_btn = Gtk.Button()
        self._update_lang_button()
        self.lang_btn.connect("clicked", self.on_toggle_language)
        header.pack_end(self.lang_btn)

        # About button
        about_btn = Gtk.Button()
        about_btn.set_icon_name("help-about-symbolic")
        about_btn.set_tooltip_text("About")
        about_btn.connect("clicked", self.on_about)
        header.pack_end(about_btn)

        main_box.append(header)

        # ── View Stack ──
        self.stack = Adw.ViewStack()

        top_switcher = Adw.ViewSwitcher()
        top_switcher.set_stack(self.stack)
        top_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(top_switcher)

        tab_bar = Adw.ViewSwitcherBar()
        tab_bar.set_stack(self.stack)
        tab_bar.set_reveal(True)

        # Build tabs
        self.file_page_content = self._build_file_tab()
        self.app_page_content = self._build_app_tab()

        self.file_stack_page = self.stack.add_titled_with_icon(
            self.file_page_content, "files",
            self.t("tab_files"), "folder-symbolic"
        )
        self.app_stack_page = self.stack.add_titled_with_icon(
            self.app_page_content, "apps",
            self.t("tab_apps"), "application-x-executable-symbolic"
        )

        main_box.append(self.stack)
        main_box.append(tab_bar)

        # ── Toast overlay ──
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)
        self.toast_overlay.set_child(main_box)

    # ────────────────────────────────────────────
    #  TAB 1 – File / Folder
    # ────────────────────────────────────────────
    def _build_file_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        # Drop area
        self.drop_label = Gtk.Label(label=self.t("drop_hint"))
        self.drop_label.set_justify(Gtk.Justification.CENTER)
        self.drop_label.add_css_class("dim-label")

        self.drop_area = Gtk.Frame()
        self.drop_area.set_size_request(-1, 120)

        drop_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        drop_inner.set_valign(Gtk.Align.CENTER)
        drop_inner.set_halign(Gtk.Align.CENTER)

        drop_icon = Gtk.Image.new_from_icon_name("document-send-symbolic")
        drop_icon.set_pixel_size(48)
        drop_icon.add_css_class("dim-label")
        drop_inner.append(drop_icon)
        drop_inner.append(self.drop_label)
        self.drop_area.set_child(drop_inner)

        drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        drop_target.connect("drop", self.on_file_drop)
        drop_target.connect("enter", lambda *_: Gdk.DragAction.COPY)
        self.drop_area.add_controller(drop_target)
        box.append(self.drop_area)

        # Path row
        self.file_path_row = Adw.ActionRow()
        self.file_path_row.set_title(self.t("no_path"))
        self.file_path_row.set_subtitle(self.t("select_file_folder"))
        self.file_path_row.add_css_class("property")

        self.btn_choose_file = Gtk.Button(label=self.t("btn_choose_file"))
        self.btn_choose_file.set_valign(Gtk.Align.CENTER)
        self.btn_choose_file.connect("clicked", self.on_choose_file)

        self.btn_choose_folder = Gtk.Button(label=self.t("btn_choose_folder"))
        self.btn_choose_folder.set_valign(Gtk.Align.CENTER)
        self.btn_choose_folder.connect("clicked", self.on_choose_folder)

        self.file_path_row.add_suffix(self.btn_choose_file)
        self.file_path_row.add_suffix(self.btn_choose_folder)

        # Name entry
        self.file_name_entry = Adw.EntryRow()
        self.file_name_entry.set_title(self.t("shortcut_name"))

        # Icon row
        self.file_icon_row = self._build_icon_row("file")

        self.file_group = Adw.PreferencesGroup()
        self.file_group.set_title(self.t("configure_shortcut"))
        self.file_group.add(self.file_path_row)
        self.file_group.add(self.file_name_entry)
        self.file_group.add(self.file_icon_row)
        box.append(self.file_group)

        self.btn_create_file = Gtk.Button(label=self.t("btn_create_file"))
        self.btn_create_file.add_css_class("suggested-action")
        self.btn_create_file.add_css_class("pill")
        self.btn_create_file.set_halign(Gtk.Align.CENTER)
        self.btn_create_file.connect("clicked", self.on_create_file_shortcut)
        box.append(self.btn_create_file)

        return box

    # ────────────────────────────────────────────
    #  TAB 2 – Apps
    # ────────────────────────────────────────────
    def _build_app_tab(self):
        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        outer_box.set_margin_top(16)
        outer_box.set_margin_bottom(16)
        outer_box.set_margin_start(16)
        outer_box.set_margin_end(16)

        self.app_search = Gtk.SearchEntry()
        self.app_search.set_placeholder_text(self.t("search_placeholder"))
        self.app_search.connect("search-changed", self.on_app_search_changed)
        outer_box.append(self.app_search)

        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_vexpand(True)
        paned.set_wide_handle(True)
        outer_box.append(paned)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(180)

        self.app_list_box = Gtk.ListBox()
        self.app_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.app_list_box.add_css_class("boxed-list")
        self.app_list_box.connect("row-selected", self.on_app_selected)

        self._populate_app_list(self.apps_list)
        scroll.set_child(self.app_list_box)
        paned.set_start_child(scroll)
        paned.set_shrink_start_child(False)

        bottom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        bottom_box.set_margin_top(8)

        self.app_name_entry = Adw.EntryRow()
        self.app_name_entry.set_title(self.t("shortcut_name") + " (optional)")

        self.app_icon_row = self._build_icon_row("app")

        self.app_config_group = Adw.PreferencesGroup()
        self.app_config_group.set_title(self.t("configure_shortcut"))
        self.app_config_group.add(self.app_name_entry)
        self.app_config_group.add(self.app_icon_row)
        bottom_box.append(self.app_config_group)

        self.btn_create_app = Gtk.Button(label=self.t("btn_create_app"))
        self.btn_create_app.add_css_class("suggested-action")
        self.btn_create_app.add_css_class("pill")
        self.btn_create_app.set_halign(Gtk.Align.CENTER)
        self.btn_create_app.connect("clicked", self.on_create_app_shortcut)
        bottom_box.append(self.btn_create_app)

        paned.set_end_child(bottom_box)
        paned.set_shrink_end_child(False)
        paned.set_position(320)

        return outer_box

    def _populate_app_list(self, apps):
        while True:
            row = self.app_list_box.get_row_at_index(0)
            if row is None:
                break
            self.app_list_box.remove(row)

        for app in apps:
            row = Adw.ActionRow()
            row.set_title(app.get("Name", self.t("unknown_app")))
            comment = app.get("Comment", app.get("GenericName", ""))
            if comment:
                row.set_subtitle(comment)

            icon_name = app.get("Icon", "application-x-executable")
            img = Gtk.Image()
            img.set_pixel_size(32)
            if os.path.isfile(icon_name):
                img.set_from_file(icon_name)
            else:
                img.set_from_icon_name(icon_name)
            row.add_prefix(img)
            row._app_info = app
            self.app_list_box.append(row)

    def _build_icon_row(self, prefix):
        row = Adw.ActionRow()
        row.set_title(self.t("custom_icon"))
        row.set_subtitle(self.t("no_icon"))

        preview = Gtk.Image()
        preview.set_pixel_size(32)
        row.add_prefix(preview)

        btn_icon = Gtk.Button(label=self.t("btn_choose_icon"))
        btn_icon.set_valign(Gtk.Align.CENTER)
        btn_icon.connect("clicked", lambda *_: self.on_choose_icon(row, preview))

        btn_clear = Gtk.Button()
        btn_clear.set_icon_name("edit-clear-symbolic")
        btn_clear.set_valign(Gtk.Align.CENTER)
        btn_clear.set_tooltip_text(self.t("btn_clear_icon"))
        btn_clear.connect("clicked", lambda *_: self.on_clear_icon(row, preview))

        row.add_suffix(btn_icon)
        row.add_suffix(btn_clear)

        # Store references for language updates
        row._btn_icon = btn_icon
        row._btn_clear = btn_clear
        row._preview = preview

        return row

    # ────────────────────────────────────────────
    #  Language switching
    # ────────────────────────────────────────────
    def on_toggle_language(self, btn):
        self.i18n.switch()
        self._update_all_labels()
        self._update_lang_button()

    def _update_lang_button(self):
        # Show flag of the OTHER language (the one you'd switch TO)
        flag = "🇩🇪" if self.i18n.lang == "en" else "🇬🇧"
        self.lang_btn.set_label(flag)
        self.lang_btn.set_tooltip_text(self.t("lang_button_tooltip"))

    def _update_all_labels(self):
        """Update all UI strings after language switch."""
        self.set_title(self.t("app_title"))

        # Tab titles
        self.file_stack_page.set_title(self.t("tab_files"))
        self.app_stack_page.set_title(self.t("tab_apps"))

        # File tab
        self.drop_label.set_label(self.t("drop_hint"))
        if not self.file_target_path:
            self.file_path_row.set_title(self.t("no_path"))
            self.file_path_row.set_subtitle(self.t("select_file_folder"))
        self.btn_choose_file.set_label(self.t("btn_choose_file"))
        self.btn_choose_folder.set_label(self.t("btn_choose_folder"))
        self.file_name_entry.set_title(self.t("shortcut_name"))
        self.file_group.set_title(self.t("configure_shortcut"))
        self.btn_create_file.set_label(self.t("btn_create_file"))

        # File icon row
        self.file_icon_row.set_title(self.t("custom_icon"))
        if not self.file_icon_row._preview.get_paintable():
            self.file_icon_row.set_subtitle(self.t("no_icon"))
        self.file_icon_row._btn_icon.set_label(self.t("btn_choose_icon"))
        self.file_icon_row._btn_clear.set_tooltip_text(self.t("btn_clear_icon"))

        # App tab
        self.app_search.set_placeholder_text(self.t("search_placeholder"))
        self.app_name_entry.set_title(self.t("shortcut_name") + " (optional)")
        self.app_config_group.set_title(self.t("configure_shortcut"))
        self.btn_create_app.set_label(self.t("btn_create_app"))

        # App icon row
        self.app_icon_row.set_title(self.t("custom_icon"))
        if not self.app_icon_row._preview.get_paintable():
            self.app_icon_row.set_subtitle(self.t("no_icon"))
        self.app_icon_row._btn_icon.set_label(self.t("btn_choose_icon"))
        self.app_icon_row._btn_clear.set_tooltip_text(self.t("btn_clear_icon"))

    # ────────────────────────────────────────────
    #  About dialog
    # ────────────────────────────────────────────
    def on_about(self, btn):
        about = Adw.AboutWindow(transient_for=self)
        about.set_application_name("Desktop Linker")
        about.set_version(APP_VERSION)
        about.set_developer_name(APP_DEVELOPER)
        about.set_comments(self.t("about_app"))
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_application_icon("insert-link")
        about.present()

    # ────────────────────────────────────────────
    #  Signal handlers
    # ────────────────────────────────────────────
    def on_file_drop(self, drop_target, value, x, y):
        if isinstance(value, Gio.File):
            path = value.get_path()
            if path:
                self._set_file_path(path)
                return True
        return False

    def _set_file_path(self, path):
        self.file_target_path = path
        self.file_path_row.set_title(os.path.basename(path))
        self.file_path_row.set_subtitle(path)
        if not self.file_name_entry.get_text():
            self.file_name_entry.set_text(os.path.basename(path))

    def on_choose_file(self, btn):
        dialog = Gtk.FileDialog()
        dialog.set_title(self.t("dialog_file_title"))
        dialog.open(self, None, self._on_file_chosen)

    def _on_file_chosen(self, dialog, result):
        try:
            f = dialog.open_finish(result)
            if f:
                self._set_file_path(f.get_path())
        except GLib.Error:
            pass

    def on_choose_folder(self, btn):
        dialog = Gtk.FileDialog()
        dialog.set_title(self.t("dialog_folder_title"))
        dialog.select_folder(self, None, self._on_folder_chosen)

    def _on_folder_chosen(self, dialog, result):
        try:
            f = dialog.select_folder_finish(result)
            if f:
                self._set_file_path(f.get_path())
        except GLib.Error:
            pass

    def on_choose_icon(self, row, preview):
        dialog = Gtk.FileDialog()
        dialog.set_title(self.t("dialog_icon_title"))
        filter_img = Gtk.FileFilter()
        filter_img.set_name(self.t("filter_images"))
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/svg+xml")
        filter_img.add_mime_type("image/x-xpixmap")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_img)
        dialog.set_filters(filters)
        dialog.open(self, None, lambda d, r: self._on_icon_chosen(d, r, row, preview))

    def _on_icon_chosen(self, dialog, result, row, preview):
        try:
            f = dialog.open_finish(result)
            if f:
                path = f.get_path()
                self.selected_icon_path = path
                row.set_subtitle(os.path.basename(path))
                preview.set_from_file(path)
        except GLib.Error:
            pass

    def on_clear_icon(self, row, preview):
        self.selected_icon_path = None
        row.set_subtitle(self.t("no_icon"))
        preview.clear()

    def on_app_search_changed(self, entry):
        text = entry.get_text().lower()
        filtered = [
            a for a in self.apps_list
            if not text
            or text in a.get("Name", "").lower()
            or text in a.get("Comment", "").lower()
            or text in a.get("GenericName", "").lower()
        ]
        self._populate_app_list(filtered)

    def on_app_selected(self, listbox, row):
        if row and hasattr(row, "_app_info"):
            self.selected_app_info = row._app_info

    def on_create_file_shortcut(self, btn):
        if not self.file_target_path:
            self.show_toast(self.t("toast_no_file"))
            return
        name = self.file_name_entry.get_text().strip() or None
        try:
            path = create_file_shortcut(self.file_target_path, self.selected_icon_path, name)
            self.show_toast(self.t("toast_created").format(os.path.basename(path)))
        except Exception as e:
            self.show_toast(self.t("toast_error").format(e))

    def on_create_app_shortcut(self, btn):
        if not self.selected_app_info:
            self.show_toast(self.t("toast_no_app"))
            return
        name = self.app_name_entry.get_text().strip() or None
        try:
            path = create_app_shortcut(
                self.selected_app_info["_path"], self.selected_icon_path, name
            )
            self.show_toast(self.t("toast_created").format(os.path.basename(path)))
        except Exception as e:
            self.show_toast(self.t("toast_error").format(e))

    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)


if __name__ == "__main__":
    app = DesktopLinkerApp()
    app.run()
