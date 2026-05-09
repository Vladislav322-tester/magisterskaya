#!/usr/bin/env python3
"""Экспериментальный runner для сравнения стратегий тестирования автоматов.

Модуль запускает unit-, Hypothesis- и комбинированные наборы тестов,
считает coverage, стабильность и mutation score, а также отдельно
учитывает невалидные или некомпетентные мутанты.
"""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List


def load_dotenv(path: str = ".env") -> bool:
    """
    Загружает локальный .env-файл в переменные окружения, если файл существует.
    """
    env_path = Path(path)
    if not env_path.exists():
        return False

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

    return True


DOTENV_LOADED = load_dotenv()
RUNS = int(os.getenv("FA_RUNS", "1"))
MUTATION_TESTING = os.getenv("FA_MUTATION_TESTING", "1") != "0"
COVERAGE_ENABLED = os.getenv("FA_COVERAGE", "1") != "0"
COV_TARGETS = {
    "FA_simple": "src.FA_simple",
    "FA_dict": "src.FA_dict",
}

ALL_TEST_SUITES = {
    "UNIT": "tests/unit/",
    "HYPOTHESIS": "tests/hypothesis/",
    "COMBINED": "tests/",
}

SUITE_NAMES = [
    item.strip().upper()
    for item in os.getenv("FA_SUITES", "UNIT,HYPOTHESIS,COMBINED").split(",")
    if item.strip()
]

TEST_SUITES = {
    name: ALL_TEST_SUITES[name]
    for name in SUITE_NAMES
    if name in ALL_TEST_SUITES
}

IMPLEMENTATIONS = [
    item.strip()
    for item in os.getenv("FA_IMPLS", "FA_simple").split(",")
    if item.strip()
]


def print_configuration() -> None:
    """
    Печатает параметры эксперимента, с которыми будет запущен runner.
    """
    print("Конфигурация:")
    print(f"  .env загружен: {'да' if DOTENV_LOADED else 'нет'}")
    print(f"  FA_RUNS={RUNS}")
    print(f"  FA_IMPLS={','.join(IMPLEMENTATIONS)}")
    print(f"  FA_SUITES={','.join(TEST_SUITES)}")
    print(f"  FA_MUTATION_TESTING={1 if MUTATION_TESTING else 0}")
    print(f"  FA_COVERAGE={1 if COVERAGE_ENABLED else 0}")


def run_command(cmd: str, env: dict | None = None) -> tuple[bool, str, float]:
    """
    Запускает shell-команду и возвращает статус, объединенный вывод и длительность.
    """
    command_env = os.environ.copy()
    if env:
        command_env.update(env)

    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=command_env,
    )
    duration = time.perf_counter() - start
    return result.returncode == 0, result.stdout + "\n" + result.stderr, duration


def parse_pytest_summary(output: str) -> tuple[int, int]:
    """
    Извлекает количество прошедших и всего выполненных тестов из вывода pytest.
    """
    for line in reversed(output.splitlines()):
        if any(word in line for word in ["passed", "failed", "error"]):
            passed = _count(line, "passed")
            failed = _count(line, "failed")
            errors = _count(line, "errors?") or _count(line, "error")
            return passed, passed + failed + errors
    return 0, 0


def _count(line: str, label_regex: str) -> int:
    """
    Извлекает числовое значение для указанной метки из строки summary pytest.
    """
    match = re.search(rf"(\d+)\s+{label_regex}", line)
    return int(match.group(1)) if match else 0


def coverage_target_for_impl(impl: str) -> str:
    """
    Возвращает модуль coverage, соответствующий выбранной реализации автомата.
    """
    return COV_TARGETS.get(impl, f"src.{impl}")


def parse_coverage(output: str) -> float | None:
    """
    Извлекает процент покрытия из строки TOTAL в отчете coverage.
    """
    for line in output.splitlines():
        if line.strip().startswith("TOTAL"):
            match = re.search(r"(\d+(?:\.\d+)?)%", line)
            return float(match.group(1)) / 100 if match else None
    return None


def pytest_run_ok(command_ok: bool, passed: int, total: int) -> bool:
    """
    Определяет, был ли pytest-прогон успешным и непустым.
    """
    return command_ok and total > 0 and passed == total


