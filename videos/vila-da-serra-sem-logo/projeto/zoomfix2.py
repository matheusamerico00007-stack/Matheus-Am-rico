import cv2,numpy as np,subprocess,sys
src,out=sys.argv[1],sys.argv[2]; W,H=1080,1920; ZM=1.26
WIN=[(23.28,23.45,24.35,24.52)]   # (início, cheio, começa a sair, fim)
def z(t):
    for a,b,c,d in WIN:
        if a<=t<=d:
            if t<b: u=(t-a)/(b-a)
            elif t>c: u=1-(t-c)/(d-c)
            else: u=1
            u=u*u*(3-2*u); return 1+(ZM-1)*u
    return 1.0
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","60","-i","-","-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
k=0
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.frombuffer(b,np.uint8).reshape(H,W,3)
    s=z(k/60)
    if s>1.0001:
        M=np.float32([[s,0,W/2*(1-s)],[0,s,H*(1-s)]])
        f=cv2.warpAffine(f,M,(W,H),flags=cv2.INTER_CUBIC)
    enc.stdin.write(f.tobytes()); k+=1
enc.stdin.close(); enc.wait(); print("ok",k)
