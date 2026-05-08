#!/usr/bin/env python3
"""
Экспериментальный раннер для оценки качества тестирования FA.

Сравниваются три подхода:
1. UNIT TESTS
2. HYPOTHESIS TESTS
3. COMBINED (UNIT + HYPOTHESIS)

Метрика TSQI:
TSQI = 0.25 * Coverage + 0.45 * Mutation + 0.2 * Stability + 0.1 * Performance
"""

import os
import re
import subprocess
import time
from typing import Dict, List
from src.fa_factory import FA


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

RUNS = 10

TEST_SUITES = {
    "UNIT": "tests/unit/",
    "HYPOTHESIS": "tests/hypothesis/",
    "COMBINED": "tests/",
}

IMPLEMENTATIONS = [
    "FA_simple",
    "FA_dict",
]

# покрытие считаем по всему src (чтобы работало для любой реализации)
COV_TARGET = "src"

MUTATIONS = [
    "FA_simple_mut_01",
    "FA_simple_mut_02",
    "FA_simple_mut_03",
    "FA_simple_mut_04",
    "FA_simple_mut_05",
    "FA_simple_mut_06",
    "FA_simple_mut_07",
    "FA_simple_mut_08",
    "FA_simple_mut_09",
    "FA_simple_mut_10",
    "FA_simple_mut_11",
    "FA_simple_mut_12",
    "FA_dict_mut_01",
    "FA_dict_mut_02",
    "FA_dict_mut_03",
    "FA_dict_mut_04",
    "FA_dict_mut_05",
    "FA_dict_mut_06",
]


# ------------------------------------------------------------
# UTILS
# ------------------------------------------------------------

def run_command(cmd: str) -> tuple[bool, str, float]:
    start = time.perf_counter()

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    duration = time.perf_counter() - start
    success = result.returncode == 0
    output = result.stdout + "\n" + result.stderr

    return success, output, duration


def parse_pytest_summary(output: str) -> tuple[int, int]:
    for line in reversed(output.splitlines()):
        if "passed" in line:
            passed = int(re.search(r"(\d+)\s+passed", line).group(1))
            failed_match = re.search(r"(\d+)\s+failed", line)
            failed = int(failed_match.group(1)) if failed_match else 0
            return passed, passed + failed
    return 0, 0


def parse_coverage(output: str) -> float:
    for line in output.splitlines():
        if line.strip().startswith("TOTAL"):
            percent = float(re.search(r"(\d+(?:\.\d+)?)%", line).group(1))
            return percent / 100
    return 0.0


# ------------------------------------------------------------
# TEST RUNS
# ------------------------------------------------------------

def run_tests_once(test_path: str) -> Dict:
    cmd = f"pytest {test_path} --cov={COV_TARGET} --cov-report=term"

    ok, out, duration = run_command(cmd)

    passed, total = parse_pytest_summary(out)
    coverage = parse_coverage(out)

    return {
        "passed": passed,
        "total": total,
        "all_passed": passed == total,
        "time": duration,
        "coverage": coverage,
    }


def run_tests_multiple(test_path: str, runs: int = RUNS) -> Dict:
    results = []

    for i in range(runs):
        print(f"   ▶️ Прогон {i + 1}/{runs}")
        results.append(run_tests_once(test_path))

    avg_time = sum(r["time"] for r in results) / runs
    avg_cov = sum(r["coverage"] for r in results) / runs
    stability = sum(r["all_passed"] for r in results) / runs

    return {
        "time": avg_time,
        "coverage": avg_cov,
        "stability": stability,
    }


# ------------------------------------------------------------
# MUTATION TESTING
# ------------------------------------------------------------

