# VÍDEO 4 – "R$ 50 mil de sinal" – estilo OFERTA com capítulos
import sys, os, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from eng import *
D=sys.argv[1]; SRC=f"{D}/original.mov"; ENG=os.path.dirname(os.path.abspath(__file__))
END=52.90; ENDC=2.8; T=END+ENDC
GRADE="eq=contrast=1.08:saturation=1.08:gamma=0.99,colorbalance=bs=0.03:bm=0.01,unsharp=5:5:0.3"
words=load_words(f"{D}/tr.json")
B=f"{D}/build"; os.makedirs(B,exist_ok=True)
NAVY=(11,37,69); LBc=(92,184,255); WHITE=(255,255,255)
CH=[(0,13.6,"OFERTA"),(13.6,17.4,"LOCALIZAÇÃO"),(17.4,26.9,"SHOPPING"),(26.9,39.4,"LAZER"),(39.4,47.0,"PLANTA"),(47.0,END,"CONDIÇÕES")]
def chapters(cv,t):
    a=ss(0,0.3,t)*(1-ss(END-0.3,END,t)); d=ImageDraw.Draw(cv)
    n=len(CH); gap=10; x0=50; tw=W-100; w=(tw-gap*(n-1))/n; y=70
    for k,(c0,c1,lab) in enumerate(CH):
        x=x0+k*(w+gap); f=min(1,max(0,(t-c0)/(c1-c0)))
        d.rounded_rectangle((x,y,x+w,y+8),4,fill=(255,255,255,int(90*a)))
        if f>0: d.rounded_rectangle((x,y,x+max(8,w*f),y+8),4,fill=(255,255,255,int(255*a)))
        if c0<=t<c1:
            fo=font("bold",30); d.text((x0,y+30),f"{k+1}/{n}  ·  {lab}",font=fo,fill=(255,255,255,int(235*a)),stroke_width=3,stroke_fill=(0,0,0,int(110*a)))
els=[Func(chapters,0,END)]
def plate(cv,t,t0,t1,big,small,y,scale=1.0):
    u=(t-t0)/0.32; sc=(1.35-0.35*ease_out_back(u))*scale if u<1 else scale; a=min(1,max(0,u*3))*(1-ss(t1-0.2,t1,t))
    fb=font("black",int(150*sc)); fs=font("bold",int(46*sc)); d=ImageDraw.Draw(cv)
    bb=d.textbbox((0,0),big,font=fb); bw=bb[2]-bb[0]; bh=bb[3]-bb[1]
    sb=d.textbbox((0,0),small,font=fs); sw=sb[2]-sb[0]
    pw=max(bw,sw)+90*sc; ph=bh+sb[3]-sb[1]+110*sc; x=(W-pw)/2
    p=Image.new("RGBA",(W,H),(0,0,0,0)); dp=ImageDraw.Draw(p)
    dp.rounded_rectangle((x,y,x+pw,y+ph),int(30*sc),fill=NAVY+(int(235*a),),outline=LBc+(int(255*a),),width=4)
    dp.text((W/2,y+40*sc-bb[1]),big,font=fb,fill=WHITE+(int(255*a),),anchor="ma")
    dp.text((W/2,y+40*sc+bh+28*sc),small,font=fs,fill=LBc+(int(255*a),),anchor="ma")
    cv.alpha_composite(p)
def stamp(cv,t,t0,t1,txt,y,size=96,col=WHITE,bg=None):
    u=(t-t0)/0.3; sc=1.5-0.5*ease_out_back(u) if u<1 else 1; a=min(1,max(0,u*3))*(1-ss(t1-0.2,t1,t))
    f=font("black",int(size*sc)); d=ImageDraw.Draw(cv)
    if bg:
        bb=d.textbbox((W/2,y),txt,font=f,anchor="mm")
        p=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle((bb[0]-30,bb[1]-18,bb[2]+30,bb[3]+18),22,fill=bg+(int(240*a),)); cv.alpha_composite(p)
    ImageDraw.Draw(cv).text((W/2,y),txt,font=f,fill=col+(int(255*a),),anchor="mm",stroke_width=0 if bg else 5,stroke_fill=(0,0,0,int(140*a)))
