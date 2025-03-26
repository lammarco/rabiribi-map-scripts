import sqlite3
from os.path import join as osjoin
from collections import defaultdict, namedtuple
from diffgenerator import MapData, map_coords, map_index

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

########################### Transitions Stuff ################################
TRIGGER_MAP = {
                200 : 227,
                201 : 228,
                202 : 229,
                203 : 230,
                204 : 231,
                205 : 232,
                206 : 176,
                207 : 177
}

TransitionInfo    = namedtuple( 'TransitionInfo', ['map_id','direction', 'trigger_x', 'target_x', 'mapid_x', 'y', 'name'] ) # tuple format, same as query schema

TransitionTrigger = namedtuple( 'TransitionTrigger', ['target_map','trigger_id','direction'] ) #tuple as key, name as value
TransitionTarget  = namedtuple( 'TransitionTarget' , ['map_id','target_id','direction'] ) #tuple as key, name as value

def trigger2target( trigger:TransitionTrigger ) -> TransitionTarget:
    target_map, trigger_id, direction = trigger
    return TransitionTarget( target_map, TRIGGER_MAP[trigger_id], not direction)

# for compact/non-duplicate view    
#def format_transition( trigger_name:str, target_name:str, direction:bool ) -> str:
#    if direction:
#        target_name, trigger_name = trigger_name, target_name
#    return f'{trigger_name} <-> {target_name}'

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
    
def _check_transition( t:tuple, positions:set) -> bool:
    '''returns True if object is at one of positions for transitions'''
    i,x = t
    return map_coords(i) in positions
    
def _get_transitions( map_id:int, cur ) -> set[TransitionInfo]:
    cur.execute('''SELECT MAP_ID,DIRECTION,TRIGGER_X,TARGET_X,MAPID_X,Y,NAME
                    FROM TRANSITIONS WHERE MAP_ID=?''', (map_id,))
    transitions = set()
    for result in cur:
        transitions.add( TransitionInfo( *result ) )
    return transitions

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
    out = {
        'items':dict(),
        'eggs':set(),
        'transition_triggers':dict(),
        'transition_targets':dict()
    }
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
        
    #transition
    for transition in _get_transitions( map_id, cur ):
        transition_xs = ( transition.mapid_x, transition.trigger_x, transition.target_x ) #TODO: improve readability
        mapid_i, trigger_i, target_i = ( map_index( x, transition.y ) for x in transition_xs)
        
        assert all( i < len(events) for i in (mapid_i, trigger_i, target_i) ) , f'Invalid transition position: {transition}'
        
        target_map = events[mapid_i] - 161
        trigger_id = events[trigger_i]
        target_id = events[target_i]
        
        try:
            assert target_map >= 0 and target_map < 10, f'Invalid transition target map: {transition}'
            assert trigger_id in TRIGGER_MAP        , f'Invalid transition trigger: {transition}'
            assert target_id in TRIGGER_MAP.values(), f'Invalid transition target: {transition}'
        except AssertionError as e:
            print( e )
            continue
        
        d = transition.direction == 'L'
        trigger = TransitionTrigger( target_map, trigger_id, d )
        target  = TransitionTarget ( map_id,     target_id,  d )
        out[ 'transition_triggers' ][ trigger ] = transition.name
        out[ 'transition_targets'  ][ target ]  = transition.name
    
    con.close()
    return out

def load():
    nums = input_maps()
    if len(nums) == 0: return (dict(),tuple())
    
    data = {'items':dict(),'eggs':defaultdict(set), 'transition_triggers':dict(), 'transition_targets':dict()}
    maps = list()
    for n in nums:
        try:
            map_data = extract_map(n)
            data['items'].update(map_data['items'])
            data['eggs'][n].update(map_data['eggs'])
            data['transition_triggers'].update( map_data['transition_triggers'] )
            data['transition_targets'] .update( map_data['transition_targets']  )
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

def items(map_data:dict, map_filter:set = None):
    item_input = input('type in the item ids, separated by commas: ex. "1,5"\n>')
    try:
        ids = [i.strip() for i in item_input.split(',')]
        for i, x in enumerate(ids):
            assert x.isdigit(), f'not a number: {x} at {i}'
            x = int(x)
            assert (x > 0) and (x <= 95), f'Item {x} is not in the range [1,95]'
            ids[i] = x
    except Exception as e:
        print(e)
        print()
        return
    items = item_list(map_data, set(ids), map_filter)
    print_items(items, sort_key = 'map')
    
def transitions(map_data:dict, map_filter:set = None):
    triggers = map_data['transition_triggers']
    targets  = map_data['transition_targets']
    
    connections: dict[int,set] = defaultdict(set)
    #pair triggers with targets
    for trigger, trigger_name in triggers.items():
        target = trigger2target( trigger )
        
        if (trigger.target_map not in map_filter) or (target not in targets): 
            continue
        
        #transition_connection = format_transition( trigger_name, targets[target], trigger.direction ) #for compact/non-duplicate view    
        
        connections[target.map_id].add( f'{targets[target]:<27} <-> {trigger_name:<27}' )
            
    for n in sorted(map_filter):
        if n not in connections: continue
        print(  f'Map {n}', '\n\t'.join( sorted(connections[n]) ), sep='\n\t' )
    
    print()

def routine(option:str, maps_data:dict):
    map_filter = _process_input(input('provide a string of map numbers from 0-9 to search in; ex: 013\n>'))
    if option == 'eggs': eggs(maps_data,map_filter)
    if option == 'progression': progression(maps_data,map_filter)
    if option == 'items': items(maps_data, map_filter)
    if option == 'transitions': transitions(maps_data, map_filter)

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
                           +'\n3. items (using item id)'
                           +'\n4. transitions'
                           +'\n5. re"load" the mapfiles'
                           +'\n6. "quit" this program'
                           +'\n'+'>').strip()
        if user_input == '1' or user_input.lower() == 'eggs':
            routine('eggs',t)
        elif user_input == '2' or user_input.lower() == 'progression':
            routine('progression',t)
        elif user_input == '3' or user_input.lower() == 'items':
            routine('items',t)
        elif user_input == '4' or user_input.lower() == 'transitions':
            routine('transitions',t)
        elif user_input == '5' or user_input.lower() == 'load':
            load_routine()
        elif user_input == '6' or user_input.lower() == 'quit':
            return
        else: print('Unrecognized input: ' + user_input)

#try:                         
main()
#except Exception as e:
#    print('Fatal Error: ',type(e),e)
#    input('Press enter/return to exit.')
