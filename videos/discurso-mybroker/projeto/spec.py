import numpy as np, subprocess, sys
def load(f,ss,t):
    b=subprocess.run(["ffmpeg","-v","error","-ss",str(ss),"-t",str(t),"-i",f,"-ac","1","-ar","48000","-f","s16le","-"],capture_output=True).stdout
    return np.frombuffer(b,np.int16).astype(float)/32768
def bands(x):
    X=np.abs(np.fft.rfft(x*np.hanning(len(x))))**2; f=np.fft.rfftfreq(len(x),1/48000)
    tot=X.sum(); return " ".join(f"{lo//1000}-{hi//1000}k:{10*np.log10(X[(f>=lo)&(f<hi)].sum()/tot+1e-12):6.1f}dB" for lo,hi in [(0,300),(300,3000),(3000,6000),(6000,10000),(10000,24000)])
for name,f,ss,t in [("original fala",  "dl/original.mov",21,6),("motiv fala","motivacional.mp4",6.33,6),("corte1 fala","corte1_o-merito-nao-e-meu.mp4",8.8,6),
                    ("original pausa", "dl/original.mov",16.9,1.2),("motiv pausa","motivacional.mp4",2.9,1.1),("trilha so","trilha.wav",20,6),("motiv cartela","motivacional.mp4",58.5,3)]:
    x=load(f,ss,t); print(f"{name:15s} rms={20*np.log10(np.sqrt((x**2).mean())):6.1f}dB clip={(np.abs(x)>0.98).sum():4d} | {bands(x)}")
