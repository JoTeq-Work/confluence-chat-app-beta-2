import json

def get_spaces_details(spaces_results):    
    spaces = []
    spaces_in_conf = []
    
    for space_result in spaces_results:    
        space_id = space_result['id']
        space_key = space_result['key']
        space_name = space_result['name']        
        spaces.append(space_name)
        space_details = {
            "space_id": space_id,
            "space_key": space_key,
            "space_name": space_name,
        }
        
        spaces_in_conf.append(space_details)
    spaces_in_conf.append({"spaces": spaces})
    
    return spaces_in_conf


def save_to_json_file(data: dict, filename: str):
    with open(f"app/{filename}.json", "w") as outfile:
        # Writing to json file
        json.dump(data, outfile, indent=4, separators=(",", ": "))
        

def read_from_json_file(filename: str):
    with open(f"app/{filename}.json", 'r') as openfile:    
        # Reading from json file
        json_object = json.load(openfile)    
    
    return json_object

def get_space_id(json_object: dict, requested_space: str):
    space_id = None
    for res in json_object[:-1]:
        if res['space_name'] == requested_space:
            space_id = res['space_id']
            return space_id
        

if __name__ == "__main__":
    print()