# Builds the "DM" monogram by cutting the D and M out of the official logo (white-text version).
# Usage: python3 make_dm_monogram.py <logo-dark.webp> "<cut points>" <gap px> <out.png>
# Used: python3 make_dm_monogram.py 4.webp "[(572,0),(566,150),(545,192),(515,232),(470,290),(330,540)]" -10 DM.png
import sys
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage
src = Image.open(sys.argv[1]).convert('RGBA'); im = np.array(src)
alpha = im[...,3] > 30
def component_mask(mask):
    lab, n = ndimage.label(mask)
    sizes = ndimage.sum(mask, lab, range(1, n+1))
    k = lab == (np.argmax(sizes)+1)
    return ndimage.binary_dilation(k, iterations=2) & (im[...,3] > 0)
def cut(sel):
    out = im.copy(); out[~sel] = 0
    o = Image.fromarray(out); return o.crop(o.getchannel('A').getbbox())
# D: left of a hand-placed cut between D and O (display coords, 2x crop at 120,350)
pts = [(120+x/2, 350+y/2) for x,y in eval(sys.argv[2])]
m = Image.new('L', src.size, 0); ImageDraw.Draw(m).polygon([(0,0)]+pts+[(0,800)], fill=255)
m = np.array(m) > 0
D = cut(component_mask(alpha & m) & m)
# M: the single connected stroke group in x 1200-1480
mm = np.zeros_like(alpha); mm[340:620, 1200:1450] = True
lab, _ = ndimage.label(alpha); ids = np.unique(lab[mm & alpha]); ids = ids[ids>0]
big = max(ids, key=lambda i: (lab==i).sum())
M = cut(ndimage.binary_dilation(lab==big, iterations=2) & (im[...,3] > 0))
gap = int(sys.argv[3])
W = D.width + gap + M.width; H = max(D.height+3, M.height)
out = Image.new('RGBA', (W, H)); out.alpha_composite(D, (0, 3)); out.alpha_composite(M, (D.width+gap, 0))
out.save(sys.argv[4])
p = Image.new('RGBA', (W+80, H+80), (10,13,11,255)); p.alpha_composite(out, (40,40)); p.save(sys.argv[4].replace('.png','-prev.png'))
print(D.size, M.size, out.size)
