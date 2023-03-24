########################## DO NOT CHANGE
#layer types
TYPE_TILELAYER = 'tilelayer'
TYPE_OBJLAYER  = 'objectgroup'
#Room layers use different dimentions for flipping
ROOMLAYERS = {'roombg','roomcolor','roomtype'}
ROOM_DIM = (480*32, 192*32)
#n_row = number of tile in a row = number of columns; used for area5 (only flip x, not y)
N_ROW, N_COL  = (500, 200)
OBJ_DIM = ( 499*32, 202*32 )
#tile id constants
x_flag = 2**31
#y_flag = 2**30
AFD = 452
#rando flags set at the start, rando[x] is event 558's position+x; set value to x position of respective column BEFORE flipping
RANDO1 = 3584
RANDO2 = 3616

TRANSITION_EVENTS = set( str(i) for r in (range(161,171), range(200,206), range(227,233), (177, 207)) for i in r )

def build_flipmap(pairs: list):
    pairs[:] = [(str(n1),str(n2)) for n1,n2 in pairs]
    flipmap = dict()
    flipmap.update((n1,n2) for n1,n2 in pairs)
    flipmap.update((n2,n1) for n1,n2 in pairs)
    return flipmap

_obj_map_x = build_flipmap([(195,196)])

def flip_map(map_id:int, map_data:dict):
    map_lambda = flip_map_x
    tile_lambda = flip_tile_x
    
    for layer in map_data['layers']:
        if map_id != 5 and layer['type'] == TYPE_TILELAYER:
            data = layer['data']
            if layer['name'] == 'collision':
                swap_collision(data)
            else:
                tile_lambda(data)
            map_lambda(data)
            
        if layer['type'] == TYPE_OBJLAYER:
            if map_id == 5 and layer['name'] == 'items': continue
            dimensions = ROOM_DIM if layer['name'] in ROOMLAYERS else OBJ_DIM
            fix_obj(map_id, layer['objects'])
            flip_obj(map_id, layer['objects'], dimensions)

def fix_obj(map_id:int, obj_list:'list<dict>'):
    def check_x_softlock(o:dict): return not (map_id == 0 and o['name'] in ('301','389'))
    obj_list[:] = [o for o in obj_list if check_x_softlock(o)]
    
def flip_tile_x(tile_list): tile_list[:] = map(lambda tile: tile if tile == 0 or tile == AFD else tile^x_flag, tile_list)
def flip_collision(tile_list, flip_dict): tile_list[:] = map(lambda tile: flip_dict[tile] if tile in flip_dict else tile, tile_list)

def flip_obj(map_id:int, obj_list:'list<dict>', dimensions:tuple): 
    for obj in obj_list:
        name = obj['name']
        if map_id == 5 and name not in TRANSITION_EVENTS: continue
        x = obj['x']
        obj['x'] = dimensions[0] - x
        if name == '420': obj['x'] += ROOM_DIM[0] #main event Rita Saya (HoM) warps 1 screen left
        if name == '307':
            if x == 3680:  obj['x'] +=  7 *32 #rando force forest uprprc
            if x == 10208: obj['x'] += -2 *32 #starting forest uprprc
        if name in _obj_map_x: obj['name'] = _obj_map_x[name]
        if (map_id == 0) and (obj['y'] <= 1344) and (int(name) >= 5000): #setting events at the start of rando
            if(x == RANDO1): obj['x'] += 2 *32
            if(x == RANDO2): obj['x'] += 4 *32

def build_collision_flip(tiles):
    col_offset = min(filter(lambda t: t != 0, tiles)) - 1
    
    col_offset_flip = not(col_offset % 2)
    collision_flipx = {i:(i+1 if i%2 ^ col_offset_flip else i-1) for i in range(col_offset+2,col_offset+14)}
    collision_flipx.update({col_offset+16:col_offset+17, col_offset+17:col_offset+16})
    
    return collision_flipx
    
def swap_collision(data):
    d = data.copy()
    x = build_collision_flip(data)
    flip_collision(data,x)

def flip_map_x(tile_list): 
    for i in range(N_COL):
        j, j1 = i*N_ROW, (i+1)*N_ROW
        tile_list[j:j1] = tile_list[j1-1::-1] if j == 0 else  \
                          tile_list[j1-1:j-1:-1]
