SHOW_WARNINGS = True

######################### DO NOT CHANGE
WIDTH, HEIGHT  = (500, 200) #y_row = number of rows = number of tiles in column = for y pos
AFD = 481

def transpose(tile_list, spacing):
    '''reorder data, from wcko87/rbrb-map-converter'''
    l = [tile_list[i::spacing] for i in range(spacing)]
    tile_list[:] = [t for x in l for t in x]

def i2xy(index: int):
    return (index % WIDTH, index // WIDTH)

def offset_307(i:int):
    x = i % WIDTH
    if x == 115: return i-7 #rando force forest uprprc
    if x == 319: return i+2 #starting forest uprprc
    return i

def get_transitions():
    events = (range(161,171), range(200,206), range(227,233), (177, 207))
    return set( i for r in events for i in r )

def build_swapmap(pairs: list):
    #pairs[:] = [(str(n1),str(n2)) for n1,n2 in pairs]
    swapmap = dict()
    swapmap.update((n1,n2) for n1,n2 in pairs)
    swapmap.update((n2,n1) for n1,n2 in pairs)
    return swapmap

def flip_row(l:list, r:int, w:int):
    '''l = 1d array of 2d map, r = i-th row, w = width, h = height'''
    f, b = r*w, (r+1)*w
    l[f:b] = l[b-1:   :-1] if r == 0 else \
             l[b-1:f-1:-1]
    
def flip_tile_x(tile: int):
    def flippable(tile_id: int):
        return (tile_id != 0) and (tile_id != AFD)
    #def flip_y(tile: int):
    #    return tile - 5000 if (abs(tile) >= 5000) ^ (tile < 0) else tile + 5000
        
    return -tile if flippable(tile) else tile


def swap(l:list, index1: int, index2: int):
    #assume indices are not out-of-bounds
    if SHOW_WARNINGS and ( i2xy(index1)[1] != i2xy(index2)[1] ):
        print('warning: swapping indices from different rows:'
            , f'i1= {index1}', f'i2= {index2}'
            , f'v1= {l[index1]}', f'v1= {l[index2]}')
        return

    l[index1], l[index2] = l[index2], l[index1]
    
#collision helper
def get_collision_offset(tiles):
    '''returns solid_collision - 1'''
    return min(filter(lambda t: t != 0, tiles)) - 1

def build_collision_flip(tiles, collision_offset):
    flip_direction = not(collision_offset % 2)
    collision_ids  = set(collision_offset+i for i in range(2,14))
    collision_ids.update(collision_offset+i for i in (16,17))

    def flip_col(i:int): return i+1 if i%2 ^ flip_direction else i-1
    collision_flipx = {i:flip_col(i) for i in collision_ids}
    
    return collision_flipx
