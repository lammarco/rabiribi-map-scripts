import sqlite3
from os.path import join as osjoin
from collections import defaultdict
from diffgenerator import MapData, map_coords

IN_DIR = r'./maps/original/' 
LOCATIONS_DB = './rbrb_locations.db'
MIRROR_MODE = True

#DO NOT CHANGE
WIDTH = 500
AREA_MAP = {
              0:'Southern Woodland',
              1:'Western Coast',
              2:'Island Core',
              3:'Northern Tundra',
              4:'Eastern Highlands',
              5:'Rabi Rabi Town',
              6:'Plurkwood',
              7:'Subterranean Area',
              8:'Warp Destination',
              9:'System Interior'
            }
PROGRESSION_IDS = {1,2,3,4,10,
                   11,16,17,18,19,
                   28,29,30,31,33,35}

############################loading################################
def d2l(layer:list):
    '''from wcko's diffgenerator, also found in mirror-mode branch'''
    l = [layer[i::200] for i in range(200)]
    return [t for l2 in l for t in l2]

def input_maps():
    return _process_input(
        input('provide a string of map numbers from 0-9 to load; ex: 013\n>')
        )
def _process_input(file_numbers:str = '') -> set:
    'provide a string of map numbers from 0-9; ex:"013" for 0,1,3'
    if file_numbers == '': return set(i for i in range(10))
    try:
        assert file_numbers.isdigit(), f'non-digit found: {file_numbers}'
        areas = set(int(n) for n in file_numbers)
        return areas
    except Exception as e: print(e)
    return set()

def _load_file(area_id:int):
    return MapData( osjoin(IN_DIR ,f'area{area_id}.map') )

def map_id2name(map_id:int) ->str:
    return f'{map_id} {AREA_MAP[map_id]}'

def filter_layer(filter_function, layer:list) -> list:
    '''returns list of indices, filterfunction should take tuple of (index, value)'''
    return filter(filter_function, enumerate(layer))

def _check_item(t:tuple) -> bool:
    '''returns True for items 1-95 (non-potions/atk ups)'''
    i, x = t
    return (x > 0) and (x <= 95)

def _check_egg(t:tuple) -> bool:
    '''returns True for event 250 (easter egg)'''
    i, x = t
    return x == 250

def extract_map(map_id:int):
    '''Process map data into layers (leaving only items and event)'''
    con = sqlite3.connect(LOCATIONS_DB,uri=True)
    cur = con.cursor()
    def parse_location(x,y):
        if MIRROR_MODE: x = WIDTH - x - 1
        cur.execute('''SELECT NAME FROM ITEM_LOCATIONS
                       WHERE MAP_ID=? AND X=? AND Y=?''',
                       (map_id,x,y))
        result = cur.fetchone()
        return result[0] if result is not None else None

    def parse_name(item_id):
        ##Only for items 1-95. Not for eggs/250s.
        cur.execute('''SELECT NAME FROM ITEM_LOCATIONS
                       WHERE ITEM_ID=?''', (item_id,))
        result = cur.fetchone()
        return result[0] if result is not None else None

    map_data = _load_file(map_id)
    items, events = (map_data.data_map[s] for s in ('items','event'))
    out = {'items':dict(),'eggs':set()}
    #items    
    for i, item in filter_layer(_check_item,items):
        name = parse_name(item)
        x,y = map_coords(i)
        location = parse_location(x,y)
        if name is None or location is None: continue
        out['items'][item] = {
                    'id':item,'name':name,
                    'map':map_id,'location':location}
    #egg    
    for i,egg in filter_layer(_check_egg,events):
        x,y = map_coords(i)
        loc = parse_location(x,y)
        if loc is not None: out['eggs'].add(loc)
    con.close()
    return out

def load():
    nums = input_maps()
    if len(nums) == 0: return (dict(),tuple())
    
    data = {'items':dict(),'eggs':defaultdict(set)}
    maps = list()
    for n in nums:
        try:
            map_data = extract_map(n)
            data['items'].update(map_data['items'])
            data['eggs'][n].update(map_data['eggs'])
            maps.append(n)
        except Exception as e:
            print(type(e),e)
            print(f'Failed to load: area{n}.json')
    return data,maps

