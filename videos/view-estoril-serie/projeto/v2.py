# VÍDEO 2 – Maquete – estilo PAINEL TECNOLÓGICO (HUD)
import sys, os, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from eng import *
D=sys.argv[1]; SRC=f"{D}/original.mov"; ENG=os.path.dirname(os.path.abspath(__file__))
END=48.25; ENDC=2.8; T=END+ENDC
GRADE="eq=contrast=1.07:saturation=1.0:gamma=0.98,colorbalance=rs=-0.03:bs=0.06:bm=0.02:rh=-0.01:bh=0.02,unsharp=5:5:0.3"
words=load_words(f"{D}/tr.json")
CY=(127,208,255); NAVY=(8,22,44)
os.makedirs(f"{D}/build",exist_ok=True)
def tx(d,xy,s,f,fill,anchor="la"): d.text(xy,s,font=f,fill=fill,anchor=anchor)
def panel(cv,box,a,r=18,fill_a=200,border=True):
    p=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle(box,r,fill=NAVY+(int(fill_a*a),))
    if border: d.rounded_rectangle(box,r,outline=CY+(int(230*a),),width=2)
    cv.alpha_composite(p)
# ---------- HUD fixo ----------
def hud(cv,t):
    a=ss(0,0.5,t)*(1-ss(END-0.3,END,t)); d=ImageDraw.Draw(cv); A=int(220*a)
    L=70; m=46
    for (x,y,sx,sy) in ((m,m,1,1),(W-m,m,-1,1),(m,H-m,1,-1),(W-m,H-m,-1,-1)):
        d.line((x,y,x+sx*L,y),fill=CY+(A,),width=4); d.line((x,y,x,y+sy*L),fill=CY+(A,),width=4)
    f=font("mono_b",26)
    if int(t*2)%2==0: d.ellipse((m+24,m+30,m+40,m+46),fill=(255,70,70,A))
    tx(d,(m+52,m+26),"REC  VIEW ESTORIL / MAQUETE",f,(255,255,255,A))
    tx(d,(W-m-24,m+26),f"T+{int(t//60):02d}:{int(t%60):02d}",f,(255,255,255,A),"ra")
    f2=font("mono",22)
    tx(d,(m+24,H-m-52),"19.96°S  43.95°W  ·  ESTORIL · BH",f2,CY+(int(200*a),))
    tx(d,(W-m-24,H-m-52),"EMCCAMP",f2,CY+(int(200*a),),"ra")
els=[Func(hud,0,END)]
# ---------- shopping nascendo (animação planta -> render) ----------
class AnimClip:
    def __init__(s,path,t0,t1,y): s.path=path; s.t0=t0; s.t1=t1; s.y=y; s.p=None; s.idx=-1; s.cur=None
    def draw(s,cv,t):
        if not (s.t0<=t<s.t1): return
        if s.p is None:
            s.p=subprocess.Popen(["ffmpeg","-v","error","-i",s.path,"-f","rawvideo","-pix_fmt","rgba","-"],stdout=subprocess.PIPE)
        want=int(round((t-s.t0)*FPS))
        while s.idx<want:
            b=s.p.stdout.read(1080*940*4)
            if len(b)<1080*940*4: break
            s.cur=Image.frombytes("RGBA",(1080,940),b); s.idx+=1
        if s.cur is not None:
            im=s.cur
            if t>s.t1-0.2:
                im=im.copy(); im.putalpha(im.getchannel("A").point(lambda v:int(v*(1-ss(s.t1-0.2,s.t1,t)))))
            cv.alpha_composite(im,(0,s.y))
A0,A1=2.20,8.95
anim=f"{D}/build/anim.mov"
if not os.path.exists(anim):
    subprocess.run(["python3","-I",f"{ENG}/../v7/anim.py",f"{BOOK}/mall.jpg",anim,f"{A1-A0:.3f}"],check=True)
els.append(AnimClip(anim,A0,A1,y=300))
def tag(cv,t,t0,t1,txt,y,sub=None):
    a=ss(t0,t0+0.25,t)*(1-ss(t1-0.2,t1,t)); d=ImageDraw.Draw(cv); f=font("mono_b",40)
    s=f"[ {txt} ]"; bb=d.textbbox((0,0),s,font=f); w=bb[2]-bb[0]
    panel(cv,((W-w)/2-22,y-14,(W+w)/2+22,y+58),a)
    tx(ImageDraw.Draw(cv),(W/2,y+22),s,f,CY+(int(255*a),),"mm")
    if sub:
        f2=font("mono",30); bb=d.textbbox((0,0),sub,font=f2); w2=bb[2]-bb[0]
        panel(cv,((W-w2)/2-18,y+760-14,(W+w2)/2+18,y+760+46),a,fill_a=170,border=False)
