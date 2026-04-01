import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, cast


class I18nService:
    """
    Singleton service to handle internationalization.
    Strictly typed for Pylance compatibility.
    """

    def __init__(self) -> None:
        self._locales: Dict[str, Dict[str, Any]] = {}
        self._base_path: Path = Path(__file__).parent / "locales"
        self._default_lang: str = "en"
        self.load_locales()

    def load_locales(self) -> None:
        """
        Loads all JSON locale files from the locales directory.
        """
        if not self._base_path.exists():
            return

        for file in self._base_path.glob("*.json"):
            lang: str = file.stem
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data: Dict[str, Any] = cast(Dict[str, Any], json.load(f))
                    self._locales[lang] = data
            except (json.JSONDecodeError, OSError) as e:
                print(f"Critical: Failed to load locale {lang}: {e}")

    def t(self, key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
        """
        Translates a key with dot notation support and variable injection.
        Guarantees string return and strictly handles unknown types.
        """
        target_lang: str = lang or self._default_lang

        translations: Dict[str, Any] = self._locales.get(target_lang, self._locales.get(self._default_lang, {}))

        keys: list[str] = key.split(".")
        current_node: Union[Dict[str, Any], Any] = translations

        for k in keys:
            if isinstance(current_node, dict):
                dict_node = cast(Dict[str, Any], current_node)
                current_node = dict_node.get(k)
            else:
                return key

        if current_node is None:
            return key

        try:
            template: str = str(current_node)
            return template.format(**kwargs)
        except (KeyError, ValueError, IndexError):
            return str(current_node)


i18n: I18nService = I18nService()
