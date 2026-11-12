# View Estoril / Open Mall – vídeo alto padrão (identidade azul)
import json, subprocess, sys, os
D=sys.argv[1]; SRC=f"{D}/original.mov"; FPS=30; HR=f"{D}/hr"
words=[[s,e,t.strip()] for seg in json.load(open(f"{D}/tr.json")) for s,e,t in seg["words"]]
m=[]
for w in words:   # junta "R" + "$420", "recém" + "-entregue"
    if m and (w[2].startswith("-") or w[2].startswith("$")): m[-1]=[m[-1][0],w[1],m[-1][2]+w[2]]
    else: m.append(w)
words=m
CUTS=[(0.0,0.70),(13.04,13.44),(17.59,17.90),(40.61,40.96),(47.40,47.68)]   # só silêncios verificados
END_SRC=74.40
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
VT=sum(b-a for a,b in SEGS); ENDC=3.0; T=VT+ENDC
# cartões do book: (src_ini, src_fim, pagina, rect, x0, x1, z0, z1, rótulo, sub)
MALL=[.47,.615,.97,.885]
BR=[(22.20,24.70,"04",[.20,.24,.86,.75],.415,.43,1.90,2.00,"VIEW ESTORIL","BY EMCCAMP"),
    (26.30,29.45,"05",MALL,.62,.80,1.00,1.04,"OPEN MALL","ASSINATURA DAVID GUERRA"),
    (29.45,31.10,"05",MALL,.62,.66,1.75,1.85,"17 LOJAS + 4 SALAS","VIRADO PARA A BARÃO"),
    (31.10,33.20,"04",[.20,.24,.86,.75],.52,.56,1.00,1.05,"+18 MIL M² DE TERRENO",None),
    (33.20,36.95,"07",[.38,.02,.99,.98],.66,.70,1.00,1.05,"3 TORRES","1, 2 E 3 QUARTOS"),
    (49.30,53.60,"05",MALL,.80,.64,1.10,1.18,"SEU SHOPPING NA PORTA","VIEW OPEN MALL"),
    (61.90,63.50,"15",[.0,.30,.50,.80],.25,.25,1.00,1.05,"LIVING",None),
    (63.50,65.00,"20",[.03,.13,.95,.90],.50,.50,1.00,1.05,"APARTAMENTO DECORADO",None),
    (65.00,67.40,"11",[.0,.20,1.0,1.0],.50,.56,1.00,1.05,"PISCINA ADULTO E INFANTIL",None),
    (67.40,69.10,"08",[.0,.18,1.0,.98],.50,.46,1.00,1.05,"ACADEMIA",None),
    (69.10,70.90,"10",[.0,.07,1.0,.90],.50,.54,1.00,1.05,"SALÃO DE FESTAS",None),
    (70.90,72.80,"09",[.0,.11,1.0,.93],.50,.46,1.00,1.05,"CHURRASQUEIRA GOURMET",None)]
CARD_Y=330
os.makedirs(f"{D}/clips",exist_ok=True)
clips=[]
for k,(s_,e_,pg,rect,x0,x1,z0,z1,lab,sub) in enumerate(BR):
    A=round(o(s_)*FPS)/FPS; B=round(o(e_)*FPS)/FPS
    contig=bool(clips) and abs(clips[-1][1]-A)<0.1
    if contig: A=clips[-1][1]
    clips.append([A,B,f"{D}/clips/c{k}.mov",lab,sub,pg,rect,x0,x1,z0,z1,not contig])
for k,c in enumerate(clips):
    dur=round((c[1]-c[0])*FPS)/FPS; c[1]=c[0]+dur
    fout=(k==len(clips)-1) or abs(clips[k+1][0]-c[1])>0.1
    if not os.path.exists(c[2]):
        subprocess.run(["python3","-I",f"{D}/kbo.py",f"{HR}/p-{c[5]}.png",c[2],str(dur),json.dumps(c[6]),str(c[7]),str(c[8]),str(c[9]),str(c[10]),str(int(c[11])),str(int(fout))],check=True)
clips=[tuple(c[:5]) for c in clips]
endclip=f"{D}/clips/end.mov"
if not os.path.exists(endclip):
    subprocess.run(["python3","-I",f"{D}/kbo.py",f"{HR}/p-05.png",endclip,str(ENDC),json.dumps(MALL),".70",".72","1.0","1.05","1","0"],check=True)
