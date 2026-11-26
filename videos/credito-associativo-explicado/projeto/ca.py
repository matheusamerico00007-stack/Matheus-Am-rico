# CRÉDITO ASSOCIATIVO – vídeo explicativo a partir dos áudios + imagens do View
import sys, os, subprocess, json, math, random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import eng; eng.SPEED=1.0
from eng import *
import numpy as np
S=sys.argv[1]; ENG=os.path.dirname(os.path.abspath(__file__))
D=f"{S}/ca"; B=f"{D}/build"; os.makedirs(B,exist_ok=True)
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
# ---------- 1) abertura sobre o estande ----------
els.append(Func(lambda cv,t: chip(cv,t,2.2,7.75,"LANÇAMENTO · BARÃO HOMEM DE MELO",300,GOLD,NAVY,40),2.2,7.75))
els.append(Card("mall.jpg",None,5.0,7.75,top=420,maxw=1000,anim="rise",border=(242,199,94,200)))
els.append(Func(lambda cv,t: chip(cv,t,5.2,7.75,"OPEN MALL EM FRENTE",860,LB,NAVY,40),5.2,7.75))
# ---------- 2) o que é ----------
ITEMS=[("Assina com a Caixa hoje",13.3),("Garante os juros de hoje",15.2),("Começa a pagar o financiamento nas chaves*",17.1)]
def s_oque(cv,t,u):
    particles(cv,t)
    T_(cv,(540,330),"VOU TE EXPLICAR O",F_("bold",40),GREY,fa(t,7.9))
    sc,a=pop(t,10.9); T_(cv,(540,440),"CRÉDITO",F_("black",int(130*sc)),WHITE,a)
    sc,a=pop(t,11.3); T_(cv,(540,580),"ASSOCIATIVO",F_("black",int(112*sc)),LB,a)
    d=ImageDraw.Draw(cv)
    for k,(s_,t0) in enumerate(ITEMS):
        a=fa(t,t0); y=760+k*130
        if a<=0: continue
        dx=int((1-ss(t0,t0+0.3,t))*60)
        d.rounded_rectangle((90+dx,y-50,990+dx,y+50),28,fill=(18,40,78,int(235*a)),outline=LB+(int(200*a),),width=2)
        d.ellipse((120+dx,y-26,172+dx,y+26),fill=GREEN+(int(255*a),)); d.line([(133+dx,y),(144+dx,y+12),(161+dx,y-12)],fill=NAVY+(int(255*a),),width=6)
        d.text((200+dx,y),s_,font=F_("bold",38 if k<2 else 33),fill=WHITE+(int(255*a),),anchor="lm")
    foot(cv,"*Durante a obra podem existir parcelas de entrada com a construtora e encargos de obra.",fa(t,17.6),1200)
els.append(Scene(7.75,20.95,s_oque))
# ---------- 3) inseguro com o cenário ----------
_walk=[];v=0.5
for k in range(60): v=min(0.92,max(0.08,v+random.uniform(-0.2,0.18))); _walk.append(v)
def s_inseguro(cv,t,u):
    particles(cv,t,RED,0.6); d=ImageDraw.Draw(cv)
    for k in range(6): d.line((90,560+k*100,990,560+k*100),fill=(80,110,160,60),width=1)
    pts=[(90+k*(900/59),1080-_walk[k]*480) for k in range(60)]
    glow_lines(cv,[partial(pts,u/2.2)],RED,5,12,0.8+0.2*math.sin(t*30))
    T_(cv,(540,330),"INSEGURO COM O",F_("bold",46),WHITE,fa(t,21.4))
    T_(cv,(540,420),"cenário político?",F_("sbi",88),RED,fa(t,23.2))
    if t>=25.0:
        sc,a=pop(t,25.0); T_(cv,(540,1180),"A MELHOR OPORTUNIDADE",F_("black",int(60*sc)),GOLD,a)
