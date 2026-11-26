import sys, subprocess, numpy as np, noisereduce as nr
from scipy.signal import butter, sosfiltfilt
D=sys.argv[1]; SR=48000
def load(n):
    b=subprocess.run(["ffmpeg","-v","error","-i",f"{D}/a{n}.m4a","-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(b,np.float32).copy()
def lev(x,fr=480): return 20*np.log10(np.sqrt(np.convolve(x**2,np.ones(fr)/fr,"same")[::fr])+1e-7)
hp=butter(4,80,"highpass",fs=SR,output="sos")
for n in sys.argv[2:]:
    x=sosfiltfilt(hp,load(n)).astype(np.float32)
    e=lev(x); thr=np.percentile(e,22)
    idx=np.where(e<=thr)[0]; noise=np.concatenate([x[i*480:(i+1)*480] for i in idx])
    y=nr.reduce_noise(y=x,sr=SR,y_noise=noise,stationary=True,prop_decrease=float(__import__("os").environ.get("PD","0.75")),n_fft=2048,freq_mask_smooth_hz=500,time_mask_smooth_ms=50)
    pass
    subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","-","-c:a","pcm_s24le",f"{D}/clean2/a{n}.wav"],input=y.astype(np.float32).tobytes(),check=True)
    e2=lev(y); print(n,"ruído",round(np.percentile(e,10),1),"->",round(np.percentile(e2,10),1),"| fala",round(np.percentile(e,90),1),"->",round(np.percentile(e2,90),1))
