import pandas as pd

from agents.cleaning_agent import clean_dataframe


def test_clean_dataframe_removes_duplicates_and_normalizes_columns():
    df = pd.DataFrame(
        {
            "User Name ": [" Alice ", "Bob", "Bob"],
            "Age": ["25", "30", "30"],
        }
    )

    cleaned, report = clean_dataframe(df)

    assert "user_name" in cleaned.columns
    assert cleaned.shape[0] == 2
    assert report["duplicates_removed"] == 1