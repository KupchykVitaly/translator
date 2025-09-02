# settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QPushButton, QListWidget, 
    QHBoxLayout, QMessageBox, QDialogButtonBox, QInputDialog,
    QListWidgetItem, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from api_manager import ApiKeyManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Керування API Ключами")
        self.setMinimumSize(600, 400)
        
        self.key_manager = ApiKeyManager()
        
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.service_widgets = {}
        for service_name in self.key_manager.data["services"].keys():
            self._create_service_tab(service_name)
            
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.buttons)

    def _create_service_tab(self, service_name):
        tab = QWidget()
        tab_layout = QHBoxLayout(tab)
        
        list_widget = QListWidget()
        tab_layout.addWidget(list_widget, 3)
        
        button_panel = QVBoxLayout()
        button_panel.setSpacing(10)
        
        btn_add = QPushButton("➕ Додати")
        btn_edit = QPushButton("✏️ Редагувати")
        btn_delete = QPushButton("❌ Видалити")
        btn_set_active = QPushButton("⭐ Зробити активним")
        
        button_panel.addWidget(btn_add)
        button_panel.addWidget(btn_edit)
        button_panel.addWidget(btn_delete)
        button_panel.addStretch()
        button_panel.addWidget(QLabel("Обраний ключ буде\nвикористовуватись\nдля перекладу:"))
        button_panel.addWidget(btn_set_active)
        
        tab_layout.addLayout(button_panel, 1)
        self.tabs.addTab(tab, service_name.capitalize())
        
        self.service_widgets[service_name] = {
            "list": list_widget, "add": btn_add, "edit": btn_edit,
            "delete": btn_delete, "set_active": btn_set_active
        }
        
        btn_add.clicked.connect(lambda: self.add_key(service_name))
        btn_edit.clicked.connect(lambda: self.edit_key(service_name))
        btn_delete.clicked.connect(lambda: self.delete_key(service_name))
        btn_set_active.clicked.connect(lambda: self.set_active_key(service_name))
        
        self.update_key_list(service_name)

    def mask_key(self, key):
        """Створює масковану версію ключа для безпечного відображення."""
        if len(key) < 8:
            return "****"
        return f"{key[:4]}...{key[-4:]}"

    def update_key_list(self, service_name):
        widgets = self.service_widgets[service_name]
        list_widget = widgets["list"]
        list_widget.clear()
        
        keys = self.key_manager.get_keys_for_service(service_name)
        active_key = self.key_manager.get_active_key(service_name)
        
        for key_value in keys:
            display_text = self.mask_key(key_value)
            item = QListWidgetItem(display_text)
            # Зберігаємо повний, незмінений ключ в даних елемента
            item.setData(Qt.ItemDataRole.UserRole, key_value)
            
            if key_value == active_key:
                font = QFont()
                font.setBold(True) # ВИПРАВЛЕНО: true -> True
                item.setFont(font)
                item.setText(f"⭐ {display_text} (Активний)")
            
            list_widget.addItem(item)
    
    def get_selected_key(self, service_name):
        """Повертає повний ключ з даних обраного елемента."""
        list_widget = self.service_widgets[service_name]["list"]
        selected_item = list_widget.currentItem()
        if not selected_item:
            return None
        return selected_item.data(Qt.ItemDataRole.UserRole)

    def add_key(self, service_name):
        new_key, ok = QInputDialog.getText(self, "Додати API Ключ", "Введіть новий API ключ:")
        if ok and new_key:
            self.key_manager.add_key(service_name, new_key)
            self.update_key_list(service_name)

    def edit_key(self, service_name):
        old_key = self.get_selected_key(service_name)
        if not old_key:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть ключ для редагування.")
            return

        new_key, ok = QInputDialog.getText(self, "Редагувати API Ключ", "Відредагуйте ключ:", text=old_key)
        if ok and new_key and new_key != old_key:
            self.key_manager.update_key(service_name, old_key, new_key)
            self.update_key_list(service_name)

    def delete_key(self, service_name):
        key_to_delete = self.get_selected_key(service_name)
        if not key_to_delete:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть ключ для видалення.")
            return
        
        masked_key = self.mask_key(key_to_delete)
        reply = QMessageBox.question(self, "Підтвердження", f"Ви впевнені, що хочете видалити ключ '{masked_key}'?")
        if reply == QMessageBox.StandardButton.Yes:
            self.key_manager.delete_key(service_name, key_to_delete)
            self.update_key_list(service_name)

    def set_active_key(self, service_name):
        key_to_activate = self.get_selected_key(service_name)
        if not key_to_activate:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть ключ, щоб зробити його активним.")
            return
        self.key_manager.set_active_key(service_name, key_to_activate)
        self.update_key_list(service_name)