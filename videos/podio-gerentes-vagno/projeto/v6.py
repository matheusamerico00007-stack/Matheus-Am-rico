# Vídeo motivacional/celebração – Pódio de gerentes, 1º lugar (equipe Vagno Silva)
import json, subprocess, sys, os, wave
import numpy as np
D=sys.argv[1]; A=f"{D}/a.mov"; B=f"{D}/b.mov"; FPS=30; SR=48000
def fa(x): return round(x*FPS)/FPS
# ---------- roteiro (tempos de origem) ----------
# peças de vídeo: (fonte, ini, fim, zoom0, zoom1, cx)   cx = centro horizontal (0-1) do recorte
# blocos: kind 'amb' (vídeo A com som ambiente) | 'voz' (fala de B; vídeo pode alternar B sincronizado / A b-roll)
CXB={1:0.47,88:0.53,98:0.53,109:0.53,123:0.52,157:0.56,170:0.56,180:0.53,186:0.53}
def cxb(t):
    k=max(k for k in CXB if k<=t+0.5); return CXB[k]
BLOCKS=[
 ("amb",[("A",0.70,3.40,1.00,1.04,.5),("A",5.00,7.40,1.04,1.00,.5),("A",11.00,12.60,1.00,1.05,.5),("A",15.00,18.20,1.02,1.08,.5)]),
 ("voz",(1.56,19.52),[(0,3.2,("A",22.6)),(9.6,12.6,("A",68.0))]),
 ("voz",(88.71,96.74),[(4.8,8.03,("A",30.8))]),
 ("voz",(98.99,100.97),[(0,1.98,("A",10.6))]),
 ("amb",[("A",35.00,40.80,1.00,1.06,.5)]),
 ("voz",(109.01,114.35),[]),
 ("voz",(123.76,131.73),[(3.3,5.9,("A",80.0))]),
 ("voz",(157.81,169.88),[(4.6,7.4,("A",48.0)),(9.6,12.07,("A",82.8))]),
 ("voz",(170.22,174.29),[]),
 ("voz",(180.42,185.43),[(2.1,5.01,("A",69.0))]),
 ("voz",(186.95,193.55),[(5.75,6.60,("A",37.6))]),
 ("amb",[("A",106.80,110.40,1.00,1.05,.5)]),
]
# ---------- linha do tempo ----------
pieces=[]   # (src, ini, nframes, z0, z1, cx)
voice_place=[]; amb_place=[]   # (out_t, src_t0, dur, gain)
marks={}; t=0.0
for bi,blk in enumerate(BLOCKS):
    if blk[0]=="amb":
        for (s,a,b,z0,z1,cx) in blk[1]:
            nf=round((b-a)*FPS); pieces.append((s,a,nf,z0,z1,cx)); amb_place.append((t,a,nf/FPS)); t+=nf/FPS
        marks[f"amb{bi}"]=t
    else:
        a,b=blk[1]; nf_total=round((b-a)*FPS); dur=nf_total/FPS
        marks[f"voz{bi}"]=t
        voice_place.append((t,a,dur))
        cur=0
        for (r0,r1,(src,s0)) in blk[2]:
            f0=round(r0*FPS); f1=min(nf_total,round(r1*FPS))
            if f0>cur: pieces.append(("B",a+cur/FPS,f0-cur,1.30,1.34,cxb(a)))
            pieces.append((src,s0,f1-f0,1.00,1.05,.5)); cur=f1
        if cur<nf_total: pieces.append(("B",a+cur/FPS,nf_total-cur,1.30,1.34,cxb(a)))
        t+=dur
VT=t; T=VT
print(f"duração total {T:.2f}s, {len(pieces)} peças de vídeo")
starts=[];acc=0
for i,blk in enumerate(BLOCKS):
    starts.append(acc)
    if blk[0]=="amb": acc+=sum(round((b-a)*FPS)/FPS for (_,a,b,*_) in blk[1])
    else: acc+=round((blk[1][1]-blk[1][0])*FPS)/FPS
E=starts[1]; BRK=starts[4]; BRKEND=starts[5]; SOFT=starts[7]; CLX=starts[9]; END=starts[11]
def o_voice(src_t):
    for (ot,a,d) in voice_place:
        if a-0.05<=src_t<=a+d+0.05: return ot+(src_t-a)
    return None
# ---------- vídeo: renderizar peças ----------
GRADE="eq=contrast=1.08:saturation=0.96:gamma=0.98,colorbalance=rs=-0.03:bs=0.05:rh=0.06:gh=0.02:bh=-0.05"
os.makedirs(f"{D}/pc",exist_ok=True)
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
for i,(src,a,nf,z0,z1,cx) in enumerate(pieces):
    out=f"{D}/pc/p{i:02d}.mkv"
    if os.path.exists(out): continue
    L=nf/FPS; SRCF=A if src=="A" else B
    zz=f"({z0}+({z1}-{z0})*t/{L:.4f})"
    vf=(f"trim=start={a}:end={a+L+0.3},setpts=PTS-{a}/TB,fps={FPS}:start_time=0,trim=end_frame={nf},setpts=PTS-STARTPTS,"
        f"scale=w='trunc(1080*{zz}/2)*2':h='trunc(1920*{zz}/2)*2':eval=frame:flags=lanczos,"
        f"crop=1080:1920:'max(0,min(iw-1080,iw*{cx}-540))':(ih-1920)*0.38,setsar=1,{GRADE}")
    run(["-copyts","-ss",str(max(0,a-2)),"-i",SRCF,"-an","-vf",vf,"-c:v","libx264","-crf","14","-preset","fast",out])
