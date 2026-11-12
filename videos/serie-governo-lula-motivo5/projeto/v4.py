import json, subprocess, sys, os
D=sys.argv[1]; SRC=f"{D}/original.mov"; FPS=30
words=[[s,e,t.strip()] for seg in json.load(open(f"{D}/tr.json")) for s,e,t in seg["words"]]
SEGS=[(0.38,2.74,"face",1.05,0,1),(2.88,6.36,"face",1.25,1,1),(6.92,8.93,"face",1.05,1,1),(9.33,14.40,"face",1.2,1,0),
 (14.40,16.70,"g1",0,0,1),(17.50,18.96,"face",1.0,1,1),(19.17,25.62,"face",1.25,1,0),(25.62,31.40,"face",1.05,0,1),
 (32.06,34.20,"face",1.25,1,0),(34.20,42.50,"g2",0,0,1),(42.80,46.40,"face",1.2,1,0),(46.40,52.45,"g3",0,0,0),
 (52.45,55.15,"face",1.05,0,0),(55.15,59.18,"face",1.25,0,1),(59.46,62.45,"face",1.0,1,1),(62.68,67.10,"face",1.25,1,1),
 (67.50,73.45,"face",1.05,1,0),(73.45,82.10,"face",1.2,0,1)]
ENDC=3.8
SEGS=[(a,a+round((b-a)*FPS)/FPS,*r) for a,b,*r in SEGS]
def o(t):
    pos=0
    for a,b,*_ in SEGS:
        if t<a: return pos
        if t<=b: return pos+t-a
        pos+=b-a
    return pos+(t-SEGS[-1][1])
VT=sum(b-a for a,b,*_ in SEGS); T=VT+ENDC
def ts(t): t=max(0,t); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
Y="&H33D6FF&"; W="&HFFFFFF&"
HEAD="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,520,1
Style: Box,Inter ExtraBold,78,&H00111111,&H00FFFFFF,&H0033D6FF,&H0033D6FF,-1,0,0,0,100,100,0,0,3,20,0,8,80,80,260,1
Style: Dark,Inter ExtraBold,54,&H00FFFFFF,&H00FFFFFF,&H00141418,&H00141418,-1,0,0,0,100,100,0,0,3,22,0,8,90,90,0,1
Style: Tag,Inter ExtraBold,40,&H00111111,&H00FFFFFF,&H0033D6FF,&H0033D6FF,-1,0,0,0,100,100,2,0,3,10,0,7,48,48,110,1
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
    en=min(nxt,o(ch[-1][1])+0.5, VT)
    for j,w in enumerate(ch):
        ws=o(w[0]); we=min(o(ch[j+1][0]) if j+1<len(ch) else en, VT)
        if we<=ws: continue
        parts=[("{\\c"+Y+"}"+x[2].rstrip(",.?").upper()+"{\\c"+W+"}") if k==j else x[2].rstrip(",.?").upper() for k,x in enumerate(ch)]
        ev.append(f"Dialogue: 0,{ts(ws)},{ts(we)},Cap,,0,0,0,,"+" ".join(parts))
POP="{\\fscx55\\fscy55\\t(0,110,\\fscx108\\fscy108)\\t(110,190,\\fscx100\\fscy100)\\fad(0,150)}"
def box(A,B,text,y=260,sfx=True,style="Box",layer=2):
    ev.append(f"Dialogue: {layer},{ts(A)},{ts(B)},{style},,0,0,{y},,{POP if style=='Box' else '{\\\\fad(150,150)}'}{text}")
    if sfx: SFX.append(A)
def hl(t): return "{\\c"+Y+"}"+t+"{\\c"+W+"}"
box(0.0,o(1.46),"NÃO INVISTA COM\\NO SEU DINHEIRO",sfx=False)
box(o(1.46),o(2.74),"INVISTA COM O\\NDINHEIRO DO LULA")
box(o(2.88),o(6.36),"MOTIVO #5 DE 5")
box(o(3.1),o(6.36),"INVESTIR EM IMÓVEIS\\NNO GOVERNO LULA",y=400,style="Dark",sfx=False)
box(o(13.1),o(14.40),"DINHEIRO DE\\NTERCEIROS")
box(o(17.6),o(18.96),"NA BOLSA")
box(o(19.2),o(25.62),"SEU GANHO DEPENDE DO\\NQUANTO "+hl("VOCÊ")+" INVESTIU",y=270,style="Dark")
box(o(25.86),o(31.40),"NO BANCO")
box(o(26.3),o(31.40),"JUROS SOBRE O QUE\\N"+hl("VOCÊ")+" COLOCOU",y=400,style="Dark",sfx=False)
box(o(32.2),o(34.20),"NO IMÓVEL\\NÉ DIFERENTE")
box(o(43.0),o(46.40),"VOCÊ PODE USAR\\N"+hl("DINHEIRO DE TERCEIROS"),y=270,style="Dark")
box(o(55.4),o(59.18),"É ASSIM QUE OS\\NRICOS PROSPERAM")
box(o(59.62),o(62.45),"EU TE DESAFIO")
box(o(62.75),o(67.10),"ME FALA UM RICO QUE\\N"+hl("NÃO")+" ALAVANCOU COM IMÓVEIS",y=270,style="Dark")
box(o(64.0),o(67.10),"COMENTA AQUI {\\fnDejaVu Sans Bold}↓",y=470)
box(o(69.18),o(73.45),"AMANHÃ")
box(o(69.5),o(73.45),"A ESTRATÉGIA DOS RICOS\\NPARA ALAVANCAR PATRIMÔNIO",y=400,style="Dark",sfx=False)
box(o(73.8),o(77.3),"EM 20 ANOS:\\N"+hl("SEM DEPENDER DE GOVERNO"),y=270,style="Dark")
box(o(77.3),o(78.95),"NEM DE DIREITA,\\NNEM DE ESQUERDA",y=270,style="Dark",sfx=False)
box(o(79.18),VT,"APOSENTAR\\NTODA A FAMÍLIA")
ev.append(f"Dialogue: 4,{ts(o(6.4))},{ts(VT)},Tag,,0,0,0,,{{\\fad(300,200)}}MOTIVO 5/5")
for st,rel in ((o(14.40),(0,0.82)),(o(34.20),(0.3,1.9,2.3,4.7,6.2)),(o(46.40),(0.58,1.40,2.58,4.86)),(VT,(0,1.1,2.3))):
    for r in rel: SFX.append(st+r)
