# Trilha épica de celebração. Uso: music2.py out.wav T E BRK BRKEND SOFT CLX END
import numpy as np, wave, sys
SR=48000; out=sys.argv[1]; T,E,BRK,BRKEND,SOFT,CLX,END=map(float,sys.argv[2:9])
N=int(SR*T); t=np.arange(N)/SR; rng=np.random.default_rng(11)
BPM=76; B=60/BPM; BAR=4*B
def m(n): return 440*2**((n-69)/12)
prog=[[48,55,60,64],[43,55,59,62],[45,52,57,60],[41,53,57,60]]  # C G Am F
L=np.zeros(N); Rr=np.zeros(N)
def add(sig,at,g=1.0,pan=0.0):
    s=int(at*SR); e=min(N,s+len(sig))
    if s>=N or e<=0: return
    sig=sig[:e-s]*g; L[s:e]+=sig*np.sqrt(0.5*(1-pan)); Rr[s:e]+=sig*np.sqrt(0.5*(1+pan))
def env(n,a,r):
    x=np.arange(n)/SR; Ln=n/SR; return np.clip(np.minimum(x/a,(Ln-x)/r),0,1)
def pad(notes,dur,bright=1.0):
    n=int(dur*SR); x=np.arange(n)/SR; s=np.zeros(n)
    for nn in notes:
        f=m(nn)
        for d in (-0.003,0,0.003):
            s+=np.sin(2*np.pi*f*(1+d)*x)+0.3*bright*np.sin(4*np.pi*f*(1+d)*x)+0.12*bright*np.sin(6*np.pi*f*(1+d)*x)
    return s*env(n,0.9,1.2)/len(notes)/3
def piano(nn,dur=2.5):
    n=int(dur*SR); x=np.arange(n)/SR; f=m(nn)
    s=np.sin(2*np.pi*f*x)+0.5*np.sin(4*np.pi*f*x)*np.exp(-x*3)+0.2*np.sin(6*np.pi*f*x)*np.exp(-x*5)
    return s*np.exp(-x*1.6)*np.minimum(1,x/0.004)
def tom(f0=90,dur=0.9,g=1):
    n=int(dur*SR); x=np.arange(n)/SR; f=f0*(1+1.2*np.exp(-x*18))
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*5)
    nz=rng.standard_normal(n)*np.exp(-x*30)*0.3
    return (s+nz)*g
def boom(dur=4.0):
    n=int(dur*SR); x=np.arange(n)/SR; f=32+70*np.exp(-x*5)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*1.1)
    nz=np.convolve(rng.standard_normal(n),np.ones(30)/30,'same')*np.exp(-x*4)*0.8
    return s+nz
def cymbal_swell(dur=2.5):
    n=int(dur*SR); x=np.arange(n)/SR; nz=rng.standard_normal(n); nz=nz-np.convolve(nz,np.ones(5)/5,'same')
    return nz*(x/dur)**2.5*0.35
def snare_roll(dur=2.0):
    n=int(dur*SR); s=np.zeros(n); k=0.0
    while k<dur:
        i=int(k*SR); m_=int(0.06*SR); x=np.arange(m_)/SR; nz=rng.standard_normal(m_); nz=nz-np.convolve(nz,np.ones(6)/6,'same')
        s[i:i+m_]+=(nz*np.exp(-x*40))[:max(0,min(m_,n-i))]*(0.2+0.8*k/dur)
        k+=0.11-0.07*k/dur
    return s*0.5
# --- seções
def section(a,b): return a<=b
k=0; tt=E
while tt<T:
    ch=prog[k%4]
    soft = (tt<BRK) or (SOFT<=tt<CLX)
    post = tt>=END
    if not post or tt<END+BAR:
        add(pad([n+12 for n in ch],BAR+1.4,0.7 if soft else 1.0),tt,0.30 if soft else 0.42)
        add(pad([ch[0]-12],BAR+1.4,0.5),tt,0.22 if (tt>=E+2*BAR and not post) else 0.08)
    if not post:
        # piano arpejo
        arp=[ch[0]+24,ch[2]+12,ch[3]+12,ch[1]+24,ch[3]+12,ch[2]+12,ch[0]+24,ch[3]+12]
        for i,nn in enumerate(arp): add(piano(nn),tt+i*B/2,0.075 if soft else 0.06,0.25 if i%2 else -0.25)
        # tambores (seções fortes)
        if not soft:
            for bt in range(4):
                add(tom(62,1.0,0.85),tt+bt*B,1.0)
                if bt in (1,3): add(tom(110,0.6,0.45),tt+bt*B+B/2,1.0,0.3)
            add(tom(150,0.4,0.3),tt+3.5*B,1.0,-0.3)
            # cordas altas (melodia)
            mel=[ch[3]+24,ch[2]+24,ch[1]+24,ch[2]+24]
            for i,nn in enumerate(mel): add(pad([nn],B*1.05,1.2),tt+i*B,0.16,0.1)
    tt+=BAR; k+=1
# impactos e transições
for cue in (BRK,CLX,END):
    add(cymbal_swell(2.4),cue-2.4,1.0); add(boom(4.5),cue,0.9)
add(snare_roll(2.0),CLX-2.0,1.0)
add(boom(5.0),E,0.55)
mix=np.stack([L,Rr],1)
# reverb simples (FFT)
IRL=int(2.6*SR); ir=rng.standard_normal(IRL)*np.exp(-np.arange(IRL)/SR*2.4); ir[:50]=0; ir/=np.sqrt((ir**2).sum())
M=1<<int(np.ceil(np.log2(N+IRL)))
for c in range(2):
    wet=np.fft.irfft(np.fft.rfft(mix[:,c],M)*np.fft.rfft(ir,M),M)[:N]; mix[:,c]=mix[:,c]*0.8+wet*0.45
# fade final
fe=int(min(3.0,T-END)*SR); mix[-fe:]*=np.linspace(1,0,fe)[:,None]
mix=np.tanh(mix*1.3); mix/=np.abs(mix).max()*1.12
w=wave.open(out,'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
