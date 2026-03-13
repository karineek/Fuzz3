from pathlib import Path

# Simple observer, just record the results for third oracle
def olc_encoder_observer(sample: tuple[int, str, str]) -> list[str]: 
    # Use the function name itself to store the attribute
    if not hasattr(olc_encoder_observer, "outputs"): 
        olc_encoder_observer.outputs = []

    # We just keep the valid answer, or if empty, the error!
    sample_data = sample[1] if sample[1] else sample[2]
    olc_encoder_observer.outputs.append(sample_data)
    return olc_encoder_observer.outputs