els.append(Func(lambda cv,t: tag(cv,t,A0+0.1,A1,"OPEN MALL",200),A0,A1))
def mallsub(cv,t):
    for (t0,t1,s) in ((A0+3.1,A0+4.9,"ASSINATURA DAVID GUERRA"),(A0+4.9,A1,"17 LOJAS + 4 SALAS")):
        if t0<=t<t1:
            a=ss(t0,t0+0.2,t)*(1-ss(t1-0.15,t1,t)); d=ImageDraw.Draw(cv); f=font("mono_b",34)
            bb=d.textbbox((0,0),s,font=f); w=bb[2]-bb[0]; y=300+40+382+34
            panel(cv,((W-w)/2-20,y-12,(W+w)/2+20,y+52),a,fill_a=190)
            tx(ImageDraw.Draw(cv),(W/2,y+20),s,f,(255,255,255,int(255*a)),"mm")
els.append(Func(mallsub,A0+3.1,A1))
# ---------- painéis de dados ----------
def slide_panel(cv,t,t0,t1,x,y,w,h,lines,side="left"):
    u=ss(t0,t0+0.35,t); a=u*(1-ss(t1-0.2,t1,t))
    off=(1-u)*(-300 if side=="left" else 300)
    panel(cv,(x+off,y,x+w+off,y+h),a)
    d=ImageDraw.Draw(cv); yy=y+26
    for (s,fname,size,col) in lines:
        f=font(fname,size); tx(d,(x+off+30,yy),s,f,col+(int(255*a),)); yy+=size+16
els.append(Func(lambda cv,t: slide_panel(cv,t,9.4,13.9,60,330,640,250,
    [("NOVO LANÇAMENTO","mono",30,CY),("EMCCAMP","black",84,(255,255,255)),("+49 ANOS DE EXPERIÊNCIA","mono",28,CY)]),9.4,13.9))
els.append(Func(lambda cv,t: slide_panel(cv,t,11.9,13.9,380,620,640,130,
    [("REGIÃO","mono",26,CY),("BURITIS · ESTORIL","black",50,(255,255,255))],side="right"),11.9,13.9))
els.append(Func(lambda cv,t: slide_panel(cv,t,15.2,17.4,60,330,760,150,
    [("À FRENTE DO SHOPPING","mono",28,CY),("AV. BARÃO HOMEM DE MELO","black",52,(255,255,255))]),15.2,17.4))
def metrics(cv,t):
    items=[(17.5,"TORRES",3,""),(18.3,"UNIDADES",512,""),(19.1,"M² DE TERRENO",18889,"")]
    for k,(t0,lab,val,suf) in enumerate(items):
        u=ss(t0,t0+0.35,t); a=u*(1-ss(21.4,21.65,t)); y=330+k*190; off=(1-u)*320
        panel(cv,(560+off,y,1020+off,y+165),a)
        v=int(val*ss(t0+0.1,t0+0.9,t)); s=f"{v:,}".replace(",",".")
        d=ImageDraw.Draw(cv); tx(d,(590+off,y+18),s,font("black",88),(255,255,255,int(255*a))); tx(d,(592+off,y+118),lab,font("mono",28),CY+(int(255*a),))
    u=ss(20.2,20.5,t); a=u*(1-ss(21.4,21.65,t))
    panel(cv,(60,330,520,495),a); d=ImageDraw.Draw(cv)
    tx(d,(90,348),"2 E 3",font("black",88),(255,255,255,int(255*a))); tx(d,(92,448),"QUARTOS",font("mono",28),CY+(int(255*a),))
els.append(Func(metrics,17.5,21.65))
# ---------- lazer: checklist escaneado + foto de cada item ----------
LZ=[(25.2,"QUADRA DE AREIA","12",[0.0326,0.0445,0.4674,0.9524]),(25.85,"PISCINA","11",None),(26.75,"SALÃO DE FESTAS","10",None),
    (28.25,"ACADEMIA","08",None),(29.25,"BRINQUEDOTECA","13",[0.0348,0.5087,0.4652,0.9555])]
