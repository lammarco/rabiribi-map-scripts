from os import makedirs as mkdirs
from os.path import join as osjoin
from rb_flip import flip_map, flip_minimap
import diffgenerator as diff

IN_DIR = r'./maps/original/'
OUT_DIR = r'./maps/generated/'

def filepath(path:str, area_id:int):
    return osjoin(path ,f'area{area_id}.map')
    
def map_routine(i:int):
    print(f'loading area{i}.map...',end='\t')
    map_data = diff.MapData(filepath(IN_DIR,i))
    if i != 8:
        flip_map(i, map_data.data_map)
        flip_minimap(map_data.data_minimap)
    map_data.save_to_file  (filepath(OUT_DIR,i))
    print(f'saving area{i}.map...')
            
def main():
    print(f'in_directory = {IN_DIR}\t\tout_directory = {OUT_DIR}')
    print('Note: map 5 (except transitions) and map 8 are unchanged due to map conflicts')
    print()
    
    #make sure directories exist
    for dir in (IN_DIR, OUT_DIR):
        mkdirs(dir, exist_ok=True)
        
    for i in range(10): map_routine(i)

if __name__ == '__main__':
    main()
    #diff.generate_maps_from_diff_file('patch.txt')
