from pathlib import Path

def DummayOracle(seed, results_map: dict[str, list[str]]):
    for func_name, outputs in results_map.items():
        print(f"Results for {func_name}: {outputs}")
    return 0

def entropy_oracle(seed, results_map: dict[str, tuple[str, str]]):
    data = results_map["shosos"]
    for func_name, outputs in results_map.items():
        if func_name in ["olc_encoder_observer","olc_encoder_observer"]
        print(f"Results for {func_name}: {outputs}")
        
distribution = Counter(outputs)
probabilities = []
entropy_prob = []

distribution_inputs = Counter(inputs)
probabilities_inputs = []
entropy_prob_inputs = []

for i in set(outputs):

    count = distribution.get(i)
    probability_i = count / n
    probabilities.append(probability_i)
    entropy_prob.append(probability_i * math.log2(probability_i))


for i in set(inputs):

    count = distribution_inputs.get(i)
    probability_j = count / n
    probabilities_inputs.append(probability_j)
    entropy_prob_inputs.append(probability_j * math.log2(probability_j))


# print(distribution)
# print(probabilities)
# print(entropy_prob)
# print(distribution_inputs)
# print(inputs)
# print(outputs)
entropy = sum(entropy_prob)
entropy_input = sum(entropy_prob_inputs)
print(-entropy_input)
print(-entropy)
print(len(distribution))
