import io
import mysql.connector
import numpy as np
import random
import zlib
from PIL import Image
class db(object):
  def init(self):
    self.connect()
    self.cursor.execute("CREATE DATABASE IF NOT EXISTS " + self.db_name)
    self.cursor.execute("USE " + self.db_name)
    self.cursor.execute("CREATE TABLE IF NOT EXISTS image(id INT NOT NULL AUTO_INCREMENT UNIQUE PRIMARY KEY, r INT NOT NULL, g INT NOT NULL, b INT NOT NULL, hash INT NOT NULL UNIQUE, img MEDIUMBLOB)")

  def connect(self):
    self.db_name = "imagedb"
    self.conn = mysql.connector.connect(host='localhost',
                                  user='root',
                                  port=3306,
                                  password='3103',
                                  use_pure=True)
    self.cursor = self.conn.cursor(buffered=True)

  def test(self):
    # this function test: insert, select
    self.testing_path='./'
    f = open(self.testing_path + 'img.jpg', 'rb')
    data = f.read()
    h = zlib.crc32(data)
    try:
      self.cursor.execute("INSERT INTO imagedb.image(r, g, b, hash, img) VALUES (%s, %s, %s, %s, %s)", (0, 0, 0, h, data))
      self.conn.commit()
    except:
      pass
    self.cursor.execute("SELECT img FROM imagedb.image WHERE rgb=%s", (0x010305,))
    result = self.cursor.fetchone()[0]
    print(len(result))
    f=open(self.testing_path + 'img2.jpg', 'wb')
    f.write(result)
    f.close()

  def avg_rgb(self, img):
    pic = self.raw_to_img(img)
    im = np.array(pic)
    # get shape
    w,h,d = im.shape
    # change shape
    im.shape = (w*h, d)
    # get average
    rgb = tuple(int(round(x)) for x in tuple(im.mean(axis=0)))
    return int('%02x%02x%02x' % rgb, 16)

  def insert_img(self, raw_img):
    try:
      img = self.resize_cut(self.raw_to_img(raw_img))
      raw_img = self.img_to_raw(img)
      h = zlib.crc32(raw_img)
      rgb = self.avg_rgb(raw_img)
      r, g, b = rgb // 65536, (rgb - rgb // 65536 * 65536) // 256, rgb % 256  
      self.cursor.execute("INSERT INTO imagedb.image(r, g, b, hash, img) VALUES (%s, %s, %s, %s, %s)", (r, g, b, h, raw_img))
      self.conn.commit()
      print((r, g, b))
    except:
      return -1
    return 1

  def select_rgb(self, rgb):
    try:
      r, g, b = rgb // 65536, (rgb - rgb // 65536 * 65536) // 256, rgb % 256
      self.cursor.execute("SELECT img FROM imagedb.image WHERE r=%s AND g=%s And b=%s", (r, g, b))
      result = self.cursor.fetchone()[0]
      # print(len(result))
    except:
      return -1
    return result

  def rgb_to_int(self, rgb):
    r, g, b = rgb
    return r*65536 + g*256 + b

  def int_to_rgb(self, rgb):
    r, g, b = rgb // 65536, (rgb - rgb // 65536 * 65536) // 256, rgb % 256
    return (r, g, b)

  def select_rough_rgb(self, rgb):
    img = None
    step = 0
    r, g, b = rgb // 65536, (rgb - rgb // 65536 * 65536) // 256, rgb % 256
    while img == None:
      try:
        # print(sql)
        step = step + 10
        self.cursor.execute("SELECT img FROM imagedb.image WHERE r > %s AND r < %s AND g > %s AND g < %s AND b > %s And b < %s;", (r - step, r + step, g - step, g + step, b - step, b + step))
        # rl, rr, gl, gr, bl, br = (r - step, r + step, g - step, g + step, b - step, b + step)
        print(step)
        img = self.cursor.fetchone()[0]
      except Exception as e:
        # print(e)
        continue
    return img

  def select_ten(self):
    self.cursor.execute("SELECT * FROM imagedb.image LIMIT 10")
    return self.cursor.fetchall()

  def close_connection(self):
    self.cursor.close()
    self.conn.close()

  def resize_cut(self, img): # @raw bytes img, any size =. 300 * 300 pix
    size=img.size
    if(size[0] > size[1]):
      img = img.resize((int(size[0]/size[1]*300), 300))
      size = img.size
      img = img.crop(( int((size[0] - 300) / 2), 0, int((size[0] + 300) / 2), 300))
    else:
      img = img.resize((300, int(size[1]/size[0]*300)))
      size = img.size
      img = img.crop(( 0, int( (size[1] - 300) / 2), 300, int( (size[1] + 300) / 2) ))
    return img

  def raw_to_img(self, raw_img): # @img obj
    return Image.open(io.BytesIO(raw_img))

  def img_to_raw(self, img):
    byteIO = io.BytesIO()
    img.save(byteIO, format='PNG')
    return byteIO.getvalue()

