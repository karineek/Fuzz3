from pathlib import Path

# Simple observer, just record the results for the third oracle
def entropy_observer(input: str, sample: tuple[int, str, str]) -> list[str]: 
    # Use the function name itself to store the attribute
    if not hasattr(olc_encoder_observer, "outputs"): 
        olc_encoder_observer.inputs = []
    if not hasattr(olc_encoder_observer, "outputs"): 
        olc_encoder_observer.outputs = []

    # store data
    olc_encoder_observer.inputs.append(input)
    # We just keep the valid answer, or if empty, the error!
    sample_data = sample[1] if sample[1] else sample[2]
    olc_encoder_observer.outputs.append(sample_data)
    
    return olc_encoder_observer.inputs, olc_encoder_observer.outputs




