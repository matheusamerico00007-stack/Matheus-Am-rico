import numpy as np, subprocess, sys
src,out=sys.argv[1],sys.argv[2]; pts=[float(x) for x in sys.argv[3:]]
def load(f,ss,t,af=None):
    c=["ffmpeg","-v","error","-ss",str(ss),"-t",str(t),"-i",f]+(["-af",af] if af else [])+["-ac","1","-ar","8000","-f","s16le","-"]
    return np.frombuffer(subprocess.run(c,capture_output=True).stdout,np.int16).astype(float)
env=lambda x: np.convolve(np.abs(x),np.ones(80)/80,'same')
for a in pts:
    s=env(load(src,a,4.4,"atempo=1.1")); ot=a/1.1
    m=env(load(out,ot-0.5,5.0)); s-=s.mean(); m-=m.mean()
    print(f"src {a}s: voz {(np.argmax(np.correlate(m,s,'valid'))/8000-0.5)*1000:+.0f} ms")
