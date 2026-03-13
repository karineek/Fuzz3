from pathlib import Path

def DummayOracle(results_map: dict[str, list[str]]):
    for func_name, outputs in results_map.items():
        print(f"Results for {func_name}: {outputs}")
    return 0

