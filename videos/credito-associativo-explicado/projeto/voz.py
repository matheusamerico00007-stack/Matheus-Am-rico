import json,subprocess,numpy as np,sys
D=sys.argv[1]; SR=48000; TL=json.load(open(f"{D}/timeline.json")); T=float(sys.argv[2])
def ld(f):
    b=subprocess.run(["ffmpeg","-v","error","-i",f,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout; return np.frombuffer(b,np.float32).copy()
out=np.zeros(int(T*SR)+SR,np.float32); occ=np.zeros_like(out)
tones=[]
for n,a,b,t0 in TL["segs"]:
    x=ld(f"{D}/clean2/a{n}.wav")[int(a*SR):int(b*SR)]
    fi,fo=int(0.06*SR),int(0.16*SR)
    x[:fi]*=np.linspace(0,1,fi)**2; x[-fo:]*=np.linspace(1,0,fo)**1.5
    i=int(t0*SR); out[i:i+len(x)]+=x; occ[i:i+len(x)]=1
    # tom de ambiente: trechos mais silenciosos do próprio áudio
    fr=480; e=np.sqrt(np.convolve(x**2,np.ones(fr)/fr,"same")[::fr]); q=np.where(e<np.percentile(e,25))[0]
    tones.append(np.concatenate([x[k*fr:(k+1)*fr] for k in q if (k+1)*fr<len(x)]))
tone=np.concatenate(tones); tone=np.tile(tone,int(len(out)/len(tone))+1)[:len(out)]
# suaviza emendas do tom
tone=np.convolve(tone,np.ones(3)/3,"same")
m=1-occ; k=int(0.12*SR); m=np.convolve(m,np.ones(k)/k,"same")
out+=tone*m*0.9
# whoosh discreto em cada troca de áudio
rng=np.random.default_rng(3)
for n,a,b,t0 in TL["segs"][1:]:
    L=int(0.55*SR); w=rng.standard_normal(L).astype(np.float32)
    sp=np.fft.rfft(w); f=np.fft.rfftfreq(L,1/SR); sp*=np.exp(-((f-2500)/2200)**2)+0.3*np.exp(-((f-600)/400)**2); w=np.fft.irfft(sp,L).astype(np.float32)
    env=np.sin(np.linspace(0,np.pi,L))**2.5; w*=env/np.abs(w).max()*0.05
    c=int((t0-0.18)*SR); out[c-L//2:c-L//2+L]+=w
out=out[:int(T*SR)]
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","-","-c:a","pcm_s24le",f"{D}/build/voz.wav"],input=out.tobytes(),check=True)
print("voz ok",len(out)/SR)
