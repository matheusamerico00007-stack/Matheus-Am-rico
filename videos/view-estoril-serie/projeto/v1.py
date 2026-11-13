# VÍDEO 1 – "Quanto você pagaria?" – estilo EDITORIAL DE REVISTA
import sys, os, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from eng import *
D=sys.argv[1]; SRC=f"{D}/original.mov"; ENG=os.path.dirname(os.path.abspath(__file__))
END=40.60; ENDC=2.7; T=END+ENDC
GRADE="eq=contrast=0.98:brightness=0.02:saturation=0.93:gamma=1.03,colorbalance=rh=0.03:gh=0.01:bh=-0.02:bs=0.02"
words=load_words(f"{D}/tr.json")
LB="&HFFB85C&"
el=[]
# moldura editorial (vídeo inteiro)
def frame(cv,t):
    d=ImageDraw.Draw(cv); m=26
    d.rectangle((m,m,W-m,H-m),outline=(255,255,255,190),width=2)
_scr=Image.new("RGBA",(W,H),(0,0,0,0))
_g=np.zeros((H,),float); yy=np.arange(H)
_g=np.maximum(np.clip(1-yy/760,0,1)**1.6*0.62, np.clip((yy-1180)/740,0,1)**1.4*0.72)
_scr.putalpha(Image.fromarray((_g[:,None]*255*np.ones((1,W))).astype(np.uint8)))
def scrim(cv,t): cv.alpha_composite(_scr)
el.insert(0,Func(scrim,0,T))
def sidepanel(cv,t):
    a=ss(3.55,3.85,t)*(1-ss(7.35,7.55,t))
    p=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle((78,940,760,1210),24,fill=(8,20,40,int(150*a)))
    cv.alpha_composite(p)
el.append(Func(sidepanel,3.55,7.6))
el.append(Func(frame,0,T))
# shopping na porta
MALL="mall.jpg"
el.append(Card(MALL,None,8.45,11.95,top=380,maxw=960,anim="rise"))
# lazer (só o que está no material oficial)
el.append(Card("12",[0.0326,0.0445,0.4674,0.9524],15.0,17.95,top=330,maxw=900,maxh=820,anim="zoom",fout=False))
el.append(Card("11",None,17.95,19.95,top=430,maxw=980,maxh=760,anim="zoom",fin=False))
# contador do aluguel
def counter(cv,t):
    v=4000*ss(32.35,33.9,t)
    if 36.0<=t<36.5: sc=1+0.06*math.sin((t-36.0)/0.5*math.pi)
    else: sc=1
    txt=f"R$ {int(round(v/10)*10):,}".replace(",",".")
    f=font("serif",int(190*sc)); d=ImageDraw.Draw(cv)
    a=int(255*min(1,ss(31.9,32.3,t))*(1-ss(36.8,37.0,t)))
    bb=d.textbbox((0,0),txt,font=f); x=(W-(bb[2]-bb[0]))/2; y=470
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((x+4,y+8),txt,font=f,fill=(0,0,0,int(a*0.55))); sh=sh.filter(ImageFilter.GaussianBlur(10)); cv.alpha_composite(sh)
    d.text((x,y),txt,font=f,fill=(255,255,255,a))
