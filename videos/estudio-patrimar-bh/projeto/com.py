import json, subprocess, sys, os
D=sys.argv[1]; SRC=f"{D}/original.mov"; FPS=30
raw=[w for s in json.load(open(f"{D}/tr.json")) for w in s["words"]]
# merge tokens like R + $ + 900 / 100 + %
words=[]
for s,e,t in raw:
    t=t.strip()
    if words and (t in ("$","%") or t.startswith("%") or (words[-1][2]=="R$" and t[:1].isdigit())):
        ps,pe,pt=words[-1]; words[-1]=[ps,e,(pt+t) if t[:1] in "$%" else pt+" "+t]; continue
    words.append([s,e,t])
FIX={"patrimar":"Patrimar","parceras":"parcelas","technojin":"Technogym"}
for w in words:
    for k,v in FIX.items(): w[2]=w[2].replace(k,v)
# segments: (src_a, src_b, zoom, cut_in, cut_out)
SEGS=[(0.00,0.15,1.0,0,1),(0.42,3.80,1.12,1,1),(4.10,8.22,1.28,1,0),(8.22,11.75,1.0,0,0),(11.75,14.60,1.25,0,0),
      (14.60,19.85,1.0,0,0),(19.85,24.25,1.3,0,0),(24.25,29.60,1.0,0,0),(29.60,33.42,1.3,0,1),(33.60,37.25,1.0,1,0),
      (37.25,42.90,1.25,0,0),(42.90,48.78,1.0,0,1),(48.96,51.30,1.25,1,0)]
HOLD=1.6
SEGS=[(a,a+round((b-a)*FPS)/FPS,z,ci,co) for a,b,z,ci,co in SEGS]
def o(t):
    pos=0
    for a,b,*_ in SEGS:
        if t<a: return pos
        if t<=b: return pos+t-a
        pos+=b-a
    return pos+(t-SEGS[-1][1])
VT=sum(b-a for a,b,*_ in SEGS); T=VT+HOLD
def ts(t): t=max(0,t); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
Y="&H33D6FF&"
HEAD="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,520,1
Style: Box,Inter ExtraBold,92,&H00111111,&H00FFFFFF,&H0033D6FF,&H0033D6FF,-1,0,0,0,100,100,0,0,3,20,0,8,80,80,300,1
Style: Sub,Inter ExtraBold,50,&H00FFFFFF,&H00FFFFFF,&H00111111,&H00111111,-1,0,0,0,100,100,2,0,3,14,0,8,80,80,0,1
Style: Chk,Inter ExtraBold,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,5,3,7,90,80,0,1
Style: Disc,Inter Medium,30,&H40FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,60,60,70,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
# --- word-by-word captions (approved style) ---
chunks=[];cur=[]
for i,w in enumerate(words):
    cur.append(w)
    if len(cur)>=3 or w[2][-1:] in ".,?!" or sum(len(x[2]) for x in cur)>14: chunks.append(cur); cur=[]
if cur: chunks.append(cur)
for i,ch in enumerate(chunks):
    nxt=o(chunks[i+1][0][0]) if i+1<len(chunks) else VT
    en=min(nxt,o(ch[-1][1])+0.5)
    for j,w in enumerate(ch):
        ws=o(w[0]); we=o(ch[j+1][0]) if j+1<len(ch) else en
        if we<=ws: continue
        parts=[("{\\c"+Y+"}"+x[2].rstrip(",.?").upper()+"{\\c&HFFFFFF&}") if k==j else x[2].rstrip(",.?").upper() for k,x in enumerate(ch)]
        ev.append(f"Dialogue: 0,{ts(ws)},{ts(we)},Cap,,0,0,0,,"+" ".join(parts))
# --- callouts ---
POP="{\\fscx55\\fscy55\\t(0,110,\\fscx108\\fscy108)\\t(110,190,\\fscx100\\fscy100)\\fad(0,120)}"
SFX=[]
def box(a,b,text,sub=None,y=300):
    A=o(a); B=o(b)
    ev.append(f"Dialogue: 2,{ts(A)},{ts(B)},Box,,0,0,{y},,{POP}{text}")
    if sub: ev.append(f"Dialogue: 2,{ts(A+0.15)},{ts(B)},Sub,,0,0,{y+(250 if '\\N' in text else 150)},,{{\\fad(120,120)}}{sub}")
    SFX.append(A)
