########################## DO NOT CHANGE
#layer types
TYPE_TILELAYER = 'tilelayer'
TYPE_OBJLAYER  = 'objectgroup'
#Room layers use different dimentions for flipping
ROOMLAYERS = {'roombg','roomcolor','roomtype'}
ROOM_DIM = (480*32, 192*32)
OBJ_DIM  = (499*32, 202*32)
#n_row = number of rows = number of tiles in column
N_COL, N_ROW  = (500, 200)

#tile id constants
x_flag = 2**31
#y_flag = 2**30
AFD = 452

#rando flags set at the start, rando[x] is event 558's position+x; set value to x position of respective column BEFORE flipping
RANDO1 = 112 * 32
RANDO2 = 113 * 32

X_SOFTLOCK = {0: (301,389)}
TRANSITIONS_EVENTS = (range(161,171), range(200,206), range(227,233), (177, 207))
TRANSITIONS = set( i for r in TRANSITIONS_EVENTS for i in r )

def build_flipmap(pairs: list):
    #pairs[:] = [(str(n1),str(n2)) for n1,n2 in pairs]
    flipmap = dict()
    flipmap.update((n1,str(n2)) for n1,n2 in pairs)
    flipmap.update((n2,str(n1)) for n1,n2 in pairs)
    return flipmap

_obj_map_x = build_flipmap([(195,196)])

def flip_map(map_id:int, map_data:dict):
    for layer in map_data['layers']:
        if map_id != 5 and layer['type'] == TYPE_TILELAYER:
            data = layer['data']
            if layer['name'] == 'collision': swap_collision(data)
            else:                            flip_layer_x(data)
            flip_map_x(data)
            
        elif layer['type'] == TYPE_OBJLAYER:
            if map_id == 5 and layer['name'] != 'event': continue
            dimensions = ROOM_DIM if layer['name'] in ROOMLAYERS else OBJ_DIM
            remove_softlocks(map_id, layer['objects'])
            flip_obj(map_id, layer['objects'], dimensions)

def flip_map_x(tile_list): #tile_list is in 1d array
    for r in range(N_ROW):
        i, i1 = r*N_COL, (r+1)*N_COL
        tile_list[i:i1] = tile_list[i1-1:   :-1] if i <= 0 else  \
                          tile_list[i1-1:i-1:-1]
        
def flip_layer_x(tile_list):
    tile_list[:] = map(flip_tile_x, tile_list)
    
def flip_tile_x(tile: int):
    def flippable_x(tile_id: int):
        return tile_id != 0 and tile_id != AFD
    return tile^x_flag if flippable_x(tile) else tile
    
def flip_collision(tile_list, flip_dict):
    def flip_collision_x(tile: int):
        return flip_dict[tile] if tile in flip_dict else tile
    tile_list[:] = map(flip_collision_x, tile_list)

def flip_obj(map_id:int, obj_list:'list<dict>', dimensions:tuple): 
    for obj in obj_list:
        name = int(obj['name'])
        if map_id == 5 and name not in TRANSITIONS: continue
        x = obj['x']
        obj['x'] = dimensions[0] - x
        
        if name in _obj_map_x: obj['name'] = _obj_map_x[name]
        if name == 420: obj['x'] += ROOM_DIM[0] #main event Rita Saya (HoM) warps 1 screen left
        if name == 307:
            if x == 3680:  obj['x'] +=  7 *32 #rando force forest uprprc
            if x == 10208: obj['x'] += -2 *32 #starting forest uprprc
        if (map_id == 0) and (obj['y'] <= (42*32)) and (name >= 5000): #setting events at the start of rando
            if(x == RANDO1): obj['x'] += 2 *32
            if(x == RANDO2): obj['x'] += 4 *32
               
def remove_softlocks(map_id:int, obj_list:'list<dict>'):
    def check_x_softlock(o:dict):
        return not (map_id in X_SOFTLOCK and int(o['name']) in X_SOFTLOCK[map_id])
    obj_list[:] = [o for o in obj_list if check_x_softlock(o)]

    
def swap_collision(data):
    d = data.copy()
    x = build_collision_flip(data)
    flip_collision(data,x)

def build_collision_flip(tiles):
    offset = min(filter(lambda t: t != 0, tiles)) - 1
    flip_direction = not(offset % 2)
    collision_ids  = set(offset+i for i in range(2,14))
    collision_ids.update(offset+i for i in (16,17))

    def flip_col(i:int): return i+1 if i%2 ^ flip_direction else i-1
    collision_flipx = {i:flip_col(i) for i in collision_ids}
    
    return collision_flipx