def has_infrastructure_error(output: str) -> bool:
    """
    Ищет в выводе pytest признаки инфраструктурной ошибки или ошибки collection.
    """
    markers = [
        "ERROR collecting",
        "ImportError",
        "ModuleNotFoundError",
        "SyntaxError",
        "IndentationError",
        "does not define expected class",
        "collected 0 items",
        "no tests ran",
    ]
    return any(marker in output for marker in markers)


def validate_factory_selection(impl: str, mutation: str | None = None) -> tuple[bool, str]:
    """
    Проверяет, что фабрика выбрала нужную реализацию и, при необходимости, мутант.
    """
    env = {"FA_IMPL": impl}
    if mutation:
        env["FA_MUTATION"] = mutation

    ok, output, _ = run_command(
        'python -c "from src.fa_factory import describe_selected_fa; print(describe_selected_fa())"',
        env=env,
    )

    expected_mutation = mutation or "none"
    selected = f"impl={impl}" in output and f"mutation={expected_mutation}" in output
    if mutation:
        selected = selected and f"src.mutations.{mutation}" in output
    return ok and selected, output.strip()


def discover_mutations(impl: str) -> list[str]:
    """
    Находит mutation-модули, относящиеся к выбранной реализации.
    """
    mutations_dir = Path("src") / "mutations"
    if not mutations_dir.exists():
        return []
    return sorted(
        path.stem
        for path in mutations_dir.glob(f"{impl}_mut_*.py")
        if path.name != "__init__.py"
    )


def run_tests_once(
    test_path: str,
    impl: str,
    mutation: str | None = None,
    with_coverage: bool = True,
) -> Dict:
    """
    Запускает один pytest-прогон для suite, реализации и опционального мутанта.
    """
    env = {"FA_IMPL": impl}
    if mutation:
        env["FA_MUTATION"] = mutation

    coverage_requested = with_coverage and COVERAGE_ENABLED
    coverage_target = coverage_target_for_impl(impl)
    if coverage_requested:
        cmd = f"pytest {test_path} --cov={coverage_target} --cov-report=term"
    else:
        cmd = f"pytest {test_path} -q"

    ok, out, duration = run_command(
        cmd,
        env=env,
    )
    passed, total = parse_pytest_summary(out)
    coverage = parse_coverage(out) if coverage_requested else 0.0
    coverage_failed = coverage_requested and coverage is None
    invalid_run = total == 0 or has_infrastructure_error(out) or coverage_failed
    all_passed = pytest_run_ok(ok, passed, total) and not coverage_failed
    return {
        "passed": passed,
        "total": total,
        "all_passed": all_passed,
        "invalid_run": invalid_run,
        "coverage": coverage if coverage is not None else 0.0,
        "coverage_target": coverage_target if coverage_requested else None,
        "coverage_failed": coverage_failed,
        "time": duration,
        "output": out,
    }


def run_tests_multiple(test_path: str, impl: str, runs: int = RUNS) -> Dict:
    """
    Повторяет baseline-прогон несколько раз и агрегирует стабильность, время и coverage.
    """
    results = []
    for i in range(runs):
        print(f"   прогон {i + 1}/{runs}")
        results.append(run_tests_once(test_path, impl, with_coverage=True))

    return {
        "time": sum(r["time"] for r in results) / runs,
        "coverage": sum(r["coverage"] for r in results) / runs,
        "stability": sum(r["all_passed"] for r in results) / runs,
        "invalid_runs": sum(r["invalid_run"] for r in results),
    }


def compute_mutation_score(test_path: str, impl: str) -> Dict:
    """
    Считает mutation score для выбранного набора тестов и реализации.
    """
    killed: list[str] = []
    survived: list[str] = []
    invalid: list[dict] = []

    if not MUTATION_TESTING:
        return {
            "score": 0.0,
            "killed": 0,
            "survived": [],
            "invalid": [],
            "valid_total": 0,
            "total": 0,
            "enabled": False,
        }

    for mutation in discover_mutations(impl):
        print(f"   мутант: {mutation}")
        valid, validation = validate_factory_selection(impl, mutation)
        if not valid:
            invalid.append({"name": mutation, "reason": validation})
            print("      НЕВАЛИДЕН: ошибка импорта или выбора фабрики")
            continue

        result = run_tests_once(
            test_path,
            impl,
            mutation=mutation,
            with_coverage=False,
        )
        if result["invalid_run"]:
            invalid.append({
                "name": mutation,
                "reason": "collection/import/API error or zero collected tests",
            })
            print("      НЕВАЛИДЕН: тестовый прогон не выполнил валидные тесты")
        elif result["all_passed"]:
            survived.append(mutation)
            print("      ВЫЖИЛ")
        else:
            killed.append(mutation)
            print("      УБИТ")

    valid_total = len(killed) + len(survived)
    return {
        "score": len(killed) / valid_total if valid_total else 0.0,
        "killed": len(killed),
        "survived": survived,
        "invalid": invalid,
        "valid_total": valid_total,
        "total": valid_total + len(invalid),
        "enabled": True,
    }