# ---------- áudio: montar trilhas em amostras exatas ----------
def load(path):
    p=subprocess.run(["ffmpeg","-v","error","-i",path,"-map","0:a:0","-ac","1","-ar",str(SR),"-f","s16le","-"],capture_output=True,check=True)
    return np.frombuffer(p.stdout,np.int16).astype(np.float32)/32768
if not os.path.exists(f"{D}/A48.npy"): np.save(f"{D}/A48.npy",load(A)); np.save(f"{D}/B48.npy",load(B))
xa=np.load(f"{D}/A48.npy"); xb=np.load(f"{D}/B48.npy")
N=int(round(T*SR))+SR
voice=np.zeros(N,np.float32); amb=np.zeros(N,np.float32)
def place(dst,srcx,ot,st,d,fi=0.03,fo=0.03,g=1.0):
    o=int(round(ot*SR)); s=int(round(st*SR)); n=int(round(d*SR))
    seg=srcx[s:s+n].copy()
    if len(seg)<n: seg=np.pad(seg,(0,n-len(seg)))
    a=int(fi*SR); b=int(fo*SR)
    if a: seg[:a]*=np.linspace(0,1,a)
    if b: seg[-b:]*=np.linspace(1,0,b)
    dst[o:o+n]+=seg*g
for (ot,a,d) in voice_place: place(voice,xb,ot,a,d,0.03,0.06)
# ambiente: abertura cheia, celebração no meio, final
for (ot,a,d) in amb_place:
    if ot<E: g=0.9
    elif ot<END: g=0.55
    else: g=0.45
    place(amb,xa,ot,a,d,0.25 if ot==0 else 0.12,0.5 if abs(ot+d-E)<0.05 else 0.12,g)
# o "Bora!" puxa a vibração da galera para o final
bo=voice_place[-1][0]+round(5.75*FPS)/FPS   # início do b-roll da galera pulando (A 37.6)
place(amb,xa,bo,37.6,END-bo,0.15,0.1,0.5)
def wsave(path,x):
    x=np.clip(x,-1,1); w=wave.open(path,'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
wsave(f"{D}/voice.wav",voice[:int(T*SR)]); wsave(f"{D}/amb.wav",amb[:int(T*SR)])
subprocess.run(["python3","-I",f"{D}/music2.py",f"{D}/music.wav",f"{T:.3f}",f"{E:.3f}",f"{BRK:.3f}",f"{BRKEND:.3f}",f"{SOFT:.3f}",f"{CLX:.3f}",f"{END:.3f}"],check=True)
# ---------- legendas e textos ----------
words=[[s,e,x.strip()] for seg in json.load(open(f"{D}/trb.json")) for s,e,x in seg["words"]]
SKIP={"Jardim","no"}
def ts(x): x=max(0,x); return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
GOLD="&H5EC7F2&"; W="&HFFFFFF&"
KEY={"DEUS","DEUS,","RESULTADO","RESPOSTA","OUSADO","DIREÇÃO","CAMINHO","CADA","VOCÊS","DEVOLVE","IMOBILIÁRIA","80%","8","6","MILHÃO","MILHÕES","MOVE","MOTIVA","PLANTANDO","HISTÓRIA","REALIZAR","REALIZADA","31","BORA!","EQUIPE","DEZEMBRO"}
HEAD="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display Bold,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,2,0,1,4.5,3,2,80,80,430,1
Style: Big,Inter Display Black,210,&H005EC7F2,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,4,0,1,5,7,5,60,60,0,1
Style: Kick,Inter Display Bold,48,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,12,0,1,3.5,3,5,60,60,0,1
Style: Num,Inter Display Black,200,&H005EC7F2,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,2,0,1,5,6,8,60,60,300,1
Style: NumS,Inter Display Bold,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,6,0,1,4,4,8,60,60,535,1
Style: LT,Inter Display Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,6,0,1,4.5,4,1,80,80,560,1
Style: LTs,Inter Display Bold,40,&H005EC7F2,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,8,0,1,3.5,3,1,82,80,515,1
Style: Tag,Inter Display SemiBold,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,4,0,1,3.5,4,5,80,80,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
def fmt(ws):
    out=[]
    for w in ws:
        u=w.upper().rstrip(",.")
        out.append("{\\c"+GOLD+"\\b1}"+u+"{\\c"+W+"\\b0}" if u.rstrip("?!,") in KEY or u in KEY else u)
    return " ".join(out)
for (ot,a,d) in voice_place:
    ws=[w for w in words if w[0]>=a-0.05 and w[1]<=a+d+0.4 and w[2] not in SKIP]
    chunks=[];cur=[]
    for w in ws:
        cur.append(w)
        if w[2][-1:] in ",.?!" or len(cur)>=4: chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
    for k,c in enumerate(chunks):
        st=ot+c[0][0]-a-0.04; en=min(ot+c[-1][1]-a+0.35, (ot+chunks[k+1][0][0]-a-0.04) if k+1<len(chunks) else ot+d)
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\fad(110,110)}}"+fmt([x[2] for x in c]))
SLAM="{\\fscx140\\fscy140\\alpha&HFF&\\t(0,180,\\fscx100\\fscy100\\alpha&H00&)\\fad(0,250)}"
POP="{\\fscx60\\fscy60\\t(0,140,\\fscx106\\fscy106)\\t(140,230,\\fscx100\\fscy100)\\fad(0,200)}"
def add(a,b,style,text,fx="{\\fad(200,200)}",layer=2,pos=None):
    p=f"\\pos({pos[0]},{pos[1]})" if pos else ""
    ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{fx[:-1]+p+'}' if fx else '{'+p+'}'}{text}")
