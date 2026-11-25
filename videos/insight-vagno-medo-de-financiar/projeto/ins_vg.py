# INSIGHT – "Não vai voltar a ter apartamento desse valor" (palestra, 2 palestrantes) -> corte de ~3 min
import sys, os, subprocess, json, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import eng; eng.SPEED=1.0
from eng import *
import numpy as np, cv2
S=sys.argv[1]; ENG=os.path.dirname(os.path.abspath(__file__))
SRC=f"{S}/i1/original.mov"; B=f"{S}/i1/build_vg"; os.makedirs(B,exist_ok=True)
GOLD=(242,199,94); LB=(92,184,255); WHITE=(255,255,255); RED=(255,96,96); GREEN=(88,214,141); NAVY=(8,16,32)
SB=lambda a,b:None
# ---------- trechos (tempo da fonte) ----------
KEEP=[(176.70,238.95)]
SPK=lambda t: "B"
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
_bg=None
def fullbg():
    global _bg
    if _bg is None:
        y=np.linspace(0,1,H)[:,None]; x=np.linspace(-1,1,W)[None,:]
        r=np.clip(1-np.sqrt(x**2*0.6+(y-0.42)**2*1.6)*1.1,0,1)
        _bg=Image.fromarray((np.array([4,8,16])+(np.array([14,32,62])-np.array([4,8,16]))*r[...,None]).astype(np.uint8)).convert("RGBA")
    return _bg
def abertura(cv,t):
    t0,t1=o(176.70),o(182.55); a=1-ss(t1-0.3,t1,t)
    lay=fullbg().copy(); d=ImageDraw.Draw(lay)
    txt(d,(540,560),"O MEDO DE QUEM FINANCIA",F_("bold",44),LB,ss(t0,t0+0.3,t))
    if t>=o(181.38):
        u=(t-o(181.38))/0.35; sc=1.4-0.4*ease_out_back(min(1,u))
        txt(d,(540,760),"420 MESES",F_("black",int(150*sc)),WHITE,min(1,u*3))
        txt(d,(540,900),"= 35 ANOS PAGANDO",F_("bold",60),RED,fa(t,181.9))
    else:
        n=int(420*ss(t0+0.2,o(181.38),t)); txt(d,(540,760),f"{n}",F_("black",170),(200,210,230),ss(t0,t0+0.3,t))
        txt(d,(540,900),"parcelas",F_("bold",50),(150,165,190),ss(t0,t0+0.3,t))
    if a<1: lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
    cv.alpha_composite(lay)
els.append(Func(abertura,o(176.70),o(182.55)))
def adiar(img,d,t):
    txt(d,(490,90),"“Vou ficar devendo",F_("sbi",62),WHITE,1)
    txt(d,(490,175),"35, 40 anos pra Caixa?”",F_("sbi",62),GOLD,fa(t,184.6))
els.append(Box(182.66,190.30,260,adiar))
def medo(img,d,t):
    txt(d,(490,60),"A CONTA QUE ASSUSTA",F_("bold",30),(170,185,210),1)
    txt(d,(270,145),"PEGA",F_("bold",30),WHITE,fa(t,194.0)); txt(d,(270,200),"R$ 200 MIL",F_("black",54),WHITE,fa(t,195.6))
    txt(d,(720,145),"PAGA",F_("bold",30),RED,fa(t,197.4)); txt(d,(720,200),"R$ 600 MIL?",F_("black",54),RED,fa(t,197.4))
    txt(d,(490,290),"“3 casas pra Caixa”",F_("sbi",50),GOLD,fa(t,198.9))
