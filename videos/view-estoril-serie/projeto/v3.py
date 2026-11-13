# VÍDEO 3 – "Ah Matheus, tá muito caro" – estilo CONVERSA DE CHAT
import sys, os, subprocess, wave
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from eng import *
D=sys.argv[1]; SRC=f"{D}/original.mov"; ENG=os.path.dirname(os.path.abspath(__file__))
END=52.25; ENDC=2.8; T=END+ENDC
GRADE="eq=contrast=1.04:saturation=1.05:gamma=1.0:brightness=0.01,colorbalance=bs=0.02:rh=0.01"
words=load_words(f"{D}/tr.json")
B=f"{D}/build"; os.makedirs(B,exist_ok=True)
CSS="""<style>*{margin:0;padding:0;box-sizing:border-box}body{background:transparent;font-family:'Inter',sans-serif}
#root{display:inline-block;padding:14px 18px}
.b{display:inline-block;max-width:760px;padding:22px 30px;border-radius:40px;font-size:44px;line-height:1.22;font-weight:600;box-shadow:0 8px 24px rgba(0,0,0,.28)}
.l{background:#E9E9EB;color:#111;border-bottom-left-radius:12px}
.r{background:#0A84FF;color:#fff;border-bottom-right-radius:12px}
.e{font-family:'Noto Color Emoji'}
.name{font-size:28px;color:#fff;font-weight:700;margin:0 0 8px 14px;text-shadow:0 2px 8px rgba(0,0,0,.6)}
</style>"""
def emo(s):
    import re
    return re.sub(r"([\U0001F300-\U0001FAFF☀-➿⭐⌛⏳]️?)",r'<span class="e">\1</span>',s)
_bub={}
def bubble(text,side,name=None):
    k=(text,side,name)
    if k in _bub: return _bub[k]
    out=f"{B}/b{len(_bub):02d}.png"
    nm=f'<div class="name">{name}</div>' if name else ""
    html=f'<html><head>{CSS}</head><body><div id="root">{nm}<div class="b {"l" if side=="l" else "r"}">{emo(text)}</div></div></body></html>'
    _bub[k]=html_png(html,out,w=1080,h=700); return _bub[k]
def typing_img(t):
    im=Image.new("RGBA",(200,110),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((18,14,182,96),40,fill=(233,233,235,255))
    for k in range(3):
        ph=(t*3-k*0.33)%1; up=max(0,math.sin(ph*math.pi))*10
        d.ellipse((54+k*36,46-up,76+k*36,68-up),fill=(140,140,145,255))
    return im
def photo_bubble(name,rect,maxw=640,maxh=600):
    img,pad,cw,ch=card_image(name,rect,maxw,maxh,radius=34,border=(255,255,255,255),bw=8)
    return img
# grupos de mensagens: (t_aparece, tipo, conteúdo, lado)
G=[ (0.0, 3.35,[(0.0,"typing",None,"l",0.45),(0.45,"msg","Matheus, apartamento no Buritis tá muito caro 😩","l","Cliente"),
                (2.45,"msg","Ah é? 🤨","r",None),(2.75,"msg","Então olha esse 👇","r",None)]),
    (3.35,14.15,[(5.9,"msg","📍 Estoril · Barão Homem de Melo","r",None),(7.7,"msg","🛣️ Do lado da Raja Gabaglia","r",None),
                 (9.1,"msg","🛍️ 5 min do BH Shopping","r",None),(12.4,"msg","🛏️ 2 quartos com varanda e suíte","r",None)]),
    (14.15,24.7,[(14.3,"msg","E sabe o que você não sabe? 🤫","r",None),(15.5,"typing",None,"l",0.55),(16.05,"msg","O quê?? 👀","l","Cliente"),
                 (18.9,"photo",("mall.jpg",None),"r",None),(20.5,"msg","Um shopping na porta do seu prédio 🛍️","r",None)]),
    (24.7,36.2,[(24.8,"msg","E tem mais… 😏","r",None),(29.8,"photo",("11",None),"r",None),
                (31.4,"msg","🏖️ Lazer resort: quadra de areia, piscina e muito mais","r",None)]),
    (36.2,45.7,[(36.3,"msg","Com um preço que você nem imagina 💰","r",None),(38.0,"typing",None,"l",0.5),(38.5,"msg","Quanto??? 😳","l","Cliente"),
                (39.9,"msg","Quer saber? 😉","r",None),(40.6,"msg","Me chama que te passo todas as condições 📲","r",None)]),
    (45.7,END,[(45.8,"msg","Eu falei que era caro né 😅","l","Cliente"),(49.1,"msg","Oportunidade assim não volta ⏳","r",None)]) ]
POPS=[]
class Chat:
    def __init__(s): s.t0=0; s.t1=END
    def draw(s,cv,t):
        for (g0,g1,items) in G:
            if not (g0<=t<g1): continue
            ga=1-ss(g1-0.22,g1,t)
            y=250
            for k,it in enumerate(items):
                ta,kind,content,side=it[0],it[1],it[2],it[3]
                if kind=="typing":
                    dur=it[4]
                    if ta<=t<ta+dur: im=typing_img(t); paste_alpha(cv,im,48,y,ga*min(1,(t-ta)/0.12))
                    if t>=ta: y+= 110 if t<ta+dur else 0
                    continue
                if t<ta: break
                if kind=="msg": im=bubble(content,side,it[4] if len(it)>4 else None)
                else: im=photo_bubble(*content)
                u=(t-ta)/0.28; sc=0.75+0.25*ease_out_back(u); a=min(1,u*3)*ga
                im2=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BICUBIC) if sc!=1 else im
                x= 30 if side=="l" else W-30-im2.width
                paste_alpha(cv,im2,x,y+(im.height-im2.height)*(0 if side=="l" else 0),a)
                y+=im.height+6
            break
