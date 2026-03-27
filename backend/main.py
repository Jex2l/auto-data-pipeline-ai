from fastapi import FastAPI, UploadFile
import pandas as pd

app = FastAPI()

@app.post("/process")
async def process_file(file: UploadFile):
    try:
        # Read uploaded file
        df = pd.read_csv(file.file)

        # Example cleaning
        cleaned_df = df.dropna()

        return {
            "status": "success",
            "original_shape": {
                "rows": int(df.shape[0]),
                "cols": int(df.shape[1])
            },
            "cleaned_shape": {
                "rows": int(cleaned_df.shape[0]),
                "cols": int(cleaned_df.shape[1])
            },
            "insights": "Data cleaned successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }