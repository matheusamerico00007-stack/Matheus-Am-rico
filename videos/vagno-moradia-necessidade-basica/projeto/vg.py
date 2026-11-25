# Vagno – "Moradia: necessidade básica" – no estilo do modelo (tipografia animada + cenas cinematográficas), elevado
import sys, os, subprocess, json, random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from eng import *
S=sys.argv[1]; ENG=os.path.dirname(os.path.abspath(__file__))
SRC=f"{S}/m2/original.mov"; B=f"{S}/m2/build"; os.makedirs(B,exist_ok=True)
SPEED=1.0; MODE=sys.argv[2] if len(sys.argv)>2 else "full"; O=f"{S}/m2/out_{MODE}"; os.makedirs(O,exist_ok=True)
END=117.65; ENDC=3.0; T=END+ENDC
words=load_words(f"{S}/m2/tr.json")
for w in words:
    if w[2]=="100" : w[2]="100%"
words=[w for w in words if w[2]!="%"]
GOLD=(242,199,94); LB=(92,184,255); WHITE=(255,255,255); RED=(255,92,92)
random.seed(7)
# ---------- fundo cinematográfico das cenas ----------
_bg=None
def scene_bg():
    global _bg
    if _bg is None:
        y=np.linspace(0,1,H)[:,None]; x=np.linspace(-1,1,W)[None,:]
        r=np.sqrt(x**2*0.6+(y-0.42)**2*1.6)
        base=np.clip(1-r*1.1,0,1)
        img=np.zeros((H,W,3)); c0=np.array([4,7,14]); c1=np.array([14,32,62])
        img=c0+(c1-c0)*base[...,None]
        _bg=Image.fromarray(img.astype(np.uint8)).convert("RGBA")
    return _bg.copy()
PART=[(random.random()*W,random.random()*H,random.uniform(1,3),random.uniform(8,30)) for _ in range(90)]
def particles(cv,t,col=GOLD,a=1.0):
    d=ImageDraw.Draw(cv)
    for (x,y,r,sp) in PART:
        yy=(y-t*sp)%H; al=int(70*a*(0.5+0.5*math.sin(t*2+x)))
        d.ellipse((x-r,yy-r,x+r,yy+r),fill=col+(al,))
def glow_lines(cv,segs,col,width=6,blur=10,a=1.0):
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for s in segs: d.line(s,fill=col+(int(255*a),),width=width*3,joint="curve")
    lay=lay.filter(ImageFilter.GaussianBlur(blur)); cv.alpha_composite(lay)
    lay2=Image.new("RGBA",(W,H),(0,0,0,0)); d2=ImageDraw.Draw(lay2)
    for s in segs: d2.line(s,fill=(255,250,235,int(255*a)),width=width,joint="curve")
    cv.alpha_composite(lay2)
def partial(poly,f):
    # devolve a fração f do comprimento de uma polilinha
    pts=poly; L=[math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1)]; tot=sum(L); goal=tot*max(0,min(1,f)); out=[pts[0]]; acc=0
    for i,l in enumerate(L):
        if acc+l>=goal:
            u=(goal-acc)/l if l else 0; out.append((pts[i][0]+(pts[i+1][0]-pts[i][0])*u,pts[i][1]+(pts[i+1][1]-pts[i][1])*u)); return out
        out.append(pts[i+1]); acc+=l
    return out
def big_text(cv,txt,y,size,col=WHITE,a=1.0,fname="serif_i",shadow=True,x=W/2):
    f=ImageFont.truetype("/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf",size) if fname=="serif_bi" else font(fname,size)
    if shadow:
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((x+3,y+6),txt,font=f,fill=(0,0,0,int(160*a)),anchor="mm"); sh=sh.filter(ImageFilter.GaussianBlur(8)); cv.alpha_composite(sh)
    ImageDraw.Draw(cv).text((x,y),txt,font=f,fill=col+(int(255*a),),anchor="mm")
def scene_alpha(t,t0,t1,fi=0.18,fo=0.18): return ss(t0,t0+fi,t)*(1-ss(t1-fo,t1,t))
_mask={}
def card_mask(w,h,r=44):
    k=(w,h)
    if k not in _mask:
        m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),r,fill=255); _mask[k]=m
    return _mask[k]
HY0,HY1=230,1310; HS=0.80; HTOP=880   # metade de baixo: recorte do miolo da cena -> cartão
class Scene:
    def __init__(s,t0,t1,fn,full=False): s.t0=t0; s.t1=t1; s.fn=fn; s.full=full
    def draw(s,cv,t):
        if not (s.t0<=t<s.t1): return
        a=scene_alpha(t,s.t0,s.t1); lay=scene_bg(); s.fn(lay,t,t-s.t0)
        if MODE=="half" and not s.full:
            crop=lay.crop((0,HY0,W,HY1)); w,h=int(W*HS),int((HY1-HY0)*HS)
            u=min(1,(t-s.t0)/0.35); sc=0.9+0.1*ease_out_back(u)
            w2,h2=max(2,int(w*sc)),max(2,int(h*sc)); crop=crop.resize((w2,h2),Image.LANCZOS)
            card=Image.new("RGBA",(w2,h2),(0,0,0,0)); card.paste(crop,(0,0),card_mask(w2,h2))
            ImageDraw.Draw(card).rounded_rectangle((0,0,w2-1,h2-1),44,outline=(242,199,94,170),width=3)
            x=(W-w2)//2; y=HTOP+(h-h2)//2
            sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((x+6,y+14,x+w2+6,y+h2+14),44,fill=(0,0,0,150)); sh=sh.filter(ImageFilter.GaussianBlur(18))
            lay=Image.new("RGBA",(W,H),(0,0,0,0)); lay.alpha_composite(sh); lay.alpha_composite(card,(x,y))
        if a<1: lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
        cv.alpha_composite(lay)
SC=[]   # (t0,t1) das cenas em tela cheia (para a tipografia descer)
def add_scene(t0,t1,fn): SC.append((t0,t1)); els.append(Scene(t0,t1,fn))
els=[]
# 1) INCERTEZAS – gráfico instável
_walk=[]; v=0.5
for k in range(60): v=min(0.9,max(0.1,v+random.uniform(-0.18,0.16))); _walk.append(v)
def s_incerteza(cv,t,u):
    particles(cv,t,RED,0.6); d=ImageDraw.Draw(cv)
    for k in range(6): d.line((80,500+k*110,1000,500+k*110),fill=(80,110,160,60),width=1)
    pts=[(80+k*(920/59),1100-_walk[k]*600) for k in range(60)]
    seg=partial(pts,u/1.6); flick=0.75+0.25*math.sin(t*40)
    if len(seg)>1: glow_lines(cv,[seg],RED,width=5,blur=12,a=flick)
    big_text(cv,"INCERTEZA",360,120,WHITE,ss(0.1,0.45,u),"serif_bi")
add_scene(2.15,4.6,s_incerteza)
# 2) MORADIA – casa desenhada em luz
HOUSE=[(330,1080),(330,760),(540,560),(750,760),(750,1080),(330,1080)]
DOOR=[(490,1080),(490,920),(590,920),(590,1080)]
def house(cv,u,a=1.0,scale=1.0,cy=0):
    def tr(p): return (540+(p[0]-540)*scale,820+(p[1]-820)*scale+cy)
    segs=[[tr(p) for p in partial(HOUSE,u)]]
    if u>0.8: segs.append([tr(p) for p in partial(DOOR,(u-0.8)/0.2)])
    glow_lines(cv,segs,GOLD,width=6,blur=14,a=a)
def s_moradia(cv,t,u):
    particles(cv,t,GOLD); house(cv,ss(0,1.6,u))
    big_text(cv,"MORADIA",1250,140,GOLD,ss(0.35,0.8,u),"serif_bi")
