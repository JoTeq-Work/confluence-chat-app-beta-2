import json

def get_spaces_details(spaces_results):    
    spaces = []
    spaces_in_conf = []
    
    for space_result in spaces_results:    
        space_name = space_result['name']
        space_id = space_result['id']
        spaces.append(space_name)
        space_details = {
            "space_id": space_id,
            "space_name": space_name,
        }
        
        spaces_in_conf.append(space_details)
    spaces_in_conf.append({"spaces": spaces})
    
    return spaces_in_conf


def save_to_json_file(data: dict, filename: str):
    with open(f"{filename}.json", "w") as outfile:
        # Writing to json file
        json.dump(data, outfile)
        

def read_from_json_file(filename: str):
    with open(f"{filename}.json", 'r') as openfile:    
        # Reading from json file
        json_object = json.load(openfile)    
    
    return json_object

def get_space_id(json_object: dict, requested_space: str):
    space_id = None
    for res in json_object[:-1]:
        if res['space_name'] == requested_space:
            space_id = res['space_id']
            return space_id