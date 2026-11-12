# Ken Burns: recorta janela 9:16 dentro do retângulo da foto e desliza/zoom suave
import sys, subprocess, json
from PIL import Image
src, out, dur, rect, x0, x1, z0, z1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), json.loads(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8])
FPS=30; W,H=1080,1920
im=Image.open(src).convert("RGB"); SW,SH=im.size
rx0,ry0,rx1,ry1=[rect[0]*SW,rect[1]*SH,rect[2]*SW,rect[3]*SH]
ph=ry1-ry0
n=round(dur*FPS)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
for i in range(n):
    u=i/max(1,n-1); u=u*u*(3-2*u)  # ease in-out
    z=z0+(z1-z0)*u
    ch=ph/z; cw=ch*9/16
    cx=(x0+(x1-x0)*u)*SW
    cx=min(max(cx,rx0+cw/2),rx1-cw/2)
    cy=(ry0+ry1)/2
    box=(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)
    fr=im.transform((W,H),Image.EXTENT,box,Image.BICUBIC)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