els.append(Scene(21.21,26.35,s_inseguro))
# ---------- 4) assina com a Caixa: juros travados ----------
def lock(cv,cx,cy,s,a,closed=True,col=GOLD):
    d=ImageDraw.Draw(cv); w,h=int(120*s),int(100*s)
    sh=int(-30*s*(1-closed))
    d.arc((cx-int(42*s),cy-h//2-int(80*s)+sh,cx+int(42*s),cy-h//2+int(10*s)+sh),180,360,fill=col+(int(255*a),),width=int(14*s))
    d.line((cx-int(42*s),cy-h//2-int(35*s)+sh,cx-int(42*s),cy-h//2+sh),fill=col+(int(255*a),),width=int(14*s))
    d.line((cx+int(42*s),cy-h//2-int(35*s)+sh,cx+int(42*s),cy-h//2+(0 if closed else sh)),fill=col+(int(255*a),),width=int(14*s))
    d.rounded_rectangle((cx-w//2,cy-h//2,cx+w//2,cy+h//2),int(16*s),fill=col+(int(255*a),))
    d.ellipse((cx-int(12*s),cy-int(16*s),cx+int(12*s),cy+int(8*s)),fill=NAVY+(int(255*a),))
def s_assina(cv,t,u):
    particles(cv,t); d=ImageDraw.Draw(cv)
    # contrato
    a=fa(t,26.5); x0,y0=250,330
    d.rounded_rectangle((x0,y0,x0+580,y0+700),24,fill=(240,244,250,int(250*a)))
    T_(cv,(x0+290,y0+70),"CONTRATO DE FINANCIAMENTO",F_("black",30),NAVY,a,shadow=False)
    for k in range(9):
        f=ss(26.8+k*0.18,27.1+k*0.18,t); d.rounded_rectangle((x0+50,y0+140+k*48,x0+50+int((480 if k%3 else 380)*f),y0+156+k*48),8,fill=(180,190,205,int(255*a)))
    if t>=28.0:
        a2=fa(t,28.0); d.rounded_rectangle((x0+40,y0+590,x0+300,y0+660),16,fill=(0,92,169,int(255*a2))); T_(cv,(x0+170,y0+625),"CAIXA",F_("black",40),WHITE,a2,shadow=False)
        pts=[(x0+330+k*9,y0+640-math.sin(k*0.7)*18-(k%4)*3) for k in range(25)]
        sig=partial(pts,ss(28.2,29.0,t));
        if len(sig)>1: d.line(sig,fill=(20,40,90,int(255*a2)),width=5,joint="curve")
    T_(cv,(540,1110),"banco garantidor do projeto",F_("sbi",56),LB,fa(t,28.9))
    if t>=30.4:
        sc,a3=pop(t,30.4); lock(cv,540,1300,1.0*sc,a3,closed=t>=30.8)
        T_(cv,(540,1440),"JUROS DE HOJE, TRAVADOS",F_("black",54),GOLD,a3)
els.append(Scene(26.35,32.25,s_assina))
# ---------- 5) objeção ----------
def s_obj(cv,t,u):
    particles(cv,t,GREY,0.5); d=ImageDraw.Draw(cv)
    sc,a=pop(t,32.3)
    p=Image.new("RGBA",(W,H),(0,0,0,0)); dp=ImageDraw.Draw(p)
    dp.rounded_rectangle((110,520,970,860),48,fill=(233,233,235,int(250*a))); dp.polygon([(160,860),(130,930),(240,860)],fill=(233,233,235,int(250*a)))
    cv.alpha_composite(p)
    T_(cv,(540,620),"“E se daqui a",F_("sbi",62),NAVY,a,shadow=False)
    T_(cv,(540,720),"2, 3 anos mudar tudo?”",F_("sbi",62),NAVY,fa(t,34.4),shadow=False)
    T_(cv,(540,1050),"?",F_("black",int(220*(1+0.05*math.sin(t*6)))),RED,fa(t,34.6))
els.append(Scene(32.25,36.15,s_obj))
# ---------- 6) mercado oscila x seu juros fixo ----------
_m=[];v=0.5
for k in range(50): v=min(0.95,max(0.05,v+random.uniform(-0.16,0.17))); _m.append(v)
def s_fixo(cv,t,u):
    particles(cv,t); d=ImageDraw.Draw(cv)
    T_(cv,(540,330),"INDEPENDENTE DO CENÁRIO",F_("black",50),WHITE,fa(t,36.3))
    for k in range(5): d.line((90,540+k*95,990,540+k*95),fill=(80,110,160,60),width=1)
    pts=[(90+k*(900/49),920-_m[k]*380) for k in range(50)]
    glow_lines(cv,[partial(pts,ss(36.4,38.6,t))],(150,160,180),4,8,0.8)
    T_(cv,(880,470),"juros do mercado",F_("semi",30),(170,180,200),fa(t,36.8),"mm",False)
    f=ss(39.4,40.4,t)
    if f>0:
        glow_lines(cv,[[(90,730),(90+900*f,730)]],GOLD,6,12)
        T_(cv,(540,1030),"SEU JUROS: TRAVADO NA ASSINATURA",F_("black",40),GOLD,fa(t,39.6))
        if t>=40.0: sc,a=pop(t,40.0); lock(cv,990,730,0.55*sc,a)
els.append(Scene(36.15,41.2,s_fixo))
# ---------- 7) passo a passo ----------
def box(cv,y,title,sub,t0,t,col=LB):
    a=fa(t,t0)
    if a<=0: return
    d=ImageDraw.Draw(cv); dx=int((1-ss(t0,t0+0.3,t))*50)
    d.rounded_rectangle((150+dx,y-62,930+dx,y+62),28,fill=(14,34,66,int(240*a)),outline=col+(int(255*a),),width=3)
    d.text((540+dx,y-(16 if sub else 0)),title,font=F_("black",40),fill=WHITE+(int(255*a),),anchor="mm")
    if sub: d.text((540+dx,y+28),sub,font=F_("semi",28),fill=col+(int(255*a),),anchor="mm")
def s_passos(cv,t,u):
    particles(cv,t); d=ImageDraw.Draw(cv)
    T_(cv,(540,290),"COMO FUNCIONA",F_("sbi",72),WHITE,fa(t,41.5))
    box(cv,440,"A CAIXA GARANTE A OBRA","banco garantidor do projeto",43.7,t)
    box(cv,610,"VOCÊ COMPRA NA PLANTA","e já assina o financiamento",47.0,t)
    box(cv,780,"JUROS GARANTIDOS","os de hoje, no contrato",51.4,t,GOLD)
    if t>=53.3:
        a=fa(t,53.3); T_(cv,(540,905),"OBRA",F_("bold",34),WHITE,a,shadow=False)
        d.rounded_rectangle((190,940,890,978),19,outline=LB+(int(255*a),),width=3)
        f=ss(53.5,55.3,t); d.rounded_rectangle((194,944,194+int(692*f),974),16,fill=LB+(int(255*a),))
    box(cv,1090,"RECEBE AS CHAVES","começa o financiamento*",55.4,t,GREEN)
    for (y0,y1,t0) in ((502,548,47.0),(672,718,51.4),(842,880,53.3),(985,1028,55.4)):
        if t>=t0: d.line((540,y0,540,y1),fill=LB+(200,),width=4)
    foot(cv,"*Na fase de obra há encargos/juros de obra e a entrada com a construtora.",fa(t,55.8),1230)
els.append(Scene(41.2,57.6,s_passos))
# ---------- 8) aluguel paga a parcela ----------
els.append(Card("20",[.034,.047,.966,.957],57.65,65.4,top=230,maxw=1000,maxh=760,anim="zoom",border=(242,199,94,190)))
def aluga(cv,t):
    chip(cv,t,58.5,65.4,"RECEBEU AS CHAVES?",1080,LB,NAVY,42)
    chip(cv,t,61.8,65.4,"ALUGA",1180,GOLD,NAVY,48)
    chip(cv,t,62.9,65.4,"E O INQUILINO PAGA A PARCELA*",1290,GREEN,NAVY,42)
    if t>=63.0: foot(cv,"*Quando o aluguel cobre a parcela. Depende do valor de aluguel e do financiamento.",fa(t,63.2),1380)
def dark(cv,t):
    a=ss(57.6,57.9,t)*(1-ss(65.2,65.45,t)); lay=scene_bg()
    if a<1: lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
    cv.alpha_composite(lay); particles(cv,t,GOLD,0.6*a)
els.insert(len(els)-1,Func(dark,57.6,65.45))
els.append(Func(aluga,58.5,65.4))
# ---------- 9) até 100% ----------
def s_100(cv,t,u):
    particles(cv,t,GREEN,0.7); d=ImageDraw.Draw(cv)
    T_(cv,(540,330),"O MAIS INTERESSANTE",F_("bold",44),GREY,fa(t,65.7))
    if t>=68.9:
        n=int(100*ss(68.9,69.6,t)); sc,a=pop(t,68.9)
        T_(cv,(540,520),f"{n}%",F_("black",int(230*sc)),GREEN,a)
        T_(cv,(540,680),"DE FINANCIAMENTO*",F_("black",58),WHITE,fa(t,69.8))
        T_(cv,(540,760),"em algumas unidades",F_("sbi",52),GOLD,fa(t,71.0))
    if t>=72.5:
        a=fa(t,72.5); T_(cv,(540,880),"análise de crédito no seu nome",F_("semi",38),WHITE,a)
    if t>=75.6:
        a=fa(t,75.6); y=1010
        d.rounded_rectangle((140,y,940,y+70),35,outline=GREEN+(int(255*a),),width=3)
        f=0.8+0.2*ss(76.6,77.4,t); d.rounded_rectangle((146,y+6,146+int(788*f*ss(75.6,76.2,t)),y+64),30,fill=GREEN+(int(240*a),))
        T_(cv,(540,y+35),f"A CAIXA LIBERA DE 80% A {int(80+20*ss(76.6,77.4,t))}%",F_("black",34),NAVY,a,shadow=False)
    foot(cv,"*Sujeito à aprovação de crédito pela Caixa e às condições de cada unidade.",fa(t,77.6),1160)
els.append(Scene(65.45,79.35,s_100))
# ---------- 10) CTA sobre a maquete ----------
def cta(cv,t):
    chip(cv,t,81.3,END,"CONHEÇA O ESTANDE DE VENDAS",300,GOLD,NAVY,40)
    chip(cv,t,86.0,END,"COM A MAQUETE",390,LB,NAVY,38)
    if t>=86.7:
        u=(t-86.7)/0.35; sc=(0.8+0.2*ease_out_back(min(1,u)))*(1+0.04*math.sin(t*7)); a=min(1,u*3)*(1-ss(END-0.2,END,t))
        w,h=int(560*sc),int(130*sc); x=(W-w)//2; y=1080
        p=Image.new("RGBA",(W,H),(0,0,0,0)); dp=ImageDraw.Draw(p)
        dp.rounded_rectangle((x,y,x+w,y+h),int(65*sc),fill=(0,149,246,int(245*a))); dp.text((W/2,y+h/2),"ME CHAMA AQUI",font=F_("black",int(50*sc)),fill=WHITE+(int(255*a),),anchor="mm"); cv.alpha_composite(p)
        T_(cv,(540,1260),"e a gente marca sua visita",F_("sbi",48),WHITE,fa(t,88.0))
els.append(Func(cta,81.3,END))
# ---------- cartela final ----------
HOUSE=[(360,980),(360,760),(540,600),(720,760),(720,980),(360,980)]
def s_end(cv,t,u):
    particles(cv,t,GOLD)
    glow_lines(cv,[partial(HOUSE,ss(0,1.0,u))],GOLD,6,14)
    T_(cv,(540,1110),"CRÉDITO ASSOCIATIVO",F_("black",62),WHITE,fa(t,END+0.2))
    T_(cv,(540,1195),"assina hoje · juros de hoje · financia nas chaves*",F_("sbi",40),GOLD,fa(t,END+0.5))
    T_(cv,(540,1300),"Me chama no direct",F_("bold",40),LB,fa(t,END+0.9))
    foot(cv,"*Sujeito à análise de crédito. Na obra há encargos e entrada com a construtora.",fa(t,END+0.9),1400)
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
    V=f"{D}/video.mp4"; n1=round(7.75*FPS); n3=round((END-79.55)*FPS); nmid=round(79.55*FPS)-n1; nend=round(ENDC*FPS)
    sc="scale=1080:-2:flags=lanczos,crop=1080:1920,unsharp=5:5:0.7,eq=contrast=1.05:saturation=1.08,setsar=1"
    fg=(f"[0:v]fps={FPS},trim=start_frame=0:end_frame={n1},setpts=PTS-STARTPTS,{sc}[a];"
        f"color=c=0x081020:s=1080x1920:r={FPS},trim=end_frame={nmid},setpts=PTS-STARTPTS,format=yuv420p[b];"
        f"[0:v]fps={FPS},trim=start=12.4,setpts=PTS-STARTPTS,trim=end_frame={n3},{sc}[c];"
        f"color=c=0x081020:s=1080x1920:r={FPS},trim=end_frame={nend},setpts=PTS-STARTPTS,format=yuv420p[d];"
        f"[a][b][c][d]concat=n=4:v=1:a=0,format=yuv420p[v]")
    run(["-i",V,"-filter_complex",fg,"-map","[v]","-c:v","libx264","-crf","15","-preset","fast",base])
# ---------- voz (áudios em sequência) ----------
voz=f"{B}/voz.wav"
parts="";labs=""
for k,(n,a,b,t0) in enumerate(TL["segs"]):
    parts+=f"[{k}:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.03:.3f}:d=0.03,adelay={int(t0*1000)}|{int(t0*1000)},apad=whole_dur={T:.3f}[s{k}];"; labs+=f"[s{k}]"
ins=[]
for n,a,b,t0 in TL["segs"]: ins+=["-i",f"{D}/a{n}.wav"]
run(ins+["-filter_complex",parts+labs+f"amix=inputs={len(TL['segs'])}:normalize=0:duration=longest,atrim=0:{T:.3f}[o]","-map","[o]","-ar","48000","-ac","1",voz])
mus=f"{B}/music.wav"
subprocess.run(["python3","-I",f"{ENG}/../v7/music3.py",mus,f"{T:.3f}","21.2","65.6",f"{END:.3f}"],check=True)
VOICE2=("highpass=f=85,afftdn=nr=6:nf=-45:tn=1,equalizer=f=220:t=q:w=1.0:g=-2,equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=6000:t=q:w=1.2:g=1.5,deesser=i=0.2,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
fgc=[f"[0:v]format=yuv420p[bv]",f"[1:v]format=yuva420p[ov]",
     f"[bv][ov]overlay=0:0:eof_action=pass,ass={assf}:fontsdir=/usr/share/fonts,format=yuv420p[vo]",
     f"[2:a]{VOICE2},asplit[vz][key]",f"[3:a]volume=0.20,aformat=channel_layouts=stereo[mu]",
     "[mu][key]sidechaincompress=threshold=0.04:ratio=4:attack=25:release=400[md]",
     "[vz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(["-i",base,"-i",ov,"-i",voz,"-i",mus,"-filter_complex",";".join(fgc),"-map","[vo]","-map","[ao]","-t",f"{T:.3f}",
     "-c:v","libx264","-preset","medium","-crf","19","-maxrate","8M","-bufsize","16M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{B}/final.mp4"])
light(f"{B}/final.mp4",f"{B}/final_leve.mp4")
print("ok",round(END,2),round(T,2))
