import json, subprocess, sys, os
D=sys.argv[1]; SRC=f"{D}/original.mov"; FPS=30; HI=f"{D}/book/hi"
words=[[s,e,t.strip()] for seg in json.load(open(f"{D}/tr.json")) for s,e,t in seg["words"]]
FIX={"origem":"Origem","terraza,":"Terrazzas,","terraza":"Terrazzas","semi":"semi","-suítes.":"-suítes."}
for w in words: w[2]=FIX.get(w[2],w[2])
# merge "semi" + "-suítes."
m=[]
for w in words:
    if m and w[2].startswith("-"): m[-1]=[m[-1][0],w[1],m[-1][2]+w[2]]
    else: m.append(w)
words=m
CUTS=[(0.0,0.30),(8.05,8.47),(13.45,13.80),(14.40,14.85),(20.05,21.62),(23.52,23.82),(29.82,30.16),(39.28,39.60),(43.36,43.74)]
END_SRC=46.95
keep=[];pos=0.0
for a,b in CUTS:
    if a>pos: keep.append((pos,a))
    pos=b
keep.append((pos,END_SRC))
SEGS=[(a,a+round((b-a)*FPS)/FPS) for a,b in keep]
def o(t):
    p=0
    for a,b in SEGS:
        if t<a: return p
        if t<=b: return p+t-a
        p+=b-a
    return p+(t-SEGS[-1][1])
VT=sum(b-a for a,b in SEGS); ENDC=2.6; T=VT+ENDC
# B-roll do book: (src_ini, src_fim, pagina, rect, x0, x1, z0, z1, rotulo, sub)
BR=[(5.30,7.95,"08",[0,0,1,1],.22,.31,1.0,1.08,None,None),
    (16.55,22.45,"10",[0,0,.735,1],.30,.50,1.0,1.06,"+3 MIL M² DE LAZER",None),
    (22.45,23.90,"14",[.25,.08,.965,.97],.47,.56,1.0,1.06,"SALÃO DE FESTAS",None),
    (23.90,26.50,"37",[.64,0,1,1],.72,.84,1.0,1.06,"ESPAÇO KIDS",None),
    (26.50,29.80,"29",[.16,0,.505,.88],.22,.33,1.0,1.06,"BARBEARIA",None),
    (30.16,30.95,"24",[.265,.08,.965,1],.58,.66,1.03,1.08,"PISCINA AQUECIDA","COM RAIA DE 25 M"),
    (30.95,31.75,"21",[.03,0,.745,.97],.36,.46,1.03,1.08,"QUADRA DE TÊNIS","DE SAIBRO"),
    (31.75,32.55,"22",[.04,.11,.985,.88],.48,.58,1.03,1.08,"PISCINA COM","DECK MOLHADO"),
    (32.55,33.36,"36",[.03,.08,.745,.88],.18,.28,1.03,1.08,"PLAYGROUND",None)]
os.makedirs(f"{D}/clips",exist_ok=True)
clips=[]
for k,(s,e,pg,rect,x0,x1,z0,z1,lab,sub) in enumerate(BR):
    A=round(o(s)*FPS)/FPS; B=round(o(e)*FPS)/FPS
    if clips and abs(clips[-1][1]-A)<0.1: A=clips[-1][1]
    dur=round((B-A)*FPS)/FPS; f=f"{D}/clips/c{k}.mp4"
    if not os.path.exists(f):
        subprocess.run(["python3","-I",f"{D}/kb.py",f"{HI}/p-{pg}.png",f,str(dur),json.dumps(rect),str(x0),str(x1),str(z0),str(z1)],check=True)
    clips.append((A,A+dur,f,lab,sub))
endclip=f"{D}/clips/end.mp4"
if not os.path.exists(endclip):
    subprocess.run(["python3","-I",f"{D}/kb.py",f"{HI}/p-08.png",endclip,str(ENDC),json.dumps([0,0,1,1]),".30",".30","1.10","1.0"],check=True)
