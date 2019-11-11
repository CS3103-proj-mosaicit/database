import ImageDB
import sys
db=ImageDB.db()
db.init()

data=db.select_rough_rgb(db.rgb_to_int((int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))))
