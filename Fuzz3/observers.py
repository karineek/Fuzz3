from pathlib import Path

# Simple observer, just record the results for third oracle
def olc_encoder_observer(sample: str) -> list[str]: 
    # Use the function name itself to store the attribute
    if not hasattr(olc_encoder_observer, "outputs"): 
        olc_encoder_observer.outputs = []
        
    olc_encoder_observer.outputs.append(sample)
    return olc_encoder_observer.outputs




