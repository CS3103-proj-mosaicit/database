import ImageDB
from image_crawler import store_raw_images


db=ImageDB.db()
db.init()
db.close_connection()

with open("./keywords.txt", 'r') as f:
  keywords = f.readlines()
  for keyword in keywords:
    try:
      keyword = keyword.replace("\n", "")
      print("Start cralwing " + keyword + "...")
      store_raw_images(keyword)
      print("Done with " + keyword)
    except:
      continue