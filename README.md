# RabiRibi Map Flipper - Mirror Mode 2

Flip rb maps just like Mirror Mode on April Fools.. except with patches to fix a lot of things break!


How to use:

0a. Have python3 installed.

0b. set input/output folders in rb_mm (default is '[script location]/maps/original' and '[script location]/maps/generated')
	(if you change output path, also change diffgenerator's paths)

1. copy original maps into [input folder]

2. run rb_mm.py

3. copy generated maps from [output folder] to a new custom map. See [wcko87's custom map guide](https://wcko87.github.io/rabiribi-map-editing/runningcustommaps) for more details.

Enjoy!


Known issues / workarounds

- springs always appear regardless of condition; no fix yet

- certain (mini)boss triggers require turning around (to the original direction). There might be AFD blocks to prevent softlocks. Example: first UPRPRC fight requires moving to the left

- certain story events warp to hardcoded positions; take the warps there to continue

- playing as cocoa: going too fast into ribbon fight = softlock; reload and go slower

- RANDOMIZER: generate seeds using ZIPS_REQUIRED = False, since zips now go in the opposite direction (in relation to the map)

Note: uses [wcko's diffgenerator.py from randomizer] (https://github.com/wcko87/revised-rabi-ribi-randomizer/blob/0cfd17deebdcfbc55247dec25b9300cbec7548cc/converter/diffgenerator.py)
