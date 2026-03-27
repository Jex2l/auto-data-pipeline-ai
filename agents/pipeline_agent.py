from __future__ import annotations

from pathlib import Path
from typing import Iterable


def generate_pandas_pipeline_code(column_names: Iterable[str]) -> str:
    cols = list(column_names)
    projection = ", ".join([repr(c) for c in cols])

    code = f'''import pandas as pd

def run_pipeline(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)

    # Example generated transformations
    df = df.drop_duplicates()
    df = df[{projection}]
    df.to_csv(output_path, index=False)
'''
    return code


def save_generated_pipeline(column_names: Iterable[str], output_file: Path) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(generate_pandas_pipeline_code(column_names))
    return output_file