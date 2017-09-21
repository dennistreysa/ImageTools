"""
ImageTools

A toolset to help splitting images into their components and to perform logical masks on pixel values.

Author: dennistreysa (https://github.com/dennistreysa)
URL: https://github.com/dennistreysa/ImageTools

License: GNU General Public License v3.0
"""

import os
import math
import numpy
import copy
import scipy.misc
from PIL import Image


class ImageTools(object):

	def __init__(self, imagePath=None):
		self._bits = 8
		self._components = None
		
		if imagePath is not None:
			self.Load(imagePath)

	def Load(self, imagePath):
		"""Loads an image via a give file-path

		imagePathe -- path to the image file
		"""
		assert os.path.isfile(imagePath), "No valid file path was passed!"
		image = Image.open(imagePath)
		self._imageData = numpy.asarray(image)
		self._height = self._imageData.shape[0]
		self._width = self._imageData.shape[1]
		self._components = self._imageData.shape[2]
		self._splittedComponents = None

	def _splitComponents(self):
		"""Splits the image data into its components (e.g. red, blue and green)
		"""
		if self._splittedComponents is None:
			self._splittedComponents = [self._imageData[:,:,component:component + 1] for component in range(self._components)]
		return copy.deepcopy(self._splittedComponents)

	def _toImage(self, data, reallyToImage=True, adjustValues=False):
		"""Converts a numpy array to a PIL-Image

		data -- The numpy array
		reallyToImage -- Indicates if the data shall really be converted, or just returned as is
		"""
		
		if not reallyToImage:
			return data

		if isinstance(data[0][0], int) or isinstance(data[0][0], float):
			components = 1
		else:
			components = data.shape[2]
		imageType = "?"

		if components == 1:
			imageType = "L"
			# toimage can't handle inner arrays with just one element, so we need to make an int out of the arrays
			data = data.reshape(data.shape[0], data.shape[1])
		elif components == 3:
			imageType = "RGB"
		elif components == 4:
			imageType = "ARGB"
		else:
			raise Exception("Could not determine image type!")

		_min = numpy.amin(data) if adjustValues else 0.0
		_max = numpy.amax(data) if adjustValues else math.pow(2, self._bits) - 1

		return scipy.misc.toimage(data, cmin=_min, cmax=_max, mode=imageType)

	def _mod(self, data, value):
		"""Performs modular arithmetic to all elements of a given numpy array

		data -- the numpy array
		value -- the value to perform the operation with
		"""
		return numpy.mod(data, value)

	def _div(self, data, value):
		"""Performs a division to all elements of a given numpy array

		data -- the numpy array
		value -- the value to perform the operation with
		"""
		return numpy.divide(data, value)

	def _and(self, data, value):
		"""Performs a bitwise AND to all elements of a given numpy array

		data -- the numpy array
		value -- the value to perform the operation with
		"""
		return numpy.bitwise_and(data, value)

	def _or(self, data, value):
		"""Performs a bitwise OR to all elements of a given numpy array

		data -- the numpy array
		value -- the value to perform the operation with
		"""
		return numpy.bitwise_or(data, value)

	def _xor(self, data, value):
		"""Performs a bitwise XOR to all elements of a given numpy array

		data -- the numpy array
		value -- the value to perform the operation with
		"""
		return numpy.bitwise_xor(data, value)

	def _shift(self, data, value):
		"""Performs a bitwise left shift to all elements of a given numpy array

		data -- the numpy array
		value -- the number of bits to shift left
		"""
		if value == 0:
			return data
		return numpy.left_shift(data, value)

	def _maskBits(self, data, fromBit, toBit):
		"""Performs a bitwise AND to all elements of a given numpy array with a mask of all zeros, only the bits from 'fromBit' to 'toBit' (including) are set to 1
		"""
		mask = sum([1<<pos for pos in range(fromBit, toBit + 1)])
		return self._and(data, mask)

	def _getMaskedComponentByIndex(self, component, function, value, shift, toImage):
		assert component < self._components, "The image does not have that many components!"
		return self._toImage(self._shift(function(self._splitComponents()[component], value), shift), toImage)

	def _getMaskedComponent(self, component, function, value, shift, toImage):
		return self._toImage(self._shift(function(component, value), shift), toImage)

	def SplitComponents(self, toImage=True):
		for component in self._splitComponents():
			yield self._toImage(component, toImage)

	def SplitBitLayersComponents(self, bits=1, toImage=True):
		for component in self._splitComponents():
			yield [self._toImage(self._shift(self._maskBits(component, layer, layer + bits - 1), self._bits - layer - bits), toImage) for layer in range(self._bits - bits + 1)]

	def SplitBitLayers(self, bits=1, toImage=True):
		"""Returns the image data splitted by bit layers (components are not seperated)

		Note:
		If bits > 1, the layers will overlap!

		Keyword arguments:
		bits [int] -- Number of bits to mask (default 1)
		"""
		assert bits > 0, "Need to mask at least one bit!"
		for layer in range(self._bits - bits + 1):
			yield self._toImage(self._shift(self._maskBits(self._imageData, layer, layer + bits - 1), self._bits - layer - bits), toImage)

	def GetAndMaskedComponent(self, component, mask, shift=0, toImage=True):
		return self._getMaskedComponentByIndex(component, self._and, mask, shift, toImage)

	def GetOrMaskedComponent(self, component, mask, shift=0, toImage=True):
		return self._getMaskedComponentByIndex(component, self._or, mask, shift, toImage)

	def GetXorMaskedComponent(self, component, mask, shift=0, toImage=True):
		return self._getMaskedComponentByIndex(component, self._xor, mask, shift, toImage)

	def GetMaskedComponents(self, masks, multiMask=True, toImage=True):
		FUNCTION = 0
		COMPONENT_INDEX = 1
		VALUE = 2
		SHIFT = 3
		componentsOriginal = self._splitComponents()
		componentsOut = []
		componentsOrder = []
		f = None
		for mask in masks:
			assert mask[COMPONENT_INDEX] < self._components, "Invalid component index!"
			if mask[FUNCTION] == "&":
				f = self._and
			elif mask[FUNCTION] == "|":
				f = self._or
			elif mask[FUNCTION] == "^":
				f = self._xor
			else:
				raise Exception("Unknown mask method!")
			if len(mask) == 3:
				# shift=0
				mask.append(0)
			
			component = copy.deepcopy(componentsOriginal[mask[COMPONENT_INDEX]])
			componentNew = self._getMaskedComponent(component, f, mask[VALUE], mask[SHIFT], False)

			if multiMask:
				componentsOriginal[mask[COMPONENT_INDEX]] = componentNew
				if mask[COMPONENT_INDEX] not in componentsOrder:
					componentsOrder.append(mask[COMPONENT_INDEX])
			else:
				componentsOut.append(componentNew)

		if multiMask:
			for index in componentsOrder:
				componentsOut.append(componentsOriginal[index])

		return self._toImage(numpy.concatenate(componentsOut, axis=2), toImage)

	def MagicEye(self, minValue=True, horizontal=True, numberOfResults=1, borderArea=0.1, toImage=True):

		# convert to greyscale
		imageData = numpy.dot(self._imageData, [0.299, 0.587, 0.114])

		# overlay image with itself for offset 10%..90%
		start = math.floor((self._width if horizontal else self._height) *  borderArea)
		end = math.floor((self._width if horizontal else self._height) * (1.0 - borderArea))

		results = []

		for offset in range(start, end):
			width = (self._width - offset) if horizontal else self._width
			height = self._height if horizontal else (self._height - offset)	
			pixels = width * height
			a = imageData[:,:self._width - offset] if horizontal else imageData[:self._height - offset,:]
			b = imageData[:,offset:] if horizontal else imageData[offset:,:]
			vpp = numpy.sum(numpy.absolute(numpy.subtract(a, b))) / pixels

			results.append([vpp, offset])

		results = sorted(results, reverse=(not minValue))[:numberOfResults]

		for result in results:
			offset = result[1]
			a = imageData[:,:self._width - offset] if horizontal else imageData[:self._height - offset,:]
			b = imageData[:,offset:] if horizontal else imageData[offset:,:]
			yield self._toImage(numpy.absolute(numpy.subtract(a, b)), toImage)

	def Treashold(self, toImage=True):

		# convert to greyscale
		_imageData = numpy.dot(self._imageData, [0.299, 0.587, 0.114])

		for value in range(1, math.floor(math.pow(2, self._bits) - 1)):
			imageData = copy.deepcopy(_imageData)
			imageData[imageData <= value] = 0
			imageData[imageData > value] = math.pow(2, self._bits) - 1
			yield self._toImage(imageData, toImage)

	@property
	def Bits(self):
		return self._bits

	@Bits.setter
	def Bits(self, value):
		assert value > 0, "Bits must be at least 1!"
		self._bits = value

	@property
	def Components(self):
		return self._components
