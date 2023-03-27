from diffgenerator import map_coords, map_index

SHOW_WARNINGS = True

######################### DO NOT CHANGE
#Room layers use different dimentions for flipping
ROOMLAYERS = {'roombg','roomcolor','roomtype'}
MINIMAP_DIM = (24, 17)
ROOM_DIM = (19,10)
WIDTH, HEIGHT  = (500, 200) #y_row = number of rows = number of tiles in column = for y pos

#tile id constants
x_flag = 2**31
#y_flag = 2**30
AFD = 452

#rando flags set at the start, event 558's position BEFORE flipping
RANDO_FLAGS_X = 111

X_SOFTLOCK = {0: (301,389)}
TRANSITIONS_EVENTS = (range(161,171), range(200,206), range(227,233), (177, 207))
TRANSITIONS = set( i for r in TRANSITIONS_EVENTS for i in r )

def offset_307(i:int):
    x = i // HEIGHT
    if x == 115: return i-map_index(7,0) #rando force forest uprprc
    if x == 319: return i+map_index(2,0) #starting forest uprprc
    return i

EVENT_OFFSETS = {420: lambda i: i - map_index(ROOM_DIM[0],0) #main event Rita Saya (HoM) warps 1 screen left
                ,307: offset_307}       

def build_swapmap(pairs: list):
    #pairs[:] = [(str(n1),str(n2)) for n1,n2 in pairs]
    swapmap = dict()
    swapmap.update((n1,n2) for n1,n2 in pairs)
    swapmap.update((n2,n1) for n1,n2 in pairs)
    return swapmap

EVENT_MAP_X = build_swapmap( [(195,196)] )

############## main flip function ##################
def flip_map(map_id:int, layers:dict):
    if map_id == 5: #only flip transitions for town
        l = layers['event']
        transpose(l, 200)
        flip_transitions(l)
        transpose(l, 500)
        return
    if map_id == 0:
        l = layers['event']
        transpose(l, 200)
        flip_rando(layers['event'])
        transpose(l, 500)

    for layer,data in layers.items():
        transpose(data, 200)
        if   layer == 'items':     pass
        elif layer == 'event':     flip_events(map_id, data)
        elif layer == 'collision': flip_collision(data, build_collision_flip(data))
        else:                      flip_layer_x(data)
        flip_map_x(data)
        transpose(data, 500)

def transpose(tile_list, spacing):
    '''reorder data, from wcko87/rbrb-map-converter'''
    l = [tile_list[i::spacing] for i in range(spacing)]
    tile_list[:] = [t for x in l for t in x]

def flip_map_x(tile_list:list):
    for r in range(HEIGHT): flip_row(tile_list, r, WIDTH, HEIGHT)

def flip_row(l:list, r:int, w:int, h:int):
    '''l = 1d array of 2d map, r = i-th row, w = width, h = height'''
    f, b = r*WIDTH, (r+1)*WIDTH
    l[f:b] = l[b-1:   :-1] if r == 0 else \
             l[b-1:f-1:-1]
     
def flip_layer_x(tile_list):
    '''flip individual tiles <- apply to entire layer'''
    tile_list[:] = map(flip_tile_x, tile_list)

# flipping individual tiles      
def flip_tile_x(tile: int):
    def flippable(tile_id: int):
        return tile_id != 0 and tile_id != AFD
    #def flip_y(tile: int):
    #    return tile - 5000 if (abs(tile) >= 5000) ^ (tile < 0) else tile + 5000
        
    return -tile if flippable(tile) else tile
    
def flip_collision(tile_list, flip_dict):
    '''collisions use different tiles instead of flipping'''
    def swap_collision(tile: int):
        return flip_dict[tile] if tile in flip_dict else tile
    tile_list[:] = map(swap_collision, tile_list)
    
def flip_events(map_id:int, events_list:'list<int>'):
    '''same as collision,but also remove or move certain events'''
    remove_softlocks(map_id, events_list)
    events_list[:] = [EVENT_MAP_X[o] if o in EVENT_MAP_X else o for o in events_list]
    offset_events(events_list)

#collision helper
def build_collision_flip(tiles):
    offset = min(filter(lambda t: t != 0, tiles)) - 1
    flip_direction = not(offset % 2)
    collision_ids  = set(offset+i for i in range(2,14))
    collision_ids.update(offset+i for i in (16,17))

    def flip_col(i:int): return i+1 if i%2 ^ flip_direction else i-1
    collision_flipx = {i:flip_col(i) for i in collision_ids}
    
    return collision_flipx

#helpers for flip_events
def swap(l:list, index1: int, index2: int):
    #assume indices are not out-of-bounds
    if SHOW_WARNINGS and map_coords(index1)[1] != map_coords(index2)[1]:
        print('warning: swapping indices from different rows:'
            , f'i1= {index1}', f'i2= {index2}'
            , f'v1= {l[index1]}', f'v1= {l[index2]}')
        return

    l[index1], l[index2] = l[index2], l[index1]
    
def offset_events(events_list):
    f = filter(lambda t: t[1] in EVENT_OFFSETS, enumerate(events_list))
    for i,event in f: swap(events_list, i, EVENT_OFFSETS[event](i))

def flip_rando(events_list:'list<int>'):                   
    '''column for setting event flags at the start of rando'''
    r = map_index(RANDO_FLAGS_X,0)
    for offset in range(1,3):
        i = map_index(offset,0)
        t = r+i
        if events_list[t] >= 5000:
            swap(events_list, t, r-i)

#def flip_transitions(               
def remove_softlocks(map_id:int, events_list:'list<int>'):
    def check_x_softlock(o:int):
        return not (map_id in X_SOFTLOCK and o in X_SOFTLOCK[map_id])
    events_list[:] = [o for o in events_list if check_x_softlock(o)]
