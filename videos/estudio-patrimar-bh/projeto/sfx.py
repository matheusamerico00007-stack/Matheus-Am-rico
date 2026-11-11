import numpy as np, wave, sys
SR=48000; T=float(sys.argv[2]); N=int(SR*T); out=np.zeros(N)
for at in map(float,sys.argv[3:]):
    x=np.arange(int(0.12*SR))/SR; f=900*np.exp(-x*18)+500
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*35)
    nz=np.random.default_rng(int(at*100)).standard_normal(int(0.18*SR)); xn=np.arange(len(nz))/SR
    sw=(nz-np.convolve(nz,np.ones(6)/6,'same'))*np.sin(np.pi*xn/0.18)**2*0.25
    i=int(max(0,at-0.12)*SR); out[i:i+len(sw)]+=sw[:N-i]
    j=int(at*SR); out[j:j+len(s)]+=s[:N-j]*0.6
out/=max(1e-9,np.abs(out).max()*1.3)
w=wave.open(sys.argv[1],'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