# ---------- textos ----------
def ts(x): x=max(0,x); return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
LB="&HFFB85C&"; W="&HFFFFFF&"
HEAD="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,470,1
Style: Box,Inter ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H0045250B,&H0045250B,-1,0,0,0,100,100,1,0,3,20,0,8,80,80,250,1
Style: BoxL,Inter ExtraBold,70,&H0045250B,&H00FFFFFF,&H00FFB85C,&H00FFB85C,-1,0,0,0,100,100,1,0,3,20,0,8,80,80,250,1
Style: Lab,Inter ExtraBold,58,&H00FFFFFF,&H00FFFFFF,&H3045250B,&H3045250B,-1,0,0,0,100,100,5,0,3,16,0,8,60,60,262,1
Style: LabS,Inter ExtraBold,40,&H00FFB85C,&H00FFFFFF,&H3045250B,&H3045250B,-1,0,0,0,100,100,6,0,3,12,0,8,60,60,972,1
Style: Price,Inter Display Black,120,&H00FFFFFF,&H00FFFFFF,&H0045250B,&H0045250B,-1,0,0,0,100,100,1,0,3,26,0,8,60,60,345,1
Style: PriceS,Inter ExtraBold,46,&H0045250B,&H00FFFFFF,&H00FFB85C,&H00FFB85C,-1,0,0,0,100,100,4,0,3,14,0,8,60,60,470,1
Style: LT,Inter Display Black,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,5,0,1,4.5,3,1,80,80,600,1
Style: LTs,Inter Display Bold,40,&H00FFB85C,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,8,0,1,3.5,3,1,82,80,555,1
Style: Brand,Inter Display Light,120,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,26,0,1,2,6,8,60,60,150,1
Style: Disc,Inter Medium,28,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,60,60,60,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
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
        parts=[("{\\c"+LB+"}"+x[2].rstrip(",.?!").upper()+"{\\c"+W+"}") if k==j else x[2].rstrip(",.?!").upper() for k,x in enumerate(ch)]
        ev.append(f"Dialogue: 0,{ts(ws)},{ts(we)},Cap,,0,0,0,,"+" ".join(parts))
POP="{\\fscx55\\fscy55\\t(0,110,\\fscx106\\fscy106)\\t(110,190,\\fscx100\\fscy100)\\fad(0,150)}"
FADE="{\\fad(160,160)}"
def add(a,b,style,text,fx=None,layer=2):
    ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{fx if fx is not None else (POP if style in ('Box','BoxL','Price') else FADE)}{text}")
add(0,o(5.00),"Box","O QUE DÁ CERTO,\\NSE REPETE.")
add(0.6,o(5.00),"LT","VAGNO SILVA",fx="{\\fad(250,200)\\move(130,1190,80,1190,0,350)}")
add(0.8,o(5.00),"LTs","GERENTE · MYBROKER RAJA",fx="{\\fad(250,200)\\pos(82,1244)}")
add(o(10.48),o(17.55),"Box","BRIZZE ESTORIL")
add(o(11.3),o(17.55),"PriceS","SUCESSO DE VENDAS · RECÉM-ENTREGUE",fx="{\\fad(200,150)\\pos(540,410)}")
add(o(18.0),o(22.15),"Box","NA MESMA AVENIDA:\\NALGO AINDA MAIOR")
for (A,B,f,lab,sub) in clips:
    if lab: add(A+0.05,B,"Lab",lab,fx="{\\fad(120,100)\\fscx92\\fscy92\\t(0,180,\\fscx100\\fscy100)}")
    if sub: add(A+0.12,B,"LabS",sub)
grp=[]
for (A,B,f,lab,sub) in clips:
    if grp and abs(grp[-1][1]-A)<0.05: grp[-1][1]=B
    else: grp.append([A,B])