add_scene(11.6,13.0,s_moradia)
# 3) 5 · 10 · 20 ANOS
def s_anos(cv,t,u):
    particles(cv,t,GOLD,0.7); house(cv,1.0,0.9,0.55,-180)
    d=ImageDraw.Draw(cv); y=1030
    d.line((170,y,910,y),fill=(120,150,200,120),width=4)
    for k,(tk,txt) in enumerate([(15.3,"5"),(16.0,"10"),(16.5,"20")]):
        x=250+k*290; on=t>=tk; a=ss(tk,tk+0.2,t)
        d.ellipse((x-22,y-22,x+22,y+22),fill=(GOLD if on else (60,70,90))+(255,))
        if on: big_text(cv,txt,y+120,110,WHITE,a,"black",x=x); big_text(cv,"ANOS",y+215,40,GOLD,a,"bold",False,x=x)
add_scene(15.15,17.15,s_anos)
# 4) CRÉDITO ASSOCIATIVO – diagrama
def icon_box(cv,x,y,label,on_t,t,sub=None):
    a=ss(on_t,on_t+0.25,t); d=ImageDraw.Draw(cv)
    if a<=0: return
    d.rounded_rectangle((x-210,y-60,x+210,y+60),26,fill=(14,34,66,int(235*a)),outline=LB+(int(255*a),),width=3)
    d.text((x,y-(12 if sub else 0)),label,font=font("black",40),fill=WHITE+(int(255*a),),anchor="mm")
    if sub: d.text((x,y+30),sub,font=font("semi",26),fill=LB+(int(255*a),),anchor="mm")
def s_assoc(cv,t,u):
    particles(cv,t,LB,0.5); d=ImageDraw.Draw(cv)
    big_text(cv,"CRÉDITO ASSOCIATIVO",300,72,WHITE,ss(0,0.3,u),"serif_bi")
    icon_box(cv,540,470,"COMPRA NA PLANTA",35.7,t)
    icon_box(cv,540,650,"ASSINA COM O BANCO",37.4,t,"garantidor da obra")
    if t>=40.6:
        a=ss(40.6,40.9,t); d.text((540,790),"OBRA · 3 ANOS",font=font("bold",36),fill=WHITE+(int(255*a),),anchor="mm")
        d.rounded_rectangle((190,830,890,866),18,outline=LB+(int(255*a),),width=3)
        f=ss(41.0,43.2,t); d.rounded_rectangle((194,834,194+692*f,862),16,fill=LB+(int(255*a),))
    icon_box(cv,540,980,"RECEBE AS CHAVES",43.4,t,"começa o financiamento")
    for (y0,y1,tk) in ((530,590,37.4),(710,770,40.6),(870,920,43.4)):
        if t>=tk: d.line((540,y0,540,y1),fill=LB+(200,),width=4)
    if t>=43.4: d.text((540,1110),"*Durante a obra podem existir parcelas de entrada e encargos de obra.",font=font("med",24),fill=(190,200,220,200),anchor="mm")
add_scene(34.85,44.85,s_assoc)
# 5) o View: imagens + animação do mall + preço (cartões sobre o vídeo)
els.append(Card("04",[0,0,1,.765],57.4,63.85,top=250,maxw=1000,anim="zoom",border=(242,199,94,170)))
def chip(cv,t,t0,t1,txt,y,col=GOLD,fg=(10,14,24),size=46):
    sc,a=(lambda u:(1.35-0.35*ease_out_back(u) if u<1 else 1.0, min(1,max(0,u*3))))((t-t0)/0.3); a*=1-ss(t1-0.2,t1,t)
    f=font("black",int(size*sc)); d=ImageDraw.Draw(cv); bb=d.textbbox((W/2,y),txt,font=f,anchor="mm")
    p=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle((bb[0]-26,bb[1]-16,bb[2]+26,bb[3]+16),20,fill=col+(int(240*a),))
    ImageDraw.Draw(p).text((W/2,y),txt,font=f,fill=fg+(int(255*a),),anchor="mm"); cv.alpha_composite(p)
