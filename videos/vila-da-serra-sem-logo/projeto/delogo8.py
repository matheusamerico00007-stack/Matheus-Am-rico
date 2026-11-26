import cv2, numpy as np, subprocess, sys
src,out,END=sys.argv[1],sys.argv[2],float(sys.argv[3])
W,H=1080,1920; X0,Y0,X1,Y1=360,185,775,350; PAD=50
RANGES=[(0.0,9.80),(23.25,32.70)]
def frame_at(t):
    b=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",src,"-frames:v","1","-f","rawvideo","-pix_fmt","bgr24","-"],capture_output=True).stdout
    return np.frombuffer(b,np.uint8).reshape(H,W,3)
ref=cv2.cvtColor(frame_at(26)[Y0:Y1,X0:X1],cv2.COLOR_BGR2GRAY).astype(np.float32)
bg=cv2.medianBlur(ref.astype(np.uint8),101).astype(np.float32)
ref2=cv2.cvtColor(frame_at(2.6)[Y0:Y1,X0:X1],cv2.COLOR_BGR2GRAY).astype(np.float32)
bg2=cv2.medianBlur(ref2.astype(np.uint8),101).astype(np.float32)
raw=(((ref-bg)>3.5)|((ref2-bg2)>3.5)).astype(np.uint8)
box=np.zeros_like(raw); box[222-Y0:320-Y0,488-X0:730-X0]=1
raw=raw*box
raw=cv2.morphologyEx(raw,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
clean=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
cv2.circle(clean,(440-X0,264-Y0),47,1,-1)
mask=cv2.dilate(clean,np.ones((11,11),np.uint8)); maskT=mask
hp=lambda g: g-cv2.GaussianBlur(g,(0,0),2.5)
tmpl=hp(ref)*cv2.dilate(clean,np.ones((3,3),np.uint8))
cv2.imwrite(sys.argv[4],mask*255)
nf=int(round(END*60))
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-frames:v",str(nf),"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","60","-i","-","-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
big=np.zeros((Y1-Y0+2*PAD,X1-X0+2*PAD),np.uint8)
CX,CY=PAD+200,PAD+80
Lb=np.zeros(big.shape,np.float32); Lb[PAD:PAD+ref.shape[0],PAD:PAD+ref.shape[1]]=cv2.GaussianBlur(np.clip(ref-bg,0,None),(0,0),1)
Mb=big.copy(); Mb[PAD:PAD+mask.shape[0],PAD:PAD+mask.shape[1]]=mask
def aff(sc): return np.float32([[sc,0,(1-sc)*CX],[0,sc,(1-sc)*CY]])
def warpL(sc):
    full=cv2.warpAffine(Lb,aff(sc),(big.shape[1],big.shape[0]))
    return full[PAD:PAD+ref.shape[0],PAD:PAD+ref.shape[1]]
def warpM(sc): return (cv2.warpAffine(Mb.astype(np.float32),aff(sc),(big.shape[1],big.shape[0]))>0.3).astype(np.uint8)
cnt=0;offs=[]
while cnt<nf:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.frombuffer(b,np.uint8).reshape(H,W,3).copy()
    if any(a<=cnt/60<=e for a,e in RANGES):
        R=f[Y0-PAD:Y1+PAD,X0-PAD:X1+PAD]
        g=hp(cv2.cvtColor(R,cv2.COLOR_BGR2GRAY).astype(np.float32))
        tt=cnt/60
        if (23.25<=tt<=24.95 or tt<=1.8):
            Rg=cv2.cvtColor(R,cv2.COLOR_BGR2GRAY).astype(np.float32)
            Rl=np.clip(Rg-cv2.medianBlur(Rg.astype(np.uint8),71).astype(np.float32),0,None)
            best=(-1,1.0)
            for sc in np.arange(0.86,1.07,0.02):
                Ls=warpL(sc); r=cv2.matchTemplate(Rl,Ls,cv2.TM_CCOEFF_NORMED)
                v=float(r[PAD,PAD]) if r.shape[0]>PAD else -1
                if v>best[0]: best=(v,sc)
            scs=([best[1]-0.03,best[1],best[1]+0.03] if best[0]>0.5 else list(np.arange(0.86,1.08,0.03)))
            mm=big.copy()
            for sc in scs: mm|=warpM(sc)
            mx=best[0]; dx,dy=PAD,PAD
        else:
            res=cv2.matchTemplate(g,tmpl,cv2.TM_CCORR_NORMED); _,mx,_,loc=cv2.minMaxLoc(res)
            dx,dy=(loc if mx>0.25 else (PAD,PAD))
            mm=big.copy(); mm[dy:dy+mask.shape[0],dx:dx+mask.shape[1]]=mask
        f[Y0-PAD:Y1+PAD,X0-PAD:X1+PAD]=cv2.inpaint(R,mm,7,cv2.INPAINT_TELEA)
        offs.append((round(cnt/60,2),dx-PAD,dy-PAD,round(mx,2)))
    enc.stdin.write(f.tobytes()); cnt+=1
enc.stdin.close(); enc.wait()
print("frames",cnt)
