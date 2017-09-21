# ImageTools
A toolset to find hidden information in images by disassembling them into their components.

## Background

Especially amongst Geocachers it's a common riddle to hide information (e.g. coordinates) in an imagefile, but since EXIF-based hideouts are now well known, people search for more advanced steganography-methods to hide data.

A very common, but kinda hard to detect method (at least with most image-processing tools) is to make use of the fact, that changing the LSB (least significant bit) of the components (e.g. red, green, blue) of a pixel makes no difference for the human eye. This gives room to hide data there.

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

### Splitting image-components

If you want to split an image into it's components, e.g. splitting a RGB-image into the red, green and blue component, do the following:

```python
from imagetools import ImageTools

it = ImageTools("image.png")

for i, component in enumerate(it.SplitComponents()):
	component.save("component_%d.png" % (i))
```
