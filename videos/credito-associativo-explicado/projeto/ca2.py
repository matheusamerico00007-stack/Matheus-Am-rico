# CRÉDITO ASSOCIATIVO – vídeo explicativo a partir dos áudios + imagens do View
import sys, os, subprocess, json, math, random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import eng; eng.SPEED=1.0
from eng import *
import numpy as np
S=sys.argv[1]; ENG=os.path.dirname(os.path.abspath(__file__))
D=f"{S}/ca2"; B=f"{D}/build"; os.makedirs(B,exist_ok=True)
TL=json.load(open(f"{D}/timeline.json")); END=TL["T"]-0.32+0.15; ENDC=2.6; T=END+ENDC
GOLD=(242,199,94); LB=(92,184,255); WHITE=(255,255,255); RED=(255,96,96); GREEN=(88,214,141); NAVY=(8,16,32); GREY=(170,185,210)
SBI="/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
def F_(n,s): return ImageFont.truetype(SBI,s) if n=="sbi" else font(n,s)
random.seed(5)
_bg=None
def scene_bg():
    global _bg
    if _bg is None:
        y=np.linspace(0,1,H)[:,None]; x=np.linspace(-1,1,W)[None,:]
        r=np.clip(1-np.sqrt(x**2*0.6+(y-0.38)**2*1.6)*1.1,0,1)
        c0=np.array([4,8,16]); c1=np.array([14,34,66])
        _bg=Image.fromarray((c0+(c1-c0)*r[...,None]).astype(np.uint8)).convert("RGBA")
    return _bg.copy()
PART=[(random.random()*W,random.random()*H,random.uniform(1,3),random.uniform(8,30)) for _ in range(80)]
def particles(cv,t,col=LB,a=1.0):
    d=ImageDraw.Draw(cv)
    for (x,y,r,sp) in PART:
        yy=(y-t*sp)%H; al=int(60*a*(0.5+0.5*math.sin(t*2+x)))
        d.ellipse((x-r,yy-r,x+r,yy+r),fill=col+(al,))
def glow_lines(cv,segs,col,width=6,blur=10,a=1.0):
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for s in segs:
        if len(s)>1: d.line(s,fill=col+(int(255*a),),width=width*3,joint="curve")
    lay=lay.filter(ImageFilter.GaussianBlur(blur)); cv.alpha_composite(lay)
    lay2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(lay2)
    for s in segs:
        if len(s)>1: d2.line(s,fill=(255,250,240,int(255*a)),width=width,joint="curve")
    cv.alpha_composite(lay2)
def partial(pts,f):
    L=[math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1)]; tot=sum(L); goal=tot*max(0,min(1,f)); out=[pts[0]]; acc=0
    for i,l in enumerate(L):
        if acc+l>=goal:
            u=(goal-acc)/l if l else 0; out.append((pts[i][0]+(pts[i+1][0]-pts[i][0])*u,pts[i][1]+(pts[i+1][1]-pts[i][1])*u)); return out
        out.append(pts[i+1]); acc+=l
    return out
def T_(cv,xy,s,f,col,a=1.0,anchor="mm",shadow=True):
    if a<=0: return
    if shadow:
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((xy[0]+3,xy[1]+6),s,font=f,fill=(0,0,0,int(150*a)),anchor=anchor); sh=sh.filter(ImageFilter.GaussianBlur(7)); cv.alpha_composite(sh)
    ImageDraw.Draw(cv).text(xy,s,font=f,fill=col+(int(255*a),),anchor=anchor)
def fa(t,t0,d=0.25): return ss(t0,t0+d,t)
def pop(t,t0,d=0.35): u=(t-t0)/d; return (0.85+0.15*ease_out_back(min(1,max(0,u)))), min(1,max(0,u*2.5))
class Scene:
    def __init__(s,t0,t1,fn,fi=0.2,fo=0.2): s.t0=t0; s.t1=t1; s.fn=fn; s.fi=fi; s.fo=fo
    def draw(s,cv,t):
        if not (s.t0<=t<s.t1): return
        a=ss(s.t0,s.t0+s.fi,t)*(1-ss(s.t1-s.fo,s.t1,t)) if s.fi>0 else (1-ss(s.t1-s.fo,s.t1,t))
        lay=scene_bg(); s.fn(lay,t,t-s.t0)
        if a<1: lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
        cv.alpha_composite(lay)
