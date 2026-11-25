import cv2, subprocess, numpy as np, json, sys
src,out=sys.argv[1],sys.argv[2]; FPS=4; w,h=540,960
p=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-vf",f"fps={FPS},scale={w}:{h}","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
fc=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
pc=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_profileface.xml")
res=[];i=0
while True:
    b=p.stdout.read(w*h)
    if len(b)<w*h: break
    g=np.frombuffer(b,np.uint8).reshape(h,w); g=cv2.equalizeHist(g)
    f=list(fc.detectMultiScale(g,1.1,5,minSize=(22,22)))
    f+=list(pc.detectMultiScale(g,1.1,5,minSize=(22,22)))
    f+=[(w-x-ww,y,ww,hh) for (x,y,ww,hh) in pc.detectMultiScale(cv2.flip(g,1),1.1,5,minSize=(22,22))]
    res.append([i/FPS,[[int(x*2+ww),int(y*2+hh),int(ww*2)] for (x,y,ww,hh) in f]]); i+=1
json.dump(res,open(out,"w"))
print(len(res))