el.append(Func(counter,31.9,37.0))
# cartela final: mall inteiro
el.append(Card(MALL,None,END,T,top=560,maxw=900,anim="rise",fout=False))
os.makedirs(f"{D}/build",exist_ok=True)
ov=f"{D}/build/overlay.mov"
if not os.path.exists(ov): render_overlay(el,T,ov)
# ---------- textos (ASS) ----------
st=[
"Style: Cap,Inter Display SemiBold,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,1.5,3,2,90,90,330,1",
"Style: Big,Caladea,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,-1,0,0,100,100,0,0,1,1.5,5,8,80,80,300,1",
"Style: Kick,Inter Display SemiBold,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,12,0,1,1.2,3,8,80,80,0,1",
"Style: Side,Inter Display SemiBold,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,8,0,1,0,4,7,110,80,0,1",
"Style: Num,Caladea,44,&H00FFB85C,&H00FFFFFF,&H00000000,&H90000000,0,-1,0,0,100,100,0,0,1,0,4,7,110,80,0,1",
"Style: Lbl,Caladea,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,-1,0,0,100,100,0,0,1,1.5,4,8,80,80,0,1",
"Style: Pill,Inter Display Bold,40,&H00FFFFFF,&H00FFFFFF,&H0045250B,&H0045250B,-1,0,0,0,100,100,6,0,3,18,0,8,80,80,0,1",
"Style: Mast,Inter Display SemiBold,26,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,14,0,1,0,3,8,80,80,62,1",
"Style: Disc,Inter Medium,26,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,60,60,58,1"]
ev=word_captions(words,"Cap",LB,END,maxw=5,maxc=26,upper=False,phrase=True)
F="{\\fad(220,220)}"
def add(a,b,style,text,fx=F,layer=2): ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{fx}{text}")
add(0,T,"Mast","VIEW ESTORIL  ·  APARTAMENTO DECORADO",fx="{\\fad(400,0)}")
add(0.15,3.25,"Big","Quanto você\\Npagaria{\\c"+LB+"}?",fx="{\\fad(250,200)\\blur0.4}")
add(0.15,3.25,"Kick","PARA MORAR AQUI",fx="{\\fad(300,200)\\pos(540,250)}")
for k,(t0,txt) in enumerate([(3.65,"ESTORIL"),(4.55,"AO LADO DO BURITIS"),(5.85,"5 MIN DO BH SHOPPING")]):
    y=980+k*86
    add(t0,7.55,"Num",f"0{k+1}",fx="{\\fad(220,200)\\pos(110,%d)}"%(y-4))
    add(t0+0.05,7.55,"Side",txt,fx="{\\fad(220,200)\\move(190,%d,170,%d,0,300)}"%(y,y))
add(8.55,11.95,"Lbl","Um shopping na sua porta.",fx="{\\fad(250,200)\\pos(540,%d)}"%(380+360+30))
add(12.3,15.0,"Big","Lazer resort.",fx="{\\fad(250,200)}")
add(15.1,17.95,"Lbl","Quadra de areia",fx="{\\fad(200,150)\\pos(540,240)}")
add(18.0,19.95,"Lbl","Piscina adulto e infantil",fx="{\\fad(200,150)\\pos(540,300)}")
add(15.0,19.95,"Disc","Imagens meramente ilustrativas",fx="")
add(8.45,11.95,"Disc","Imagem meramente ilustrativa",fx="")
add(22.3,26.1,"Big","Investir sem tirar\\Ndinheiro do bolso.",fx="{\\fad(250,200)}")
add(26.8,30.6,"Pill","PLANO ASSOCIATIVO APROVADO",fx="{\\fad(200,200)\\pos(540,520)}")
add(32.0,36.9,"Kick","DE ALUGUEL POR MÊS*",fx="{\\fad(250,200)\\pos(540,700)}")
add(32.0,36.9,"Disc","*Valor estimado, sujeito a mercado",fx="")
add(37.0,END,"Big","Me chama aqui.",fx="{\\fad(250,0)}")
add(37.3,END,"Kick","E GARANTA SUA UNIDADE",fx="{\\fad(300,0)\\pos(540,460)}")
add(END,T,"Big","View Estoril",fx="{\\fad(300,0)}")
add(END+0.2,T,"Kick","OPEN MALL  ·  ESTORIL  ·  BH",fx="{\\fad(300,0)\\pos(540,460)}")
add(END+0.5,T,"Pill","ME CHAMA AQUI",fx="{\\fad(250,0)\\pos(540,%d)}"%(560+338+40))
add(END,T,"Disc","Imagem meramente ilustrativa",fx="")
assf=f"{D}/build/v.ass"; open(assf,"w").write(ass_head(st)+"\n".join(ev)+"\n")
# ---------- base, música, composição ----------
render_base(D,SRC,END,GRADE,f"{D}/build/base.mkv")
render_endbg(SRC,39.2,ENDC,GRADE,f"{D}/build/endbg.mkv",dark=-0.12,blur=12)
mus=f"{D}/build/music.wav"
subprocess.run(["python3","-I",f"{ENG}/../v7/music3.py",mus,f"{T/SPEED:.3f}",f"{12.0/SPEED:.3f}",f"{31.9/SPEED:.3f}",f"{END/SPEED:.3f}"],check=True)
compose(D,f"{D}/build/base.mkv",f"{D}/build/endbg.mkv",ov,assf,mus,f"{D}/build/final.mp4",music_vol=0.26)
light(f"{D}/build/final.mp4",f"{D}/build/final_leve.mp4")
print("ok",T,T/SPEED)
