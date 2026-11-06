from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

W, H, FPS, DURATION = 1080, 1920, 24, 8
OUT = "output"
os.makedirs(OUT, exist_ok=True)

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def centered(draw, y, text, f, fill, spacing=0):
    box = draw.textbbox((0,0), text, font=f, stroke_width=0)
    x = (W - (box[2]-box[0])) // 2
    draw.text((x,y), text, font=f, fill=fill)

total = FPS * DURATION
for n in range(total):
    t = n / FPS
    im = Image.new("RGB", (W,H), (5,12,27))
    pix = im.load()
    # subtle cinematic blue glow
    for y in range(H):
        v = y / H
        for x in range(W):
            dx=(x-W*0.5)/(W*0.8); dy=(y-H*0.43)/(H*0.8)
            glow=max(0,1-math.sqrt(dx*dx+dy*dy))
            pix[x,y]=(int(5+4*glow), int(12+13*glow), int(27+28*glow))
    d=ImageDraw.Draw(im, "RGBA")
    cx,cy=W//2,H//2-40
    pulse=1+0.018*math.sin(t*2.4)
    # animated orbital rings
    for i in range(4):
        r=int((260+i*34)*pulse + 10*math.sin(t*1.4+i))
        d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=(194,151,73,max(22,100-i*17)), width=3 if i==0 else 2)
    # moving gold light point
    a=t*1.1
    px=cx+int(300*math.cos(a)); py=cy+int(300*math.sin(a))
    d.ellipse((px-13,py-13,px+13,py+13), fill=(255,218,137,210))
    # soft central highlight
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse((cx-250,cy-250,cx+250,cy+250), fill=(198,147,65,20))
    glow=glow.filter(ImageFilter.GaussianBlur(90)); im=Image.alpha_composite(im.convert("RGBA"),glow)
    d=ImageDraw.Draw(im,"RGBA")
    # title enters during first 2 seconds
    alpha=int(255*min(1,max(0,(t-0.65)/0.9)))
    yoff=int(35*(1-min(1,max(0,(t-0.65)/0.9))))
    centered(d,cy-85+yoff,"KILAS FAKTA",font(104,True),(245,224,177,alpha))
    # gold separator
    line_alpha=int(220*min(1,max(0,(t-1.4)/0.7)))
    d.rounded_rectangle((W//2-180,cy+55,W//2+180,cy+61),radius=3,fill=(205,164,91,line_alpha))
    # tagline
    ta=int(255*min(1,max(0,(t-2.0)/0.8)))
    centered(d,cy+120,"MEMBUKA LEMBARAN",font(38,True),(229,232,239,ta))
    centered(d,cy+180,"FAKTA SEJARAH DUNIA",font(38,True),(229,232,239,ta))
    # footer
    fa=int(190*min(1,max(0,(t-3.0)/0.8)))
    centered(d,H-250,"MENELUSURI JEJAK MASA LALU",font(25,False),(202,171,112,fa))
    # sweeping light across title
    if 1.3 < t < 4.0:
        sx=int(-100+(W+200)*(t-1.3)/2.7)
        sweep=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sweep)
        sd.polygon([(sx-55,cy-160),(sx+10,cy-160),(sx+170,cy+90),(sx+105,cy+90)],fill=(255,240,195,32))
        sweep=sweep.filter(ImageFilter.GaussianBlur(24)); im=Image.alpha_composite(im,sweep)
    im.convert("RGB").save(f"{OUT}/frame_{n:04d}.jpg",quality=92)
