import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class MessageManager:
    _messages: Optional[Dict[str, Any]] = None

    @classmethod
    def load(cls) -> None:
        yaml_path = Path(__file__).parent.parent / "messages.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"{yaml_path} file is missing.")
        
        with open(yaml_path, "r", encoding="utf-8") as file:
            cls._messages = yaml.safe_load(file) or {}

    @classmethod
    def get(cls, key: str, /, **kwargs: Any) -> str:
        if cls._messages is None:
            cls.load()
        
        keys = key.split(".")
        value: Any = cls._messages
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return f"Missing key: {key}"
        
        if not isinstance(value, str):
            return str(value)
        
        if kwargs:
            return value.format(**kwargs)
        return value

def get_msg(key: str, /, **kwargs: Any) -> str:
    return MessageManager.get(key, **kwargs)
