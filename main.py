"""Moonlight Teacup — original PNG art using Python 3 standard library only.
Designed for make.fun/cutest-picture-01. Purely offline and deterministic.
"""
import math
import os
import random
import struct
import zlib
from pathlib import Path

W = H = 640
pixels = [bytearray(W * 3) for _ in range(H)]

def paint(x, y, rgb, alpha=1.0):
    if 0 <= x < W and 0 <= y < H:
        r = pixels[y]
        i = x * 3
        if alpha >= 1:
            r[i:i + 3] = bytes(rgb)
        else:
            r[i:i + 3] = bytes(int(r[i+j] * (1-alpha) + rgb[j]*alpha) for j in range(3))

def ellipse(cx,cy,rx,ry,color,alpha=1.0,angle=0):
    c,s=math.cos(angle),math.sin(angle)
    radius=int(max(rx,ry)+2)
    for y in range(max(0,int(cy-radius)), min(H,int(cy+radius+1))):
        for x in range(max(0,int(cx-radius)), min(W,int(cx+radius+1))):
            dx,dy=x-cx,y-cy
            xx=dx*c+dy*s
            yy=-dx*s+dy*c
            if xx*xx/(rx*rx)+yy*yy/(ry*ry)<=1:
                paint(x,y,color,alpha)

def poly(pts,color,alpha=1):
    low=max(0,int(min(y for _,y in pts)))
    high=min(H-1,int(max(y for _,y in pts)))
    for y in range(low,high+1):
        cuts=[]
        for a,b in zip(pts,pts[1:]+pts[:1]):
            x1,y1=a; x2,y2=b
            if (y1<=y<y2) or (y2<=y<y1):
                cuts.append(x1+(y-y1)*(x2-x1)/(y2-y1))
        cuts.sort()
        for q in range(0,len(cuts)-1,2):
            for x in range(max(0,int(cuts[q])),min(W,int(cuts[q+1])+1)):
                paint(x,y,color,alpha)

def line(points,color,thick=2):
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        length=max(1,int(math.hypot(x2-x1,y2-y1)*1.7))
        for i in range(length+1):
            t=i/length
            ellipse(x1+(x2-x1)*t,y1+(y2-y1)*t,thick,thick,color)

def heart(cx,cy,r,color):
    ellipse(cx-r*.48,cy-r*.28,r*.55,r*.55,color)
    ellipse(cx+r*.48,cy-r*.28,r*.55,r*.55,color)
    poly([(cx-r,cy-r*.22),(cx+r,cy-r*.22),(cx,cy+r*1.13)],color)

def png_bytes():
    def chunk(tag,data):
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    raw=b''.join(b'\0'+bytes(row) for row in pixels)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')

