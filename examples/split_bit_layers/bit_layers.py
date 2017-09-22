from imagetools import ImageTools

it = ImageTools("bit_layers.png")

for i, layer in enumerate(it.SplitBitLayers()):
	layer.save("bitlayer_%d.png" % (i))