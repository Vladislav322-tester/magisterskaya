#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов
"""
import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Печать заголовка"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def run_command(cmd, description):
    """Запуск команды с выводом результата"""
    print(f"\n▶ {description}")
    print("-" * 40)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Успешно")
            if result.stdout:
                print(result.stdout[:500])  # Первые 500 символов вывода
        else:
            print("❌ Ошибка")
            if result.stderr:
                print(result.stderr)

        return result.returncode

    except Exception as e:
        print(f"❌ Исключение: {e}")
        return 1


def main():
    """Основная функция"""
    project_root = Path(__file__).parent

    print("🚀 Запуск тестов для магистерской диссертации")
    print(f"📁 Рабочая директория: {project_root}")

    # Проверяем Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"🐍 Версия Python: {python_version}")

    # Добавляем src в PYTHONPATH
    src_path = project_root / 'src'
    if src_path.exists():
        sys.path.insert(0, str(src_path))

    results = {}

    # 1. Запуск модульных тестов
    print_header("Модульные тесты")

    # FA_simple
    results['unit_fa_simple'] = run_command(
        f'python -m pytest tests/unit/test_fa_simple.py -v',
        'Модульные тесты для FA_simple'
    )

    # FA
    results['unit_fa'] = run_command(
        f'python -m pytest tests/unit/test_fa.py -v',
        'Модульные тесты для FA'
    )

    # MYEFA
    results['unit_myefa'] = run_command(
        f'python -m pytest tests/unit/test_myefa.py -v',
        'Модульные тесты для MYEFA'
    )

    # 2. Запуск интеграционных тестов
    print_header("Интеграционные тесты")
    results['integration'] = run_command(
        f'python -m pytest tests/integration/ -v',
        'Интеграционные тесты'
    )

    # 3. Запуск всех тестов с покрытием
    print_header("Тесты с покрытием кода")
    results['coverage'] = run_command(
        f'python -m pytest tests/ --cov=src --cov-report=term-missing',
        'Тесты с покрытием кода'
    )

    # 4. Сводка результатов
    print_header("Сводка результатов")

    total_tests = len(results)
    passed_tests = sum(1 for code in results.values() if code == 0)

    print(f"📊 Всего категорий тестов: {total_tests}")
    print(f"✅ Успешно пройдено: {passed_tests}")
    print(f"❌ Не пройдено: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("\n🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("\n⚠️ Некоторые тесты не пройдены.")
        for name, code in results.items():
            status = "✅" if code == 0 else "❌"
            print(f"  {status} {name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())