def draw():
    for y in range(H):
        for x in range(W):
            glow=max(0, 1-math.hypot((x-320)/460,(y-290)/500))
            pixels[y][x*3:x*3+3]=bytes((int(19+32*glow+12*y/H),int(24+29*glow+9*y/H),int(55+45*glow+16*y/H)))
    rng=random.Random(77123)
    for _ in range(135):
        x,y=rng.randrange(27,610),rng.randrange(24,613)
        if 138<x<526 and 155<y<540: continue
        radius=rng.choice((1.1,1.4,1.9,2.2))
        ellipse(x,y,radius*2.4,radius*2.4,(254,217,187),.12)
        ellipse(x,y,radius,radius,(255,242,208),.75)
    ellipse(114,121,38,38,(255,229,170))
    ellipse(130,105,38,38,(34,48,87))
    for x,y,s in [(465,106,12),(565,199,9),(97,333,7),(558,474,10),(222,65,7),(90,506,6)]:
        line([(x-s,y),(x+s,y)],(255,232,174),1.5)
        line([(x,y-s),(x,y+s)],(255,232,174),1.5)
        ellipse(x,y,3,3,(255,248,227))
    for radius,alpha in [(225,.025),(195,.025),(165,.03)]:
        ellipse(324,350,radius,radius,(255,210,195),alpha)
    ellipse(314,545,228,31,(10,14,42),.55)
    ellipse(318,523,214,24,(255,226,233))
    ellipse(318,522,175,14,(226,162,198))
    ellipse(490,410,91,94,(252,231,236))
    ellipse(492,404,61,65,(47,52,92))
    poly([(213,317),(220,208),(284,277)],(210,128,77))
    poly([(234,284),(232,238),(263,274)],(255,178,169))
    poly([(358,281),(410,215),(396,333)],(210,128,77))
    poly([(367,280),(399,243),(393,304)],(255,178,169))
    ellipse(459,266,24,86,(245,220,228),angle=.14)
    ellipse(507,282,24,87,(245,220,228),angle=.31)
    ellipse(459,266,10,63,(240,163,189),angle=.14)
    ellipse(507,282,10,62,(240,163,189),angle=.31)
    ellipse(306,342,127,109,(210,123,72))
    ellipse(305,333,119,105,(246,171,104))
    ellipse(268,382,63,42,(255,241,220))
    ellipse(344,382,63,42,(255,241,220))
    ellipse(222,371,28,17,(237,123,120),.6)
    ellipse(379,371,28,17,(237,123,120),.6)
    line([(244,344),(254,352),(266,354),(280,350)],(91,55,67),3)
    line([(331,349),(347,354),(362,351),(370,343)],(91,55,67),3)
    heart(306,387,8,(95,64,73))
    line([(307,394),(307,403),(299,410),(291,408)],(97,68,76),2)
    line([(307,403),(315,410),(322,407)],(97,68,76),2)
    ellipse(470,357,71,74,(226,194,208))
    ellipse(470,350,68,70,(252,237,240))
    ellipse(447,361,11,13,(71,59,79))
    ellipse(494,361,11,13,(71,59,79))
    ellipse(444,356,4,4,(255,255,255))
    ellipse(491,356,4,4,(255,255,255))
    ellipse(431,387,20,10,(244,151,169),.72)
    ellipse(508,387,20,10,(244,151,169),.72)
    heart(470,389,5,(173,105,126))
    heart(410,213,21,(255,177,196))
    ellipse(400,204,3,3,(255,244,231))
    ellipse(324,448,187,74,(110,107,169))
    ellipse(323,433,182,73,(172,167,233))
    line([(160,439),(206,416),(258,440),(310,429),(360,441),(418,425),(488,437)],(238,223,251),4)
    for x,y in [(253,473),(371,465),(438,465)]:
        line([(x-8,y),(x+8,y)],(234,228,255),1.5)
        line([(x,y-8),(x,y+8)],(234,228,255),1.5)
    poly([(136,443),(178,505),(226,527),(321,534),(423,525),(470,502),(503,443)],(240,187,207))
    poly([(149,450),(184,497),(226,517),(321,525),(412,516),(462,491),(493,450)],(255,224,224))
    ellipse(320,444,185,22,(255,242,236))
    ellipse(320,443,171,12,(227,174,192))
    ellipse(318,482,49,35,(255,245,231),.66)
    heart(318,479,19,(233,131,155))
    line([(319,496),(320,512)],(113,147,125),2)
    ellipse(305,503,12,6,(127,174,147),angle=-.5)
    ellipse(333,504,12,6,(127,174,147),angle=.5)
    ellipse(257,439,19,12,(255,242,223))
    ellipse(361,439,19,12,(255,242,223))
    ellipse(471,438,16,11,(251,239,244))
    for x,y in [(140,562),(195,579),(475,570),(536,552)]:
        ellipse(x,y,3,3,(255,235,207))

if __name__=='__main__':
    draw()
    output=Path(os.environ.get('MAKEFUN_OUTPUT_DIR','/output'))
    output.mkdir(parents=True,exist_ok=True)
    (output/'entry.png').write_bytes(png_bytes())