box(6.60,8.22,"PARCELAS DE\\NR$ 900","PATRIMAR · REGIÃO HOSPITALAR")
CHK="{\\fnDejaVu Sans\\c"+Y+"}✔{\\fnInter ExtraBold\\c&HFFFFFF&} "
items=[(8.70,"100% REVESTIDO"),(10.18,"VAGA PARA TODOS"),(11.80,"LAZER ENXUTO"),(14.70,"ACADEMIA TECHNOGYM")]
for k,(t0,txt) in enumerate(items):
    ev.append(f"Dialogue: 2,{ts(o(t0))},{ts(o(17.5))},Chk,,0,0,0,,{{\\pos(90,{330+k*95})\\fad(150,150)\\fscx80\\fscy80\\t(0,150,\\fscx100\\fscy100)}}{CHK}{txt}")
    SFX.append(o(t0))
box(21.55,24.25,"R$ 5 MIL/MÊS","NO ALUGUEL TRADICIONAL")
box(25.40,29.60,"AIRBNB LIBERADO","NA CONVENÇÃO DO CONDOMÍNIO")
box(30.40,33.42,"+ DE R$ 9 MIL/MÊS","NO AIRBNB")
box(39.00,40.38,"PARCELAS DE\\NR$ 900")
box(40.38,42.90,"≈ 1% AO MÊS","DE RENTABILIDADE")
box(45.40,48.78,"60% VENDIDO\\NEM 1 SEMANA")
ev.append(f"Dialogue: 3,{ts(o(48.96))},{ts(T)},Box,,0,0,760,,{POP}ME CHAMA AQUI")
ev.append(f"Dialogue: 3,{ts(o(48.96)+0.2)},{ts(T)},Sub,,0,0,910,,{{\\fad(120,0)}}E RECEBA TODAS AS INFORMAÇÕES")
SFX.append(o(48.96))
for a,b in [(19.85,33.42),(37.25,42.90)]:
    ev.append(f"Dialogue: 1,{ts(o(a))},{ts(o(b))},Disc,,0,0,0,,{{\\fad(200,200)}}*Valores estimados. Rentabilidade não garantida.")
open(f"{D}/com.ass","w").write(HEAD+"\n".join(ev)+"\n")
print(f"video {VT:.2f}s total {T:.2f}s")
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
GRADE="eq=contrast=1.06:saturation=1.10:gamma=1.0,unsharp=5:5:0.4"
n=len(SEGS)
for i,(a,b,z,ci,co) in enumerate(SEGS):
    L=b-a; out=f"{D}/s{i}.mkv"
    if os.path.exists(out): continue
    zz=f"({z}+0.03*t/{L})"
    v=(f"trim=start={a}:end={a+L+0.2},setpts=PTS-{a}/TB,fps={FPS}:start_time=0,trim=end_frame={round(L*FPS)},setpts=PTS-STARTPTS,"
       f"scale=w='trunc(1080*{zz}/2)*2':h='trunc(1920*{zz}/2)*2':eval=frame:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.42,setsar=1,{GRADE}")
    if i==n-1: v+=f",tpad=stop_mode=clone:stop_duration={HOLD}"
    af=f"atrim=start={a}:end={b},asetpts=PTS-STARTPTS"
    if ci: af+=",afade=t=in:d=0.03"
    if co: af+=f",afade=t=out:st={L-0.04}:d=0.04"
    af+=f",apad,atrim=0:{L+(HOLD if i==n-1 else 0):.6f}"
    run(["-copyts","-ss",str(max(0,a-2)),"-i",SRC,"-map","0:v:0","-map","0:a:0","-vf",v,"-af",af,"-ac","1",
         "-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
subprocess.run(["python3","-I",f"{D}/beat.py",f"{D}/beat.wav",str(T),str(o(33.60)),str(o(42.90)),str(o(48.96))],check=True)
subprocess.run(["python3","-I",f"{D}/sfx.py",f"{D}/sfx.wav",str(T)]+[f"{x:.3f}" for x in SFX],check=True)
ins=[]
for i in range(n): ins+=["-i",f"{D}/s{i}.mkv"]
VOICE=("highpass=f=80,afftdn=nr=10:nf=-40:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
       "deesser=i=0.4:m=0.5:f=0.5,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3000:t=q:w=1.5:g=1.5,"
       "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
fg=["".join(f"[{i}:v][{i}:a]" for i in range(n))+f"concat=n={n}:v=1:a=1[cv][ca]",
    f"[cv]ass={D}/com.ass,format=yuv420p[vo]",
    f"[ca]{VOICE},asplit[voz][key]",
    f"[{n}:a]volume=0.30,aformat=channel_layouts=stereo[mus]",
    "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[mduck]",
    f"[{n+1}:a]volume=0.28,aformat=channel_layouts=stereo[fx]",
    "[voz][mduck][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(ins+["-i",f"{D}/beat.wav","-i",f"{D}/sfx.wav","-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
    "-c:v","libx264","-preset","medium","-crf","20","-maxrate","12M","-bufsize","24M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/comercial.mp4"])