# abertura: oferta
els.append(Func(lambda cv,t: stamp(cv,t,0.05,6.6,"3 QUARTOS",300,120),0.05,6.6))
els.append(Func(lambda cv,t: plate(cv,t,3.1,6.6,"R$ 50 MIL","DE SINAL",420),3.1,6.6))
els.append(Func(lambda cv,t: plate(cv,t,4.3,6.6,"R$ 2 MIL","DE PARCELA",760,0.82),4.3,6.6))
els.append(Func(lambda cv,t: stamp(cv,t,5.3,6.6,"É ISSO MESMO!",1100,64,NAVY,LBc),5.3,6.6))
# shopping
els.append(Card("mall.jpg",None,17.5,26.9,top=420,maxw=980,anim="zoom"))
def ring(cv,t):   # destaque pulsante no "olha esse shopping"
    if 20.15<=t<21.6:
        u=(t-20.15)%0.7/0.7; img,pad,cw,ch=card_image("mall.jpg",None,980,840)
        x0=(W-cw)/2; y0=420; e=int(10+u*26); a=int(220*(1-u))
        p=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle((x0-e,y0-e,x0+cw+e,y0+ch+e),28+e,outline=LBc+(a,),width=6); cv.alpha_composite(p)
els.append(Func(ring,20.15,21.6))
# lazer: checklist + fotos (somente itens do material oficial)
LZ=[(31.2,"QUADRA DE AREIA","12",[0.0326,0.0445,0.4674,0.9524]),(33.5,"PISCINA","11",None),(35.5,"CHURRASQUEIRA","09",None),
    (36.7,"ESPAÇO BELEZA","14",[0.515,0.0476,0.9674,0.4913]),(37.5,"ACADEMIA E MUITO MAIS","08",None)]
