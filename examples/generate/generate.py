import math
from PIL import Image


def Components(img):
	px = img.load()
	for iComponent, component in enumerate(["red", "green", "blue"]):
		componentImg = Image.open("%s.png" % (component)).convert("1")
		componentPx = componentImg.load()
		for h in range(componentImg.size[1]):
			for w in range(componentImg.size[0]):
				mask = 0x00 if componentPx[w, h] == 0 else 0xff
				newPx = list(px[w, h])
				newPx[iComponent] = newPx[iComponent] & mask
				px[w, h] = tuple(newPx)
	return img


def BitLayers(img):
	px = img.load()
	for layer in range(1, 9):
		layerImg = Image.open("%d.png" % (layer)).convert("1")
		layerPx = layerImg.load()
		for h in range(layerImg.size[1]):
			for w in range(layerImg.size[0]):
				mask = 0xff ^ ((0x01 if layerPx[w, h] == 0 else 0x00) << (8 - layer))
				px[w, h] = (px[w, h][0] & mask, px[w, h][1] & mask, px[w, h][2] & mask)
	return img

Components(Image.new("RGB", (500,500), "white")).save("components.png")
BitLayers(Image.new("RGB", (500,500), "white")).save("bit_layers.png")
Components(BitLayers(Image.new("RGB", (500,500), "white"))).save("bit_layers_and_components.png")
