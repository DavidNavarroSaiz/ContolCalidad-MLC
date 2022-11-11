from field_size import RectangleDimensions


image_path = './compareimages/2junio_10x10.tiff' # 
<<<<<<< HEAD
mm_px = 0.283
width = RectangleDimensions(image_path)
width.evaluate_image(mm_px)
=======
mm_px = 0.2506
w_size = 100
width = RectangleDimensions(image_path)
width.evaluate_image(mm_px, w_size)
print("width.relation_mmpx", width.relation_mmpx) 
>>>>>>> 9dead0b2a6ba92a1ea1ef97e1a3fa9bc3ff8c2e2
