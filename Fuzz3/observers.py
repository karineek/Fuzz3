from pathlib import Path

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




