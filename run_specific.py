#!/usr/bin/env python3
"""
Скрипт для запуска конкретных тестов
"""
import sys
import subprocess


def main():
    """Запуск конкретных тестов"""
    if len(sys.argv) < 2:
        print("Использование: python run_specific.py <тип_тестов>")
        print("Доступные типы:")
        print("  unit       - все модульные тесты")
        print("  simple     - тесты FA_simple")
        print("  fa         - тесты FA")
        print("  efa        - тесты MYEFA")
        print("  integration - интеграционные тесты")
        print("  all        - все тесты")
        return

    test_type = sys.argv[1].lower()

    commands = {
        'unit': 'pytest tests/unit/ -v',
        'simple': 'pytest tests/unit/test_fa_simple.py -v',
        'fa': 'pytest tests/unit/test_fa.py -v',
        'efa': 'pytest tests/unit/test_myefa.py -v',
        'integration': 'pytest tests/integration/ -v',
        'all': 'pytest tests/ -v'
    }

    if test_type not in commands:
        print(f"Неизвестный тип тестов: {test_type}")
        return

    cmd = commands[test_type]
    print(f"Запуск: {cmd}")
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    main()