def chip(cv,t,t0,t1,txt,y,col=GOLD,fg=NAVY,size=44):
    if not (t0<=t<t1): return
    sc,a=pop(t,t0); a*=1-ss(t1-0.2,t1,t)
    f=font("black",int(size*sc)); d=ImageDraw.Draw(cv); bb=d.textbbox((W/2,y),txt,font=f,anchor="mm")
    p=Image.new("RGBA",(W,H),(0,0,0,0)); dp=ImageDraw.Draw(p)
    dp.rounded_rectangle((bb[0]-28,bb[1]-18,bb[2]+28,bb[3]+18),22,fill=col+(int(240*a),)); dp.text((W/2,y),txt,font=f,fill=fg+(int(255*a),),anchor="mm"); cv.alpha_composite(p)
def foot(cv,txt,a,y=1260): T_(cv,(540,y),txt,F_("med",26),(185,195,215),a,shadow=False)
els=[]
CTA0=50.0
# 1) gancho: inseguro
_walk=[];v=0.5
for k in range(60): v=min(0.92,max(0.08,v+random.uniform(-0.2,0.18))); _walk.append(v)
def s_inseguro(cv,t,u):
    particles(cv,t,RED,0.6); d=ImageDraw.Draw(cv)
    for k in range(6): d.line((90,600+k*95,990,600+k*95),fill=(80,110,160,60),width=1)
    pts=[(90+k*(900/59),1080-_walk[k]*440) for k in range(60)]
    glow_lines(cv,[partial(pts,u/2.4)],RED,5,12,0.8+0.2*math.sin(t*30))
    T_(cv,(540,330),"INSEGURO COM O",F_("bold",48),WHITE,fa(t,0.0,0.2))
    T_(cv,(540,425),"cenário político?",F_("sbi",90),RED,fa(t,1.1))
    T_(cv,(540,1200),"e com os juros dos próximos anos?",F_("sbi",54),GOLD,fa(t,2.6))
els.append(Scene(0.0,3.9,s_inseguro,fi=0.0))
# 2) título
def s_titulo(cv,t,u):
    particles(cv,t)
    T_(cv,(540,560),"DEIXA EU TE EXPLICAR UMA OPÇÃO",F_("bold",40),GREY,fa(t,4.0))
    sc,a=pop(t,5.55); T_(cv,(540,720),"CRÉDITO",F_("black",int(150*sc)),WHITE,a)
    sc,a=pop(t,6.1); T_(cv,(540,880),"ASSOCIATIVO",F_("black",int(124*sc)),LB,a)