# abertura
p0=pieces[0][2]/FPS; p1=p0+pieces[1][2]/FPS; p2=p1+pieces[2][2]/FPS
add(0.15,p0,"Kick","PÓDIO DE GERENTES",pos=(540,330))
add(p1,p2,"Big","1º LUGAR",fx=SLAM,pos=(540,760))
add(p1+0.25,p2,"Kick","EQUIPE SEALS",pos=(540,920))
# lower third quando ele se levanta
add(p2+0.4,E-0.1,"LT","VAGNO SILVA",fx="{\\fad(250,200)\\move(130,1352,80,1352,0,350)}")
add(p2+0.6,E-0.1,"LTs","GERENTE · EQUIPE SEALS",fx="{\\fad(250,200)\\pos(82,1408)}")
# celebração no meio
add(BRK+0.2,BRKEND-0.1,"Big","SEALS",fx=SLAM,pos=(540,780))
add(BRK+0.6,BRKEND-0.1,"Kick","OPERANDO EM QUALQUER CENÁRIO",fx="{\\fad(250,200)}",pos=(540,930))
# números
def numcard(src_a,src_b,big,sub):
    a=o_voice(src_a); b=o_voice(src_b)
    add(a,b,"Num",big,fx=POP); add(a+0.15,b,"NumS",sub)
numcard(109.55,111.25,"80%","DA EQUIPE VENDEU")
numcard(111.70,114.30,"8 DE 10","CORRETORES VENDERAM")
numcard(123.80,127.10,"6","CORRETORES ACIMA\\NDE R$ 1 MILHÃO")
numcard(129.90,131.70,"+R$ 10 MI","EM VENDAS")
# final
add(END+0.15,T,"Big","1º LUGAR",fx=SLAM,pos=(540,1330))
add(END+0.45,T,"Kick","EQUIPE SEALS\\NMYBROKER RAJA",fx="{\\fad(250,0)}",pos=(540,1485))
add(END+1.1,T,"Tag","Operando em qualquer cenário.",fx="{\\fad(400,0)}",pos=(540,1610))
ev.append(f"Dialogue: 1,{ts(END)},{ts(T)},Cap,,0,0,0,,{{\\fad(400,0)\\an7\\pos(0,1100)\\bord0\\shad0\\1c&H000000&\\1a&H60&\\blur40\\p1}}m 0 0 l 1080 0 1080 820 0 820{{\\p0}}")
open(f"{D}/v6.ass","w").write(HEAD+"\n".join(ev)+"\n")
# ---------- composição final ----------
ins=[]
for i in range(len(pieces)): ins+=["-i",f"{D}/pc/p{i:02d}.mkv"]
n=len(pieces)
fg=["".join(f"[{i}:v]" for i in range(n))+f"concat=n={n}:v=1:a=0[cv]",
    f"[cv]vignette=angle=PI/4.6,noise=alls=4:allf=t,ass={D}/v6.ass,format=yuv420p[vo]",
    f"[{n}:a]highpass=f=85,afftdn=nr=8:nf=-40:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
    f"equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.4:g=1.5,deesser=i=0.3,"
    f"acompressor=threshold=-20dB:ratio=2.5:attack=15:release=220,loudnorm=I=-15:TP=-2:LRA=8,aresample={SR},aformat=channel_layouts=stereo,asplit[voz][key]",
    f"[{n+1}:a]aformat=channel_layouts=stereo,volume=1.0[amb]",
    f"[{n+2}:a]volume=0.55,aformat=channel_layouts=stereo[mus]",
    "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=450[mduck]",
    "[voz][mduck][amb]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(ins+["-i",f"{D}/voice.wav","-i",f"{D}/amb.wav","-i",f"{D}/music.wav","-filter_complex",";".join(fg),
    "-map","[vo]","-map","[ao]","-c:v","libx264","-preset","medium","-crf","20","-maxrate","9M","-bufsize","18M",
    "-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/podio_gerentes.mp4"])
json.dump({"voice_place":voice_place,"END":END,"E":E,"T":T},open(f"{D}/timeline.json","w"))
