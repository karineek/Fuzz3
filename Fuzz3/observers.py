import os
from collections import deque

# dummy observer: no observation on output  diversity; we can only check regular input diversification.
def null_observer(input: str, sample: tuple[int, str, str]) -> list[str]: 
    # Use the function name itself to store the attribute
    if not hasattr(entropy_observer, "inputs"): 
        entropy_observer.inputs = []
    if not hasattr(entropy_observer, "outputs"): 
        entropy_observer.outputs = []

    # store data
    entropy_observer.inputs.append(input)
    entropy_observer.outputs.append("null")
    return entropy_observer.inputs, entropy_observer.outputs
    
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
    #else:
    #    print(f">> (FUZZ3, Observer) Window size is {WINDOW_SIZE}")
        
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

    #print(f">> (FUZZ3, Observer) data size is {len(entropy_sliding_window_observer.outputs)}")
    return entropy_sliding_window_observer.inputs, entropy_sliding_window_observer.outputs


# Statistical observer, used when the results are a distribution or are expected to be drawn from a distribution
def statistical_observer(input: str, sample: tuple[int, str, str]) -> list[str]: 
    # Use the function name itself to store the attribute
    if not hasattr(statistical_observer, "inputs"):
        statistical_observer.inputs = []
    if not hasattr(statistical_observer, "outputs"):
        statistical_observer.outputs = []

    # Distribution is the last line of stdout; no need the stderr otherwise.
    sample_data = sample[1].strip().splitlines()[-1] if sample[1] else None

    if sample_data is not None:
        statistical_observer.inputs.append(input)
        statistical_observer.outputs.append(sample_data)

    return statistical_observer.input, statistical_observer.outputs

STAT_TEST_WINDOW_SIZE = int(os.environ.get("STATISTICAL_WINDOW_SIZE", "1024"))
def statistical_sliding_window_observer(input: str, sample: tuple[int, str, str]) -> list[str]: 
    if STAT_TEST_WINDOW_SIZE < 2:
        raise ValueError("Window size must be at least 2")
        
    # Use the function name itself to store the attribute
    if not hasattr(statistical_sliding_window_observer, "inputs"):
        statistical_sliding_window_observer.inputs = deque(maxlen=STAT_TEST_WINDOW_SIZE)
    if not hasattr(statistical_sliding_window_observer, "outputs"):
        statistical_sliding_window_observer.outputs = deque(maxlen=STAT_TEST_WINDOW_SIZE)

    # Distribution is the last line of stdout; no need the stderr otherwise.
    sample_data = sample[1].strip().splitlines()[-1] if sample[1] else None

    if sample_data is not None:
        statistical_sliding_window_observer.inputs.append(input)
        statistical_sliding_window_observer.outputs.append(sample_data)

    return statistical_sliding_window_observer.input, statistical_sliding_window_observer.outputs
