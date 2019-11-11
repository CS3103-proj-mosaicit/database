import ImageDB
from PIL import Image
import io
from image_crawler import store_raw_images

db = ImageDB.db()
# db.tesging_path='./'# rmb to put an image img.jpg under 

db.init()

print("The testing cralwing may take 20s...")
# store_raw_images("sky")
print("Skipping crawl testing...")

print("Opening 10 testing images...")
ten = db.select_ten()
for row in ten:
  print((row[1], row[2], row[3]))
  db.raw_to_img(row[5]).show()

print("Selecting a pic close to light blue color...")
img = db.select_rough_rgb(0x79FFEE)
rgb=db.avg_rgb(img)
r, g, b = rgb // 65536, (rgb - rgb // 65536 * 65536) // 256, rgb % 256
print("Input rgb: (121, 255, 238), output rgb:" + str((r, g, b)))
db.raw_to_img(img).show()
