# RabiRibi Map Flipper - Mirror Mode 2

Flip rb maps just like Mirror Mode on April Fools.. except with patches to fix a lot of things break!


How to use: (to be improved)

0a. set up folders/paths (check under this set of directions)

0b. set up for custom maps (check wcko87's map editing tutorial https://wcko87.github.io/rabiribi-map-editing/)

0c. Have python installed.


a1. Open rb_mm.py

a2. at the bottom, make sure "main()" is uncommented, while generate_maps... is ('#' before a line = comment)

a3. use wcko's map converter to get json files

a4. put json maps into the path specified in JSON_IN_DIR (at top of rb_mm.py)

a5. run rb_mm.py

-you should get flipped json maps in JSON_OUT_DIR

b1. convert the flipped jsons back to map files

b2. move map files to DIR_ORIGINAL_MAPS (at top of diffgenerator.py)

b3. swap the comments mentioned in a2 (to apply patch.txt)

b4. run_mm.py after the swap

-now you have patched files in DIR_GENERATED_MAPS

Copy over any missing maps (because they had no patchs), and enjoy! (Check wcko's tutorial on how to run custom maps: https://wcko87.github.io/rabiribi-map-editing/runningcustommaps)


Known issues / workarounds

- springs always appear regardless of condition; no fix yet

- certain (mini)boss triggers require turning around (to the original direction). There might be AFD blocks to prevent softlocks. Example: first UPRPRC fight requires moving to the left

- certain story events warp to hardcoded positions; take the warps there to continue

- playing as cocoa: going too fast into ribbon fight = softlock; reload and go slower

TODO:

1. skip converting to json by directly using diffgenerator.MapData

2. using #1, simplify the workflow to "paste here, run code, paste back"

3. separate patches into specific fixes


Note: uses wcko's diffgenerator.py from randomizer: https://github.com/wcko87/revised-rabi-ribi-randomizer/blob/0cfd17deebdcfbc55247dec25b9300cbec7548cc/converter/diffgenerator.py
