import os
from collections import deque

# Simple observer, just record the results for the third oracle
def entropy_observer(input: str, sample: tuple[int, str, str]) -> list[str]: 
    # Use the function name itself to store the attribute
    if not hasattr(entropy_observer, "inputs"): 
        entropy_observer.inputs = []
    if not hasattr(entropy_observer, "outputs"): 
        entropy_observer.outputs = []

    # store data
    entropy_observer.inputs.append(input)
    # We just keep the valid answer, or if empty, the error!
    sample_data = sample[1] if sample[1] else sample[2]
    entropy_observer.outputs.append(sample_data)
    
    return entropy_observer.inputs, entropy_observer.outputs

WINDOW_SIZE = int(os.environ.get("ENTROPY_WINDOW_SIZE", "1024"))
def entropy_sliding_window_observer(input: str, sample: tuple[int, str, str]) -> list[str]:
    if WINDOW_SIZE < 2:
        raise ValueError("Window size must be at least 2")
        
    # Use the function name itself to store the attribute
    if not hasattr(entropy_sliding_window_observer, "inputs"):
        entropy_sliding_window_observer.inputs = deque(maxlen=WINDOW_SIZE)
    if not hasattr(entropy_sliding_window_observer, "outputs"):
        entropy_sliding_window_observer.outputs = deque(maxlen=WINDOW_SIZE)

    # store data
    entropy_sliding_window_observer.inputs.append(input)
    # We just keep the valid answer, or if empty, the error!
    sample_data = sample[1] if sample[1] else sample[2]
    entropy_sliding_window_observer.outputs.append(sample_data)    
    entropy_sliding_window_observer.outputs.append(sample_data)

    return entropy_sliding_window_observer.inputs, entropy_sliding_window_observer.outputs