els.append(Func(lambda cv,t: chip(cv,t,58.4,63.85,"ESTORIL · BURITIS · BARÃO",820),58.4,63.85))
els.append(Func(lambda cv,t: chip(cv,t,62.8,63.85,"2 E 3 QUARTOS",920,LB),62.8,63.85))
els.append(Func(lambda cv,t: chip(cv,t,64.0,66.9,"LANÇAMENTO 2026",380,GOLD,(10,14,24),72),64.0,66.9))
class AnimClip:
    def __init__(s,path,t0,t1,y): s.path=path; s.t0=t0; s.t1=t1; s.y=y; s.p=None; s.idx=-1; s.cur=None
    def draw(s,cv,t):
        if not (s.t0<=t<s.t1): return
        if s.p is None: s.p=subprocess.Popen(["ffmpeg","-v","error","-i",s.path,"-f","rawvideo","-pix_fmt","rgba","-"],stdout=subprocess.PIPE)
        want=int(round((t-s.t0)*FPS))
        while s.idx<want:
            b=s.p.stdout.read(1080*940*4)
            if len(b)<1080*940*4: break
            s.cur=Image.frombytes("RGBA",(1080,940),b); s.idx+=1
        if s.cur is not None:
            im=s.cur
            if t>s.t1-0.2: im=im.copy(); im.putalpha(im.getchannel("A").point(lambda v:int(v*(1-ss(s.t1-0.2,s.t1,t)))))
            cv.alpha_composite(im,(0,s.y))
A0,A1=68.6,73.15
anim=f"{B}/anim.mov"
if not os.path.exists(anim): subprocess.run(["python3","-I",f"{ENG}/../v7/anim.py",f"{BOOK}/mall.jpg",anim,f"{A1-A0:.3f}"],check=True)
els.append(AnimClip(anim,A0,A1,y=170))
els.append(Func(lambda cv,t: chip(cv,t,69.0,A1,"SHOPPING A CÉU ABERTO",700,GOLD),69.0,A1))
els.append(Func(lambda cv,t: chip(cv,t,71.3,A1,"3 TORRES · LAZER COMPLETO",800,LB,(10,14,24),40),71.3,A1))
def preco(cv,t):
    t0,t1=73.2,82.75; a=ss(t0,t0+0.25,t)*(1-ss(t1-0.25,t1,t))
    p=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle((70,200,1010,760),34,fill=(6,14,30,int(225*a)),outline=GOLD+(int(220*a),),width=3); cv.alpha_composite(p)
    d=ImageDraw.Draw(cv)
    if t>=74.1:
        aa=ss(74.1,74.4,t)*a; d.text((540,270),"A PARTIR DE",font=font("bold",38),fill=GOLD+(int(255*aa),),anchor="mm")
        v=int(420*ss(74.6,75.4,t)); d.text((540,375),f"R$ {v} MIL",font=font("black",120),fill=WHITE+(int(255*aa),),anchor="mm")
    if t>=78.9:
        aa=ss(78.9,79.2,t)*a; d.text((540,520),"FINANCIE QUASE 100%*",font=font("black",56),fill=LB+(int(255*aa),),anchor="mm")
    if t>=81.0:
        aa=ss(81.0,81.3,t)*a; d.text((540,610),"E COMECE A PAGAR NAS CHAVES*",font=font("bold",44),fill=WHITE+(int(255*aa),),anchor="mm")
        d.text((540,700),"*Conforme renda e aprovação de crédito. Pode haver encargos durante a obra.",font=font("med",23),fill=(190,200,220,int(220*aa)),anchor="mm")
els.append(Func(preco,73.2,82.75))
# 6) siga o Vagno + quem paga é o inquilino
def follow(cv,t):
    t0,t1=86.7,88.4; u=(t-t0)/0.3; sc=1.35-0.35*ease_out_back(u) if u<1 else 1.0; a=min(1,max(0,u*3))*(1-ss(t1-0.2,t1,t))
    clicked=t>=87.6; w,h=int(520*sc),int(120*sc); x=(W-w)/2; y=380
    p=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle((x,y,x+w,y+h),int(26*sc),fill=((40,40,48) if clicked else (0,149,246))+(int(245*a),))
    d.text((W/2,y+h/2),"Seguindo ✓" if clicked else "Seguir",font=font("black",int(54*sc)),fill=WHITE+(int(255*a),),anchor="mm")
    d.text((W/2,y-50),"VAGNO SILVA",font=font("black",58),fill=WHITE+(int(255*a),),anchor="mm",stroke_width=4,stroke_fill=(0,0,0,int(120*a)))
    cv.alpha_composite(p)
