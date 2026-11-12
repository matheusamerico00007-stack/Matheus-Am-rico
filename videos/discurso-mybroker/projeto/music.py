import numpy as np, wave, sys
SR=48000; T=float(sys.argv[2]); N=int(SR*T); t=np.arange(N)/SR
CUE=dict(enter=6.10, climax=39.17, end=57.57)
def midi(n): return 440*2**((n-69)/12)
# Am F C G  (vi IV I V) in A minor, chord len
CL=60/70*4
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
out=np.zeros(N); pad=np.zeros(N); arp=np.zeros(N); bass=np.zeros(N); hi=np.zeros(N); hits=np.zeros(N)
def env_lin(x,a,r,L):
    e=np.ones_like(x); e=np.minimum(e,x/a); e=np.minimum(e,(L-x)/r); return np.clip(e,0,1)
nc=int(np.ceil(T/CL))+1
for i in range(nc):
    st=i*CL; ch=chords[i%4]; L=CL+1.2
    s0=int(st*SR); s1=min(N,int((st+L)*SR))
    if s0>=N: break
    x=np.arange(s1-s0)/SR; e=env_lin(x,1.0,1.2,L)
    for n in ch+[ch[0]-12]:
        f=midi(n)
        for d in (-0.15,0.15):
            ff=f*2**(d/12/10)
            w=np.sin(2*np.pi*ff*x)+0.35*np.sin(4*np.pi*ff*x)+0.12*np.sin(6*np.pi*ff*x)
            pad[s0:s1]+=w*e*0.05
        hi[s0:s1]+=np.sin(2*np.pi*f*2*x+0.3)*e*0.035
    bass[s0:s1]+=np.sin(2*np.pi*midi(ch[0]-24)*x)*e*0.25
    # arpeggio 8ths
    step=CL/8; pattern=[0,1,2,1,0+12,2,1,2]
    tones=[ch[0]+12,ch[1]+12,ch[2]+12]
    for k in range(8):
        a=st+k*step; n=(tones*2)[k%6] if k!=4 else ch[0]+24
        s=int(a*SR); L2=2.0; e2=min(N,s+int(L2*SR))
        if s>=N: break
        x2=np.arange(e2-s)/SR; f=midi(n)
        w=(np.sin(2*np.pi*f*x2)+0.4*np.sin(4*np.pi*f*x2)*np.exp(-x2*3)+0.15*np.sin(6*np.pi*f*x2)*np.exp(-x2*5))
        arp[s:e2]+=w*np.exp(-x2*2.2)*np.minimum(1,x2/0.004)*0.10
def boom(at,g=1.0):
    s=int(at*SR); L=int(3.5*SR); e=min(N,s+L); x=np.arange(e-s)/SR
    f=35+40*np.exp(-x*6); ph=2*np.pi*np.cumsum(f)/SR
    w=np.sin(ph)*np.exp(-x*1.3)
    nz=np.random.default_rng(1).standard_normal(len(x)); nz=np.convolve(nz,np.ones(40)/40,'same')*np.exp(-x*5)*0.6
    hits[s:e]+=(w+nz)*g
def swell(at,dur=2.5):
    s=int((at-dur)*SR); e=int(at*SR); x=np.arange(e-s)/SR
    nz=np.random.default_rng(2).standard_normal(len(x)); nz=np.convolve(nz,np.ones(12)/12,'same')
    hits[s:e]+=nz*(x/dur)**3*0.25
def kick(at,g=0.5):
    s=int(at*SR); e=min(N,s+int(0.6*SR)); x=np.arange(e-s)/SR
    f=45+90*np.exp(-x*30); hits[s:e]+=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*7)*g
swell(CUE['enter']); boom(CUE['enter'],0.9)
swell(CUE['climax'],3); boom(CUE['climax'],1.0)
b=60/70; k=CUE['climax']
while k<CUE['end']-0.2: kick(k,0.45); k+=b*2
boom(CUE['end'],1.1)
def auto(points):
    xs,ys=zip(*points); return np.interp(t,xs,ys)
A_pad=auto([(0,0.55),(CUE['enter'],0.75),(CUE['climax'],0.8),(CUE['climax']+0.5,1.1),(CUE['end'],1.2),(T-3.5,1.0),(T,0)])
A_arp=auto([(0,0),(CUE['enter']-0.01,0),(CUE['enter'],0.8),(CUE['climax'],0.9),(CUE['climax']+0.3,1.1),(CUE['end'],1.1),(CUE['end']+0.01,0.6),(T-3,0.3),(T,0)])
A_bass=auto([(0,0),(CUE['climax']-0.01,0),(CUE['climax'],1),(CUE['end']+3,1),(T,0)])
A_hi=auto([(0,0),(CUE['climax']-0.01,0),(CUE['climax']+2,1),(CUE['end'],1.3),(T,0)])
dry=pad*A_pad+arp*A_arp+bass*A_bass+hi*A_hi
# reverb via FFT convolution with exponential noise IR
rng=np.random.default_rng(3); IRL=int(2.8*SR); ir=rng.standard_normal(IRL)*np.exp(-np.arange(IRL)/SR*2.2); ir[0]=0
ir=np.convolve(ir,np.ones(6)/6,'same'); ir/=np.sqrt((ir**2).sum())
M=1<<int(np.ceil(np.log2(N+IRL)))
wet=np.fft.irfft(np.fft.rfft(dry,M)*np.fft.rfft(ir,M),M)[:N]
mix=dry*0.75+wet*0.55+hits*0.8
mix=np.tanh(mix*1.2); mix/=np.abs(mix).max()*1.12
st=np.stack([mix, np.roll(mix,int(0.012*SR))*0.98+mix*0.02],1)
w=wave.open(sys.argv[1],'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
