# test.py
# Цей скрипт перевіряє роботу класу DeepLTranslator з файлу translators.py

# Переконуємось, що ми можемо імпортувати наш клас
try:
    from translators import DeepLTranslator
except ImportError:
    print("❌ Помилка: не вдалося знайти файл 'translators.py' або клас 'DeepLTranslator' у ньому.")
    print("Будь ласка, переконайтесь, що 'test.py' знаходиться в тій самій папці, що й 'translators.py'.")
    exit()

def run_deepl_test():
    """Основна функція для тестування перекладу DeepL."""
    
    print("=== Тестування інтеграції з DeepL API ===")
    
    # 1. Запитуємо API ключ у користувача
    api_key = input("Введіть ваш ключ DeepL API для тестування: ")
    if not api_key:
        print("Тест скасовано, оскільки ключ не було введено.")
        return

    # 2. Намагаємось ініціалізувати перекладач
    print("\nНамагаюся створити екземпляр DeepLTranslator...")
    try:
        translator = DeepLTranslator(api_key=api_key)
        print("✅ Успіх! Перекладач ініціалізовано.")
    except Exception as e:
        print(f"❌ Помилка під час ініціалізації: {e}")
        print("Будь ласка, перевірте правильність вашого API ключа.")
        return

    # 3. Готуємо тестові дані
    sample_data = [
        {'text': 'Hello, this is a test of the DeepL API.'},
        {'text': 'The quick brown fox jumps over the lazy dog.'},
        {'text': ''},  # Перевірка порожнього рядка
        {'text': 'How are you today?'}
    ]

    print("\nПочинаю переклад тестових речень з англійської (en) на українську (uk)...")
    print("-" * 30)

    # 4. Викликаємо метод перекладу
    try:
        results = translator.translate_batch(
            items=sample_data, 
            src_lang='en', 
            dest_lang='uk'
        )
        
        # 5. Виводимо результати
        print("✅ Переклад завершено! Результати:")
        for item in results:
            original = item.get('text', '')
            translated = item.get('translated', 'ПОМИЛКА')
            print(f"  '{original}'  ->  '{translated}'")
            
    except Exception as e:
        print(f"❌ Під час виконання перекладу сталася помилка: {e}")

if __name__ == "__main__":
    run_deepl_test()