#!/usr/bin/env python3
"""
Система тестирования для проекта:
«Модульное тестирование системы анализа и синтеза конечных и расширенных автоматов»
"""
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime


def run_command(cmd: str, description: str = "", measure_time: bool = False) -> tuple[bool, str, float]:
    """Запустить команду и вернуть результат с временем выполнения"""
    print(f"\n▶️  {description}...")
    print(f"   Команда: {cmd}")

    try:
        start_time = time.time()

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        end_time = time.time()
        execution_time = end_time - start_time if measure_time else 0.0

        success = (result.returncode == 0)
        output = result.stdout + "\n" + result.stderr

        if success:
            print("   ✅ Успешно")
        else:
            print("   ❌ Ошибка", end="")

        return success, output, execution_time

    except Exception as e:
        print(f"   ❌ Исключение: {e}")
        return False, str(e), 0.0


def parse_pytest_output(output: str) -> tuple[int, int]:
    """Парсинг вывода pytest для получения количества тестов"""
    lines = output.strip().split('\n')

    for line in reversed(lines):  # Ищем с конца
        line = line.strip()
        if 'passed' in line or 'failed' in line:
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


def count_lines_of_code(directory: str, extension: str = ".py") -> int:
    """Подсчет строк кода в директории"""
    loc = 0
    dir_path = Path(directory)

    if not dir_path.exists():
        return 0

    for file_path in dir_path.rglob(f"*{extension}"):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Считаем непустые строки
                    loc += sum(1 for line in f if line.strip())
            except:
                continue

    return loc


def count_asserts_in_tests() -> int:
    """Подсчет количества assert'ов в тестах"""
    assert_count = 0
    test_dir = Path("tests")

    if not test_dir.exists():
        return 0

    for test_file in test_dir.rglob("*.py"):
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Считаем assert'ы
                assert_count += content.count('assert ')
                # Также считаем многострочные assert
                assert_count += content.count('assert\n')
                assert_count += content.count('assert(')
        except:
            continue

    return assert_count


def calculate_test_metrics() -> dict:
    """Вычисление дополнительных метрик тестов"""
    metrics = {
        "test_loc": 0,
        "prod_loc": 0,
        "test_to_code_ratio": 0.0,
        "assert_count": 0,
        "assert_density": 0.0
    }

    # Считаем LOC тестов
    metrics["test_loc"] = count_lines_of_code("tests", ".py")

    # Считаем LOC продакшена
    metrics["prod_loc"] = count_lines_of_code("src", ".py")

    # Считаем assert'ы
    metrics["assert_count"] = count_asserts_in_tests()

    # Рассчитываем производные метрики
    if metrics["prod_loc"] > 0:
        metrics["test_to_code_ratio"] = metrics["test_loc"] / metrics["prod_loc"]

    if metrics["test_loc"] > 0:
        metrics["assert_density"] = metrics["assert_count"] / metrics["test_loc"]

    return metrics


