# ImageTools
A toolset to help splitting images into their components and to perform logical masks on pixel values.

## Background

Especially amongst Geocachers it's a common riddle to hide information (e.g. coordinates) in an imagefile, but since EXIF-based hideouts are now well known, people search for more advanced steganography-methods to hide data.

A very common, but kinda hard to detect method (at least with most image-processing tools) is to make use of the fact, that changing the LSB (least significant bit) of the components (e.g. red, green, blue) of a pixel makes no difference for the human eye.

With the help of this toolset it's possible to extract that data easily.

## Requirements

To run this toolset properly, one needs to have the following libraries installed:

* [Pillow](https://python-pillow.org/)
* [NumPy](http://www.numpy.org/)
* [SciPy](https://www.scipy.org/)

If you don't want to install them all by hand, I recommend a Python distrubution like [Anaconda](https://www.anaconda.com/download/) which comes with all needed libaries pre-installed.

## Usage

Usage of the toolset is easy. Just get an instance of *ImageTools*, load the image you want to process and you're ready to go.

```python
from imagetools import ImageTools

it = ImageTools()
it.Load("image.png")
```

Or more condensed:

```python
from imagetools import ImageTools

it = ImageTools("image.png")
```

#### Note

All methods in the upcoming examples yield *iterators* to **PIL.Image.Image** objects. If you rather prefer the raw data, pass  `toImage=False` to the method and you'll receive and iterator to the raw **numpy.ndarray**s instead.

## Splitting

### Splitting an image into its components

If you want to split an image into its components, e.g. splitting a RGB-image into the red, green and blue component, call the `SplitComponents` method:

```python
from imagetools import ImageTools

it = ImageTools("image.png")

for i, component in enumerate(it.SplitComponents()):
	component.save("component_%d.png" % (i))
```

### Splitting an image into its bit-layers

If you need the bit-layers of an image, use `SplitBitLayers`. **Note:** This will not seperate the image by its components, so for a normal 8-bit RGB image, it will return 8 images. If you also want to split the image by its components have a look at the next method!

```python
from imagetools import ImageTools

it = ImageTools("image.png")

for i, layer in enumerate(it.SplitBitLayers()):
	layer.save("bitlayer_%d.png" % (i))
```

If you want your layer to have more than one bit, just pass the `bits` parameter with the number of desired bits. Note that the layers will overlap!

### Splitting an image into its bit-layers AND components

If you want to combine the `SplitComponents` and `SplitBitLayers` methods, use `SplitBitLayersComponents` (who would have guessed it 😄). **Note:** The method will yield an array containing the bit-layers for each component.

```python
from imagetools import ImageTools

it = ImageTools("image.png")

for c, component in enumerate(it.SplitBitLayersComponents()):
	for l, layer in enumerate(component):
		layer.save("component_%d_layer_%d.png" % (c, l))
```

Or course you can also pass the `bits` parameter.

## Masking

Sometimes you want to apply a special mask to a component of an image, e.g. *"invert bit 0 and 2 of the second component"*.
This can be done via the three mask-methods `GetAndMaskedComponent`, `GetOrMaskedComponent`, `GetXorMaskedComponent`.
**Note:** All three methods only work on a specific component, if you want to perform the same operation on all components, or maybe even different operations on different components, have a look at `GetMaskedComponents`.

### And-masking

This will perform a logic *AND*-operation on all values of a given component.

For example the following code sets every second bit of the second component to zero.

```python
from imagetools import ImageTools

it = ImageTools("image.png")
it.GetAndMaskedComponent(1, 0xaa).save("and_masked.png")
```

If you want to left-shift the values (useful if you only keep lower bits), pass the `shift` parameter.

### Or-masking

Performs a logic *OR*-operation on all values of a given component, have a look at `GetAndMaskedComponent` for details.

### Xor-masking

Performs a logic *XOR*-operation on all values of a given component, have a look at `GetAndMaskedComponent` for details.

### Combining masks

If you want to perform multiple masks on multiple components, or just multiple masks on a single component, use `GetMaskedComponents`.
To properly call that function you need to pass an array which consits of sub-arrays that look like the following:

`[MASK_TYPE, COMPONENT, MASK(, SHIFT)]`

*MASK_TYPE* can have the following values:

* *"&"*: AND-Mask
* *"|"*: OR-Mask
* *"^"*: XOR-Mask

For example if you want to perform `AND 0xaa` on the first component, `OR 0xbb` on the second component and `XOR 0xcc` on the third component, the code looks like the following:

```python
from imagetools import ImageTools

it = ImageTools("image.png")

masks = [
	["&", 0, 0xaa],
	["|", 1, 0xbb],
	["^", 2, 0xcc]
]

it.GetMaskedComponents(masks).save("masked.png")
```

If you want to perform the masks from above all on the first component, the masks would look like the following:

```python
masks = [
	["&", 0, 0xaa],
	["|", 0, 0xbb],
	["^", 0, 0xcc]
]
```

**Note:** This will return an image with only one component, the untouched components won't be added. If you would like to perserve them, just add an `AND 0xff` or `XOR 0x00` mask:

```python
masks = [
	["&", 0, 0xaa],
	["|", 0, 0xbb],
	["^", 0, 0xcc],
	["&", 1, 0xff],
	["&", 2, 0xff]
]
```
If you would like to create a new component for for each mask instead of performing the mask to the same component, just pass the `multiMask=False` parameter:

```python
from imagetools import ImageTools

it = ImageTools("image.png")

masks = [
	["&", 0, 0xaa],
	["|", 0, 0xbb],
	["^", 0, 0xcc]
]

it.GetMaskedComponents(masks, multiMask=False).save("masked.png")
```

This will return an image with three components.




