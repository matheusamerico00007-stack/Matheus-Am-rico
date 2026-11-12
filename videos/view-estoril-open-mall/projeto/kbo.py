# Cartão 16:9 com transparência (RGBA) para sobrepor ao vídeo: sombra, cantos arredondados, entrada/saída suave
import sys, subprocess, json
from PIL import Image, ImageDraw, ImageFilter
src,out,dur,rect,x0,x1,z0,z1,fin,fout=sys.argv[1],sys.argv[2],float(sys.argv[3]),json.loads(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7]),float(sys.argv[8]),int(sys.argv[9]),int(sys.argv[10])
FPS=30; W,H=1080,680; CW,CH=1020,574; CX,CY=30,40; R=30
im=Image.open(src).convert("RGB"); SW,SH=im.size
rx0,ry0,rx1,ry1=rect[0]*SW,rect[1]*SH,rect[2]*SW,rect[3]*SH
bh=min(ry1-ry0,(rx1-rx0)*9/16)
mask=Image.new("L",(CW,CH),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,CW-1,CH-1),R,fill=255)
sh=Image.new("L",(W,H),0); ImageDraw.Draw(sh).rounded_rectangle((CX,CY+16,CX+CW,CY+CH+16),R,fill=170); sh=sh.filter(ImageFilter.GaussianBlur(22))
border=Image.new("RGBA",(CW,CH),(0,0,0,0)); ImageDraw.Draw(border).rounded_rectangle((0,0,CW-1,CH-1),R,outline=(255,255,255,110),width=3)
n=round(dur*FPS); NF=6
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-c:v","qtrle","-pix_fmt","argb",out],stdin=subprocess.PIPE)
for i in range(n):
    u=i/max(1,n-1); u=u*u*(3-2*u)
    z=z0+(z1-z0)*u; ch=bh/z; cw=ch*16/9
    cx=(x0+(x1-x0)*u)*SW; cx=min(max(cx,rx0+cw/2),rx1-cw/2); cy=(ry0+ry1)/2
    card=im.transform((CW,CH),Image.EXTENT,(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.BICUBIC).convert("RGBA")
    card.alpha_composite(border)
    a=1.0; dy=0
    if fin and i<NF: t=(i+1)/NF; a=t; dy=int((1-t)**2*40)
    if fout and i>=n-NF: t=(n-i)/NF; a=min(a,t)
    fr=Image.new("RGBA",(W,H),(0,0,0,0))
    shadow=Image.new("RGBA",(W,H),(0,0,0,255)); shadow.putalpha(sh.point(lambda v:int(v*a)))
    fr.alpha_composite(shadow)
    c2=card.copy(); c2.putalpha(mask.point(lambda v:int(v*a)))
    fr.alpha_composite(c2,(CX,CY+dy))
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