def compute_tsq(cov: float, mut: float, stab: float, time_val: float) -> float:
    """
    Вычисляет сводный показатель качества тестов из coverage, mutation score, стабильности и времени.
    """
    perf = 1 / (1 + time_val / 5)
    return 0.25 * cov + 0.45 * mut + 0.2 * stab + 0.1 * perf


def evaluate(test_path: str, suite_name: str, impl: str) -> Dict:
    """
    Проводит полную оценку одного test suite для одной реализации автомата.
    """
    print("\n" + "=" * 80)
    print(f"Оценка: {suite_name} [{impl}]")
    print("=" * 80)

    selected, details = validate_factory_selection(impl)
    if not selected:
        print(f"Не удалось выбрать реализацию через фабрику: {details}")
        return {
            "coverage": 0.0,
            "stability": 0.0,
            "time": 0.0,
            "mutation": {
                "score": 0.0,
                "killed": 0,
                "survived": [],
                "invalid": [{"name": impl, "reason": details}],
                "valid_total": 0,
                "total": 0,
            },
            "tsqi": 0.0,
        }

    print(f"Фабрика: {details}")
    coverage_label = coverage_target_for_impl(impl) if COVERAGE_ENABLED else "отключено"
    print(f"Цель coverage: {coverage_label}")
    base = run_tests_multiple(test_path, impl)
    mutations = compute_mutation_score(test_path, impl)

    return {
        "coverage": base["coverage"],
        "stability": base["stability"],
        "time": base["time"],
        "invalid_runs": base["invalid_runs"],
        "mutation": mutations,
        "tsqi": compute_tsq(
            cov=base["coverage"],
            mut=mutations["score"],
            stab=base["stability"],
            time_val=base["time"],
        ),
    }


def print_final_table(results: Dict) -> None:
    """
    Печатает итоговую таблицу экспериментальных метрик.
    """
    print("\n" + "=" * 80)
    print("ИТОГОВАЯ ТАБЛИЦА")
    print("=" * 80)
    header = (
        f"{'Реализация':10} | {'Набор':10} | {'Cov':6} | {'Mut':6} | "
        f"{'Stab':6} | {'Время':7} | {'Невал.':7} | {'TSQI':6}"
    )
    print(header)
    print("-" * len(header))

    for impl, suites in results.items():
        for suite_name, metrics in suites.items():
            mutation = metrics["mutation"]
            invalid_count = len(mutation["invalid"]) + metrics.get("invalid_runs", 0)
            print(
                f"{impl:10} | {suite_name:10} | "
                f"{metrics['coverage'] * 100:5.1f}% | "
                f"{mutation['score'] * 100:5.1f}% | "
                f"{metrics['stability'] * 100:5.1f}% | "
                f"{metrics['time']:6.2f}s | "
                f"{invalid_count:7d} | "
                f"{metrics['tsqi']:.3f}"
            )


def main() -> int:
    """
    Точка входа experiment runner: запускает все выбранные реализации и наборы тестов.
    """
    print("=" * 80)
    print("ЭКСПЕРИМЕНТ ТЕСТИРОВАНИЯ АВТОМАТОВ")
    print("=" * 80)
    print_configuration()

    results = {}
    for impl in IMPLEMENTATIONS:
        results[impl] = {}
        for suite_name, test_path in TEST_SUITES.items():
            results[impl][suite_name] = evaluate(test_path, suite_name, impl)

    print_final_table(results)

    print("\nНевалидные/некомпетентные мутанты исключены из mutation score.")
    for impl, suites in results.items():
        print(f"\n{impl}:")
        for suite_name, metrics in suites.items():
            invalid = metrics["mutation"]["invalid"]
            survived = metrics["mutation"]["survived"]
            print(f"  {suite_name}: выжившие={survived or []}, невалидные={len(invalid)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
