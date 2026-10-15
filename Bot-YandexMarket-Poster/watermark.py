import requests
from PIL import Image 
from io import StringIO
def water_mark(img):
    #fd = urllib.request.urlopen(img)
    #image_file = io.BytesIO(fd.read())
    img_data = requests.get(img).content
    with open(r"geeksforgeeks.png", 'wb') as handler:
        handler.write(img_data)
    wm = Image.open(r"wm.png").convert("RGBA")
    img1 = Image.open(r"geeksforgeeks.png").convert("RGBA")
    img1.paste(wm, (0,0), mask = wm)
    width, height = img1.size
    img1 = img1.resize((width*3, height*3))
    return img1
    
#water_mark("https://avatars.mds.yandex.net/get-mpic/5256749/2a00000194db70f14cbcd079b74c13c8023c/240x320")
#water_mark("https://avatars.mds.yandex.net/i?id=e201690da29265171d780fcb08ed2f056fb96564-12431474-images-thumbs&n=13")