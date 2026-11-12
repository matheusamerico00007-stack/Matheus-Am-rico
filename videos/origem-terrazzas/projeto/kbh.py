# Imagem horizontal 16:9 (pouco recorte) em cartão arredondado sobre fundo desfocado da mesma imagem
import sys, subprocess, json
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
src,out,dur,rect,x0,x1,z0,z1=sys.argv[1],sys.argv[2],float(sys.argv[3]),json.loads(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7]),float(sys.argv[8])
FPS=30; W,H=1080,1920; CW,CH=1020,574; CX,CY=(W-CW)//2,610; R=30
im=Image.open(src).convert("RGB"); SW,SH=im.size
rx0,ry0,rx1,ry1=rect[0]*SW,rect[1]*SH,rect[2]*SW,rect[3]*SH
rw,rh=rx1-rx0,ry1-ry0
bh=min(rh,rw*9/16)   # maior janela 16:9 que cabe na foto
mask=Image.new("L",(CW,CH),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,CW-1,CH-1),R,fill=255)
shadow=Image.new("L",(W,H),0); ImageDraw.Draw(shadow).rounded_rectangle((CX,CY+18,CX+CW,CY+CH+18),R,fill=150); shadow=shadow.filter(ImageFilter.GaussianBlur(28))
# fundo: foto inteira (retângulo) desfocada, cobrindo a tela
full=im.crop((int(rx0),int(ry0),int(rx1),int(ry1)))
sc=max(W/full.width,H/full.height)*1.15
bg0=full.resize((max(1,int(full.width*sc/6)),max(1,int(full.height*sc/6))),Image.BILINEAR)
bg0=bg0.filter(ImageFilter.GaussianBlur(9)); bg0=ImageEnhance.Brightness(bg0).enhance(0.42)
bg0=bg0.resize((int(full.width*sc),int(full.height*sc)),Image.BICUBIC)
n=round(dur*FPS)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
black=Image.new("RGB",(W,H),(0,0,0))
for i in range(n):
    u=i/max(1,n-1); u=u*u*(3-2*u)
    z=z0+(z1-z0)*u; ch=bh/z; cw=ch*16/9
    cx=(x0+(x1-x0)*u)*SW; cx=min(max(cx,rx0+cw/2),rx1-cw/2); cy=(ry0+ry1)/2
    card=im.transform((CW,CH),Image.EXTENT,(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.BICUBIC)
    off=int((bg0.width-W)/2+(u-0.5)*40)
    fr=bg0.crop((off,(bg0.height-H)//2,off+W,(bg0.height-H)//2+H))
    fr=Image.composite(black,fr,shadow)
    fr.paste(card,(CX,CY),mask)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
