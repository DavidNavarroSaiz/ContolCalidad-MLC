from compare_images import CompareImages


# image_1_path = './compareimages/PicketFenceY2.tiff'
# image_2_path = './compareimages/PicketFenceY2_5.tiff'
# output_path = './compareimages/PicketFenceY2_5_fixed.tiff'
image_1_path = './compareimages/1mayo_10X10.tiff'
image_2_path = './compareimages/2junio_10x10.tiff'

number_iterations = 25
mm_px = 0.1136
compareimages = CompareImages(image_1_path,image_2_path)
compareimages.evaluate_images(number_iterations,mm_px)