open(f"{D}/v4.ass","w").write(HEAD+"\n".join(ev)+"\n")
print(f"video {VT:.2f}s total {T:.2f}s")
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
GRADE="hqdn3d=1.2:1.2:5:5,eq=contrast=1.05:saturation=1.06:gamma=1.0,colorbalance=rm=-0.02:bm=0.01"
n=len(SEGS)
for i,(a,b,kind,z,ci,co) in enumerate(SEGS):
    L=b-a; out=f"{D}/s{i}.mkv"; nf=round(L*FPS)
    if os.path.exists(out): continue
    base=f"trim=start={a}:end={a+L+0.2},setpts=PTS-{a}/TB,fps={FPS}:start_time=0,trim=end_frame={nf},setpts=PTS-STARTPTS"
    af=f"atrim=start={a}:end={b},asetpts=PTS-STARTPTS"
    if ci: af+=",afade=t=in:d=0.03"
    if co: af+=f",afade=t=out:st={L-0.04}:d=0.04"
    af+=f",apad,atrim=0:{L:.6f}"
    pre=["-copyts","-ss",str(max(0,a-2)),"-i",SRC]
    if kind=="face":
        zz=f"({z}+0.04*t/{L})"
        fg=(f"[0:v]{base},scale=w='trunc(1080*{zz}/2)*2':h='trunc(1920*{zz}/2)*2':eval=frame:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.45,setsar=1,{GRADE}[v];"
            f"[0:a:0]{af}[a]")
        run(pre+["-filter_complex",fg,"-map","[v]","-map","[a]","-ac","1","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
    else:
        fg=(f"[0:v]{base},crop=1600:1600:300:850,scale=320:320,{GRADE}[pip];[2:v]format=gray,scale=320:320[m];[pip][m]alphamerge[pc];"
            f"[1:v]fps={FPS},tpad=stop_mode=clone:stop_duration=0.2,trim=end_frame={nf},setpts=PTS-STARTPTS,format=yuv420p[bg];"
            f"[bg][pc]overlay=380:1500:shortest=1[t1];[t1][3:v]overlay=368:1488:shortest=1,trim=end_frame={nf},setsar=1[v];[0:a:0]{af}[a]")
        run(pre+["-framerate",str(FPS),"-i",f"{D}/gfx/{kind}_%04d.png","-loop","1","-i",f"{D}/mask.png","-loop","1","-i",f"{D}/ring.png",
                 "-filter_complex",fg,"-map","[v]","-map","[a]","-ac","1","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
endf=f"{D}/s{n}.mkv"; nfe=round(ENDC*FPS)
if not os.path.exists(endf):
    run(["-framerate",str(FPS),"-i",f"{D}/gfx/g4_%04d.png","-f","lavfi","-i","anullsrc=r=48000:cl=mono",
         "-filter_complex",f"[0:v]fps={FPS},tpad=stop_mode=clone:stop_duration=0.2,trim=end_frame={nfe},setpts=PTS-STARTPTS,format=yuv420p,setsar=1[v];[1:a]atrim=0:{nfe/FPS:.6f}[a]",
         "-map","[v]","-map","[a]","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",endf])
subprocess.run(["python3","-I",f"{D}/beat.py",f"{D}/beat.wav",str(T),str(o(59.46)),str(o(67.50)),str(VT)],check=True)
subprocess.run(["python3","-I",f"{D}/sfx.py",f"{D}/sfx.wav",str(T)]+[f"{x:.3f}" for x in SFX],check=True)
ins=[]
for i in range(n+1): ins+=["-i",f"{D}/s{i}.mkv"]
VOICE=("highpass=f=80,afftdn=nr=12:nf=-38:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
       "deesser=i=0.4:m=0.5:f=0.5,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3000:t=q:w=1.5:g=1.0,"
       "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
fg=["".join(f"[{i}:v][{i}:a]" for i in range(n+1))+f"concat=n={n+1}:v=1:a=1[cv][ca]",
    f"[cv]ass={D}/v4.ass,format=yuv420p[vo]",
    f"[ca]{VOICE},asplit[voz][key]",
    f"[{n+1}:a]volume=0.27,aformat=channel_layouts=stereo[mus]",
    "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[mduck]",
    f"[{n+2}:a]volume=0.24,aformat=channel_layouts=stereo[fx]",
    "[voz][mduck][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(ins+["-i",f"{D}/beat.wav","-i",f"{D}/sfx.wav","-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
    "-c:v","libx264","-preset","medium","-crf","20","-maxrate","9M","-bufsize","18M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/motivo5.mp4"])