def compute_mutation_score(test_path: str, mutations: List[str]) -> Dict:
    killed = 0
    survived = []
    if not mutations:
        return {
            "score": 0.0,
            "killed": 0,
            "total": 0,
            "survived": [],
        }
    else:
        for mut in mutations:
            print(f"   🧬 Мутация: {mut}")
            try:
                os.environ["FA_MUTATION"] = mut

                result = run_tests_once(test_path)

                if not result["all_passed"]:
                    killed += 1
                    print("      ❌ УБИТ")
                else:
                    survived.append(mut)
                    print("      ⚠️  ВЫЖИЛ")

            finally:
                os.environ.pop("FA_MUTATION", None)

    score = killed / len(mutations)

    return {
        "score": score,
        "killed": killed,
        "total": len(mutations),
        "survived": survived,
    }


# ------------------------------------------------------------
# TSQI
# ------------------------------------------------------------

def compute_tsq(cov: float, mut: float, stab: float, time_val: float) -> float:
    # немного сглаженная метрика производительности
    perf = 1 / (1 + time_val / 5)

    return (
        0.25 * cov +
        0.45 * mut +
        0.2 * stab +
        0.1 * perf
    )


# ------------------------------------------------------------
# EVALUATION
# ------------------------------------------------------------

def evaluate(test_path: str, name: str, impl: str) -> Dict:
    print("\n" + "=" * 80)
    print(f"🔍 Оценка: {name} [{impl}]")
    print("=" * 80)

    os.environ["FA_IMPL"] = impl

    print("\n▶️ Прогоны тестов")
    base = run_tests_multiple(test_path)

    print("\n▶️ Мутационное тестирование")

    # мутации применяем к FA_simple и FA_dict
    relevant_mutations = [
        m for m in MUTATIONS
        if m.startswith(f"{impl}_")
    ]

    mut_data = compute_mutation_score(test_path, relevant_mutations)

    tsqi = compute_tsq(
        cov=base["coverage"],
        mut=mut_data["score"],   # <-- ВАЖНЫЙ ФИКС
        stab=base["stability"],
        time_val=base["time"],
    )

    os.environ.pop("FA_IMPL", None)

    return {
        "coverage": base["coverage"],
        "stability": base["stability"],
        "time": base["time"],
        "mutation": mut_data,
        "tsqi": tsqi,
    }


# ------------------------------------------------------------
# FINAL TABLE
# ------------------------------------------------------------

def print_final_table(results: Dict):
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ ТАБЛИЦА")
    print("=" * 80)

    header = f"{'Impl':10} | {'Approach':10} | {'Cov':6} | {'Mut':6} | {'Stab':6} | {'Time':6} | {'TSQI':6}"
    print(header)
    print("-" * len(header))

    for impl, approaches in results.items():
        for name, m in approaches.items():
            print(
                f"{impl:10} | {name:10} | "
                f"{m['coverage']*100:5.1f}% | "
                f"{m['mutation']['score']*100:5.1f}% | "
                f"{m['stability']*100:5.1f}% | "
                f"{m['time']:5.2f}s | "
                f"{m['tsqi']:.3f}"
            )


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    print("=" * 80)
    print("🧪 ЭКСПЕРИМЕНТ: СРАВНЕНИЕ РЕАЛИЗАЦИЙ И ПОДХОДОВ")
    print("=" * 80)

    results = {}

    for impl in IMPLEMENTATIONS:
        print("\n" + "#" * 80)
        print(f"🚀 РЕАЛИЗАЦИЯ: {impl}")
        print("#" * 80)

        unit = evaluate(TEST_SUITES["UNIT"], "UNIT", impl)
        hypo = evaluate(TEST_SUITES["HYPOTHESIS"], "HYPOTHESIS", impl)
        combined = evaluate(TEST_SUITES["COMBINED"], "COMBINED", impl)

        results[impl] = {
            "UNIT": unit,
            "HYPOTHESIS": hypo,
            "COMBINED": combined,
        }

    print_final_table(results)

    print("\n" + "=" * 80)
    print("⚠️ ВЫЖИВШИЕ МУТАЦИИ")
    print("=" * 80)

    for impl, approaches in results.items():
        print(f"\n{impl}:")
        for name, m in approaches.items():
            surv = m["mutation"]["survived"]
            if surv:
                print(f"  {name:<12} -> {surv}")
            else:
                print(f"  {name:<12} -> нет")

if __name__ == "__main__":
    main()