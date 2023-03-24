import json
from rb_flip import flip_map
from diffgenerator import generate_maps_from_diff_file

JSON_IN_DIR = r'./maps/original/'
JSON_OUT_DIR = r'./maps/out/'

def load_file(file_number:int):
    filename = f'{JSON_IN_DIR}area{file_number}.json'
    print(f'loading: area{file_number}.json',end='\t')
    with open(filename,'r') as f:
        return json.load(f)
        
def save_file(file_number:int, map_data:dict):
    filename = f'{JSON_OUT_DIR}area{file_number}.json'
    print(f'save: {filename}')
    with open(filename,'w') as f:
        return json.dump(map_data,f)

    
def map_routine(i:int):
    map_data = load_file(i)

    if i != 8:
        flip_map(i, map_data)
    

    save_file(i,map_data)
            
def main():
    print(f'in_directory = {JSON_IN_DIR}\t\tout_directory = {JSON_OUT_DIR}')
    print('Note: map 5 (except tarnsitions) and map 8 are unchanged due to map conflicts')
    print()
    
    for i in range(10): map_routine(i)

if __name__ == '__main__':
    main()
    #generate_maps_from_diff_file('patch.txt')
