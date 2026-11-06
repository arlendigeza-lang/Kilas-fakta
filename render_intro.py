from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os
W,H,FPS,DURATION=1080,1920,24,8
OUT="output"; os.makedirs(OUT,exist_ok=True)

def font(size,bold=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,size)

def centered(d,y,s,f,fill):
    b=d.textbbox((0,0),s,font=f); d.text(((W-(b[2]-b[0]))//2,y),s,font=f,fill=fill)

# Build the atmospheric background once; reuse it for every frame.
bg=Image.new("RGB",(W,H),(5,12,27))
halo=Image.new("RGBA",(W,H),(0,0,0,0)); hd=ImageDraw.Draw(halo)
hd.ellipse((W//2-440,H//2-520,W//2+440,H//2+360),fill=(15,35,64,120))
halo=halo.filter(ImageFilter.GaussianBlur(180))
bg=Image.alpha_composite(bg.convert("RGBA"),halo)
for n in range(FPS*DURATION):
    t=n/FPS; im=bg.copy(); d=ImageDraw.Draw(im,"RGBA")
    cx,cy=W//2,H//2-40; pulse=1+0.018*math.sin(t*2.4)
    for i in range(4):
        r=int((260+i*34)*pulse+10*math.sin(t*1.4+i))
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(194,151,73,max(22,100-i*17)),width=3 if i==0 else 2)
    a=t*1.1; px=cx+int(300*math.cos(a)); py=cy+int(300*math.sin(a))
    d.ellipse((px-13,py-13,px+13,py+13),fill=(255,218,137,220))
    alpha=int(255*min(1,max(0,(t-.65)/.9))); yoff=int(35*(1-min(1,max(0,(t-.65)/.9))))
    centered(d,cy-85+yoff,"KILAS FAKTA",font(104,True),(245,224,177,alpha))
    la=int(220*min(1,max(0,(t-1.4)/.7)))
    d.rounded_rectangle((W//2-180,cy+55,W//2+180,cy+61),radius=3,fill=(205,164,91,la))
    ta=int(255*min(1,max(0,(t-2)/.8)))
    centered(d,cy+120,"MEMBUKA LEMBARAN",font(38,True),(229,232,239,ta))
    centered(d,cy+180,"FAKTA SEJARAH DUNIA",font(38,True),(229,232,239,ta))
    fa=int(190*min(1,max(0,(t-3)/.8)))
    centered(d,H-250,"MENELUSURI JEJAK MASA LALU",font(25),(202,171,112,fa))
    if 1.3<t<4:
        sx=int(-100+(W+200)*(t-1.3)/2.7)
        sw=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sw)
        sd.polygon([(sx-55,cy-160),(sx+10,cy-160),(sx+170,cy+90),(sx+105,cy+90)],fill=(255,240,195,35))
        im=Image.alpha_composite(im,sw.filter(ImageFilter.GaussianBlur(24)))
    im.convert("RGB").save(f"{OUT}/frame_{n:04d}.jpg",quality=88)
