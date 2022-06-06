from PIL import Image
from pathlib import Path
import os, random, shutil
import numpy as np
import pygame

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

# conver
def grayscale(img):
    arr = pygame.surfarray.array3d(img)
    avgs = [[(r*0.298 + g*0.587 + b*0.114) for (r,g,b) in col] for col in arr]
    arr = np.array([[[avg,avg,avg] for avg in col] for col in avgs])
    return pygame.surfarray.make_surface(arr)

# numpys slightly modified matrix flip with color inveresion
def flip(matrix, axis=None):
    if not hasattr(matrix, 'ndim'):
        matrix = np.asarray(matrix)
    if axis is None:
        slicer = (np.s_[::-1],) * matrix.ndim
    else:
        axis = np.core.numeric.normalize_axis_tuple(axis, matrix.ndim)
        slicer = [np.s_[:]] * matrix.ndim
        for ax in axis:
            slicer[ax] = np.s_[::-1]
        slicer = tuple(slicer)
    return matrix[slicer]

# numpys slightly modified matrix rotation
def rotate_90(m, k=1, axes=(0, 1)):
    axes = tuple(axes)
    m = np.asanyarray(m)
    k %= 4
    if k == 0:
        return m[:]
    if k == 2:
        return flip(flip(m, axes[0]), axes[1])

    axes_list = np.arange(0, m.ndim)
    (axes_list[axes[0]], axes_list[axes[1]]) = (axes_list[axes[1]], axes_list[axes[0]])
    if k == 1:
        return np.transpose(flip(m, axes[1]), axes_list)
    else:
        return flip(np.transpose(m, axes_list), axes[1])

def flip_image(image):
    matrix = pygame.surfarray.array3d(image)
    return pygame.surfarray.make_surface(flip(matrix, (0,2)))

def rotate_left(image):
    matrix = pygame.surfarray.array3d(image)
    return pygame.surfarray.make_surface(rotate_90(matrix, 3))

def rotate_right(image):
    matrix = pygame.surfarray.array3d(image)
    return pygame.surfarray.make_surface(rotate_90(matrix, 1))