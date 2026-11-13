# Trilha "luxury deep house": Rhodes, grave quente, batida discreta. Uso: music3.py out.wav T HIT1 HIT2 END
import numpy as np, wave, sys
SR=48000; out=sys.argv[1]; T,H1,H2,END=map(float,sys.argv[2:6])
N=int(SR*T); rng=np.random.default_rng(5); BPM=124; B=60/BPM; BAR=4*B
L=np.zeros(N); R=np.zeros(N)
def m(n): return 440*2**((n-69)/12)
def add(s,at,g=1.0,pan=0.0):
    i=int(at*SR)
    if i<0: s=s[-i:]; i=0
    e=min(N,i+len(s))
    if i>=N or e<=0: return
    s=s[:e-i]*g; L[i:e]+=s*np.sqrt(0.5*(1-pan)); R[i:e]+=s*np.sqrt(0.5*(1+pan))
def rhodes(notes,dur):
    n=int(dur*SR); x=np.arange(n)/SR; s=np.zeros(n)
    for k in notes:
        f=m(k); trem=1+0.15*np.sin(2*np.pi*4.5*x)
        s+=(np.sin(2*np.pi*f*x+0.8*np.sin(2*np.pi*f*x)*np.exp(-x*6))*np.exp(-x*1.2))*trem
    return s/len(notes)*np.minimum(1,x/0.005)
def pad(notes,dur):
    n=int(dur*SR); x=np.arange(n)/SR; e=np.clip(np.minimum(x/0.8,(dur-x)/1.0),0,1)
    return sum(np.sin(2*np.pi*m(k)*x*(1+d)) for k in notes for d in (-0.002,0.002))*e/len(notes)/2
def kick():
    x=np.arange(int(0.3*SR))/SR; f=48+80*np.exp(-x*40); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*10)
def hat(open_=False):
    x=np.arange(int((0.18 if open_ else 0.05)*SR))/SR; nz=rng.standard_normal(len(x)); nz=nz-np.convolve(nz,np.ones(3)/3,'same')
    return nz*np.exp(-x*(18 if open_ else 80))
def rim():
    x=np.arange(int(0.06*SR))/SR; return (np.sin(2*np.pi*1700*x)*0.5+rng.standard_normal(len(x))*0.4)*np.exp(-x*70)
def bass(k,dur):
    x=np.arange(int(dur*SR))/SR; f=m(k); s=np.sin(2*np.pi*f*x)+0.2*np.sin(4*np.pi*f*x); return s*np.exp(-x*3.5)*np.minimum(1,x/0.004)
prog=[[52,55,59,62,66],[48,52,55,59,62],[55,59,62,66,69],[50,54,57,60,64]]   # Am9 Fmaj9 Cmaj9 G6/9
nb=int(T/B)+2
for i in range(nb):
    t=i*B; bar=i//4; ch=prog[bar%4]; post=t>=END
    if i%4==0 and t<END+BAR: add(pad([n+12 for n in ch[:4]],BAR+1.2),t,0.10)
    if post: continue
    intro = t<H1
    if i%4==0: add(rhodes(ch,BAR*0.95),t,0.18)
    if i%4==2: add(rhodes(ch[1:],B*1.5),t+B*0.5,0.10,0.2)
    if not intro:
        add(kick(),t,0.55)
        add(hat(),t+B/2,0.10,0.3)
        if i%2==1: add(rim(),t,0.10,-0.2)
        if i%8==7: add(hat(True),t+B/2,0.06)
        add(bass(ch[0]-24,B*0.45),t+B/2,0.30)
        if i%4==3: add(bass(ch[0]-24+7,B*0.3),t+B*0.75,0.18)
# transições suaves (sem estouro): sopro de ruído filtrado + sub
for h in (H1,H2):
    x=np.arange(int(1.6*SR))/SR; nz=np.convolve(rng.standard_normal(len(x)),np.ones(20)/20,'same'); add(nz*(x/1.6)**2*0.25,h-1.6)
    xs=np.arange(int(1.4*SR))/SR; add(np.sin(2*np.pi*np.cumsum(40+30*np.exp(-xs*6))/SR)*np.exp(-xs*3),h,0.35)
mix=np.stack([L,R],1)
IRL=int(1.8*SR); ir=rng.standard_normal(IRL)*np.exp(-np.arange(IRL)/SR*3.2); ir[:40]=0; ir/=np.sqrt((ir**2).sum())
M=1<<int(np.ceil(np.log2(N+IRL)))
for c in range(2):
    wet=np.fft.irfft(np.fft.rfft(mix[:,c],M)*np.fft.rfft(ir,M),M)[:N]; mix[:,c]=mix[:,c]*0.85+wet*0.3
fe=int(min(2.5,T-END+0.5)*SR); mix[-fe:]*=np.linspace(1,0,fe)[:,None]
mix=np.tanh(mix*1.2); mix/=np.abs(mix).max()*1.12
w=wave.open(out,'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
