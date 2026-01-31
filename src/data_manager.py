from datetime import datetime

def add_row_to_csv(filename: str, duration_sec: int):
    with open(filename, "a") as f:
        f.write(f"{datetime.now().strftime("%d/%m/%Y,%H:%M:%S")},{duration_sec}")