els.append(Scene(3.9,6.95,s_titulo))
# 3) assina com a Caixa
def lock(cv,cx,cy,s,a,closed=True,col=GOLD):
    d=ImageDraw.Draw(cv); w,h=int(120*s),int(100*s); sh=int(-30*s*(1-closed))
    d.arc((cx-int(42*s),cy-h//2-int(80*s)+sh,cx+int(42*s),cy-h//2+int(10*s)+sh),180,360,fill=col+(int(255*a),),width=int(14*s))
    d.line((cx-int(42*s),cy-h//2-int(35*s)+sh,cx-int(42*s),cy-h//2+sh),fill=col+(int(255*a),),width=int(14*s))
    d.line((cx+int(42*s),cy-h//2-int(35*s)+sh,cx+int(42*s),cy-h//2+(0 if closed else sh)),fill=col+(int(255*a),),width=int(14*s))
    d.rounded_rectangle((cx-w//2,cy-h//2,cx+w//2,cy+h//2),int(16*s),fill=col+(int(255*a),))
    d.ellipse((cx-int(12*s),cy-int(16*s),cx+int(12*s),cy+int(8*s)),fill=NAVY+(int(255*a),))
def s_assina(cv,t,u):
    particles(cv,t); d=ImageDraw.Draw(cv)
    T_(cv,(540,300),"VOCÊ ASSINA COM A CAIXA HOJE",F_("black",46),WHITE,fa(t,8.0))
    a=fa(t,7.0); x0,y0=250,400
    d.rounded_rectangle((x0,y0,x0+580,y0+680),24,fill=(240,244,250,int(250*a)))
    T_(cv,(x0+290,y0+70),"CONTRATO DE FINANCIAMENTO",F_("black",30),NAVY,a,shadow=False)
    for k in range(9):
        f=ss(7.2+k*0.15,7.5+k*0.15,t); d.rounded_rectangle((x0+50,y0+140+k*46,x0+50+int((480 if k%3 else 380)*f),y0+156+k*46),8,fill=(180,190,205,int(255*a)))
    if t>=8.85:
        a2=fa(t,8.85); d.rounded_rectangle((x0+40,y0+580,x0+300,y0+650),16,fill=(0,92,169,int(255*a2))); T_(cv,(x0+170,y0+615),"CAIXA",F_("black",40),WHITE,a2,shadow=False)
        pts=[(x0+330+k*9,y0+630-math.sin(k*0.7)*18-(k%4)*3) for k in range(25)]
        sig=partial(pts,ss(9.0,9.8,t))
        if len(sig)>1: d.line(sig,fill=(20,40,90,int(255*a2)),width=5,joint="curve")
els.append(Scene(6.95,10.0,s_assina))
def obra_bg(cv,t):
    a=ss(9.9,10.1,t)*(1-ss(11.45,11.65,t)); lay=scene_bg()
    if a<1: lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
    cv.alpha_composite(lay)
els.append(Func(obra_bg,9.9,11.65))
els.append(Card("mall.jpg",None,10.0,11.65,top=520,maxw=1000,anim="zoom",border=(242,199,94,200)))
els.append(Func(lambda cv,t: chip(cv,t,10.0,11.65,"QUE FINANCIA E GARANTE A OBRA",360,GOLD,NAVY,42),10.0,11.65))
# 4) juros travados
_m=[];v=0.5
for k in range(50): v=min(0.95,max(0.05,v+random.uniform(-0.16,0.17))); _m.append(v)
def s_fixo(cv,t,u):
    particles(cv,t); d=ImageDraw.Draw(cv)
    T_(cv,(540,300),"E GARANTE A TAXA DE JUROS",F_("black",48),WHITE,fa(t,12.0))
    T_(cv,(540,380),"contratada hoje",F_("sbi",58),GOLD,fa(t,14.0))
    for k in range(5): d.line((90,560+k*95,990,560+k*95),fill=(80,110,160,60),width=1)
    pts=[(90+k*(900/49),940-_m[k]*380) for k in range(50)]
    glow_lines(cv,[partial(pts,ss(11.8,16.8,t))],(150,160,180),4,8,0.8)
    T_(cv,(860,500),"juros do mercado",F_("semi",30),(170,180,200),fa(t,12.4),"mm",False)
    f=ss(13.4,14.6,t)
    if f>0:
        glow_lines(cv,[[(90,750),(90+900*f,750)]],GOLD,6,12)
        if t>=14.6: sc,a=pop(t,14.6); lock(cv,990,750,0.55*sc,a)
    T_(cv,(540,1060),"INDEPENDENTE DO CENÁRIO",F_("black",46),WHITE,fa(t,15.3))
    T_(cv,(540,1140),"daqui 2 ou 3 anos",F_("sbi",50),LB,fa(t,16.9))
els.append(Scene(11.65,18.3,s_fixo))
# 5) 80% a 100%
def s_fin(cv,t,u):
    particles(cv,t,GREEN,0.7); d=ImageDraw.Draw(cv)
    T_(cv,(540,300),"E O MELHOR:",F_("bold",46),GREY,fa(t,18.5))
    T_(cv,(540,385),"A CAIXA PODE FINANCIAR",F_("black",52),WHITE,fa(t,19.4))
    if t>=20.6:
        a=fa(t,20.6); y=480
        d.rounded_rectangle((140,y,940,y+80),40,outline=GREEN+(int(255*a),),width=3)
        g=ss(20.6,21.1,t)*(0.8+0.2*ss(21.6,22.2,t)); d.rounded_rectangle((146,y+6,146+int(788*g),y+74),34,fill=GREEN+(int(240*a),))
        T_(cv,(540,y+40),f"DE 80% ATÉ {int(80+20*ss(21.6,22.2,t))}% DO IMÓVEL",F_("black",36),NAVY,a,shadow=False)
    if t>=25.3:
        n=int(100*ss(25.3,25.9,t)); sc,a=pop(t,25.3)
        T_(cv,(540,780),f"{n}%",F_("black",int(230*sc)),GREEN,a)
        T_(cv,(540,940),"de aprovação para alguns clientes",F_("sbi",50),GOLD,fa(t,25.9))
    elif t>=23.1:
        T_(cv,(540,800),"APROVAÇÕES DE",F_("black",60),WHITE,fa(t,23.1))
    T_(cv,(540,1080),"dependendo da análise de crédito e da unidade",F_("semi",34),(200,210,225),fa(t,26.9))
els.append(Scene(18.3,29.9,s_fin))
# 6) só paga nas chaves (com aérea do View)
def chaves_bg(cv,t):
    a=ss(29.8,30.0,t)*(1-ss(33.55,33.8,t)); lay=scene_bg()
    if a<1: lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
    cv.alpha_composite(lay); particles(cv,t,GOLD,0.5*a)
els.append(Func(chaves_bg,29.8,33.8))
els.append(Card("04",[0,0,1,.765],29.9,33.8,top=230,maxw=1000,maxh=560,anim="rise",border=(242,199,94,190)))
def chaves(cv,t):
    a=ss(30.0,30.25,t)*(1-ss(33.55,33.8,t)); d=ImageDraw.Draw(cv)
    if a<=0: return
    T_(cv,(330,880),"OBRA",F_("bold",34),WHITE,a,shadow=False)
    d.rounded_rectangle((150,920,690,958),19,outline=LB+(int(255*a),),width=3)
    f=ss(30.3,32.6,t); d.rounded_rectangle((154,924,154+int(532*f),954),16,fill=LB+(int(255*a),))
    if t>=32.6:
        sc,a2=pop(t,32.6); a2*=a
        d.ellipse((760-int(46*sc),940-int(46*sc),760+int(46*sc),940+int(46*sc)),outline=GOLD+(int(255*a2),),width=int(12*sc))
        d.rounded_rectangle((800,930,920,950),6,fill=GOLD+(int(255*a2),)); d.rectangle((880,950,895,975),fill=GOLD+(int(255*a2),)); d.rectangle((905,950,918,968),fill=GOLD+(int(255*a2),))
    T_(cv,(540,1070),"SÓ COMEÇA A PAGAR O",F_("black",48),WHITE,ss(31.0,31.25,t)*a)
    T_(cv,(540,1145),"financiamento nas chaves*",F_("sbi",62),GOLD,ss(31.9,32.15,t)*a)
    foot(cv,"*Durante a obra há entrada com a construtora e encargos/juros de obra.",ss(32.6,32.9,t)*a,1240)
els.append(Func(chaves,29.9,33.8))
# 7) e se os juros caírem? portabilidade
def s_port(cv,t,u):
    particles(cv,t,GREY,0.5); d=ImageDraw.Draw(cv)
    sc,a=pop(t,33.85)
    p=Image.new("RGBA",(W,H),(0,0,0,0)); dp=ImageDraw.Draw(p)
    dp.rounded_rectangle((110,280,970,500),48,fill=(233,233,235,int(250*a))); dp.polygon([(160,500),(130,560),(240,500)],fill=(233,233,235,int(250*a)))
    cv.alpha_composite(p)
    T_(cv,(540,390),"“E se os juros caírem?”",F_("sbi",62),NAVY,fa(t,34.8),shadow=False)
    if t>=36.4:
        a=fa(t,36.4);
        for k,(nm,tx,col) in enumerate((("SEU BANCO","taxa atual",(150,160,180)),("OUTRO BANCO","taxa menor",GREEN))):
            x=290+k*500; y=820
            d.rounded_rectangle((x-190,y-90,x+190,y+90),28,fill=(14,34,66,int(240*a)),outline=col+(int(255*a),),width=3)
            T_(cv,(x,y-22),nm,F_("black",36),WHITE,a,shadow=False); T_(cv,(x,y+30),tx,F_("semi",30),col,a,shadow=False)
        f=ss(37.0,37.6,t)
        if f>0:
            x1=480+int(140*f); d.line((480,820,x1,820),fill=GOLD+(int(255*a),),width=8)
            if f>0.95: d.polygon([(x1,800),(x1+26,820),(x1,840)],fill=GOLD+(int(255*a),))
        T_(cv,(540,1040),"PORTABILIDADE",F_("black",76),GOLD,fa(t,37.0))
        T_(cv,(540,1130),"você leva o financiamento pra quem cobrar menos",F_("semi",32),WHITE,fa(t,38.2))
els.append(Scene(33.8,39.45,s_port))
# 8) renda: aluguel ajuda a pagar
def dark(cv,t):
    a=ss(39.4,39.7,t)*(1-ss(49.8,50.05,t)); lay=scene_bg()
    if a<1: lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
    cv.alpha_composite(lay); particles(cv,t,GOLD,0.6*a)
els.append(Func(dark,39.4,50.05))
els.append(Card("20",[.034,.047,.966,.957],39.5,50.0,top=230,maxw=1000,maxh=740,anim="zoom",border=(242,199,94,190)))
def renda(cv,t):
    chip(cv,t,40.2,50.0,"PENSANDO EM INVESTIR E TER RENDA?",1060,LB,NAVY,40)
    chip(cv,t,42.4,50.0,"O ALUGUEL AJUDA A PAGAR AS PARCELAS*",1165,GOLD,NAVY,40)
    chip(cv,t,47.3,50.0,"O INQUILINO PAGA O FINANCIAMENTO*",1270,GREEN,NAVY,40)
    if t>=42.6: foot(cv,"*Quando o valor do aluguel cobre a parcela.",fa(t,42.8),1360)
els.append(Func(renda,40.2,50.0))
# 9) CTA sobre a maquete (vídeo do estande na base)
def cta(cv,t):
    chip(cv,t,50.3,END,"QUER CONHECER O PROJETO?",300,GOLD,NAVY,42)
    chip(cv,t,52.5,END,"E ENTENDER O CRÉDITO ASSOCIATIVO?",395,LB,NAVY,36)
    if t>=54.1:
        u=(t-54.1)/0.35; sc=(0.8+0.2*ease_out_back(min(1,u)))*(1+0.04*math.sin(t*7)); a=min(1,u*3)*(1-ss(END-0.15,END,t))
        w,h=int(560*sc),int(130*sc); x=(W-w)//2; y=1080
        p=Image.new("RGBA",(W,H),(0,0,0,0)); dp=ImageDraw.Draw(p)
        dp.rounded_rectangle((x,y,x+w,y+h),int(65*sc),fill=(0,149,246,int(245*a))); dp.text((W/2,y+h/2),"ME CHAMA AQUI",font=F_("black",int(50*sc)),fill=WHITE+(int(255*a),),anchor="mm"); cv.alpha_composite(p)
els.append(Func(cta,50.3,END))
HOUSE=[(360,980),(360,760),(540,600),(720,760),(720,980),(360,980)]
def s_end(cv,t,u):
    particles(cv,t,GOLD)
    glow_lines(cv,[partial(HOUSE,ss(0,1.0,u))],GOLD,6,14)
    T_(cv,(540,1110),"CRÉDITO ASSOCIATIVO",F_("black",62),WHITE,fa(t,END+0.2))
    T_(cv,(540,1195),"juros de hoje · até 100%* · paga nas chaves*",F_("sbi",42),GOLD,fa(t,END+0.5))
    T_(cv,(540,1300),"Me chama no direct",F_("bold",40),LB,fa(t,END+0.9))
    foot(cv,"*Sujeito à análise de crédito. Na obra há entrada e encargos de obra.",fa(t,END+0.9),1400)
els.append(Scene(END,T,s_end,fi=0.25,fo=0))
if os.environ.get("PREVIEW"):
    for t in [float(x) for x in os.environ["PREVIEW"].split(",")]:
        cv=Image.new("RGBA",(W,H),(40,40,40,255))
        for e in els:
            if getattr(e,"t0",0)<=t<getattr(e,"t1",T): e.draw(cv,t)
        cv.convert("RGB").resize((270,480)).save(f"{B}/pv_{t:06.2f}.png")
    sys.exit()
ov=f"{B}/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- legendas ----------
FIXW={"Encamp,":"Emccamp,","alocar":"alugar","Mall":"Mall"}
ws=[]
for w in TL["words"]:
    tx=FIXW.get(w[2],w[2])
    if tx=="%" and ws: ws[-1][2]+="%"; ws[-1][1]=w[1]; continue
    ws.append([w[0],w[1],tx])
st=["Style: Cap,Inter ExtraBold,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,2,2,70,70,300,1"]
ev=word_captions(ws,"Cap","&HFFB85C&",END)
assf=f"{B}/c.ass"; open(assf,"w").write(ass_head(st)+"\n".join(ev)+"\n")
# ---------- base: estande no começo e no fim, azul-escuro no meio ----------
base=f"{B}/base.mkv"
if not os.path.exists(base):
    V=f"{D}/video.mp4"; nmid=round(CTA0*FPS); n3=round((END-CTA0)*FPS); nend=round(ENDC*FPS)
    sc="scale=1080:-2:flags=lanczos,crop=1080:1920,unsharp=5:5:0.7,eq=contrast=1.05:saturation=1.08,setsar=1"
    fg=(f"color=c=0x081020:s=1080x1920:r={FPS},trim=end_frame={nmid},setpts=PTS-STARTPTS,format=yuv420p[b];"
        f"[0:v]fps={FPS},trim=start=12.4,setpts=PTS-STARTPTS,trim=end_frame={n3},{sc}[c];"
        f"color=c=0x081020:s=1080x1920:r={FPS},trim=end_frame={nend},setpts=PTS-STARTPTS,format=yuv420p[d];"
        f"[b][c][d]concat=n=3:v=1:a=0,format=yuv420p[v]")
    run(["-i",V,"-filter_complex",fg,"-map","[v]","-c:v","libx264","-crf","15","-preset","fast",base])
# ---------- voz (áudios em sequência) ----------
voz=f"{B}/voz.wav"
subprocess.run(["python3","-I",f"{ENG}/../cap/voz.py",D,f"{T:.3f}"],check=True)
mus=f"{B}/music.wav"
subprocess.run(["python3","-I",f"{ENG}/../v7/music3.py",mus,f"{T:.3f}","11.65","39.4",f"{END:.3f}"],check=True)
VOICE2=("highpass=f=75,agate=threshold=0.012:ratio=2:attack=5:release=200:range=0.25:knee=4,equalizer=f=220:t=q:w=1.0:g=-2,equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=6000:t=q:w=1.2:g=1.5,deesser=i=0.2,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
fgc=[f"[0:v]format=yuv420p[bv]",f"[1:v]format=yuva420p[ov]",
     f"[bv][ov]overlay=0:0:eof_action=pass,ass={assf}:fontsdir=/usr/share/fonts,format=yuv420p[vo]",
     f"[2:a]{VOICE2},asplit[vz][key]",f"[3:a]volume=0.20,aformat=channel_layouts=stereo[mu]",
     "[mu][key]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=650[md]",
     "[vz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(["-i",base,"-i",ov,"-i",voz,"-i",mus,"-filter_complex",";".join(fgc),"-map","[vo]","-map","[ao]","-t",f"{T:.3f}",
     "-c:v","libx264","-preset","medium","-crf","19","-maxrate","8M","-bufsize","16M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{B}/final.mp4"])
light(f"{B}/final.mp4",f"{B}/final_leve.mp4")
print("ok",round(END,2),round(T,2))
