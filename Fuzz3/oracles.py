from pathlib import Path
from collections import Counter
import math

# For statistical test oracles
from scipy.stats import chi2_contingency
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy

def dummy_oracle(seed, results_map: dict[str, list[str]]):
    for func_name, outputs in results_map.items():
        print(f"Results for {func_name}: {outputs}")
    return 0


def entropy_oracle(seed, results_map: dict[str, tuple[str, str]]):
    # Check which observer we used.
    if "entropy_observer" in results_map:
        data = results_map["entropy_observer"]
    elif "entropy_sliding_window_observer" in results_map:
        data = results_map["entropy_sliding_window_observer"]
    else:
        raise ValueError("No entropy observer data found")

    inputs = data[0]
    outputs = data[1]
    n = len(inputs)
    if n != len(outputs):
        return 0, 0, 0, 0

    # Then the code as is!
    distribution = Counter(outputs)
    probabilities_output = []
    entropy_prob_output = []

    distribution_inputs = Counter(inputs)
    probabilities_inputs = []
    entropy_prob_inputs = []

    for i in set(outputs):
        count = distribution.get(i)
        probability_i = count / n
        probabilities_output.append(probability_i)
        entropy_prob_output.append(probability_i * math.log2(probability_i))

    for i in set(inputs):
        count = distribution_inputs.get(i)
        probability_j = count / n
        probabilities_inputs.append(probability_j)
        entropy_prob_inputs.append(probability_j * math.log2(probability_j))

    entropy_output = sum(entropy_prob_output)
    entropy_input = sum(entropy_prob_inputs)
    return -entropy_input, -entropy_output, len(distribution), n

# Helper function
def _statistical_oracle(seed, results_map: dict[str, tuple[str, str]], func):
    if "statistical_observer" in results_map:
        data = results_map["statistical_observer"]
    elif "statistical_sliding_window_observer" in results_map:
        data = results_map["statistical_sliding_window_observer"]
    else:
        raise ValueError("No statistical observer data found")

    inputs = data[0]
    outputs = data[1]
    n = len(inputs)

    if n != len(outputs):
        return 0, 0, 0, 0

    code_in = seed.read_text(encoding="utf-8")
    output_before = None
    for i in range(len(inputs) - 1, -1, -1):
        if inputs[i] == code_in:
            output_before = outputs[i]
            break
    if output_before is None:
        return 0, 0, 0, n

    # Newly executed mutant
    output_after = outputs[-1]

    stat_test_res = func(output_before, output_after)
    return output_before, output_after, stat_test_res, n

def statistical_oracle_chi_square(seed, results_map: dict[str, tuple[str, str]]):
    return _statistical_oracle(seed, results_map, chi2_contingency)

