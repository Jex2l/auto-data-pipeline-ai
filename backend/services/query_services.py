import matplotlib.pyplot as plt
import base64
from io import BytesIO


def execute_query(df, code):
    local_vars = {"df": df, "plt": plt}

    try:
        exec(code, {}, local_vars)

        result = local_vars.get("result", "No result")

        # Capture plot
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        image_base64 = base64.b64encode(buf.read()).decode()

        plt.close()

        return result, image_base64

    except Exception as e:
        return str(e), None