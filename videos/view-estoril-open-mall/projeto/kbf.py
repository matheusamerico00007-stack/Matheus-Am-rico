# Cartão com a IMAGEM INTEIRA (sem recorte, sem zoom): encaixa na caixa máxima mantendo a proporção.
# Canvas RGBA 1080x940; cartão centralizado na horizontal, topo em y=40. Uso: kbf.py img out.mov dur rect fin fout
import sys, subprocess, json
from PIL import Image, ImageDraw, ImageFilter
src,out,dur,rect,fin,fout=sys.argv[1],sys.argv[2],float(sys.argv[3]),json.loads(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6])
FPS=30; W,H=1080,940; MAXW,MAXH=1020,860; TOP=40; R=28
def size_for(iw,ih):
    s=min(MAXW/iw,MAXH/ih); return int(round(iw*s/2)*2), int(round(ih*s/2)*2)
im=Image.open(src).convert("RGB"); SW,SH=im.size
crop=im.crop((int(rect[0]*SW),int(rect[1]*SH),int(rect[2]*SW),int(rect[3]*SH)))
CW,CH=size_for(*crop.size); CX=(W-CW)//2
card0=crop.resize((CW,CH),Image.LANCZOS).convert("RGBA")
ImageDraw.Draw(card0).rounded_rectangle((0,0,CW-1,CH-1),R,outline=(150,214,255,120),width=3)
mask=Image.new("L",(CW,CH),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,CW-1,CH-1),R,fill=255)
sh=Image.new("L",(W,H),0); ImageDraw.Draw(sh).rounded_rectangle((CX,TOP+16,CX+CW,TOP+CH+16),R,fill=170); sh=sh.filter(ImageFilter.GaussianBlur(22))
n=round(dur*FPS); NF=6
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-c:v","qtrle","-pix_fmt","argb",out],stdin=subprocess.PIPE)
for i in range(n):
    a=1.0; dy=0
    if fin and i<NF: t=(i+1)/NF; a=t; dy=int((1-t)**2*30)
    if fout and i>=n-NF: a=min(a,(n-i)/NF)
    fr=Image.new("RGBA",(W,H),(0,0,0,0))
    s2=Image.new("RGBA",(W,H),(0,0,0,255)); s2.putalpha(sh.point(lambda v:int(v*a))); fr.alpha_composite(s2)
    c=card0.copy(); c.putalpha(Image.composite(card0.getchannel("A"),Image.new("L",(CW,CH),0),mask).point(lambda v:int(v*a)))
    fr.alpha_composite(c,(CX,TOP+dy))
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
print(CW,CH)