for A,B in grp: add(A,B,"Disc","Imagens meramente ilustrativas",fx="",layer=1)
add(o(37.36),o(44.15),"Box","PARA O INVESTIDOR")
add(o(40.0),o(44.15),"PriceS","A REGIÃO QUE MAIS ALUGA EM BH",fx="{\\fad(200,150)\\pos(540,410)}")
add(o(44.22),o(47.35),"BoxL","5 MIN DO BH SHOPPING")
add(o(47.70),o(49.25),"BoxL","ACESSO À RAJA")
add(o(54.20),o(61.85),"Price","R$ 420 MIL")
add(o(54.20),o(55.25),"PriceS","APARTAMENTOS A PARTIR DE",fx="{\\fad(150,100)\\pos(540,235)}")
add(o(55.30),o(61.85),"PriceS","APARTAMENTOS A PARTIR DE",fx="{\\pos(540,235)}")
add(o(57.40),o(61.85),"Box","MODALIDADE ASSOCIATIVA",fx="{\\fad(200,150)\\pos(540,600)\\an8\\fs52}")
add(o(72.86),VT,"BoxL","ME CHAMA AQUI")
# cartela final
add(VT,T,"Brand","VIEW",fx="{\\fad(300,0)\\fsp40\\t(0,1500,\\fsp26)}")
add(VT+0.3,T,"LabS","OPEN MALL · ESTORIL · BH",fx="{\\fad(250,0)}")
add(VT+0.5,T,"BoxL","ME CHAMA AQUI",fx="{\\fad(250,0)\\pos(540,1110)\\an8}")
add(VT,T,"Disc","Imagens meramente ilustrativas",fx="",layer=1)
open(f"{D}/v7.ass","w").write(HEAD+"\n".join(ev)+"\n")
print(f"video {VT:.2f}s total {T:.2f}s, {len(clips)} cartões")
# ---------- render ----------
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
GRADE="eq=contrast=1.07:saturation=1.06:gamma=0.98,colorbalance=rs=-0.03:bs=0.05:bm=0.02:rh=-0.01:bh=0.02,unsharp=5:5:0.35"
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
    nfe=round(ENDC*FPS)
    run(["-ss","73.9","-i",SRC,"-i",endclip,"-f","lavfi","-i","anullsrc=r=48000:cl=mono","-filter_complex",
         f"[0:v]trim=end_frame=1,scale=1080:1920,setsar=1,{GRADE},eq=brightness=-0.22,gblur=sigma=10,loop=loop={nfe}:size=1,fps={FPS},trim=end_frame={nfe},setpts=PTS-STARTPTS[bg];"
         f"[1:v]format=yuva420p[cd];[bg][cd]overlay=0:{CARD_Y}:eof_action=repeat,trim=end_frame={nfe},format=yuv420p[v];[2:a]atrim=0:{nfe/FPS:.6f}[a]",
         "-map","[v]","-map","[a]","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",endseg])
subprocess.run(["python3","-I",f"{D}/music3.py",f"{D}/music.wav",f"{T:.3f}",f"{o(10.48):.3f}",f"{o(26.30):.3f}",f"{VT:.3f}"],check=True)
ins=[]
for i in range(n+1): ins+=["-i",f"{D}/s{i}.mkv"]
for c in clips: ins+=["-i",c[2]]
NB=n+1; NC=len(clips)
fg=["".join(f"[{i}:v][{i}:a]" for i in range(NB))+f"concat=n={NB}:v=1:a=1[b0][ca]"]
pieces=[]; cur=0; NFT=round(VT*FPS)
for k,(A,B,f,lab,sub) in enumerate(clips):
    a=round(A*FPS); b=round(B*FPS)
    if a>cur: pieces.append(("gap",a-cur))
    pieces.append((k,b-a)); cur=b
if NFT>cur: pieces.append(("gap",NFT-cur))
lbl=[]
for j,(kind,nf) in enumerate(pieces):
    if kind=="gap": fg.append(f"color=c=black@0.0:s=1080x680:r={FPS},format=yuva420p,trim=end_frame={nf},setpts=PTS-STARTPTS[p{j}]")
    else: fg.append(f"[{NB+kind}:v]fps={FPS},format=yuva420p,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={nf},setpts=PTS-STARTPTS[p{j}]")
    lbl.append(f"[p{j}]")
fg.append("".join(lbl)+f"concat=n={len(lbl)}:v=1:a=0,format=yuva420p[trk]")
fg.append(f"[b0][trk]overlay=0:{CARD_Y}:eof_action=pass[b1]")
fg.append(f"[b1]ass={D}/v7.ass,format=yuv420p[vo]")
VOICE=("highpass=f=90,afftdn=nr=8:nf=-40:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
       "deesser=i=0.3,equalizer=f=200:t=q:w=1:g=1.2,equalizer=f=3000:t=q:w=1.5:g=1.2,"
       "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
MI=NB+NC
fg+=[f"[ca]{VOICE},asplit[voz][key]",f"[{MI}:a]volume=0.30,aformat=channel_layouts=stereo[mus]",
     "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[mduck]",
     "[voz][mduck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(ins+["-i",f"{D}/music.wav","-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
    "-c:v","libx264","-preset","medium","-crf","20","-maxrate","9M","-bufsize","18M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/view.mp4"])
