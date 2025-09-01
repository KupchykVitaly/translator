# api_manager.py
import json
import os

class ApiKeyManager:
    def __init__(self, filename="api_keys.json"):
        self.filepath = filename
        self.data = self._load()

    def _load(self):
        """Завантажує ключі з файлу. Якщо файл не існує, створює структуру за замовчуванням."""
        if not os.path.exists(self.filepath):
            return {
                "services": {"deepl": [], "gpt": [], "gemini": []},
                "active_keys": {"deepl": None, "gpt": None, "gemini": None}
            }
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._load()

    def save(self):
        """Зберігає поточні дані у файл."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get_keys_for_service(self, service_name):
        """Повертає список ключів для вказаного сервісу."""
        return self.data["services"].get(service_name, [])

    def get_active_key(self, service_name):
        """Повертає активний ключ для сервісу."""
        return self.data["active_keys"].get(service_name)

    def add_key(self, service_name, key_value):
        """Додає новий ключ, якщо його ще немає."""
        keys = self.get_keys_for_service(service_name)
        if key_value not in keys:
            keys.append(key_value)
            self.save()

    def update_key(self, service_name, old_key, new_key):
        """Оновлює значення існуючого ключа."""
        keys = self.get_keys_for_service(service_name)
        try:
            index = keys.index(old_key)
            keys[index] = new_key
            # Якщо оновлюємо активний ключ, його також треба оновити
            if self.data["active_keys"].get(service_name) == old_key:
                self.data["active_keys"][service_name] = new_key
            self.save()
        except ValueError:
            print(f"Error: Key {old_key} not found for updating.")

    def delete_key(self, service_name, key_value):
        """Видаляє ключ зі списку."""
        keys = self.get_keys_for_service(service_name)
        if key_value in keys:
            keys.remove(key_value)
            if self.data["active_keys"].get(service_name) == key_value:
                self.data["active_keys"][service_name] = None
            self.save()

    def set_active_key(self, service_name, key_value):
        """Встановлює активний ключ для сервісу."""
        self.data["active_keys"][service_name] = key_value
        self.save()