els.append(Box(193.8,201.9,350,medo,accent=RED))
def amort(img,d,t):
    txt(d,(490,60),"A VIRADA: AMORTIZAÇÃO",F_("black",44),GREEN,fa(t,206.0))
    n=42; cut=int(12*ss(o(211.2),o(212.4),t))
    for k in range(n):
        x=50+k*21; col=(70,90,120) if k>=n-cut else LB
        a=fa(t,206.4+k*0.01,0.2)*(0.25 if k>=n-cut else 1)
        d.rounded_rectangle((x,130,x+15,220),5,fill=col+(int(255*a),))
    txt(d,(50,250),"1ª parcela",F_("med",24),(180,190,210),fa(t,206.4),"lm"); txt(d,(930,250),"última",F_("med",24),(180,190,210),fa(t,206.4),"rm")
    if t>=o(209.6): txt(d,(490,305),"+ R$ 10 mil abatendo as últimas parcelas",F_("bold",32),WHITE,fa(t,209.6))
    if t>=o(214.4):
        a=fa(t,214.4); d.rounded_rectangle((260,345,720,405),20,fill=GREEN+(int(240*a),)); txt(d,(490,375),"ANOS A MENOS DE PRAZO",F_("black",32),NAVY,a)
    txt(d,(490,440),"*o quanto reduz depende do saldo, da taxa e do contrato",F_("med",22),(170,180,200),fa(t,214.4))
els.append(Box(203.0,217.65,470,amort,accent=GREEN))
def porta(img,d,t):
    txt(d,(490,60),"A CASA FOI",F_("bold",32),(170,185,210),1)
    txt(d,(490,140),"a porta de entrada.",F_("sbi",72),GOLD,fa(t,219.2))
els.append(Box(217.75,223.10,220,porta,accent=GOLD))
def coragem(img,d,t):
    txt(d,(490,70),"SEM A CORAGEM DE FINANCIAR",F_("black",42),WHITE,1)
    txt(d,(490,160),"não teria o apartamento de hoje.",F_("sbi",52),GOLD,fa(t,227.4))
els.append(Box(223.2,231.0,230,coragem,accent=GOLD))
def momento(img,d,t):
    txt(d,(490,85),"NÃO EXISTE",F_("black",60),WHITE,1)
    txt(d,(490,180),"momento perfeito.",F_("sbi",80),GOLD,fa(t,237.3))
els.append(Box(235.2,238.95,270,momento,accent=GOLD))
# cartela final
def endcard(cv,t):
    u=t-END; a=ss(0,0.3,u)
    big=F_("sbi",88); d=ImageDraw.Draw(cv)
    txt(d,(540,820),"Medo de financiar?",big,WHITE,a)
    txt(d,(540,930),"Manda pra quem precisa ouvir isso.",F_("semi",38),GOLD,ss(0.3,0.6,u))
    if u>0.6:
        a2=ss(0.6,0.9,u); d.rounded_rectangle((380,1030,700,1120),26,fill=(0,149,246,int(245*a2))); txt(d,(540,1075),"Seguir",F_("black",46),WHITE,a2)
els.append(Func(endcard,END,T))
ov=f"{B}/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- legendas palavra a palavra ----------
FIXW={"paba":"","Samonte,":"","em":"em","Bob,":"Rico,","caixa,":"Caixa,","caixa":"Caixa","Buritins,":"Buritis,","Buritins":"Buritis","Financei":"Financiei","financei,":"financiei,","horas":"vagas","Bob,":"Rico,"}
ws=[]
for w in WORDS:
    if any(a<=w[0]<b for a,b,s in OUT):
        tx=FIXW.get(w[2],w[2])
        if tx.startswith(",") and ws and ws[-1][2][-1:].isdigit(): ws[-1][2]+=","+tx[1:]; ws[-1][1]=o(w[1]); continue
        if not tx: continue
        if tx=='que' and 212.4<w[0]<212.7: continue
        if tx=='em' and 191.8<w[0]<192.0: continue
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
subprocess.run(["python3","-I",f"{ENG}/../v7/music3.py",mus,f"{T:.3f}",f"{o(202.0):.3f}",f"{o(231.0):.3f}",f"{END:.3f}"],check=True)
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
