#!/usr/bin/env python3
"""
Система тестирования для проекта:
«Модульное тестирование системы анализа и синтеза конечных и расширенных автоматов»
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_command(cmd: str, description: str = "") -> tuple[bool, str]:
    """Запустить команду и вернуть результат"""
    print(f"\n▶️  {description}...")
    print(f"   Команда: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        success = (result.returncode == 0)
        output = result.stdout + "\n" + result.stderr

        if success:
            print("   ✅ Успешно")
        else:
            print("   ❌ Ошибка")

        return success, output

    except Exception as e:
        print(f"   ❌ Исключение: {e}")
        return False, str(e)


def parse_pytest_output(output: str) -> tuple[int, int]:
    """Парсинг вывода pytest для получения количества тестов"""
    lines = output.strip().split('\n')

    for line in reversed(lines):  # Ищем с конца
        line = line.strip()
        if 'passed' in line or 'failed' in line:
            # Примеры: "69 passed in 1.23s" или "68 passed, 1 failed in 1.23s"
            import re

            # Ищем числа перед "passed" и "failed"
            passed_match = re.search(r'(\d+)\s+passed', line)
            failed_match = re.search(r'(\d+)\s+failed', line)

            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0

            return passed, passed + failed

    return 0, 0


def parse_coverage_output(output: str) -> dict:
    """Парсинг вывода coverage"""
    coverage = {"percentage": 0, "total": 0, "missed": 0}

    for line in output.split('\n'):
        if 'TOTAL' in line and '%' in line:
            import re

            # Ищем числа в строке
            numbers = re.findall(r'\d+', line)
            if len(numbers) >= 3:
                coverage["total"] = int(numbers[0])
                coverage["missed"] = int(numbers[1])

            # Ищем процент
            percent_match = re.search(r'(\d+(?:\.\d+)?)%', line)
            if percent_match:
                coverage["percentage"] = float(percent_match.group(1))

            break

    return coverage


def main() -> int:
    """Основная функция"""
    print("=" * 80)
    print("  🧪 СИСТЕМА ТЕСТИРОВАНИЯ: АНАЛИЗ И СИНТЕЗ АВТОМАТОВ")
    print("=" * 80)
    print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"📁 Проект: {Path.cwd().name}")

    # 1. ПРОВЕРКА ТЕСТОВ ПО ОТДЕЛЬНОСТИ
    print("\n" + "─" * 40)
    print("  1. ЗАПУСК МОДУЛЬНЫХ ТЕСТОВ")
    print("─" * 40)

    success_unit, output_unit = run_command(
        "pytest tests/unit/test_fa_simple.py -v",
        "Модульные тесты FA_simple"
    )

    passed_unit, total_unit = parse_pytest_output(output_unit)
    print(f"   📊 Результат: {passed_unit}/{total_unit} тестов")

    # 2. ИНТЕГРАЦИОННЫЕ ТЕСТЫ
    print("\n" + "─" * 40)
    print("  2. ЗАПУСК ИНТЕГРАЦИОННЫХ ТЕСТОВ")
    print("─" * 40)

    success_integration, output_integration = run_command(
        "pytest tests/integration/test_transformations.py -v",
        "Интеграционные тесты"
    )

    passed_integration, total_integration = parse_pytest_output(output_integration)
    print(f"   📊 Результат: {passed_integration}/{total_integration} тестов")

    # 3. ПОКРЫТИЕ КОДА
    print("\n" + "─" * 40)
    print("  3. АНАЛИЗ ПОКРЫТИЯ КОДА")
    print("─" * 40)

    # Coverage от модульных тестов
    success_cov_unit, output_cov_unit = run_command(
        "pytest tests/unit/test_fa_simple.py --cov=src.FA_simple --cov-report=term-missing",
        "Coverage от модульных тестов"
    )

    cov_unit = parse_coverage_output(output_cov_unit)
    print(f"   📈 Покрытие: {cov_unit['percentage']:.1f}%")
    print(f"      Строк: {cov_unit['total']}, Непокрыто: {cov_unit['missed']}")

    # Coverage от интеграционных тестов
    success_cov_integration, output_cov_integration = run_command(
        "pytest tests/integration/test_transformations.py --cov=src.FA_simple --cov-report=term-missing",
        "Coverage от интеграционных тестов"
    )

    cov_integration = parse_coverage_output(output_cov_integration)
    print(f"   📈 Покрытие: {cov_integration['percentage']:.1f}%")
    print(f"      Строк: {cov_integration['total']}, Непокрыто: {cov_integration['missed']}")

    # Общее coverage
    success_cov_total, output_cov_total = run_command(
        "pytest tests/ --cov=src --cov-report=term-missing",
        "Общее покрытие кода"
    )

    cov_total = parse_coverage_output(output_cov_total)
    print(f"   📈 Общее покрытие: {cov_total['percentage']:.1f}%")
    print(f"      Строк: {cov_total['total']}, Непокрыто: {cov_total['missed']}")

    # 4. ИТОГОВЫЙ ОТЧЕТ
    print("\n" + "=" * 80)
    print("  📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)

    total_passed = passed_unit + passed_integration
    total_tests = total_unit + total_integration

    print(f"\n🎯 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   • Модульные тесты: {passed_unit}/{total_unit} пройдено")
    print(f"   • Интеграционные тесты: {passed_integration}/{total_integration} пройдено")
    print(f"   • Всего тестов: {total_tests}")
    print(f"   • Пройдено тестов: {total_passed}")

    print(f"\n📈 ПОКРЫТИЕ КОДА:")
    print(f"   • От модульных тестов: {cov_unit['percentage']:.1f}%")
    print(f"   • От интеграционных тестов: {cov_integration['percentage']:.1f}%")
    print(f"   • Общее покрытие: {cov_total['percentage']:.1f}%")

    # 5. ОЦЕНКА
    print("\n" + "─" * 40)
    print("  🏆 ОЦЕНКА РЕЗУЛЬТАТОВ")
    print("─" * 40)

    all_tests_passed = (passed_unit == total_unit) and (passed_integration == total_integration)

    if all_tests_passed:
        print("   ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")

        if cov_total['percentage'] >= 90:
            print(f"   🏆 ОТЛИЧНОЕ покрытие кода: {cov_total['percentage']:.1f}%")
        elif cov_total['percentage'] >= 80:
            print(f"   👍 ХОРОШЕЕ покрытие кода: {cov_total['percentage']:.1f}%")
        elif cov_total['percentage'] >= 70:
            print(f"   ✅ УДОВЛЕТВОРИТЕЛЬНОЕ покрытие: {cov_total['percentage']:.1f}%")
        else:
            print(f"   ⚠️ Покрытие можно улучшить: {cov_total['percentage']:.1f}%")

        return 0
    else:
        print("   ⚠️ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ")

        if passed_unit < total_unit:
            print(f"   ❌ Модульные тесты: {total_unit - passed_unit} тестов не прошло")

        if passed_integration < total_integration:
            print(f"   ❌ Интеграционные тесты: {total_integration - passed_integration} тестов не прошло")

        print("\n🔧 ДЛЯ ОТЛАДКИ:")
        print("   • Запустите тесты с детальным выводом:")
        print("     pytest tests/ -v")
        print("   • Только упавшие тесты:")
        print("     pytest tests/ --lf")
        print("   • Конкретный упавший тест:")
        print("     pytest tests/ -k 'название_теста' -v")

        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)