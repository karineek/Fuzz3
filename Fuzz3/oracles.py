from pathlib import Path
from collections import Counter
import math
import json
import os

# For statistical test oracles
from scipy.stats import chi2_contingency
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy, ks_2samp, chisquare, wilcoxon

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


################################################################
# Debugging of the statistical oracles: https://colab.research.google.com/drive/1Wwwht85zu_HHAsIbhhjjIA1O55BCvLsz?usp=sharing

# Helper function
def _align_distributions(before: str, after: str):
    # 1. Already lists
    if isinstance(before, list) and isinstance(after, list):
        return before, after

    # 2. Already dictionaries
    if isinstance(before, dict) and isinstance(after, dict):
        states = sorted(set(before) | set(after))

        p = [before.get(state, 0) for state in states]
        q = [after.get(state, 0) for state in states]

        return p, q
        
    # 3. JSON
    try:
        p = json.loads(before)
        q = json.loads(after)

        if isinstance(p, dict) and isinstance(q, dict):
            # Sort all possible states and fill missing entries with 0
            states = sorted(set(p) | set(q))
  
            p = [p.get(state, 0) for state in states]
            q = [q.get(state, 0) for state in states]

            return p, q

        if not isinstance(p, dict) and not isinstance(q, dict):
            return p, q

    except Exception:
        pass

    # 4. Python dict / Counter
    try:
        if before.startswith("Counter(") and before.endswith(")"):
            before = before[len("Counter("):-1]
    
        if after.startswith("Counter(") and after.endswith(")"):
            after = after[len("Counter("):-1]
    
        p = ast.literal_eval(before)
        q = ast.literal_eval(after)
    
        if isinstance(p, dict) and isinstance(q, dict):
            states = sorted(set(p) | set(q))
    
            p = [p.get(state, 0) for state in states]
            q = [q.get(state, 0) for state in states]
    
            return p, q
    
        if isinstance(p, list) and isinstance(q, list):
            return p, q
    
    except Exception:
        pass
        
    return None, None

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
    code_in = seed.read_text(encoding="utf-8")
    output_before = None
    for i in range(len(inputs) - 1, -1, -1):
        if inputs[i] == code_in:
            output_before = outputs[i]
            break
    if output_before is None:
        return 0, 0, 0, 0

    # Newly executed mutant
    output_after = outputs[-1]

    p, q = _align_distributions(output_before, output_after)
    if p is None or q is None:
        return output_before, output_after, -1, 0

    if (len(p) == len(q)):
        stat_test_res = func(p, q)
        return output_before, output_after, stat_test_res, len(p)
    else:
        return output_before, output_after, -1, len(p) 

        
STATISTICAL_CONFIDENCE = float(os.environ.get("STATISTICAL_CONFIDENCE_PARAM", "0.05"))

# chi2_contingency(table) - statistical test
def _chi_square(p, q):
    result = chi2_contingency([p, q])

    conf = STATISTICAL_CONFIDENCE if 0 < STATISTICAL_CONFIDENCE < 1 else 0.01
    return 0 if result.pvalue >= conf else 1

def chi_square_statistical_oracle(seed, results_map: dict[str, tuple[str, str]]):
    return _statistical_oracle(seed, results_map, _chi_square)


# entropy(p, q) - KL divergence
def _KL(p, q):
    divergence = entropy(p, q)

    conf = STATISTICAL_CONFIDENCE if 0 < STATISTICAL_CONFIDENCE < 1 else 0.01
    return 0 if divergence <= conf else 1

def KL_statistical_oracle(seed, results_map: dict[str, tuple[str, str]]):
    return _statistical_oracle(seed, results_map, _KL)


# jensenshannon(p, q) - JS distance
def _jensenshannon(p, q):
    distance = jensenshannon(p, q)

    conf = STATISTICAL_CONFIDENCE if 0 < STATISTICAL_CONFIDENCE < 1 else 0.01
    return 0 if distance <= conf else 1

def jensenshannon_statistical_oracle(seed, results_map: dict[str, tuple[str, str]]):
    return _statistical_oracle(seed, results_map, _jensenshannon)


# The code below is ChatGPT-generated based on the KL_statistical_oracle above (August 12, 2026, 17:17)
def _chi_square(p, q):
    result = chisquare(f_obs=q, f_exp=p)

    conf = STATISTICAL_CONFIDENCE if 0 < STATISTICAL_CONFIDENCE < 1 else 0.01
    return 0 if result.pvalue >= conf else 1

def chi_square_statistical_oracle(seed, results_map: dict[str, tuple[str, str]]):
    return _statistical_oracle(seed, results_map, _chi_square)

def _wilcoxon(p, q):
    if p == q:
        return 0

    result = wilcoxon(p, q)

    conf = STATISTICAL_CONFIDENCE if 0 < STATISTICAL_CONFIDENCE < 1 else 0.01
    return 0 if result.pvalue >= conf else 1

def wilcoxon_statistical_oracle(seed, results_map: dict[str, tuple[str, str]]):
    return _statistical_oracle(seed, results_map, _wilcoxon)

def _KS(p, q):
    p_samples = []
    q_samples = []

    for state, count in enumerate(p):
        p_samples += [state] * int(count)

    for state, count in enumerate(q):
        q_samples += [state] * int(count)

    result = ks_2samp(p_samples, q_samples)

    conf = STATISTICAL_CONFIDENCE if 0 < STATISTICAL_CONFIDENCE < 1 else 0.01
    return 0 if result.pvalue >= conf else 1

def KS_statistical_oracle(seed, results_map: dict[str, tuple[str, str]]):
    return _statistical_oracle(seed, results_map, _KS)
