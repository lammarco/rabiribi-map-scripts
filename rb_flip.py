from diffgenerator import map_coords, map_index
import rb_flip_helpers as rbf

# !!! Run rb_mm.py; rb_flip just has the actual flipper functions
######################### DO NOT CHANGE
MINIMAP_DIM = (25, 18)
ROOM_DIM = (19,10)
WIDTH, HEIGHT  = (500, 200) #y_row = number of rows = number of tiles in column = for y pos

#rando flags set at the start, event 558's position BEFORE flipping
RANDO_FLAGS_X = 111

X_SOFTLOCK = {0: (301,389)}
TRANSITIONS = rbf.get_transitions()
EVENT_MAP_X = rbf.build_swapmap( [(195,196)] )
EVENT_OFFSETS = {420: lambda i: i - ROOM_DIM[0] #main event Rita Saya (HoM) warps 1 screen left
                ,307: rbf.offset_307}       


############## main flip function ##################
def flip_minimap(layers:dict):
    w,h = MINIMAP_DIM
    for data in layers.values():
        l = [data[i*h:(i+1)*h:] for i in range(w)] #list of columns
        l.reverse()
        data[:] = [t for l2 in l for t in l2]
        
def flip_map(map_id:int, layers:dict):
    if map_id == 5 or map_id == 0: #only flip transitions for town
        l = layers['event']
        rbf.transpose(l, 200)
        if map_id == 5: flip_transitions(l)
        elif map_id == 0: flip_rando(l)
        rbf.transpose(l, 500)
        if map_id == 5: return 

    for layer,data in layers.items():
        rbf.transpose(data, 200)
        if   layer == 'items':     pass
        elif layer == 'event':     flip_events(map_id, data)
        elif layer == 'collision': flip_collision(data, rbf.build_collision_flip(data))
        else:                      flip_layer_x(data)
        flip_map_x(data)
        rbf.transpose(data, 500)


def flip_map_x(tile_list:list):
    for r in range(HEIGHT): rbf.flip_row(tile_list, r, WIDTH)

def flip_layer_x(tile_list):
    '''flip individual tiles <- apply to entire layer'''
    tile_list[:] = map(rbf.flip_tile_x, tile_list)

    
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



#helpers for flip_events
    
def offset_events(events_list):
    f = filter(lambda t: t[1] in EVENT_OFFSETS, enumerate(events_list))
    for i,event in f: rbf.swap(events_list, i, EVENT_OFFSETS[event](i))

def flip_rando(events_list:'list<int>'):                   
    '''column for setting event flags at the start of rando'''
    for y in range(42):
        i = y*WIDTH + RANDO_FLAGS_X
        for offset in range(1,3):
            t = i+offset
            if events_list[t] >= 5000:
                rbf.swap(events_list, t, i-offset)

def flip_transitions(events_list):
    def get_flipmap(row: int):
        out = dict()
        r, r1 = row*WIDTH, (row+1)*WIDTH
        for i,t in enumerate(events_list[r:r1]):
            if t not in TRANSITIONS: continue
            i1, i2 = r+i, r1-i-1
            t2 = events_list[i2]
            
            if (t2 != 0) and (i1 in out) and (out[i1] != t2):
                print('\nwarning: transition overwriting:'
                      ,f'i={i1} old={out[i1]} new={t2}')
            
            out[i1] = t2; out[i2] = t
        return out
    
    def swap_row(swap_map: dict):
        nonlocal events_list
        for i,t in swap_map.items():
            events_list[i] = t
            
    for y in range(HEIGHT): swap_row(get_flipmap(y))
    
def remove_softlocks(map_id:int, events_list:'list<int>'):
    def is_softlock_x(o:int): 
        return map_id in X_SOFTLOCK and o in X_SOFTLOCK[map_id]
    events_list[:] = [0 if is_softlock_x(t) else t for t in events_list]
