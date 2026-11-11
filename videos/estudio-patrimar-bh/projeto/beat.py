import numpy as np, wave, sys
SR=48000; T=float(sys.argv[2]); N=int(SR*T); BPM=118; B=60/BPM
BREAK=(float(sys.argv[3]),float(sys.argv[4]))  # beat drops out
END=float(sys.argv[5])
rng=np.random.default_rng(7)
out=np.zeros((N,2))
def add(sig,at,g=1.0,pan=0.0):
    s=int(at*SR); e=min(N,s+len(sig))
    if s>=N or e<=0: return
    l=np.sqrt(0.5*(1-pan)); r=np.sqrt(0.5*(1+pan))
    out[s:e,0]+=sig[:e-s]*g*l; out[s:e,1]+=sig[:e-s]*g*r
def m(n): return 440*2**((n-69)/12)
def kick():
    x=np.arange(int(0.35*SR))/SR; f=50+120*np.exp(-x*35); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x*9)
def hat():
    x=np.arange(int(0.06*SR))/SR; n=rng.standard_normal(len(x)); n=n-np.convolve(n,np.ones(4)/4,'same'); return n*np.exp(-x*70)
def clap():
    x=np.arange(int(0.2*SR))/SR; n=rng.standard_normal(len(x)); n=n-np.convolve(n,np.ones(8)/8,'same'); return n*np.exp(-x*22)*0.8
def pluck(notes,L=0.45):
    x=np.arange(int(L*SR))/SR; s=sum(np.sin(2*np.pi*m(n)*x)+0.3*np.sin(4*np.pi*m(n)*x)*np.exp(-x*8) for n in notes); return s*np.exp(-x*6)*np.minimum(1,x/0.003)
def pad(notes,L):
    x=np.arange(int(L*SR))/SR; e=np.minimum(1,np.minimum(x/0.4,(L-x)/0.6)).clip(0)
    return sum(np.sin(2*np.pi*m(n)*x*(1+d))*0.5 for n in notes for d in (-0.002,0.002))*e
def bassn(n,L):
    x=np.arange(int(L*SR))/SR; f=m(n); s=np.sin(2*np.pi*f*x)+0.25*np.sin(4*np.pi*f*x); return s*np.exp(-x*4)*np.minimum(1,x/0.005)
prog=[[53,57,60,64],[55,59,62,65],[52,55,59,62],[57,60,64,67]]  # Fmaj7 G7 Em7 Am7
beats=int(T/B)+1
for i in range(beats):
    t=i*B; bar=i//4; ch=prog[bar%4]; inbreak=BREAK[0]<=t<BREAK[1]; post=t>=END
    if i%4==0: add(pad(ch,4*B+0.3),t,0.05 if not inbreak else 0.09)
    if inbreak or post: continue
    add(kick(),t,0.9)
    add(hat(),t+B/2,0.18,0.3); add(hat(),t+B/4*3,0.07,-0.3)
    if i%2==1: add(clap(),t,0.25)
    add(bassn(ch[0]-24,B/2),t+B/2,0.35)
    if i%2==0: add(pluck([n+12 for n in ch[1:]]),t+B*0.75,0.07,0.4)
# riser into the drop back + impact
x=np.arange(int(2.0*SR))/SR; nz=rng.standard_normal(len(x)); add(nz*(x/2)**3*0.12,BREAK[1]-2.0)
xk=np.arange(int(1.5*SR))/SR; add(np.sin(2*np.pi*np.cumsum(40+60*np.exp(-xk*8))/SR)*np.exp(-xk*2.5),BREAK[1],0.7)
add(np.sin(2*np.pi*np.cumsum(40+60*np.exp(-xk*8))/SR)*np.exp(-xk*2.5),END,0.8)
fade=np.ones(N); fl=int(1.2*SR); fade[-fl:]=np.linspace(1,0,fl); out*=fade[:,None]
out=np.tanh(out*1.1); out/=np.abs(out).max()*1.12
w=wave.open(sys.argv[1],'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
