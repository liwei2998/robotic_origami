from PIL import Image


img = Image.open("simple_plane_state1.png")
img = img.convert("RGBA")

x,y=img.size

for i in range(x):
    for k in range(y):
        color = img.getpixel((i,k))
        color = color[:-1] + (100,)
        img.putpixel((i,k),color)

img.save("state1.png")
