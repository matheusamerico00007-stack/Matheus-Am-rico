import numpy as np, subprocess, sys
def load(f,ss,t):
    b=subprocess.run(["ffmpeg","-v","error","-ss",str(ss),"-t",str(t),"-i",f,"-ac","1","-ar","8000","-f","s16le","-"],capture_output=True).stdout
    return np.frombuffer(b,np.int16).astype(float)
src=sys.argv[1]; out=sys.argv[2]
# (src_time, expected_out_video_time)
for st,ov in [(float(a),float(b)) for a,b in (p.split(":") for p in sys.argv[3:])]:
    s=load(src,st+1,4); o=load(out,ov+1-0.5,5)
    env=lambda x: np.convolve(np.abs(x),np.ones(80)/80,'same')
    s=env(s); o=env(o); s-=s.mean(); o-=o.mean()
    c=np.correlate(o,s,'valid'); lag=np.argmax(c)/8000-0.5
    print(f"src {st}: voz {lag*1000:+.0f} ms em relação à imagem")
