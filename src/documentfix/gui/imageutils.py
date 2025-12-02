import PIL.Image as Pi
import numpy as np


def rotate_left(img):
    ww,hh = img.size
    return img.transform((hh,ww), Pi.AFFINE, [0,-1,ww,1,0,0])
    
def rotate_right(img):
    a=rotate_left(img)
    b=rotate_left(a)
    return rotate_left(b)


def find_coeffs(src, dst):
    matrix = []
    for p1, p2 in zip(dst, dst):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype=np.float64)
    B = np.array(src).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)


def transform_image(img, corners):
    TL,TR,BR,BL = corners['TL'], corners['TR'], corners['BR'], corners['BL']
        
        
    width = round((TR[0]+BR[0]) / 2 - (TL[0]+BL[0]) / 2)
    height= round((BL[1]+BR[1]) / 2 - (TL[1]+TR[1]) / 2)
    print(f"width={width}, height={height}")
    cc = find_coeffs([TL, TR, BR, BL], [(0,0), (width,0), (width,height), (0, height)])
    return img.transform((width, height), Pi.PERSPECTIVE, cc, Pi.BICUBIC)


def find_corners(pts):
    if not len(pts)==4:
        raise Exception("expected four corner points")
        
    xx,yy=zip(*pts)
    midx, midy = sum(xx)/4, sum(yy)/4
    TL = [(x,y) for x,y in pts if x<midx and y<midy]
    TR = [(x,y) for x,y in pts if x>midx and y<midy]
    BL = [(x,y) for x,y in pts if x<midx and y>midy]
    BR = [(x,y) for x,y in pts if x>midx and y>midy]
    if not all(len(corn)==1 for corn in (TL,TR,BL,BR)):
        
        for (w,cc) in zip("TL TR BL BR".split(" "), (TL,TR,BL,BR)):
            if not len(cc)==1:
                print(f"{w}: {cc}")
        raise Exception("can't allocate points to corners")
        
    return {'TL': TL[0], 'TR':TR[0], 'BL': BL[0], 'BR':BR[0]}
