import json, subprocess, sys, os
D=sys.argv[1]; SRC=f"{D}/original.mov"; FPS=30
raw=[w for s in json.load(open(f"{D}/tr.json")) for w in s["words"]]
words=[[s,e,t.strip()] for s,e,t in raw]
# (a,b,kind,zoom,cut_in,cut_out)  kind: face | c1 | c2
SEGS=[(0.00,3.55,"face",1.05,0,1),(3.80,4.98,"face",1.25,1,1),(5.28,9.95,"face",1.05,1,1),(10.10,18.95,"c1",0,1,1),
      (19.22,23.40,"face",1.25,1,1),(23.76,30.40,"c2",0,1,0),(30.40,34.98,"face",1.05,0,1),(35.20,38.00,"face",1.3,1,0)]
HOLD=1.8
SEGS=[(a,a+round((b-a)*FPS)/FPS,*r) for a,b,*r in SEGS]
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
Style: Box,Inter ExtraBold,78,&H00111111,&H00FFFFFF,&H0033D6FF,&H0033D6FF,-1,0,0,0,100,100,0,0,3,20,0,8,80,80,260,1
Style: Dark,Inter ExtraBold,50,&H00FFFFFF,&H00FFFFFF,&H00141418,&H00141418,-1,0,0,0,100,100,0,0,3,22,0,8,90,90,0,1
Style: Year,Inter Display Black,150,&H0033D6FF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,4,0,1,0,6,8,90,90,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]; SFX=[]
chunks=[];cur=[]
for w in words:
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
POP="{\\fscx55\\fscy55\\t(0,110,\\fscx108\\fscy108)\\t(110,190,\\fscx100\\fscy100)\\fad(0,150)}"
def box(A,B,text,y=260,sfx=True):
    ev.append(f"Dialogue: 2,{ts(A)},{ts(B)},Box,,0,0,{y},,{POP}{text}")
    if sfx: SFX.append(A)
box(0.05,o(3.55),"O QUE O McDONALD'S SABE\\NSOBRE IMÓVEIS QUE\\NVOCÊ NÃO SABE?",sfx=False)
box(o(7.04),o(9.95),"NÃO BASTA\\NSER APROVADO")
box(o(20.0),o(23.40),"PELO MUNDO TODO")
A=o(30.55); B=o(34.98)
ev.append(f"Dialogue: 2,{ts(A)},{ts(B)},Year,,0,0,230,,{POP}1956")
ev.append(f"Dialogue: 2,{ts(A+0.35)},{ts(B)},Dark,,0,0,440,,{{\\fad(150,150)}}O McDONALD'S CRIA A\\N{{\\c{Y}}}FRANCHISE REALTY CORP.{{\\c&HFFFFFF&}}\\NSÓ PARA COMPRAR OS TERRENOS\\NDAS FRANQUIAS")
SFX.append(A)
A=o(37.9)
ev.append(f"Dialogue: 3,{ts(A)},{ts(T)},Box,,0,0,260,,{POP}SALVA ESSE VÍDEO")
ev.append(f"Dialogue: 3,{ts(A+0.2)},{ts(T)},Dark,,0,0,400,,{{\\fad(150,0)}}E MANDA PRA QUEM QUER\\NCONSTRUIR PATRIMÔNIO")
SFX.append(A)
# gfx step sfx (relative to card start)
for t in (0.0,0.84,2.02,4.40,6.58): SFX.append(o(10.10)+t)
for t in (0.0,2.5,3.45,4.0): SFX.append(o(23.76)+t)
open(f"{D}/v3.ass","w").write(HEAD+"\n".join(ev)+"\n")
print(f"video {VT:.2f}s total {T:.2f}s")
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
GRADE="hqdn3d=1.5:1.5:6:6,eq=contrast=1.06:saturation=1.12:brightness=0.015"
n=len(SEGS)
for i,(a,b,kind,z,ci,co) in enumerate(SEGS):
    L=b-a; out=f"{D}/s{i}.mkv"; nf=round(L*FPS)
    if os.path.exists(out): continue
    base=f"trim=start={a}:end={a+L+0.2},setpts=PTS-{a}/TB,fps={FPS}:start_time=0,trim=end_frame={nf},setpts=PTS-STARTPTS"
    af=f"atrim=start={a}:end={b},asetpts=PTS-STARTPTS"
    if ci: af+=",afade=t=in:d=0.03"
    if co: af+=f",afade=t=out:st={L-0.04}:d=0.04"
    hold=HOLD if i==n-1 else 0
    af+=f",apad,atrim=0:{L+hold:.6f}"
    pre=["-copyts","-ss",str(max(0,a-2)),"-i",SRC]
    if kind=="face":
        zz=f"({z}+0.04*t/{L})"
        v=f"[0:v]{base},scale=w='trunc(1080*{zz}/2)*2':h='trunc(1920*{zz}/2)*2':eval=frame:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.55,setsar=1,{GRADE}"
        if hold: v+=f",tpad=stop_mode=clone:stop_duration={hold}"
        fg=v+"[v];[0:a:0]"+af+"[a]"
        run(pre+["-filter_complex",fg,"-map","[v]","-map","[a]","-ac","1","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
    else:
        fg=(f"[0:v]{base},crop=1100:1100:420:1450,scale=320:320,{GRADE}[pip];[2:v]format=gray,scale=320:320[m];[pip][m]alphamerge[pc];"
            f"[1:v]fps={FPS},trim=end_frame={nf},setpts=PTS-STARTPTS,format=yuv420p[bg];[bg][pc]overlay=380:1500[t1];[t1][3:v]overlay=368:1488:shortest=1,trim=end_frame={nf},setsar=1[v];[0:a:0]{af}[a]")
        run(pre+["-framerate",str(FPS),"-i",f"{D}/gfx/{kind}_%04d.png","-loop","1","-i",f"{D}/mask.png","-loop","1","-i",f"{D}/ring.png",
                 "-filter_complex",fg,"-map","[v]","-map","[a]","-ac","1","-t",f"{L:.6f}","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
subprocess.run(["python3","-I",f"{D}/beat.py",f"{D}/beat.wav",str(T),str(o(30.40)),str(o(35.20)),str(VT)],check=True)
subprocess.run(["python3","-I",f"{D}/sfx.py",f"{D}/sfx.wav",str(T)]+[f"{x:.3f}" for x in SFX],check=True)
ins=[]
for i in range(n): ins+=["-i",f"{D}/s{i}.mkv"]
VOICE=("highpass=f=80,afftdn=nr=12:nf=-38:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
       "deesser=i=0.4:m=0.5:f=0.5,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3000:t=q:w=1.5:g=1.0,"
       "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
fg=["".join(f"[{i}:v][{i}:a]" for i in range(n))+f"concat=n={n}:v=1:a=1[cv][ca]",
    f"[cv]ass={D}/v3.ass,format=yuv420p[vo]",
    f"[ca]{VOICE},asplit[voz][key]",
    f"[{n}:a]volume=0.28,aformat=channel_layouts=stereo[mus]",
    "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[mduck]",
    f"[{n+1}:a]volume=0.26,aformat=channel_layouts=stereo[fx]",
    "[voz][mduck][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(ins+["-i",f"{D}/beat.wav","-i",f"{D}/sfx.wav","-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
    "-c:v","libx264","-preset","medium","-crf","20","-maxrate","12M","-bufsize","24M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/mcdonalds.mp4"])
