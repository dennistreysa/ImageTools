from imagetools import ImageTools

it = ImageTools("components.png")

for i, component in enumerate(it.SplitComponents()):
	component.save("component_%d.png" % (i))