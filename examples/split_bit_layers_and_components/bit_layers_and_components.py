from imagetools import ImageTools

it = ImageTools("bit_layers_and_components.png")

for c, component in enumerate(it.SplitBitLayersComponents()):
	for l, layer in enumerate(component):
		layer.save("component_%d_layer_%d.png" % (c, l))