for (g0,g1,items) in G:
    for it in items:
        if it[1] in ("msg","photo"): POPS.append(it[0])
# cabeçalho do chat
_hdr=None
def header(cv,t):
    global _hdr
    if _hdr is None:
        html=f'''<html><head>{CSS}<style>.h{{display:flex;align-items:center;gap:22px;background:rgba(20,20,24,.72);padding:18px 34px;border-radius:44px}}
        .av{{width:78px;height:78px;border-radius:50%;background:#0A84FF;display:flex;align-items:center;justify-content:center;font-size:44px}}
        .n{{color:#fff;font-size:38px;font-weight:800}}.s{{color:#7ee787;font-size:26px;font-weight:600}}</style></head>
        <body><div id="root"><div class="h"><div class="av"><span class="e">🏠</span></div><div><div class="n">Cliente</div><div class="s">● online</div></div></div></div></body></html>'''
        _hdr=html_png(html,f"{B}/hdr.png",w=1080,h=300)
    a=ss(0,0.3,t)*(1-ss(END-0.3,END,t)); paste_alpha(cv,_hdr,(W-_hdr.width)/2,96,a)
# barra de mensagem no CTA
def inputbar(cv,t):
    a=ss(50.6,50.9,t); full="Quero saber as condições!"; n=min(len(full),int(max(0,t-50.8)*22))
    p=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(p); y=1180
    d.rounded_rectangle((40,y,W-40,y+120),60,fill=(255,255,255,int(240*a)))
    d.text((90,y+60),full[:n]+("|" if int(t*3)%2==0 else ""),font=font("semi",44),fill=(30,30,30,int(255*a)),anchor="lm")
    pulse=1+0.08*math.sin(t*8) if n==len(full) else 1
    r=int(44*pulse); cx,cy=W-110,y+60
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(10,132,255,int(255*a)))
    d.polygon([(cx-16,cy-22),(cx+22,cy),(cx-16,cy+22),(cx-8,cy)],fill=(255,255,255,int(255*a)))
    cv.alpha_composite(p)
els=[Func(header,0,END),Chat(),Func(inputbar,50.6,END)]
POPS.append(50.6)
# cartela final
els.append(Card("mall.jpg",None,END,T,top=560,maxw=940,anim="rise",fout=False,border=(255,255,255,230),bw=6))
ov=f"{B}/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- legendas ----------
st=["Style: Cap,Inter ExtraBold,82,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,300,1",
    "Style: Big,Inter Display Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,2,0,1,4,4,8,80,80,0,1",
    "Style: Btn,Inter ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00FF840A,&H00FF840A,-1,0,0,0,100,100,1,0,3,22,0,8,80,80,0,1",
    "Style: Disc,Inter Medium,26,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,60,60,110,1"]
ev=word_captions(words,"Cap","&HFF840A&",END)
def add(a,b,style,text,fx="{\\fad(200,200)}",layer=2): ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{fx}{text}")
add(18.9,24.7,"Disc","Imagem meramente ilustrativa",fx="")
add(29.8,36.2,"Disc","Imagem meramente ilustrativa",fx="")
add(END,T,"Big","VIEW ESTORIL",fx="{\\fad(300,0)\\pos(540,330)}")
add(END+0.5,T,"Btn","ME CHAMA AQUI",fx="{\\fad(250,0)\\pos(540,%d)}"%(560+352+50))
add(END,T,"Disc","Imagem meramente ilustrativa",fx="")
assf=f"{B}/v.ass"; open(assf,"w").write(ass_head(st)+"\n".join(ev)+"\n")
render_base(D,SRC,END,GRADE,f"{B}/base.mkv")
render_endbg(SRC,50.2,ENDC,GRADE,f"{B}/endbg.mkv",dark=-0.2,blur=12)
# trilha leve + "pops" das mensagens
mus=f"{B}/music.wav"
if not os.path.exists(f"{ENG}/beat_light.py"):
    s=open(f"{ENG}/../v3/beat.py").read().replace("BPM=118","BPM=100").replace("prog=[[53,57,60,64],[55,59,62,65],[52,55,59,62],[57,60,64,67]]","prog=[[60,64,67,72],[55,59,62,67],[57,60,64,69],[53,57,60,65]]")
    open(f"{ENG}/beat_light.py","w").write(s)
subprocess.run(["python3","-I",f"{ENG}/beat_light.py",f"{B}/m0.wav",f"{T/SPEED:.3f}","0","0",f"{END/SPEED:.3f}"],check=True)
subprocess.run(["python3","-I",f"{ENG}/../v3/sfx.py",f"{B}/pops.wav",f"{T/SPEED:.3f}"]+[f"{p/SPEED:.3f}" for p in POPS],check=True)
run(["-i",f"{B}/m0.wav","-i",f"{B}/pops.wav","-filter_complex","[1:a]aformat=channel_layouts=stereo,volume=1.6[p];[0:a][p]amix=inputs=2:duration=first:normalize=0","-ar","48000",mus])
compose(D,f"{B}/base.mkv",f"{B}/endbg.mkv",ov,assf,mus,f"{B}/final.mp4",music_vol=0.26)
light(f"{B}/final.mp4",f"{B}/final_leve.mp4")
print("ok",T,T/SPEED)