def ts(t): t=max(0,t); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
Y="&H33D6FF&"; W_="&HFFFFFF&"
HEAD="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,520,1
Style: Box,Inter ExtraBold,78,&H00111111,&H00FFFFFF,&H0033D6FF,&H0033D6FF,-1,0,0,0,100,100,0,0,3,20,0,8,80,80,260,1
Style: Dark,Inter ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00141418,&H00141418,-1,0,0,0,100,100,1,0,3,18,0,8,90,90,0,1
Style: Lab,Inter ExtraBold,66,&H00FFFFFF,&H00FFFFFF,&H50101014,&H50101014,-1,0,0,0,100,100,6,0,3,18,0,8,60,60,290,1
Style: LabS,Inter ExtraBold,42,&H0033D6FF,&H00FFFFFF,&H50101014,&H50101014,-1,0,0,0,100,100,8,0,3,12,0,8,60,60,398,1
Style: Brand,Inter Display Light,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,30,0,1,0,8,8,60,60,330,1
Style: BrandS,Inter Medium,38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,14,0,1,0,6,8,60,60,520,1
Style: Chk,Inter ExtraBold,62,&H00FFFFFF,&H00FFFFFF,&H30101014,&H30101014,-1,0,0,0,100,100,0,0,3,14,0,7,90,80,0,1
Style: Disc,Inter Medium,28,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,60,60,60,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[];SFX=[]
chunks=[];cur=[]
for w in words:
    if w[0]>=END_SRC: break
    cur.append(w)
    if len(cur)>=3 or w[2][-1:] in ".,?!" or sum(len(x[2]) for x in cur)>14: chunks.append(cur); cur=[]
if cur: chunks.append(cur)
for i,ch in enumerate(chunks):
    nxt=o(chunks[i+1][0][0]) if i+1<len(chunks) else VT
    en=min(nxt,o(ch[-1][1])+0.5,VT)
    for j,w in enumerate(ch):
        ws=o(w[0]); we=min(o(ch[j+1][0]) if j+1<len(ch) else en,VT)
        if we<=ws: continue
        parts=[("{\\c"+Y+"}"+x[2].rstrip(",.?").upper()+"{\\c"+W_+"}") if k==j else x[2].rstrip(",.?").upper() for k,x in enumerate(ch)]
        ev.append(f"Dialogue: 0,{ts(ws)},{ts(we)},Cap,,0,0,0,,"+" ".join(parts))
POP="{\\fscx55\\fscy55\\t(0,110,\\fscx108\\fscy108)\\t(110,190,\\fscx100\\fscy100)\\fad(0,150)}"
FADE="{\\fad(150,150)}"
def add(A,B,style,text,y=0,layer=2,fx=None,sfx=True):
    ev.append(f"Dialogue: {layer},{ts(A)},{ts(B)},{style},,0,0,{y},,{fx if fx is not None else (POP if style=='Box' else FADE)}{text}")
    if sfx: SFX.append(A)
add(0,o(3.40),"Box","4 QUARTOS COM\\NQUADRA DE TÊNIS?",sfx=False)
# marca sobre a fachada
a,b=clips[0][0],clips[0][1]
add(a+0.1,b,"Brand","ORIGEM",fx="{\\fad(300,200)\\fsp30\\t(0,1200,\\fsp18)}")
add(a+0.5,b,"BrandS","LUXURY RESIDENCE · TERRAZZAS",sfx=False)
CHK="{\\fnDejaVu Sans\\c"+Y+"}✔{\\fnInter ExtraBold\\c&HFFFFFF&} "
for k,(t0,txt) in enumerate([(7.20,"4 QUARTOS"),(8.58,"2 SUÍTES"),(9.66,"2 SEMISSUÍTES")]):
    ev.append(f"Dialogue: 2,{ts(o(max(t0,7.96)))},{ts(o(11.0))},Chk,,0,0,0,,{{\\pos(90,{330+k*110})\\fad(150,150)\\fscx80\\fscy80\\t(0,150,\\fscx100\\fscy100)}}{CHK}{txt}")
    SFX.append(o(max(t0,7.96)))
add(o(11.0),o(14.40),"Box","SUÍTE MASTER")
for (A,B,f,lab,sub) in clips[1:]:
    if lab: add(A+0.05,B,"Lab",lab,fx="{\\fad(120,100)\\fscx90\\fscy90\\t(0,180,\\fscx100\\fscy100)}")
    if sub: add(A+0.12,B,"LabS",sub,sfx=False)
# aviso só sobre as imagens do book (agrupa clipes contíguos)
grp=[]
for (A,B,f,lab,sub) in clips:
    if grp and abs(grp[-1][1]-A)<0.05: grp[-1][1]=B
    else: grp.append([A,B])