els.append(Func(follow,86.7,88.4))
els.append(Func(lambda cv,t: chip(cv,t,90.6,92.75,"QUEM PAGA É O SEU INQUILINO*",420,GOLD),90.6,92.75))
# 7) fechamento: Bitcoin, bolsa, dólar, governo -> teto
def s_flash(label,sym,col):
    def fn(cv,t,u):
        particles(cv,t,col,0.6); a=ss(0,0.25,u)
        big_text(cv,sym,780,260 if len(sym)<4 else 200,col,a,"black")
        big_text(cv,label,1060,86,WHITE,a,"serif_bi")
        big_text(cv,"DAQUI 30 ANOS?",1180,48,col,ss(0.3,0.6,u),"bold",False)
    return fn
def s_bolsa(cv,t,u):
    particles(cv,t,RED,0.6); d=ImageDraw.Draw(cv); random.seed(3)
    for k in range(14):
        x=180+k*52; o_=random.uniform(560,900); c=o_+random.uniform(-140,140); hi=min(o_,c)-random.uniform(20,80); lo=max(o_,c)+random.uniform(20,80)
        if k/14>ss(0,0.9,u): break
        col=(90,220,140) if c<o_ else RED; d.line((x,hi,x,lo),fill=col+(255,),width=4); d.rectangle((x-16,min(o_,c),x+16,max(o_,c)),fill=col+(255,))
    big_text(cv,"BOLSA DE VALORES",1060,80,WHITE,ss(0,0.25,u),"serif_bi"); big_text(cv,"DAQUI 30 ANOS?",1180,48,RED,ss(0.3,0.6,u),"bold",False)
def s_gov(cv,t,u):
    particles(cv,t,LB,0.6); f=ss(0,0.9,u)
    cols=[[(x,920),(x,640)] for x in (360,460,620,720)]
    roof=[(300,640),(540,500),(780,640),(300,640)]; base=[(280,920),(800,920)]
    segs=[partial(roof,f)]+[partial(c,f) for c in cols]+[partial(base,f)]
    glow_lines(cv,[s for s in segs if len(s)>1],LB,width=5,blur=12)
    big_text(cv,"GOVERNO",1060,96,WHITE,ss(0,0.25,u),"serif_bi"); big_text(cv,"DAQUI 30 ANOS?",1180,48,LB,ss(0.3,0.6,u),"bold",False)
add_scene(98.3,100.35,s_flash("BITCOIN","BTC",GOLD))
add_scene(100.35,103.1,s_bolsa)
add_scene(103.1,105.75,s_flash("DÓLAR","US$",(120,220,150)))
add_scene(105.75,108.15,s_gov)
def s_teto(cv,t,u):
    particles(cv,t,GOLD); house(cv,ss(0,1.4,u))
    big_text(cv,"UM TETO",1250,130,GOLD,ss(0.3,0.7,u),"serif_bi")
add_scene(110.0,113.85,s_teto)
def onda(cv,t):  # "surfando essa onda"
    a=ss(116.5,116.8,t); pts=[(x,1180+math.sin(x/70+t*4)*30) for x in range(60,1021,20)]
    seg=partial(pts,ss(116.5,117.4,t))
    if len(seg)>1: glow_lines(cv,[seg],LB,width=5,blur=10,a=a)
