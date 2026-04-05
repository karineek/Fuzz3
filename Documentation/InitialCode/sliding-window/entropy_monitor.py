#!/usr/bin/env python3
"""
Sliding window entropy monitor.

Usage:
    python entropy_monitor.py <window_size> <total_iterations> <script_to_run>

The script_to_run should output two lines per invocation:
    Line 1: input string
    Line 2: output string

Flags an error if H(Y) - H(X) deviates more than 2 std devs from the rolling mean.
"""

import sys
import subprocess
import math
from collections import Counter, deque
import statistics


def compute_entropy(counter: Counter, n: int) -> float:
    """Compute Shannon entropy from a Counter and total count n."""
    entropy = 0.0
    for count in counter.values():
        if count > 0:
            p = count / n
            entropy -= p * math.log2(p)
    return entropy


def run_script(script: str) -> tuple[str, str]:
    """Run the external script and return (input_str, output_str)."""
    result = subprocess.run(
        script,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {result.stderr.strip()}")
    lines = result.stdout.strip().splitlines()
    if len(lines) < 2:
        raise ValueError(f"Script must output 2 lines, got: {result.stdout!r}")
    return lines[0], lines[1]


def main():
    if len(sys.argv) != 4:
        sys.exit("Usage: python entropy_monitor.py <window_size> <total_iterations> <script>")

    try:
        w = int(sys.argv[1])
        total = int(sys.argv[2])
    except ValueError:
        sys.exit("window_size and total_iterations must be integers")

    script = sys.argv[3]

    if w < 2:
        sys.exit("Window size must be at least 2")
    if total <= w:
        sys.exit("total_iterations must be greater than window_size")

    # Sliding window storage
    window: deque[tuple[str, str]] = deque()
    input_counter = Counter()
    output_counter = Counter()

    # Rolling history of entropy differences (for baseline)
    entropy_diff_history: list[float] = []

    print(f"{'Iteration':<12} {'H(X)':<10} {'H(Y)':<10} {'H(Y)-H(X)':<12} {'Mean':<10} {'Std':<10} {'Status'}")
    print("-" * 80)

    # --- Phase 1: Fill the initial window (w iterations) ---
    for i in range(w):
        inp, out = run_script(script)
        window.append((inp, out))
        input_counter[inp] += 1
        output_counter[out] += 1

    h_x = compute_entropy(input_counter, w)
    h_y = compute_entropy(output_counter, w)
    diff = h_y - h_x
    entropy_diff_history.append(diff)
    print(f"{w:<12} {h_x:<10.4f} {h_y:<10.4f} {diff:<12.4f} {'(baseline)':<10} {'':<10} OK")

    # --- Phase 2: Sliding window from w+1 to total ---
    for i in range(w + 1, total + 1):
        # Add new pair
        inp, out = run_script(script)
        window.append((inp, out))
        input_counter[inp] += 1
        output_counter[out] += 1

        # Remove oldest pair
        old_inp, old_out = window.popleft()
        input_counter[old_inp] -= 1
        output_counter[old_out] -= 1
        if input_counter[old_inp] == 0:
            del input_counter[old_inp]
        if output_counter[old_out] == 0:
            del output_counter[old_out]

        h_x = compute_entropy(input_counter, w)
        h_y = compute_entropy(output_counter, w)
        diff = h_y - h_x

        # Compute rolling mean and std from history
        mean_diff = statistics.mean(entropy_diff_history)
        std_diff = statistics.stdev(entropy_diff_history) if len(entropy_diff_history) > 1 else 0.0

        status = "OK"
        flagged = False
        if std_diff > 0 and abs(diff - mean_diff) > 2 * std_diff:
            status = "*** FLAGGED ***"
            flagged = True

        print(f"{i:<12} {h_x:<10.4f} {h_y:<10.4f} {diff:<12.4f} {mean_diff:<10.4f} {std_diff:<10.4f} {status}")

        entropy_diff_history.append(diff)

        if flagged:
            sys.exit(
                f"\nERROR: Entropy difference {diff:.4f} at iteration {i} "
                f"deviates more than 2 std devs (mean={mean_diff:.4f}, std={std_diff:.4f}) "
                f"from rolling baseline."
            )

    print("\nCompleted all iterations without flagging.")


if __name__ == "__main__":
    main()
