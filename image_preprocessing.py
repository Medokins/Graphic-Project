from PIL import Image
from pathlib import Path
import os, random, shutil

def crop(input, size):
    [f.unlink() for f in Path("pool").glob("*") if f.is_file()]
    [f.unlink() for f in Path("processed_tiles").glob("*") if f.is_file()] 
    im = Image.open(input)
    row = -1
    imgwidth, imgheight = im.size
    for i in range(0,imgheight,size):
        row += 1
        column = -1
        for j in range(0,imgwidth,size):
            column += 1
            box = (j, i, j+size, i+size)
            a = im.crop(box)
            a.save(os.path.join("pool", f"{row:02}{column:02}.png"))

# this could use some optimization but it's the simplest implementation that I thought about
def choose_radnom(row_index):
    random_image = random.choice(os.listdir("pool"))
    while (int(random_image[:2]) != row_index):
        random_image = random.choice(os.listdir("pool"))
    return random_image

def move_to_processed(image):
    shutil.move(os.path.join("pool", image), "processed_tiles")

def move_to_pool(image):
    shutil.move(os.path.join("processed_tiles", image), "pool")