for A,B in grp: add(A,B,"Disc","Imagens meramente ilustrativas",layer=1,fx="",sfx=False)
add(o(34.98),o(37.60),"Box","CONDIÇÕES\\NESPECIAIS")
add(o(41.88),o(44.60),"Box","ÚLTIMAS\\NUNIDADES")
add(o(44.62),VT,"Box","ME CHAMA AQUI")
# cartela final sobre a fachada
add(VT,T,"Brand","ORIGEM",fx="{\\fad(250,0)}",sfx=False)
add(VT+0.2,T,"BrandS","LUXURY RESIDENCE · GUTIERREZ · BH",sfx=False)
add(VT+0.4,T,"Box","ME CHAMA AQUI",y=1240)
add(VT,T,"Disc","Imagens meramente ilustrativas",layer=1,sfx=False)
for (A,B,f,lab,sub) in clips: SFX.append(A)
open(f"{D}/v5.ass","w").write(HEAD+"\n".join(ev)+"\n")
print(f"video {VT:.2f}s total {T:.2f}s, {len(clips)} imagens do book")
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
GRADE="eq=contrast=1.05:saturation=1.10:gamma=0.98,colorbalance=rm=0.02:gm=0.0:bm=-0.03"
n=len(SEGS)
for i,(a,b) in enumerate(SEGS):
    L=b-a; out=f"{D}/s{i}.mkv"; nf=round(L*FPS)
    if os.path.exists(out): continue
    v=(f"[0:v]trim=start={a}:end={a+L+0.2},setpts=PTS-{a}/TB,fps={FPS}:start_time=0,trim=end_frame={nf},setpts=PTS-STARTPTS,"
       f"scale=1080:1920:flags=lanczos,setsar=1,{GRADE}[v]")
    af=f"[0:a:0]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={L-0.04}:d=0.04,apad,atrim=0:{L:.6f}[a]"
    run(["-copyts","-ss",str(max(0,a-2)),"-i",SRC,"-filter_complex",v+";"+af,"-map","[v]","-map","[a]","-ac","1",
         "-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
endseg=f"{D}/s{n}.mkv"
if not os.path.exists(endseg):
    run(["-i",endclip,"-f","lavfi","-i","anullsrc=r=48000:cl=mono","-map","0:v","-map","1:a","-t",f"{ENDC:.6f}","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",endseg])
subprocess.run(["python3","-I",f"{D}/beat.py",f"{D}/beat.wav",str(T),"0","0",str(VT)],check=True)
subprocess.run(["python3","-I",f"{D}/sfx.py",f"{D}/sfx.wav",str(T)]+[f"{x:.3f}" for x in sorted(set(round(s,2) for s in SFX))],check=True)
ins=[]
for i in range(n+1): ins+=["-i",f"{D}/s{i}.mkv"]
for c in clips: ins+=["-i",c[2]]
NB=n+1; NC=len(clips)
fg=["".join(f"[{i}:v][{i}:a]" for i in range(NB))+f"concat=n={NB}:v=1:a=1[b0][ca]"]
last="b0"
for k,(A,B,f,lab,sub) in enumerate(clips):
    fg.append(f"[{NB+k}:v]setpts=PTS-STARTPTS+{A:.4f}/TB[o{k}]")
    fg.append(f"[{last}][o{k}]overlay=enable='between(t,{A:.4f},{B-0.001:.4f})':eof_action=pass[b{k+1}]"); last=f"b{k+1}"
fg.append(f"[{last}]ass={D}/v5.ass,format=yuv420p[vo]")
VOICE=("highpass=f=80,afftdn=nr=12:nf=-38:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
       "deesser=i=0.4:m=0.5:f=0.5,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3000:t=q:w=1.5:g=1.0,"
       "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
MI=NB+NC
fg+=[f"[ca]{VOICE},asplit[voz][key]",f"[{MI}:a]volume=0.27,aformat=channel_layouts=stereo[mus]",
     "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[mduck]",
     f"[{MI+1}:a]volume=0.22,aformat=channel_layouts=stereo[fx]",
     "[voz][mduck][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(ins+["-i",f"{D}/beat.wav","-i",f"{D}/sfx.wav","-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
    "-c:v","libx264","-preset","medium","-crf","20","-maxrate","9M","-bufsize","18M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/origem.mp4"])
