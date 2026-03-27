import pandas as pd

from agents.schema_agent import infer_schema_summary


def test_schema_summary_contains_column_metadata():
    df = pd.DataFrame({"name": ["a", "b"], "score": [1, 2]})
    schema = infer_schema_summary(df)

    assert schema["column_count"] == 2
    assert schema["row_count"] == 2
    assert len(schema["columns"]) == 2