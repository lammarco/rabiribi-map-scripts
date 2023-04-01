from os import makedirs as mkdirs
from os import walk
from os.path import join as osjoin
from rb_flip import flip_map, flip_minimap
import diffgenerator as diff

IN_DIR = r'./maps/original/'
OUT_DIR = r'./maps/generated/'

def filepath(path:str, area_id:int):
    return osjoin(path ,f'area{area_id}.map')

def check_paths() -> bool:
    '''returns if there was error'''
    #make sure directories exist
    for dir in (IN_DIR, OUT_DIR):
        mkdirs(dir, exist_ok=True)

    root, dirs, files1 = next(walk(IN_DIR))
    root, dirs, files2 = next(walk(OUT_DIR))
    if len(files1) < 10:
        print(f'input directory is missing files: requires area0-9.map')
    if len(files2) > 0:
        print(f'output directory contains files, please manually empty it')
    return (len(files1) < 10) or (len(files2) > 0)
        
def map_routine(i:int):
    print(f'loading area{i}.map...',end='\t')
    map_data = diff.MapData(filepath(IN_DIR,i))
    flip_map(i, map_data.data_map)
    flip_minimap(map_data.data_minimap)
    map_data.save_to_file  (filepath(OUT_DIR,i))
    print(f'saving area{i}.map...')
            
def main():
    print(f'in_directory = {IN_DIR}\t\tout_directory = {OUT_DIR}')
    print('Note: map 5 (except transitions) and map 8 are unchanged due to map conflicts')
    print()
    
    if check_paths(): return
    for i in range(10): map_routine(i)

    print('applying patch...')
    diff.generate_maps_from_diff_file('patch.txt')
    print('done!')

if __name__ == '__main__':
    main()
    