LZE=39.35
def checklist(cv,t):
    for k,(t0,lab,pg,rc) in enumerate(LZ):
        if t<t0: continue
        u=(t-t0)/0.25; a=min(1,u*2)*(1-ss(LZE-0.25,LZE,t)); y=1090+k*76; dx=(1-ss(t0,t0+0.25,t))*-80
        p=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(p)
        d.rounded_rectangle((60+dx,y,720+dx,y+64),18,fill=NAVY+(int(225*a),))
        d.ellipse((78+dx,y+12,118+dx,y+52),fill=LBc+(int(255*a),))
        d.text((98+dx,y+32),"✓",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",30),fill=NAVY+(int(255*a),),anchor="mm")
        d.text((138+dx,y+32),lab,font=font("bold",36),fill=WHITE+(int(255*a),),anchor="lm")
        cv.alpha_composite(p)
els.append(Func(lambda cv,t: stamp(cv,t,27.0,29.9,"E TEM MAIS…",560,110),27.0,29.9))
els.append(Func(lambda cv,t: stamp(cv,t,30.0,LZE,"LAZER RESORT",250,84,NAVY,LBc),30.0,LZE))
els.append(Func(checklist,31.2,LZE))
for k,(t0,lab,pg,rc) in enumerate(LZ):
    t1=LZ[k+1][0] if k+1<len(LZ) else LZE
    els.append(Card(pg,rc,t0,t1,top=360,maxw=900,maxh=680,anim="zoom" if k==0 else "left",fin=True,fout=(k==len(LZ)-1)))
# planta 3 quartos
PL=("plan3q.png",None)
els.append(Card(PL[0],PL[1],39.45,47.0,top=330,maxw=1000,maxh=720,anim="rise",border=(255,255,255,220)))
els.append(Func(lambda cv,t: plate(cv,t,43.1,47.0,"R$ 50 MIL","DE SINAL  +  R$ 2 MIL/MÊS",1110,0.78),43.1,47.0))
# CTA
els.append(Func(lambda cv,t: stamp(cv,t,47.1,END,"AGRADEÇA O SEU ALGORITMO",420,62,NAVY,LBc),47.1,END))
els.append(Func(lambda cv,t: stamp(cv,t,48.4,END,"ME MANDA MENSAGEM",600,74),48.4,END))
els.append(Func(lambda cv,t: stamp(cv,t,50.9,END,"E VEM VISITAR O DECORADO",760,58,WHITE,NAVY),50.9,END))
# cartela final
els.append(Card("mall.jpg",None,END,T,top=600,maxw=940,anim="rise",fout=False))
els.append(Func(lambda cv,t: plate(cv,t,END+0.3,T+1,"R$ 50 MIL","DE SINAL",1020,0.6),END,T))
ov=f"{B}/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- legendas ----------
st=["Style: Cap,Inter ExtraBold,82,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,280,1",
    "Style: Lab,Inter ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00450B0B,&H40452B0B,-1,0,0,0,100,100,3,0,3,16,0,8,60,60,0,1",
    "Style: Big,Inter Display Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,2,0,1,4,4,8,80,80,0,1",
    "Style: Disc,Inter Medium,26,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,60,60,100,1"]
ev=word_captions(words,"Cap","&HFFB85C&",END)
def add(a,b,style,text,fx="{\\fad(200,200)}",layer=2): ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{fx}{text}")
add(7.0,13.5,"Lab","📍 NA MELHOR LOCALIZAÇÃO DO ESTORIL".replace("📍 ",""),fx="{\\fad(200,200)\\pos(540,330)}")
add(13.8,17.4,"Lab","5 MIN DO BH SHOPPING",fx="{\\fad(200,200)\\pos(540,330)}")
add(17.6,26.9,"Lab","SHOPPING NA PORTA",fx="{\\fad(200,200)\\pos(540,320)}")
add(39.5,47.0,"Lab","3 QUARTOS · SUÍTE E VARANDA · 59,12 m²",fx="{\\fad(200,200)\\pos(540,240)}")
add(3.1,6.6,"Disc","Condições sujeitas a análise de crédito e alteração sem aviso",fx="")
add(43.1,47.0,"Disc","Condições sujeitas a análise de crédito e alteração sem aviso",fx="")
add(17.5,26.9,"Disc","Imagem meramente ilustrativa",fx="")
add(31.2,LZE,"Disc","Imagens meramente ilustrativas",fx="")
add(39.45,43.0,"Disc","Planta ilustrativa · 59,12 m² (área privativa)",fx="")
add(END,T,"Big","VIEW ESTORIL",fx="{\\fad(300,0)\\pos(540,370)}")
add(END,T,"Disc","Imagem ilustrativa · condições sujeitas a análise de crédito",fx="")
assf=f"{B}/v.ass"; open(assf,"w").write(ass_head(st)+"\n".join(ev)+"\n")
render_base(D,SRC,END,GRADE,f"{B}/base.mkv")
render_endbg(SRC,51.2,ENDC,GRADE,f"{B}/endbg.mkv",dark=-0.2,blur=12)
mus=f"{B}/music.wav"
if not os.path.exists(f"{ENG}/music_fast.py"):
    s=open(f"{ENG}/../v7/music3.py").read().replace("BPM=112","BPM=124").replace(
      "prog=[[57,60,64,67,71],[53,57,60,64,67],[48,52,55,59,62],[55,59,62,65,69]]","prog=[[52,55,59,62,66],[48,52,55,59,62],[55,59,62,66,69],[50,54,57,60,64]]")
    open(f"{ENG}/music_fast.py","w").write(s)
subprocess.run(["python3","-I",f"{ENG}/music_fast.py",mus,f"{T/SPEED:.3f}","0.01",f"{30.0/SPEED:.3f}",f"{END/SPEED:.3f}"],check=True)
compose(D,f"{B}/base.mkv",f"{B}/endbg.mkv",ov,assf,mus,f"{B}/final.mp4",music_vol=0.26)
light(f"{B}/final.mp4",f"{B}/final_leve.mp4")
print("ok",T,T/SPEED)
