# Animação "shopping nascendo": planta técnica azul se desenha de baixo pra cima -> linha de luz revela o render -> pronto com push-in.
# Saída: cartão RGBA 1080x680 (mesmo canvas dos outros cartões). Uso: anim.py img out.mov dur
import sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src,out,dur=sys.argv[1],sys.argv[2],float(sys.argv[3])
FPS=30; W,H=1080,940; R=28
im=Image.open(src).convert("RGB"); SW,SH=im.size
# janela de enquadramento (mostra o mall inteiro): proporção do cartão
sc=min(1020/SW,860/SH); CW=int(round(SW*sc/2)*2); CH=int(round(SH*sc/2)*2); CX=(W-CW)//2; CY=40
base=im.resize((CW*2,CH*2),Image.LANCZOS)   # imagem inteira, sem recorte
# --- planta técnica (bordas) ---
g=np.asarray(base.convert("L").filter(ImageFilter.GaussianBlur(1.2))).astype(float)
gx=np.zeros_like(g); gy=np.zeros_like(g)
gx[:,1:-1]=g[:,2:]-g[:,:-2]; gy[1:-1,:]=g[2:,:]-g[:-2,:]
mag=np.hypot(gx,gy); mag=np.clip((mag-10)/38,0,1)**0.8
NAVY=np.array([10,31,58],float); LINE=np.array([150,214,255],float)
yy,xx=np.mgrid[0:CH*2,0:CW*2]
grid=((xx%60<2)|(yy%60<2)).astype(float)*0.10
bp=NAVY[None,None,:]*(1-grid[...,None])+np.array([40,80,130])[None,None,:]*grid[...,None]
blueprint=bp*(1-mag[...,None])+LINE[None,None,:]*mag[...,None]
render=np.asarray(base).astype(float)
mask=Image.new("L",(CW,CH),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,CW-1,CH-1),R,fill=255)
sh=Image.new("L",(W,H),0); ImageDraw.Draw(sh).rounded_rectangle((CX,CY+16,CX+CW,CY+CH+16),R,fill=170); sh=sh.filter(ImageFilter.GaussianBlur(22))
border=Image.new("RGBA",(CW,CH),(0,0,0,0)); ImageDraw.Draw(border).rounded_rectangle((0,0,CW-1,CH-1),R,outline=(150,214,255,140),width=3)
def ss(e0,e1,x): t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
n=round(dur*FPS)
T1=1.35; T2=3.05   # fim do desenho / fim da revelação (s)
Hh=CH*2; ys=yy.astype(float)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-c:v","qtrle","-pix_fmt","argb",out],stdin=subprocess.PIPE)
for i in range(n):
    t=i/FPS
    # fase 1: linhas desenhando de baixo pra cima
    f1=ss(0,T1,t); front1=Hh*(1.05-1.15*f1)
    draw=np.clip((ys-front1)/40+1,0,1)     # 1 abaixo da frente
    frame=NAVY[None,None,:]*(1-grid[...,None])+np.array([40,80,130])[None,None,:]*grid[...,None]
    frame=frame*(1-(mag*draw)[...,None])+LINE[None,None,:]*(mag*draw)[...,None]
    # fase 2: revelação do render com linha de luz
    if t>T1*0.85:
        f2=ss(T1*0.85,T2,t); front2=Hh*(1.08-1.2*f2)
        rev=np.clip((ys-front2)/50,0,1)
        frame=frame*(1-rev[...,None])+render*rev[...,None]
        glow=np.exp(-((ys-front2)/22)**2)*(0.9*(1-ss(T2-0.2,T2+0.2,t)))
        frame=frame+np.array([120,190,255])[None,None,:]*glow[...,None]*0.55
    frame=np.clip(frame,0,255).astype(np.uint8)
    # push-in suave ao longo de todo o clipe
    z=1.0   # sem zoom: imagem sempre inteira
    big=Image.fromarray(frame); bw,bh=big.size; cw2,ch2=bw/z,bh/z
    card=big.crop((int((bw-cw2)/2),int((bh-ch2)/2),int((bw+cw2)/2),int((bh+ch2)/2))).resize((CW,CH),Image.BICUBIC).convert("RGBA")
    card.alpha_composite(border)
    a=min(1.0,(i+1)/6)
    fr=Image.new("RGBA",(W,H),(0,0,0,0))
    shadow=Image.new("RGBA",(W,H),(0,0,0,255)); shadow.putalpha(sh.point(lambda v:int(v*a))); fr.alpha_composite(shadow)
    c2=card.copy(); c2.putalpha(mask.point(lambda v:int(v*a))); fr.alpha_composite(c2,(CX,CY+int((1-a)**2*30)))
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
