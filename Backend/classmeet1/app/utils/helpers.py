import pandas as pd
from fastapi.responses import FileResponse
from datetime import datetime

def export_to_csv(data: list, filename: str):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return FileResponse(filename, media_type="text/csv", filename=filename)