els.append(Func(onda,116.5,END))
# cartela final
def s_end(cv,t,u):
    particles(cv,t,GOLD); house(cv,1.0,0.85,0.62,-170)
    big_text(cv,"VAGNO SILVA",1060,96,WHITE,ss(0,0.3,u),"black")
    big_text(cv,"Invista em necessidade básica: moradia.",1160,44,GOLD,ss(0.3,0.6,u),"serif_i",False)
    if u>0.8:
        a=ss(0.8,1.1,u); d=ImageDraw.Draw(cv); x0,y0=540-160,1280
        d.rounded_rectangle((x0,y0,x0+320,y0+90),24,fill=(0,149,246,int(245*a))); d.text((540,y0+45),"Seguir",font=font("black",46),fill=WHITE+(int(255*a),),anchor="mm")
els.append(Scene(END,T,s_end,full=True)); SC.append((END,T))
# ---------- tipografia animada (estilo do modelo) ----------
EMPH={"investidor","incertezas","patrimônio","necessidade","básica","moradia","teto","governo","cidade","crédito","associativo","banco","planta","financiamento","inquilino","parcela","shopping","aberto","torres","chave","bitcoin","bolsa","dólar","certeza","onda","vagno","silva","seguro","proteger","construir","estoril","buritis","lançamento","capital","surfando","investir"}
def is_num(s): return any(ch.isdigit() for ch in s)
chunks=[];cur=[]
for w in words:
    if w[0]>=END: break
    cur.append(w); txt=" ".join(x[2] for x in cur)
    if w[2][-1:] in ".,?!" or len(cur)>=5 or len(txt)>26: chunks.append(cur); cur=[]
if cur: chunks.append(cur)
def in_scene(t): return any(a-0.05<=t<b+0.05 for a,b in SC)
def typo(cv,t):
    for i,ch in enumerate(chunks):
        st=ch[0][0]-0.05; en=min(chunks[i+1][0][0]-0.02 if i+1<len(chunks) else END, ch[-1][1]+0.7)
        if not (st<=t<en): continue
        yc=(250 if (MODE=='half' and (in_scene(st+0.05) or in_scene(t))) else 1480)
        toks=[]
        for w in ch:
            raw=w[2]; clean=raw.strip(",.?!").lower()
            emph=clean in EMPH; num=is_num(raw) or clean in ("mil","reais")
            f=ImageFont.truetype("/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf",86) if emph else font("semi",70)
            col=LB if num else WHITE
            toks.append((raw.strip(",.") if not raw.endswith("?") else raw,f,col,w[0]))
        # quebra em até 2 linhas
        d=ImageDraw.Draw(cv); sp=18; widths=[d.textbbox((0,0),s,font=f)[2] for s,f,_,_ in toks]
        lines=[[]]; lw=0
        for k,wd in enumerate(widths):
            if lines[-1] and lw+wd>900: lines.append([]); lw=0
            lines[-1].append(k); lw+=wd+sp
        y0=yc-(len(lines)-1)*55
        for li,ln in enumerate(lines):
            tot=sum(widths[k] for k in ln)+sp*(len(ln)-1); x=(W-tot)/2; y=y0+li*110
            for k in ln:
                s_,f,col,wt=toks[k]; a=ss(wt-0.05,wt+0.1,t)*(1-ss(en-0.12,en,t)); dy=(1-ss(wt-0.05,wt+0.12,t))*16
                if a>0:
                    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((x+3,y+dy+5),s_,font=f,fill=(0,0,0,int(170*a)),anchor="ls"); sh=sh.filter(ImageFilter.GaussianBlur(6)); cv.alpha_composite(sh)
                    ImageDraw.Draw(cv).text((x,y+dy),s_,font=f,fill=col+(int(255*a),),anchor="ls")
                x+=widths[k]+sp
els.append(Func(typo,0,END))
if os.environ.get("PREVIEW"):
    for t in [float(x) for x in os.environ["PREVIEW"].split(",")]:
        fr=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",f"{B}/base.mkv","-frames:v","1","-f","rawvideo","-pix_fmt","rgba","-"],capture_output=True).stdout
        cv=Image.frombytes("RGBA",(W,H),fr)
        for e in els:
            if getattr(e,"t0",0)<=t<getattr(e,"t1",T): e.draw(cv,t)
        cv.convert("RGB").resize((360,640)).save(f"{O}/pv_{t}.png")
    sys.exit()
