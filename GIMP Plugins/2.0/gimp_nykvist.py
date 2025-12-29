#!/usr/bin/env python
# -*- coding: utf8 -*-

from gimpfu import *

def nykvist( img, draw, brightAdjust, contrastAdjust, isGlow, sharpAmount ):
	
	current_f=pdb.gimp_context_get_foreground()
	current_b=pdb.gimp_context_get_background()

	#clean start
	img.disable_undo()
	pdb.gimp_context_push()

	#set colors
	pdb.gimp_context_set_foreground((255, 255, 255))
	pdb.gimp_context_set_background((0, 0, 0))

	#get height and width
	pdb.gimp_selection_all
	sel_size=pdb.gimp_selection_bounds(img)
	w=sel_size[3]-sel_size[1]
	h=sel_size[4]-sel_size[2]

	#set blend start points
	startX = w/2
	startY = h/2
	
	#use diagonal as basis for blend end points
	diagonal = (math.sqrt(h*h + w*w))*0.95
	endX = w/2 + diagonal/2
	endY = h/2
	sharpenX = w/2 + diagonal*0.85
	sharpenY = h/2

	###
	### Desaturate and adjust brightness/contrast
	###

	#layer copy from background
	copyLayer1=pdb.gimp_layer_new_from_visible(img, img, "BaseCopy")
	pdb.gimp_image_insert_layer(img, copyLayer1, None, -1)

	#desaturate it
	pdb.gimp_desaturate_full(copyLayer1, 1)
	pdb.gimp_colorize( copyLayer1, 215, 11, 0)

	#adjust brightness and contrast
	pdb.gimp_drawable_brightness_contrast(copyLayer1, brightAdjust, contrastAdjust)


	###
	### Add softglow
	###

	if isGlow == TRUE:

		#copy the visible image for softglow
		copyLayer3=pdb.gimp_layer_new_from_visible(img, img, "SoftglowBase")
		pdb.gimp_image_insert_layer(img, copyLayer3, None, -1) 

		#apply softglow plugin to the layer
		#glow diameter is scaled to a percentage of the picture width
		glowWidth = w*0.05
		pdb.plug_in_softglow(img, copyLayer3, glowWidth, 0.7, 0.5)

		#create new layer mask with black fill 
		layerMask3 = copyLayer3.create_mask(1)
		copyLayer3.add_mask(layerMask3)

		#add radial gradient w/start point in center of image to control softglow visibility
		glowOpacity = 70
		glowOffset = 10
		gradientInvert = TRUE
		mode = LAYER_MODE_NORMAL
		pdb.gimp_edit_blend(layerMask3, 2, mode, 2, glowOpacity, glowOffset, 0, gradientInvert, FALSE, 1, 0, TRUE, startX, startY, endX, endY)

		#Transform into a layer that applies the softglow effect to the original image
		#so that it can be added or removed by changing the layer visibility

		#Put a copy of the BaseCopy layer above it and set the mode to subtract
		copyLayer11=pdb.gimp_layer_copy(copyLayer1, 1)
		pdb.gimp_image_insert_layer(img, copyLayer11, None, -1)
		copyLayer11.name = "SoftglowSubtract"
		copyLayer11.mode = LAYER_MODE_SUBTRACT

		#Create a new layer as copy from visible and set the mode to addition
		#This will add in the softglow effect
		copyLayer12=pdb.gimp_layer_new_from_visible(img, img, "SoftglowAdd")
		pdb.gimp_image_insert_layer(img, copyLayer12, None, -1)
		copyLayer12.mode = LAYER_MODE_ADDITION

		#Delete the second copy of the base layer and original Softglow (or at least make them non visible)
		copyLayer3.visible = 0
		copyLayer11.visible = 0


	###
	### Add vignette
	###

	#add a new layer for vignette
	copyLayer2=pdb.gimp_layer_new(img, w, h, 1, "Vignette", 100.0, 23)
	pdb.gimp_image_insert_layer(img, copyLayer2, None, -2)
	pdb.gimp_drawable_fill(copyLayer2, 3)

	#add layer mask with black fill 
	#layerMask2 = copyLayer2.create_mask(1)
	#copyLayer2.add_mask(layerMask2)

	#add radial gradient w/start point in center of image
	vignetteOpacity = 15
	vignetteOffset = 80
	gradientInvert = TRUE
	mode = LAYER_MODE_NORMAL
	pdb.gimp_edit_blend(copyLayer2, 2, mode, 2, vignetteOpacity, vignetteOffset, 0, gradientInvert, FALSE, 1, 0, TRUE, startX, startY, endX, endY)


	###
	### Add sharpening
	###

	if sharpAmount > 0:
		#copy the visible image for sharpening
		copyLayer4=pdb.gimp_layer_new_from_visible(img, img, "Sharpen")
		pdb.gimp_image_insert_layer(img, copyLayer4, None, -1)

		#unsharp mask settings
		sharpRadius = 2
		sharpThreshold = 0

		#add unsharp mask
		pdb.plug_in_unsharp_mask(img, copyLayer4, sharpRadius, sharpAmount, sharpThreshold)

		#add layer mask with black fill 
		layerMask4 = copyLayer4.create_mask(1)
		copyLayer4.add_mask(layerMask4)

		#apply a blend that fades out sharpening away from the center of the image
		sharpOpacity = 70
		gradientInvert = FALSE
		mode = LAYER_MODE_NORMAL
		pdb.gimp_edit_blend(layerMask4, 2, mode, 2, sharpOpacity, 0.5, 0, gradientInvert, FALSE, 1, 0, TRUE, startX, startY, sharpenX, sharpenY)
		

	#clean up	
	pdb.gimp_displays_flush()
	pdb.gimp_context_pop()
	img.enable_undo()
	pdb.gimp_context_set_foreground(current_f)
	pdb.gimp_context_set_background(current_b)


register( "gimp_nykvist",
  "Add soft b/w effect",
  "Add soft b/w effect",
  "Simon Bland",
  "(©) 2021 Simon Bland",
  "2021-03-01",
  "<Image>/Filters/Nykvist",
  'RGB*',
  [
	(PF_SLIDER, "brightAdjust","Brightness", 0.4, (-0.5, 0.5, 0.1)),
	(PF_SLIDER, "contrastAdjust", "Contrast", 0.3, (-0.5, 0.5, 0.1)),
	(PF_TOGGLE, "isGlow", "Glow effect", 1),
	(PF_SLIDER, "sharpAmount", "Sharpen amount", 0.5, (0, 5.0, 0.1))
  ],
  '',
  nykvist)

main()

