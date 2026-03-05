from openlocationcode import openlocationcode
import random
from collections import Counter
import math

n = 1024 * 1024
func = openlocationcode.encode
outputs = []
inputs = []
# temp_lat_inputs = [x for x in range(n)]
# temp_long_inputs = [y for y in range(n)]
for i in range(n):
    lat = random.randint(-90, 90)
    long = random.randint(-180, 180)
    inputs.append((lat, long))
    outputs.append(func(lat, long))

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
