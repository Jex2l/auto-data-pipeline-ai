from __future__ import annotations

import base64
from io import BytesIO

import matplotlib.pyplot as plt


def execute_query(df, code):
    local_vars = {
        "df": df,
        "plt": plt,
        "result": None,
    }

    try:
        plt.close("all")

        def safe_exec(code, local_vars):
            try:
                # Remove markdown formatting if present
                code = code.strip()

                if code.startswith("```"):
                    code = code.split("```")[1]

                exec(code, {}, local_vars)
                return None
            except Exception as e:
                return str(e)

        error = safe_exec(code, local_vars)

        if error:
            return f"Error in generated code: {error}", None
        result = local_vars.get("result")

        if result is None:
            # fallback: try last variable
            result = next(
                (v for k, v in local_vars.items() if k != "df"),
                "No result generated"
            )

        image_base64 = None
        if plt.get_fignums():
            buf = BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode("utf-8")
            buf.close()

        plt.close("all")
        return result, image_base64

    except Exception as exc:
        plt.close("all")
        return str(exc), None