import json,re,sqlite3
from collections import defaultdict
LOCATIONS_DB = 'rbrb_locations.db'
JSON_MAPS_DIR = r'./s2_editable_maps/'
############################loading################################
def _process_input(file_numbers:str = '') -> list:
    'provide a string of map numbers from 0-9; ex:"013" for 0,1,3'
    if file_numbers == '': return [i for i in range(10)]
    try:
        assert type(file_numbers) is str, 'only strings accepted'
        file_numbers = list(set(int(n) for n in file_numbers))
        assert all(n >= 0 and n <= 9 for n in file_numbers), f'only numbers from 0-9: {n}'
        return file_numbers
    except Exception as e:
        print('unknown input: ' + file_numbers)
        print(type(e),e)
    return []

def _load_file(file_number:int):
    filename = JSON_MAPS_DIR + f'area{file_number}.json'
    print(f'loading: {filename}')
    with open(filename,'r') as f:
        return json.load(f)

def _check_item(obj:dict) -> bool:
    '''returns True for items 1-95 (non-potions/atk ups)'''
    try:
        name = int(obj['name'])
        return (name > 0 and name <= 95)
    except:
        return False

def _check_egg(obj:dict) -> bool:
    '''returns True for event 250 (easter egg)'''
    try:
        name = int(obj['name'])
        return name == 250
    except:
        return False

def map_id2name(map_id:int) ->str:
    id_map = {
              0:'Southern Woodland',
              1:'Western Coast',
              2:'Island Core',
              3:'Northern Tundra',
              4:'Eastern Highlands',
              5:'Rabi Rabi Town',
              6:'Plurkwood',
              7:'Subterranean Area',
              8:'Warp Destination',
              9:'System Interior'}
    return f'{map_id} {id_map[map_id]}'

def id_str2int(id_str):
    try:
        return int(id_str)
    except:
        #error
        return 0

def _load2layer(map_id:int,mapfile_data:dict):
    '''Process map data into layers (leaving only items and event)'''
    con = sqlite3.connect(LOCATIONS_DB,uri=True)
    cur = con.cursor()
    out = {'items':dict(),'eggs':defaultdict(set)}

    def parse_location(x,y):
        cur.execute('''SELECT NAME FROM ITEM_LOCATIONS
                       WHERE MAP_ID=? AND X=? AND Y=?''',
                       (map_id,x/32,y/32))
        result = cur.fetchone()
        return result[0] if result is not None else None

    def parse_name(item_id):
        ##Only for items 1-95. Not for eggs/250s.
        cur.execute('''SELECT NAME FROM ITEM_LOCATIONS
                       WHERE ITEM_ID=?''', (item_id,))
        result = cur.fetchone()
        return result[0] if result is not None else None

    for layer in mapfile_data['layers']:
        if layer['name'] == 'items':
            items = layer['objects']
        if layer['name'] == 'event':
            events = layer['objects'] 
        
    for item in filter(_check_item,items):
            id_int = id_str2int(item['name'])
            name = parse_name(item['name'])
            location = parse_location(item['x'],item['y'])
            if id_int != 0 and name is not None and location is not None:
                out['items'][id_int] = {
                    'id':id_int,'name':name,
                    'map':map_id,'location':location}
    for egg in filter(_check_egg,events):
            out['eggs'][map_id].add(parse_location(egg['x'],egg['y']))
    con.close()
    return out

def load():
    nums = _process_input(input('provide a string of map numbers from 0-9 to load; ex: 013\n>'))
    if len(nums) == 0: return (dict(),0)
    
    data = defaultdict(dict)
    maps = list()
    for n in nums:
        try:
            map_data = _load2layer(n,_load_file(n))
            for k,v in map_data.items():
                data[k].update(v)
            maps.append(n)
        except Exception as e:
            print(type(e),e)
            print(f'Failed to load: area{n}.json')
    return (data,maps)

#################################process/search############################
def item_list(maps_data:dict,id_filter:set = None,map_filter:set = None):
    if map_filter is None: map_filter = {i for i in range(10)}
    if id_filter is None: id_filter = {i for i in range(1,96)}
    items = [i for i in maps_data['items'].values()
                if i['id'] in id_filter and i['map'] in map_filter]
    return items

def print_items(items:list,sort_key="id"):
    assert sort_key in {'id','name','map','location'},\
           "sort_key is not one of these: 'id','name','map','location'"
    if sort_key != "":
        items.sort(key=lambda d: d[sort_key])
    for item in items:
        print(f"ID:{item['id']:<3} "+
              f"Name:{item['name']:<15} "+
              f"Map:{map_id2name(item['map'])}")
        print(' '*7+f"Location:{item['location']}")
        print()
        
def progression_locations(maps_data:dict,map_filter:set = None):
    progression_ids = {1,2,3,4,10,
                       11,16,17,18,19,
                       28,29,30,31,33,35}
    return item_list(maps_data,id_filter=progression_ids,map_filter=map_filter)

def progression(maps_data:dict,map_filter:set = None,sort_key='id'):
    print_items(progression_locations(maps_data,map_filter),sort_key)

def eggs(maps_data:dict,map_filter:set = None):
    maps = set(maps_data['eggs'].keys())
    if map_filter is not None:
        maps = maps.intersection(map_filter)
    for map_id in maps:
        print(f"Map:{map_id2name(map_id):<20}"+
              f" Egg Count={len(maps_data['eggs'][map_id])}")
        for egg in maps_data['eggs'][map_id]: print(' '*6 + egg)
        print()

def routine(option:str, maps_data:dict):
    map_filter = _process_input(input('provide a string of map numbers from 0-9 to search in; ex: 013\n>'))
    if len(map_filter) == 0: return
    if option == 'eggs': eggs(maps_data,map_filter)
    if option == 'progression': progression(maps_data,map_filter)

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
                           +'\n'+'>')
        if user_input == '1' or user_input.lower() == 'eggs':
            routine('eggs',t)
        elif user_input == '2' or user_input.lower() == 'progression':
            routine('progression',t)
        elif user_input == '3' or user_input.lower() == 'item':
            item(t['items'])
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
