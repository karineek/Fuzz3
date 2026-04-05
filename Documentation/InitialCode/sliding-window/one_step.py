#!/usr/bin/env python3
from openlocationcode import openlocationcode
import random
from collections import Counter
import math

# randomly generate inputs
lat = random.randint(-90, 90)
long = random.randint(-180, 180)

# compute the result
res = openlocationcode.encode(lat, long)

# print the output
print(f"{lat},{long}")
print(res)

