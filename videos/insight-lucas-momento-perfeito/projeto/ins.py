# INSIGHT – "Não vai voltar a ter apartamento desse valor" (palestra, 2 palestrantes) -> corte de ~3 min
import sys, os, subprocess, json, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import eng; eng.SPEED=1.0
from eng import *
import numpy as np, cv2
S=sys.argv[1]; ENG=os.path.dirname(os.path.abspath(__file__))
SRC=f"{S}/i1/original.mov"; B=f"{S}/i1/build"; os.makedirs(B,exist_ok=True)
GOLD=(242,199,94); LB=(92,184,255); WHITE=(255,255,255); RED=(255,96,96); GREEN=(88,214,141); NAVY=(8,16,32)
SB=lambda a,b:None
# ---------- trechos (tempo da fonte) ----------
KEEP=[(136.20,139.25),(0.62,6.85),(21.30,43.30),(52.35,55.55),(58.05,67.85),(68.85,72.45),(80.86,110.82),(117.90,131.30),(243.95,279.62)]
SPK=lambda t: "A"
raw=json.load(open(f"{S}/i1/tr.json")); WORDS=[[w[0],w[1],w[2].strip()] for s in raw for w in s["words"]]
# energia (para só cortar silêncio de verdade)
au=subprocess.run(["ffmpeg","-v","error","-i",SRC,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
au=np.frombuffer(au,np.int16).astype(np.float32)/32768
fr=int(16000*0.02); env=20*np.log10(np.sqrt(np.convolve(au**2,np.ones(fr)/fr,"same")[::fr])+1e-6)
TH=np.percentile(env,15)+6
def silent(a,b): i,j=int(a/0.02),int(b/0.02); return j>i and env[i:j].max()<TH
# pausas longas dentro dos trechos -> encurta para 0.30s (somente se o meio for silêncio)
PIECES=[]
for a,b in KEEP:
    ws=[w for w in WORDS if a<=w[0]<b]; cur=a
    for k in range(len(ws)-1):
        g0,g1=ws[k][1],ws[k+1][0]
        if g1-g0>0.75:
            c0,c1=g0+0.15,g1-0.15
            if silent(c0,c1): PIECES.append((cur,c0)); cur=c1
    PIECES.append((cur,b))
# alinha a frames
PIECES=[(round(a*FPS)/FPS,round(b*FPS)/FPS) for a,b in PIECES]
OUT=[];acc=0
for a,b in PIECES: OUT.append((a,b,acc)); acc+=b-a
END=acc; ENDC=2.2; T=END+ENDC
def o(t):
    for a,b,s in OUT:
        if a-1e-6<=t<=b+1e-6: return s+(t-a)
    best=min(OUT,key=lambda p: min(abs(t-p[0]),abs(t-p[1]))); a,b,s=best
    return s if abs(t-a)<abs(t-b) else s+(b-a)
print("trechos",len(PIECES),"duração",round(END,2))
# ---------- rastreio do rosto de quem fala ----------
F=json.load(open(f"{S}/i1/faces.json"))
track=[];prev=None
for t,fs in F:
    fs=[f for f in fs if f[1]<1150 and f[2]>=120]
    spk=SPK(t); rng=(380,1080) if spk=="A" else (0,700)
    c=[f for f in fs if rng[0]<=f[0]<=rng[1]]
    if c:
        if prev is None or (prev[2]!=spk): f=max(c,key=lambda f:f[2])
        else: f=min(c,key=lambda f:abs(f[0]-prev[0])+abs(f[1]-prev[1]))
        if prev is not None and prev[2]==spk and abs(f[0]-prev[0])>320: f=[prev[0],prev[1]]
        prev=(f[0],f[1],spk)
    track.append((t,prev[0] if prev else 540,prev[1] if prev else 700))
tt=np.array([x[0] for x in track]); tx=np.array([x[1] for x in track],float); ty=np.array([x[2] for x in track],float)
def smooth(v,sig=1.4):
    k=np.exp(-0.5*(np.arange(-24,25)/ (sig*4))**2); k/=k.sum(); return np.convolve(np.pad(v,24,mode="edge"),k,"valid")
sx,sy=smooth(tx),smooth(ty)
def center(t): return float(np.interp(t,tt,sx)),float(np.interp(t,tt,sy))
# ---------- base (crop dinâmico + zoom alternado nos cortes) ----------
base=f"{B}/base.mkv"
if not os.path.exists(base):
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s","1080x1920","-r",str(FPS),"-i","-",
        "-c:v","libx264","-crf","15","-preset","fast","-pix_fmt","yuv420p",f"{B}/v.mkv"],stdin=subprocess.PIPE)
    for k,(a,b,s) in enumerate(OUT):
        Z=1.32 if k%2==0 else 1.55
        n=round((b-a)*FPS)
        dec=subprocess.Popen(["ffmpeg","-v","error","-ss",f"{a:.3f}","-i",SRC,"-vf",f"fps={FPS}","-frames:v",str(n),"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
        got=0
        while got<n:
            buf=dec.stdout.read(1080*1920*3)
            if len(buf)<1080*1920*3: break
            fr_=np.frombuffer(buf,np.uint8).reshape(1920,1080,3)
            cx,cy=center(a+got/FPS); cw,ch=1080/Z,1920/Z
            x0=min(max(cx-cw/2,0),1080-cw); y0=min(max(cy-ch*0.42,0),1920-ch)
            M=np.float32([[Z,0,-x0*Z],[0,Z,-y0*Z]])
            enc.stdin.write(cv2.warpAffine(fr_,M,(1080,1920),flags=cv2.INTER_LANCZOS4).tobytes()); got+=1; last=fr_
        dec.wait()
        while got<n: enc.stdin.write(cv2.warpAffine(last,M,(1080,1920),flags=cv2.INTER_LANCZOS4).tobytes()); got+=1
    enc.stdin.close(); enc.wait()
    parts="".join(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={b-a-0.012:.4f}:d=0.012[a{k}];" for k,(a,b,s) in enumerate(OUT))
    run(["-i",SRC,"-i",f"{B}/v.mkv","-filter_complex",parts+"".join(f"[a{k}]" for k in range(len(OUT)))+f"concat=n={len(OUT)}:v=0:a=1[a]",
         "-map","1:v","-map","[a]","-c:v","copy","-c:a","pcm_s16le","-ac","1",base])
    os.remove(f"{B}/v.mkv")
# ---------- elementos gráficos (tempo da fonte -> saída) ----------
SERIF_BI="/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
def F_(n,s): return ImageFont.truetype(SERIF_BI,s) if n=="sbi" else font(n,s)
class Box:
    """painel de vidro escuro no topo, acima do rosto"""
    def __init__(s,ts0,ts1,h,fn,y=190,w=980,accent=LB):
        s.t0=o(ts0); s.t1=o(ts1); s.h=h; s.fn=fn; s.y=y; s.w=w; s.acc=accent
    def draw(s,cv,t):
        if not (s.t0<=t<s.t1): return
        u=(t-s.t0)/0.35; sc=0.9+0.1*ease_out_back(min(1,u)); a=min(1,u*2.5)*(1-ss(s.t1-0.25,s.t1,t))
        img=Image.new("RGBA",(s.w,s.h),(0,0,0,0)); d=ImageDraw.Draw(img)
        d.rounded_rectangle((0,0,s.w-1,s.h-1),36,fill=NAVY+(222,),outline=s.acc+(200,),width=3)
        s.fn(img,d,t)
        if sc!=1: img=img.resize((max(2,int(s.w*sc)),max(2,int(s.h*sc))),Image.BICUBIC)
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); x=(W-img.width)//2; y=s.y+(s.h-img.height)//2
        ImageDraw.Draw(sh).rounded_rectangle((x+4,y+14,x+img.width+4,y+img.height+14),36,fill=(0,0,0,int(140*a))); sh=sh.filter(ImageFilter.GaussianBlur(16))
        if a<1: img.putalpha(img.getchannel("A").point(lambda v:int(v*a)))
        cv.alpha_composite(sh); cv.alpha_composite(img,(x,y))
def fa(t,ts,d=0.25): return ss(o(ts),o(ts)+d,t)
def txt(d,xy,s,f,col,a,anchor="mm"):
    if a>0: d.text(xy,s,font=f,fill=col+(int(255*a),),anchor=anchor)
def count(t,ts,v0,v1,d=0.7): return int(v0+(v1-v0)*ss(o(ts),o(ts)+d,t))
els=[]
def hook(img,d,t):
    txt(d,(490,62),"INSIGHT · MERCADO IMOBILIÁRIO",F_("bold",30),LB,1)
    txt(d,(490,150),"De R$ 365 mil",F_("sbi",80),WHITE,fa(t,136.3))
    txt(d,(490,245),"a R$ 800 mil.",F_("sbi",80),GOLD,fa(t,137.4))
els.append(Box(136.20,6.85,320,hook,accent=GOLD))
def preco(img,d,t):
    txt(d,(250,60),"NOVE ANOS ATRÁS",F_("bold",30),(170,185,210),fa(t,28.0))
    if t>=o(30.8): txt(d,(250,135),f"R$ {count(t,30.8,300,365)} MIL",F_("black",64),WHITE,fa(t,30.8))
    txt(d,(730,60),"HOJE",F_("bold",30),GOLD,fa(t,33.4))
    if t>=o(35.7): txt(d,(730,135),f"R$ {count(t,35.7,365,800)} MIL",F_("black",64),GOLD,fa(t,35.7))
    f=ss(o(33.2),o(36.4),t)
    if f>0:
        pts=[(60+k*(860/30),330-((k/30)**1.7)*120-math.sin(k*1.3)*6) for k in range(31)]
        n=max(2,int(31*f)); d.line(pts[:n],fill=GREEN+(255,),width=6,joint="curve")
        x,y=pts[n-1]; d.ellipse((x-9,y-9,x+9,y+9),fill=GREEN+(255,))
    if t>=o(36.6):
        a=fa(t,36.6); d.rounded_rectangle((790,200,950,256),18,fill=GREEN+(int(240*a),)); txt(d,(870,228),"+119%",F_("black",36),NAVY,a)
    txt(d,(490,400),"75 m²  ·  3 QUARTOS  ·  2 VAGAS",F_("bold",34),WHITE,fa(t,38.1))
els.append(Box(27.9,43.30,450,preco,accent=GOLD))
def aluguelhoje(img,d,t):
    txt(d,(490,55),"ALUGUEL NA REGIÃO HOJE",F_("bold",30),(170,185,210),1)
    txt(d,(490,130),"R$ 4.800 a 5.000/mês",F_("black",64),GOLD,fa(t,53.9))
els.append(Box(52.40,55.55,190,aluguelhoje,accent=GOLD))
def barras(img,d,t):
    txt(d,(490,52),"9 ANOS DEPOIS",F_("bold",30),(170,185,210),1)
    for k,(lab,val,ts,col) in enumerate((("QUEM FOI DE ALUGUEL",5000,64.4,RED),("QUEM COMPROU (prestação)",2000,66.4,GREEN))):
        y=120+k*130; a=fa(t,ts)
        txt(d,(50,y),lab,F_("bold",30),WHITE,a,"lm")
        f=ss(o(ts),o(ts)+0.6,t); wbar=int(700*val/5000*f)
        if wbar>0: d.rounded_rectangle((50,y+28,50+wbar,y+80),14,fill=col+(int(235*a),))
        if f>0: txt(d,(70+wbar,y+54),f"R$ {int(val*f):,}".replace(",","."),F_("black",40),WHITE,a,"lm")
els.append(Box(58.6,67.85,390,barras))
def porta(img,d,t):
    txt(d,(490,55),"PORTABILIDADE",F_("black",44),LB,1)
    txt(d,(270,140),"NA COMPRA",F_("bold",28),(170,185,210),fa(t,85.8)); txt(d,(270,205),"10,5%",F_("black",68),WHITE,fa(t,86.9))
    txt(d,(710,140),"NEGOCIANDO",F_("bold",28),(170,185,210),fa(t,100.2)); txt(d,(710,205),"7,4%",F_("black",68),GREEN,fa(t,102.9))
    if t>=o(102.9): d.line((420,205,560,205),fill=WHITE+(int(220*fa(t,102.9)),),width=5); d.polygon([(560,190),(585,205),(560,220)],fill=WHITE+(int(220*fa(t,102.9)),))
    txt(d,(490,300),"“o banco não quer te perder”",F_("sbi",44),GOLD,fa(t,108.6))
els.append(Box(68.9,110.78,360,porta))
def parcela(img,d,t):
    txt(d,(490,55),"RESULTADO",F_("bold",30),(170,185,210),1)
    txt(d,(490,130),"−R$ 500/mês na parcela",F_("black",56),GREEN,fa(t,119.7))
    if t>=o(126.3): txt(d,(490,225),"Aluguel de R$ 5 mil = 2,5 parcelas",F_("bold",40),WHITE,fa(t,128.8))
els.append(Box(117.95,131.30,290,parcela,accent=GREEN))
def momento(img,d,t):
    txt(d,(490,85),"NÃO EXISTE",F_("black",60),WHITE,1)
    txt(d,(490,180),"momento perfeito.",F_("sbi",80),GOLD,fa(t,237.3))
LIST=[("Casamento","R$ 120 mil",249.9,RED),("Entrada do apê","R$ 40 mil",255.5,LB),("Obra: 1 ano e meio","R$ 2 mil/mês",263.2,LB),("Financiou o saldo","~R$ 200–250 mil",266.9,LB)]
def vida(img,d,t):
    txt(d,(490,52),"NADA PERFEITO NA ÉPOCA",F_("bold",30),(170,185,210),1)
    for k,(l,v,ts,col) in enumerate(LIST):
        a=fa(t,ts); y=115+k*78
        if a<=0: continue
        d.rounded_rectangle((40,y-30,940,y+30),18,fill=(20,40,75,int(230*a)))
        txt(d,(70,y),l,F_("semi",34),WHITE,a,"lm"); txt(d,(910,y),v,F_("black",38),col,a,"rm")
els.append(Box(244.0,269.30,440,vida))
def patr(img,d,t):
    txt(d,(490,55),"PATRIMÔNIO HOJE",F_("bold",30),(170,185,210),1)
    if t>=o(271.7): txt(d,(490,130),f"R$ {count(t,271.7,0,800)} MIL",F_("black",72),GOLD,fa(t,271.7))
    txt(d,(490,230),"vira a entrada do próximo:",F_("semi",34),WHITE,fa(t,274.8))
    txt(d,(490,295),"R$ 1,2 a 1,4 MILHÃO",F_("black",50),LB,fa(t,275.9))
els.append(Box(270.0,279.62,350,patr,accent=GOLD))
# cartela final
def endcard(cv,t):
    u=t-END; a=ss(0,0.3,u)
    big=F_("sbi",88); d=ImageDraw.Draw(cv)
    txt(d,(540,820),"Gostou do insight?",big,WHITE,a)
    txt(d,(540,930),"Manda pra quem ainda espera o momento perfeito.",F_("semi",38),GOLD,ss(0.3,0.6,u))
    if u>0.6:
        a2=ss(0.6,0.9,u); d.rounded_rectangle((380,1030,700,1120),26,fill=(0,149,246,int(245*a2))); txt(d,(540,1075),"Seguir",F_("black",46),WHITE,a2)
els.append(Func(endcard,END,T))
ov=f"{B}/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- legendas palavra a palavra ----------
FIXW={"paba":"","Buritins,":"Buritis,","Buritins":"Buritis","Financei":"Financiei","financei,":"financiei,","horas":"vagas","Bob,":"Rico,"}
ws=[]
for w in WORDS:
    if any(a<=w[0]<b for a,b,s in OUT):
        tx=FIXW.get(w[2],w[2])
        if tx.startswith(",") and ws and ws[-1][2][-1:].isdigit(): ws[-1][2]+=","+tx[1:]; ws[-1][1]=o(w[1]); continue
        if not tx: continue
        if tx.startswith('-') and ws: ws[-1][2]+=tx; ws[-1][1]=o(w[1]); continue
        ws.append([o(w[0]),o(min(w[1],[b for a,b,s in OUT if a<=w[0]<b][0])),tx])
st=["Style: Cap,Inter ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,2,70,70,330,1"]
ev=word_captions(ws,"Cap","&HFFB85C&",END)
assf=f"{B}/c.ass"; open(assf,"w").write(ass_head(st)+"\n".join(ev)+"\n")
# ---------- fundo da cartela ----------
endbg=f"{B}/endbg.mkv"
if not os.path.exists(endbg):
    nfe=round(ENDC*FPS)
    run(["-ss",f"{END-0.3:.3f}","-i",base,"-f","lavfi","-i","anullsrc=r=48000:cl=mono","-filter_complex",f"[0:v]trim=end_frame=1,loop=loop={nfe}:size=1,setpts=N/({FPS}*TB),trim=end_frame={nfe},gblur=sigma=28,eq=brightness=-0.22:saturation=0.7[v]",
         "-map","[v]","-map","1:a","-t",f"{nfe/FPS:.4f}","-c:v","libx264","-crf","15","-preset","fast","-c:a","pcm_s16le",endbg])
# ---------- trilha + mix ----------
mus=f"{B}/music.wav"
subprocess.run(["python3","-I",f"{ENG}/../v7/music3.py",mus,f"{T:.3f}",f"{o(80.86):.3f}",f"{o(243.95):.3f}",f"{END:.3f}"],check=True)
VOICE2=("highpass=f=95,lowpass=f=12000,afftdn=nr=8:nf=-42:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
        "equalizer=f=250:t=q:w=1.0:g=-3,equalizer=f=500:t=q:w=1.0:g=-1.5,equalizer=f=3000:t=q:w=1.2:g=3,equalizer=f=5500:t=q:w=1.2:g=2,deesser=i=0.2,"
        "acompressor=threshold=-22dB:ratio=3:attack=10:release=180,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
fg=[f"[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[cv][ca]",f"[2:v]format=yuva420p[ov]",
    f"[cv]eq=contrast=1.06:saturation=1.06:gamma=0.98,colorbalance=bs=0.03:rh=0.02,unsharp=5:5:0.4[cg]",
    f"[cg][ov]overlay=0:0:eof_action=pass,ass={assf}:fontsdir=/usr/share/fonts,format=yuv420p[vo]",
    f"[ca]{VOICE2},asplit[voz][key]",f"[3:a]volume=0.16,aformat=channel_layouts=stereo[mus]",
    "[mus][key]sidechaincompress=threshold=0.04:ratio=4:attack=25:release=400[md]",
    "[voz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(["-i",base,"-i",endbg,"-i",ov,"-i",mus,"-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
     "-c:v","libx264","-preset","medium","-crf","20","-maxrate","6M","-bufsize","12M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{B}/final.mp4"])
light(f"{B}/final.mp4",f"{B}/final_leve.mp4")
json.dump(OUT,open(f"{B}/map.json","w"))
print("ok",round(END,2),round(T,2))
