import json
import os
from PyQt6.QtCore import QObject, pyqtSignal
from paths import data_dir, resource_dir

_LANG_FILE = os.path.join(resource_dir(), "datasets", "language.json")
_PREF_FILE = os.path.join(data_dir(), "datasets", "lang_pref.txt")

_translations = {}
_current_lang = "en"


def _load_translations():
    global _translations
    with open(_LANG_FILE, encoding="utf-8") as f:
        _translations = json.load(f)


def _load_pref():
    if os.path.exists(_PREF_FILE):
        with open(_PREF_FILE, encoding="utf-8") as f:
            lang = f.read().strip()
            if lang in ("en", "vi"):
                return lang
    return "en"


def _save_pref(lang):
    os.makedirs(os.path.dirname(_PREF_FILE), exist_ok=True)
    with open(_PREF_FILE, "w", encoding="utf-8") as f:
        f.write(lang)


def tr(key, **kwargs):
    lang_dict = _translations.get(_current_lang, _translations.get("en", {}))
    text = lang_dict.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError, IndexError):
            pass
    return text.replace("%n", "\n")


class LanguageManager(QObject):
    language_changed = pyqtSignal()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            QObject.__init__(inst)
            inst._initialized = True
            cls._instance = inst
        return cls._instance

    def __init__(self):
        pass

    def set_language(self, lang):
        global _current_lang
        if lang not in ("en", "vi"):
            return
        _current_lang = lang
        _save_pref(lang)
        self.language_changed.emit()

    def current_language(self):
        return _current_lang


def get_manager():
    return LanguageManager()


_load_translations()
_current_lang = _load_pref()
