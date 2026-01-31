import json 

def read_config(json_file: str) -> dict:
    with open(json_file, "r") as f:
        timer_dict = json.load(f)['timer']
    return timer_dict