#################################process/search############################
def item_list(maps_data:dict,id_filter:set = None,map_filter:set = None):
    if map_filter is None: map_filter = {i for i in range(10)}
    if id_filter is None: id_filter = {i for i in range(1,96)}
    items = [i for i in maps_data['items'].values()
                if i['id'] in id_filter and i['map'] in map_filter]
    return items

def print_items(items:list,sort_key="id"):
    try:
        assert sort_key in {'id','name','map','location'},\
               "sort_key is not one of these: 'id','name','map','location'"
    except Exception as e: print(e); return
    items.sort(key=lambda d: d[sort_key])
    for item in items:
        print(f"ID:{item['id']:<3} "+
              f"Name:{item['name']:<15} "+
              f"Map:{map_id2name(item['map'])}")
        print(' '*7+f"Location:{item['location']}")
        print()
        
def progression(maps_data:dict,map_filter:set = None,sort_key='id'):
    items = item_list(maps_data,id_filter=PROGRESSION_IDS,map_filter=map_filter)
    print_items(items,sort_key)

def eggs(maps_data:dict,map_filter:set = None):
    maps = set(maps_data['eggs'].keys())
    if map_filter is not None:
        maps = maps.intersection(map_filter)
    for map_id in maps:
        print(f"Map:{map_id2name(map_id):<20}"+
              f" Egg Count={len(maps_data['eggs'][map_id])}")
        for egg in maps_data['eggs'][map_id]: print(' '*6 + egg)
        print()

def item(items:dict):
    item_input = input('type in the item id\n>')
    try:
        item_id = int(item_input)
        if not (item_id > 0 and item_id <= 95):
            print(f'Item {item_id} is not in the range (0,95]')
            return
        if item_id not in items.keys():
            print(f'Item {item_id} not found in the loaded maps.')
            return
        print_items([items[item_id]])
    except Exception as e:
        print('unknown input:',item_input)
        print(type(e),e)

def routine(option:str, maps_data:dict):
    map_filter = _process_input(input('provide a string of map numbers from 0-9 to search in; ex: 013\n>'))
    if option == 'eggs': eggs(maps_data,map_filter)
    if option == 'progression': progression(maps_data,map_filter)
    if option == 'items': item(maps_data['items'])

def main():
    t=None
    maps=set()
    def load_routine():
        nonlocal t,maps
        t,maps= load()
    user_input = ''
    load_routine()
    while(user_input.lower() != 'quit'):
        print()
        print('#'*20)
        print(f'{len(maps)} maps loaded: {maps}')
        if len(maps) == 0:
            input('Make sure the mapfiles are in the correct directory.\n(Exit the program or Press enter to reload)')
            load_routine()
            continue
        #######
        user_input = input('Which would you like to search for? \n(type in the number or the name; e.g. "1" or "eggs"):'
                           +'\n1. eggs'
                           +'\n2. progression (which shows items'
                           +'\n'+' '*8 + '1,2,3,4,10,11,16,17,18,19,'
                           +'\n'+' '*8 + '28,29,30,31,33,35)'
                           +'\n3. item'
                           +'\n4. re"load" the mapfiles'
                           +'\n5. "quit" this program'
                           +'\n'+'>').strip()
        if user_input == '1' or user_input.lower() == 'eggs':
            routine('eggs',t)
        elif user_input == '2' or user_input.lower() == 'progression':
            routine('progression',t)
        elif user_input == '3' or user_input.lower() == 'item':
            routine('item',t)
        elif user_input == '4' or user_input.lower() == 'load':
            load_routine()
        elif user_input == '5' or user_input.lower() == 'quit':
            return
        else: print('Unrecognized input: ' + user_input)

#try:                         
main()
#except Exception as e:
#    print('Fatal Error: ',type(e),e)
#    input('Press enter/return to exit.')