ov=f"{B}/overlay.mov" if MODE=="full" else f"{O}/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- base: P&B na abertura, zoom de impacto, desfoque nas transições ----------
GR="eq=contrast=1.08:saturation=0.92:gamma=0.98,colorbalance=rs=-0.03:bs=0.05:rh=0.05:gh=0.01:bh=-0.04"
ZW=[(73.2,75.6,1.12),(108.2,110.0,1.16),(113.9,116.45,1.08)]
zexpr="1"+"".join(f"+{z-1:.2f}*between(t,{a},{b})" for a,b,z in ZW)
base=f"{B}/base.mkv"
if not os.path.exists(base):
    nf=round(END*FPS)
    v=(f"[0:v]fps={FPS}:start_time=0,trim=end_frame={nf},setpts=PTS-STARTPTS,"
       f"scale=w='trunc(1080*({zexpr})/2)*2':h='trunc(1920*({zexpr})/2)*2':eval=frame:flags=lanczos,crop=1080:1920:(iw-1080)*0.46:(ih-1920)*0.34,setsar=1,{GR},hue=s=0:enable='lt(t,1.78)'[v]")
    a=f"[0:a:0]atrim=0:{END},asetpts=PTS-STARTPTS,afade=t=out:st={END-0.08}:d=0.08,apad,atrim=0:{nf/FPS:.6f}[a]"
    run(["-i",SRC,"-filter_complex",v+";"+a,"-map","[v]","-map","[a]","-ac","1","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",base])
endbg=f"{B}/endbg.mkv"
if not os.path.exists(endbg):
    nfe=round(ENDC*FPS)
    run(["-f","lavfi","-i",f"color=c=black:s=1080x1920:r={FPS}:d={nfe/FPS:.4f}","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t",f"{nfe/FPS:.4f}",
         "-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",endbg])
# transições: desfoque rápido nas entradas/saídas das cenas e nas viradas
TR=sorted(set([1.78]+[a for a,b in SC]+[b for a,b in SC if b<END]+[57.4,63.85,68.6,73.2,82.75]))
blur="".join(f",gblur=sigma=26:enable='between(t,{x-0.09:.2f},{x+0.09:.2f})'" for x in TR)
mus=f"{O}/music.wav"
subprocess.run(["python3","-I",f"{ENG}/../v6/music2.py",mus,f"{T/SPEED:.3f}",f"{1.78/SPEED:.3f}",f"{55.3/SPEED:.3f}",f"{82.8/SPEED:.3f}",f"{93.9/SPEED:.3f}",f"{108.2/SPEED:.3f}",f"{END/SPEED:.3f}"],check=True)
VOICE2=("highpass=f=90,afftdn=nr=6:nf=-44:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
        "equalizer=f=300:t=q:w=1.0:g=-2,equalizer=f=2800:t=q:w=1.2:g=2.5,equalizer=f=5000:t=q:w=1.2:g=2.5,deesser=i=0.25,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=12:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
fg=[f"[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[cv][ca]",f"[2:v]format=yuva420p[ov]",
    f"[cv][ov]overlay=0:0:eof_action=pass{blur}[c2]",
    f"[c2]setpts=PTS/{SPEED},fps={FPS},format=yuv420p[vo]",
    f"[ca]atempo={SPEED},{VOICE2},asplit[voz][key]",f"[3:a]volume=0.30,aformat=channel_layouts=stereo[mus]",
    "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=450[md]",
    "[voz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(["-i",base,"-i",endbg,"-i",ov,"-i",mus,"-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
     "-c:v","libx264","-preset","medium","-crf","20","-maxrate","9M","-bufsize","18M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{O}/final.mp4"])
light(f"{O}/final.mp4",f"{O}/final_leve.mp4")
print("ok",round(T,2),round(T/SPEED,2),len(SC),"cenas")