def main() -> int:
    """Основная функция"""
    print("=" * 80)
    print("  🧪 СИСТЕМА ТЕСТИРОВАНИЯ: АНАЛИЗ И СИНТЕЗ АВТОМАТОВ")
    print("=" * 80)
    print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"📁 Проект: {Path.cwd().name}")

    # Общее время начала выполнения скрипта
    script_start_time = time.time()

    # 1. ПРОВЕРКА ОБЫЧНЫХ МОДУЛЬНЫХ ТЕСТОВ
    print("\n" + "─" * 40)
    print("  1. ЗАПУСК ОБЫЧНЫХ МОДУЛЬНЫХ ТЕСТОВ")
    print("─" * 40)

    success_unit, output_unit, time_unit = run_command(
        "pytest tests/unit/test_fa_simple.py -v",
        "Обычные модульные тесты FA_simple",
        measure_time=True
    )

    passed_unit, total_unit = parse_pytest_output(output_unit)
    print(f"   📊 Результат: {passed_unit}/{total_unit} тестов")
    print(f"   ⏱️  Время выполнения: {time_unit:.2f} сек")

    # 2. ТЕСТЫ С HYPOTHESIS (РАНДОМИЗИРОВАННЫЕ)
    print("\n" + "─" * 40)
    print("  2. ЗАПУСК РАНДОМИЗИРОВАННЫХ ТЕСТОВ (HYPOTHESIS)")
    print("─" * 40)

    success_hypothesis, output_hypothesis, time_hypothesis = run_command(
        "pytest tests/unit/test_fa_simple_hypothesis.py -v",
        "Тесты с Hypothesis",
        measure_time=True
    )

    passed_hypothesis, total_hypothesis = parse_pytest_output(output_hypothesis)
    print(f"   📊 Результат: {passed_hypothesis}/{total_hypothesis} тестов")
    print(f"   ⏱️  Время выполнения: {time_hypothesis:.2f} сек")

    # 3. ПОКРЫТИЕ КОДА ОТ ОБЫЧНЫХ ТЕСТОВ
    print("\n" + "─" * 40)
    print("  3. АНАЛИЗ ПОКРЫТИЯ КОДА")
    print("─" * 40)

    # Coverage от обычных тестов
    success_cov_unit, output_cov_unit, time_cov_unit = run_command(
        "pytest tests/unit/test_fa_simple.py --cov=src.FA_simple --cov-report=term-missing",
        "Coverage от обычных тестов",
        measure_time=True
    )

    cov_unit = parse_coverage_output(output_cov_unit)
    print(f"   📈 Покрытие от обычных тестов: {cov_unit['percentage']:.1f}%")
    print(f"      Строк: {cov_unit['total']}, Непокрыто: {cov_unit['missed']}")
    print(f"   ⏱️  Время анализа покрытия: {time_cov_unit:.2f} сек")

    # Coverage от Hypothesis тестов
    success_cov_hypothesis, output_cov_hypothesis, time_cov_hypothesis = run_command(
        "pytest tests/unit/test_fa_simple_hypothesis.py --cov=src.FA_simple --cov-report=term-missing",
        "Coverage от тестов с Hypothesis",
        measure_time=True
    )

    cov_hypothesis = parse_coverage_output(output_cov_hypothesis)
    print(f"   📈 Покрытие от Hypothesis тестов: {cov_hypothesis['percentage']:.1f}%")
    print(f"      Строк: {cov_hypothesis['total']}, Непокрыто: {cov_hypothesis['missed']}")
    print(f"   ⏱️  Время анализа покрытия: {time_cov_hypothesis:.2f} сек")

    # Общее coverage от всех тестов
    success_cov_total, output_cov_total, time_cov_total = run_command(
        "pytest tests/unit/ --cov=src.FA_simple --cov-report=term-missing",
        "Общее покрытие от всех тестов",
        measure_time=True
    )

    cov_total = parse_coverage_output(output_cov_total)
    print(f"   📈 Общее покрытие: {cov_total['percentage']:.1f}%")
    print(f"      Строк: {cov_total['total']}, Непокрыто: {cov_total['missed']}")
    print(f"   ⏱️  Время анализа покрытия: {time_cov_total:.2f} сек")

    # 4. СБОР ДОПОЛНИТЕЛЬНЫХ МЕТРИК
    print("\n" + "─" * 40)
    print("  4. АНАЛИЗ ДОПОЛНИТЕЛЬНЫХ МЕТРИК")
    print("─" * 40)

    print("\n📊 Анализ метрик кода...")
    test_metrics = calculate_test_metrics()

    print(f"   • LOC тестов:          {test_metrics['test_loc']}")
    print(f"   • LOC продакшена:      {test_metrics['prod_loc']}")
    print(f"   • Test/Code ratio:     {test_metrics['test_to_code_ratio']:.2f}")
    print(f"   • Количество assert'ов: {test_metrics['assert_count']}")
    print(f"   • Плотность assert'ов:  {test_metrics['assert_density']:.3f}")

    # 5. ИТОГОВЫЙ ОТЧЕТ
    print("\n" + "=" * 80)
    print("  📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)

    total_passed = passed_unit + passed_hypothesis
    total_tests = total_unit + total_hypothesis
    total_test_time = time_unit + time_hypothesis
    total_coverage_time = time_cov_unit + time_cov_hypothesis + time_cov_total

    # Общее время выполнения скрипта
    script_end_time = time.time()
    total_script_time = script_end_time - script_start_time

    print(f"\n🎯 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   • Обычные тесты: {passed_unit}/{total_unit} пройдено")
    print(f"   • Тесты с Hypothesis: {passed_hypothesis}/{total_hypothesis} пройдено")
    print(f"   • Всего тестов: {total_tests}")
    print(f"   • Пройдено тестов: {total_passed}")

    print(f"\n📊 СТАТИСТИКА ТЕСТОВ:")
    print(f"   • Обычные тесты: {total_unit} тестов")
    print(f"   • Hypothesis тесты: {total_hypothesis} тестов")
    if total_tests > 0:
        hypothesis_percentage = (total_hypothesis / total_tests) * 100
        print(f"   • Hypothesis составляет: {hypothesis_percentage:.1f}% от всех тестов")

    print(f"\n⏱️  ВРЕМЯ ВЫПОЛНЕНИЯ:")
    print(f"   • Обычные тесты:          {time_unit:8.2f} сек")
    print(f"   • Тесты с Hypothesis:     {time_hypothesis:8.2f} сек")
    print(f"   • Общее время тестов:     {total_test_time:8.2f} сек")

    if total_tests > 0:
        avg_test_time = total_test_time / total_tests
        print(f"   • Среднее время на тест:  {avg_test_time:8.4f} сек")

    print(f"   • Анализ покрытия:        {total_coverage_time:8.2f} сек")
    print(f"   • Общее время скрипта:    {total_script_time:8.2f} сек")

    print(f"\n📈 ПОКРЫТИЕ КОДА:")
    print(f"   • От обычных тестов: {cov_unit['percentage']:.1f}%")
    print(f"   • От тестов с Hypothesis: {cov_hypothesis['percentage']:.1f}%")
    print(f"   • Общее покрытие: {cov_total['percentage']:.1f}%")
    print(f"   • Непокрытых строк: {cov_total['missed']} из {cov_total['total']}")

    print(f"\n📊 МЕТРИКИ КОДА:")
    print(f"   • Test/Code ratio:     {test_metrics['test_to_code_ratio']:.2f}")
    print(f"   • Плотность assert'ов:  {test_metrics['assert_density']:.3f}")

    # Эффективность Hypothesis тестов
    print(f"\n🔬 ЭФФЕКТИВНОСТЬ HYPOTHESIS:")
    if total_hypothesis > 0 and total_unit > 0:
        avg_time_unit = time_unit / total_unit if total_unit > 0 else 0
        avg_time_hypothesis = time_hypothesis / total_hypothesis if total_hypothesis > 0 else 0

        print(f"   • Среднее время unit теста:       {avg_time_unit:.4f} сек")
        print(f"   • Среднее время hypothesis теста: {avg_time_hypothesis:.4f} сек")

        if avg_time_unit > 0:
            time_ratio = avg_time_hypothesis / avg_time_unit
            print(f"   • Hypothesis тесты {'медленнее' if time_ratio > 1 else 'быстрее'} в {time_ratio:.2f} раз")

    if cov_unit['percentage'] > 0 and cov_hypothesis['percentage'] > 0:
        coverage_gain = cov_total['percentage'] - cov_unit['percentage']
        print(f"   • Прирост покрытия от Hypothesis: {coverage_gain:+.1f}%")

    # 6. ОЦЕНКА
    print("\n" + "─" * 40)
    print("  🏆 ОЦЕНКА РЕЗУЛЬТАТОВ")
    print("─" * 40)

    all_tests_passed = (passed_unit == total_unit) and (passed_hypothesis == total_hypothesis)

    if all_tests_passed:
        print("   ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")

        # Оценка покрытия
        if cov_total['percentage'] >= 95:
            print(f"   🏆 ОТЛИЧНОЕ покрытие кода: {cov_total['percentage']:.1f}%")
            print("   💪 Проект готов к использованию!")
        elif cov_total['percentage'] >= 90:
            print(f"   👍 ОЧЕНЬ ХОРОШЕЕ покрытие: {cov_total['percentage']:.1f}%")
            print("   🚀 Можно продолжать разработку")
        elif cov_total['percentage'] >= 85:
            print(f"   ✅ ХОРОШЕЕ покрытие: {cov_total['percentage']:.1f}%")
            print("   📝 Рекомендуется добавить тесты для edge cases")
        elif cov_total['percentage'] >= 80:
            print(f"   ⚠️  УДОВЛЕТВОРИТЕЛЬНОЕ покрытие: {cov_total['percentage']:.1f}%")
            print("   🔧 Нужно добавить больше тестов")
        elif cov_total['percentage'] >= 70:
            print(f"   ⚠️  СРЕДНЕЕ покрытие: {cov_total['percentage']:.1f}%")
            print("   🛠️  Требуется доработка тестов")
        else:
            print(f"   ❗ НИЗКОЕ покрытие: {cov_total['percentage']:.1f}%")
            print("   🛠️  Требуется существенная доработка тестов")

        # Оценка производительности
        print(f"\n   ⏱️  ОЦЕНКА ПРОИЗВОДИТЕЛЬНОСТИ:")
        if total_test_time < 5:
            print(f"   🚀 Отличная производительность: {total_test_time:.2f} сек")
        elif total_test_time < 15:
            print(f"   ✅ Хорошая производительность: {total_test_time:.2f} сек")
        elif total_test_time < 30:
            print(f"   ⚠️  Средняя производительность: {total_test_time:.2f} сек")
        else:
            print(f"   🐌 Низкая производительность: {total_test_time:.2f} сек")

        # Оценка плотности тестов
        print(f"\n   📊 ОЦЕНКА ПЛОТНОСТИ ТЕСТОВ:")
        if test_metrics['assert_density'] >= 0.5:
            print(f"   👍 Высокая плотность проверок: {test_metrics['assert_density']:.3f}")
        elif test_metrics['assert_density'] >= 0.2:
            print(f"   ✅ Средняя плотность проверок: {test_metrics['assert_density']:.3f}")
        else:
            print(f"   ⚠️  Низкая плотность проверок: {test_metrics['assert_density']:.3f}")

        return 0
    else:
        print("   ⚠️ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ")

        if passed_unit < total_unit:
            failed_unit = total_unit - passed_unit
            print(f"   ❌ Обычные тесты: {failed_unit} тестов не прошло")

        if passed_hypothesis < total_hypothesis:
            failed_hypothesis = total_hypothesis - passed_hypothesis
            print(f"   ❌ Тесты с Hypothesis: {failed_hypothesis} тестов не прошло")

        print("\n🔧 ДЛЯ ОТЛАДКИ:")
        print("   • Запустите все тесты с детальным выводом:")
        print("     pytest tests/unit/ -v")
        print("   • Только упавшие тесты:")
        print("     pytest tests/unit/ --lf")
        print("   • Конкретный упавший тест:")
        print("     pytest tests/unit/ -k 'название_теста' -v")
        print("   • Тесты с Hypothesis с отладочным выводом:")
        print("     pytest tests/unit/test_fa_simple_hypothesis.py -v -s")

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
        traceback.print_exc()
        sys.exit(1)