LZ_END=31.9
def lazer(cv,t):
    a0=ss(22.0,22.35,t)*(1-ss(LZ_END-0.25,LZ_END,t))
    panel(cv,(60,300,1020,400),a0); d=ImageDraw.Draw(cv)
    tx(d,(540,350),"LAZER RESORT ENTRE AS TORRES",font("mono_b",38),(255,255,255,int(255*a0)),"mm")
    for k,(t0,lab,pg,rc) in enumerate(LZ):
        if t<t0: continue
        a=ss(t0,t0+0.2,t)*(1-ss(LZ_END-0.25,LZ_END,t)); y=1130+k*62
        panel(cv,(60,y,560,y+52),a,r=12,fill_a=190,border=False)
        d=ImageDraw.Draw(cv); tx(d,(84,y+8),"✓",ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",32),CY+(int(255*a),))
        tx(d,(130,y+10),lab,font("mono_b",30),(255,255,255,int(255*a)))
        # barra de varredura
        if t<t0+0.35:
            sx=60+500*ss(t0,t0+0.35,t); d.line((sx,y,sx,y+52),fill=CY+(int(255*a),),width=3)
els.append(Func(lazer,22.0,LZ_END))
for k,(t0,lab,pg,rc) in enumerate(LZ):
    t1=LZ[k+1][0] if k+1<len(LZ) else LZ_END
    els.append(Card(pg,rc,t0,t1,top=440,maxw=980,maxh=640,anim="zoom" if k==0 else "right",fin=True,fout=(k==len(LZ)-1),border=(127,208,255,200)))
# ---------- preço digitado ----------
def price(cv,t):
    a=ss(39.2,39.45,t)*(1-ss(42.3,42.55,t)); panel(cv,(90,560,990,900),a)
    d=ImageDraw.Draw(cv); tx(d,(540,620),"UNIDADES A PARTIR DE",font("mono",34),CY+(int(255*a),),"mm")
    full="R$ 450 MIL"; n=int(len(full)*ss(40.0,41.0,t)+0.999) if t>=40.0 else 0
    s=full[:n]+("_" if int(t*3)%2==0 and t<42.3 else "")
    tx(d,(540,760),s,font("mono_b",120),(255,255,255,int(255*a)),"mm")
els.append(Func(price,39.2,42.55))
def cta(cv,t):
    a=ss(42.6,42.85,t); d=ImageDraw.Draw(cv); full="> ME CHAMA AGORA"
    n=min(len(full),int((t-42.7)*18)) if t>42.7 else 0; s=full[:max(0,n)]+("_" if int(t*3)%2==0 else "")
    panel(cv,(90,600,990,760),a); tx(d,(130,680),s,font("mono_b",64),(255,255,255,int(255*a)),"lm")
els.append(Func(cta,42.6,END))
els.append(Card("mall.jpg",None,END,T,top=560,maxw=940,anim="rise",fout=False,border=(127,208,255,200)))
ov=f"{D}/build/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- legendas (ASS) ----------
st=["Style: Cap,JetBrains Mono,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,2,80,80,300,1",
    "Style: Big,Inter Display Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,2,0,1,4,4,8,80,80,0,1",
    "Style: Mono,JetBrains Mono,36,&H00FFD07F,&H00FFFFFF,&H002C1608,&H002C1608,-1,0,0,0,100,100,2,0,3,14,0,8,80,80,0,1",
    "Style: Disc,Inter Medium,26,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,60,60,110,1"]
ev=word_captions(words,"Cap","&HFFD07F&",END,maxw=3,maxc=15)
def add(a,b,style,text,fx="{\\fad(200,200)}",layer=2): ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{fx}{text}")
add(A0,A1,"Disc","Imagem meramente ilustrativa",fx="")
add(25.2,LZ_END,"Disc","Imagens meramente ilustrativas",fx="")
add(END,T,"Big","VIEW ESTORIL",fx="{\\fad(300,0)\\pos(540,330)}")
add(END+0.2,T,"Mono","OPEN MALL · ESTORIL · BH",fx="{\\fad(300,0)\\pos(540,460)}")
add(END+0.5,T,"Mono","> ME CHAMA AQUI_",fx="{\\fad(250,0)\\pos(540,%d)}"%(560+352+40))
add(END,T,"Disc","Imagem meramente ilustrativa",fx="")
assf=f"{D}/build/v.ass"; open(assf,"w").write(ass_head(st)+"\n".join(ev)+"\n")
render_base(D,SRC,END,GRADE,f"{D}/build/base.mkv")
render_endbg(SRC,46.5,ENDC,GRADE,f"{D}/build/endbg.mkv",dark=-0.2,blur=12)
mus=f"{D}/build/music.wav"
subprocess.run(["python3","-I",f"{ENG}/../v3/beat.py",mus,f"{T/SPEED:.3f}","0","0",f"{END/SPEED:.3f}"],check=True)
compose(D,f"{D}/build/base.mkv",f"{D}/build/endbg.mkv",ov,assf,mus,f"{D}/build/final.mp4",music_vol=0.24)
light(f"{D}/build/final.mp4",f"{D}/build/final_leve.mp4")
print("ok",T,T/SPEED)
