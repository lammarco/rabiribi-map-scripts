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
#collision cannot be flipped; manually replace via map/dict
debug_col = False
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
#_obj_map_y = build_flipmap([(198,199),(103,105),(80,81)])

def flip_map(map_id:int, map_data:dict, flip_x:bool = True, flip_y:bool = False):
    #map_lambda  = flip_map_x if not flip_y else flip_map_xy
    #tile_lambda = flip_tile_x if not flip_y else flip_tile_xy
    map_lambda = flip_map_x
    tile_lambda = flip_tile_x
    
    for layer in map_data['layers']:
        if map_id != 5 and layer['type'] == TYPE_TILELAYER:
            data = layer['data']
            if layer['name'] == 'collision':
                swap_collision(data, flip_x, flip_y)
            else:
                tile_lambda(data)
            map_lambda(data)
            
        if layer['type'] == TYPE_OBJLAYER:
            if map_id == 5 and layer['name'] == 'items': continue
            dimensions = ROOM_DIM if layer['name'] in ROOMLAYERS else OBJ_DIM
            fix_obj(map_id, layer['objects'], flip_x = flip_x, flip_y = flip_y)
            flip_obj(map_id, layer['objects'], dimensions, flip_x = flip_x, flip_y = flip_y)

def fix_obj(map_id:int, obj_list:'list<dict>', flip_x, flip_y):
    if not flip_x: return
    def check_x_softlock(o:dict): return not (map_id == 0 and o['name'] in ('301','389'))
    #def check_y_softlock(o:dict): return True
    obj_list[:] = [o for o in obj_list if (not flip_x or check_x_softlock(o))]# and (not flip_y or check_y_softlock(o))
            
def flip_tile_x(tile_list): tile_list[:] = map(lambda tile: tile if tile == 0 or tile == AFD else tile^x_flag, tile_list)
def flip_tile_y(tile_list): tile_list[:] = map(lambda tile: tile if tile == 0 or tile == AFD else tile^y_flag, tile_list)
def flip_tile_xy(tile_list): flip_tile_x(tile_list); flip_tile_y(tile_list)
def flip_collision(tile_list, flip_dict): tile_list[:] = map(lambda tile: flip_dict[tile] if tile in flip_dict else tile, tile_list)

def flip_obj(map_id:int, obj_list:'list<dict>', dimensions:tuple, flip_x:bool = True, flip_y:bool = True): 
    for obj in obj_list:
        name = obj['name']
        if map_id == 5 and name not in TRANSITION_EVENTS: continue
        if flip_x:
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
        if map_id != 5 and flip_y:
            obj['y'] = dimensions[1] - obj['y']
            if name in _obj_map_y: obj['name'] = _obj_map_y[name]

def build_collision_flip(tiles):
    col_offset = min(filter(lambda t: t != 0, tiles)) - 1
    if debug_col: print('col offset =', col_offset,end='\t')
    
    col_offset_flip = not(col_offset % 2)
    collision_flipx = {i:(i+1 if i%2 ^ col_offset_flip else i-1) for i in range(col_offset+2,col_offset+14)}
    collision_flipy = {i:col_offset+1 for i in range(col_offset+2,col_offset+14)}
    collision_flipx.update({col_offset+16:col_offset+17, col_offset+17:col_offset+16})
    collision_flipy.update({col_offset+14:col_offset+15, col_offset+15:col_offset+14})

    return collision_flipx, collision_flipy
    
def swap_collision(data, flip_x:bool = True, flip_y:bool = True):
    d = data.copy()
    x,y = build_collision_flip(data)
    flip_collision(data,x)
    if debug_col: print(sum( int(d[i] != data[i]) for i in range(len(d))), 'collisions changed',end='\t') #check how many changed
    if flip_y: flip_collision(data,y)

def flip_map_x(tile_list): 
    for i in range(N_COL):
        j, j1 = i*N_ROW, (i+1)*N_ROW
        tile_list[j:j1] = tile_list[j1-1::-1] if j == 0 else  \
                          tile_list[j1-1:j-1:-1]
    
def flip_map_xy(tile_list):
    tile_list[:] = tile_list[3*N_ROW:] + tile_list[:3*N_ROW] #adjust for 3 bottom row
    tile_list.reverse()
