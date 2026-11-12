import numpy as np, wave, json
w=wave.open("b.wav"); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)
hop=int(0.01*sr); win=int(0.02*sr)
rms=np.array([np.sqrt((x[i:i+win]**2).mean()) for i in range(0,len(x)-win,hop)]); db=20*np.log10(rms+1)
def voiced(t):
    i=int(t*sr); f=x[i:i+int(0.03*sr)]
    if len(f)<10: return 0
    f=f*np.hanning(len(f)); ac=np.correlate(f,f,'full')[len(f)-1:]; ac/=ac[0]+1e-9
    return ac[int(sr/350):int(sr/75)].max()
def best(t,span=0.14):
    a=int((t-span)/0.01); b=int((t+span)/0.01)
    k=a+int(np.argmin(db[a:b])); return k*0.01+0.01, db[k]
CL=[("C1",1.45,9.90),("C2",10.00,18.64),("C3",88.80,96.60),("C4",98.85,100.98),("C5",109.00,114.25),
    ("C6",123.72,131.60),("C7",157.70,169.98),("C8",170.08,174.31),("C9",180.42,185.42),("C10",186.82,193.20)]
p90=np.percentile(db,90)
out=[]
for name,a,b in CL:
    sa,da=best(a); sb,db_=best(b)
    out.append([name,round(sa,2),round(sb,2)])
    print(f"{name}: {sa:6.2f} ({da-p90:+5.1f} dB, voz {voiced(sa):.2f})  ->  {sb:6.2f} ({db_-p90:+5.1f} dB, voz {voiced(sb-0.03):.2f})   dur {sb-sa:.2f}s")
json.dump(out,open("clips_b.json","w"))
print("total voz:",round(sum(b-a for _,a,b in out),2),"s")
