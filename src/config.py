import json 

def read_config(json_file: str) -> dict:
    with open(json_file, "r") as f:
        configs = json.load(f)
        timer_dict = configs['timer']
    return timer_dict