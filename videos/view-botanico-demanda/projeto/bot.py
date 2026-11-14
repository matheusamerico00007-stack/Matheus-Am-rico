# "O shopping de baixo não dá demanda?" – estudo de caso Botânico -> View Estoril
import sys, os, subprocess, wave, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from eng import *
S=sys.argv[1]; ENG=os.path.dirname(os.path.abspath(__file__))
FACE=f"{S}/b1/original.mov"; BOT=f"{S}/b2/original.mov"; B=f"{S}/b1/build"; os.makedirs(B,exist_ok=True)
CUTS=[(30.95,33.00),(48.33,51.40)]   # repetições, em silêncios verificados
END_SRC=76.75; ENDC=2.7
keep=[];pos=0.0
for a,b in CUTS: keep.append((pos,a)); pos=b
keep.append((pos,END_SRC))
KEEP=[(a,a+round((b-a)*FPS)/FPS) for a,b in keep]
def o(t):
    p=0
    for a,b in KEEP:
        if t<a: return p
        if t<=b: return p+t-a
        p+=b-a
    return p+(t-KEEP[-1][1])
VT=sum(b-a for a,b in KEEP); T=VT+ENDC
# ---------- vídeo: rosto ou Botânico, por trecho (tempos da fala) ----------
BROLL=[(3.58,6.20,9.0),(6.20,8.65,37.0),(8.65,11.30,0.4),(11.75,14.30,45.0),(14.30,16.95,24.5),
       (23.64,24.50,9.0),(24.50,25.30,11.0),(25.30,26.20,13.4),(26.20,27.10,31.4),(27.10,28.30,45.4),(28.30,29.30,54.0),(29.30,30.95,50.4),
       (37.40,41.80,29.6),(41.80,47.95,19.9),(51.40,58.75,48.9)]
def piece_list():
    out=[]  # (src, ini_src_video, nframes)
    for (ka,kb) in KEEP:
        t=ka
        evs=sorted([b for b in BROLL if b[0]<kb and b[1]>ka])
        for (b0,b1,bs) in evs:
            b0=max(b0,ka); b1=min(b1,kb)
            if b0>t: out.append(("F",t,round((o(b0)-o(t))*FPS)))
            out.append(("B",bs,round((o(b1)-o(b0))*FPS))); t=b1
        if kb>t: out.append(("F",t,round((o(kb)-o(t))*FPS)))
    return out
PIECES=piece_list()
# corrige arredondamento: soma de quadros = VT*FPS
tot=sum(p[2] for p in PIECES); NF=round(VT*FPS)
if tot!=NF: s,a,n=PIECES[-1]; PIECES[-1]=(s,a,n+NF-tot)
GF="eq=contrast=1.05:saturation=1.04:gamma=0.99,colorbalance=bs=0.02"
GB="eq=contrast=1.06:saturation=1.08:gamma=0.98,colorbalance=rh=0.03:gh=0.01:bh=-0.02,unsharp=5:5:0.3"
def render_piece(i,src,a,nf):
    out=f"{B}/pc{i:02d}.mkv"
    if os.path.exists(out): return out
    L=nf/FPS; f=FACE if src=="F" else BOT; g=GF if src=="F" else GB
    zz=f"(1.0+0.04*t/{L:.3f})" if src=="B" else "1.0"
    vf=(f"trim=start={a}:end={a+L+0.3},setpts=PTS-{a}/TB,fps={FPS}:start_time=0,trim=end_frame={nf},setpts=PTS-STARTPTS,"
        f"scale=w='trunc(1080*{zz}/2)*2':h='trunc(1920*{zz}/2)*2':eval=frame:flags=lanczos,crop=1080:1920,setsar=1,{g}")
    run(["-copyts","-ss",str(max(0,a-2)),"-i",f,"-an","-vf",vf,"-c:v","libx264","-crf","14","-preset","fast",out]); return out
files=[render_piece(i,*p) for i,p in enumerate(PIECES)]
render_endbg(FACE,75.9,ENDC,GF,f"{B}/endbg.mkv",dark=-0.22,blur=12)
# ---------- áudio: voz (b1) + ambiente do Botânico nos trechos de b-roll ----------
SR=48000
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-map","0:a:0","-ac","1","-ar",str(SR),"-f","s16le","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
xv=load(FACE); xa=load(BOT); N=int(round(T*SR))+SR
voice=np.zeros(N,np.float32); amb=np.zeros(N,np.float32)
def place(dst,src,ot,st,d,fi,fo,g=1.0):
    oi=int(round(ot*SR)); si=int(round(st*SR)); n=int(round(d*SR)); seg=src[si:si+n].copy()
    if len(seg)<n: seg=np.pad(seg,(0,n-len(seg)))
    if fi: seg[:int(fi*SR)]*=np.linspace(0,1,int(fi*SR))
    if fo: seg[-int(fo*SR):]*=np.linspace(1,0,int(fo*SR))
    dst[oi:oi+n]+=seg*g
for (ka,kb) in KEEP: place(voice,xv,o(ka),ka,kb-ka,0.03,0.05)
for (b0,b1,bs) in BROLL:
    if b0>=31: continue    # ambiente só na parte do Botânico
    place(amb,xa,o(b0),bs,o(b1)-o(b0),0.15,0.15,0.30)
def wsave(p,x):
    w=wave.open(p,'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes()); w.close()
wsave(f"{B}/voice.wav",voice[:int(T*SR)]); wsave(f"{B}/amb.wav",amb[:int(T*SR)])
# ---------- sobreposições ----------
NAVY=(11,37,69); LBc=(92,184,255); W_=(255,255,255)
els=[]
def box_text(cv,txt,y,size,a,fg=W_,bg=NAVY,font_name="black",pad=(30,16),r=20,anchor_x=W/2):
    d=ImageDraw.Draw(cv); f=font(font_name,size); bb=d.textbbox((anchor_x,y),txt,font=f,anchor="mm")
    p=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle((bb[0]-pad[0],bb[1]-pad[1],bb[2]+pad[0],bb[3]+pad[1]),r,fill=bg+(int(240*a),))
    ImageDraw.Draw(p).text((anchor_x,y),txt,font=f,fill=fg+(int(255*a),),anchor="mm"); cv.alpha_composite(p)
def pop(t,t0,t1,fade=0.2): u=(t-t0)/0.3; return (1.4-0.4*ease_out_back(u)) if u<1 else 1.0, min(1,max(0,u*3))*(1-ss(t1-fade,t1,t))
# 1) objeção
def hook(cv,t):
    a=ss(0,0.25,t)*(1-ss(o(3.3)-0.2,o(3.3),t)); d=ImageDraw.Draw(cv)
    f=font("serif_i",64); txt="“O shopping de bairro\nnão dá demanda…”"
    p=Image.new("RGBA",(W,H),(0,0,0,0)); dp=ImageDraw.Draw(p)
    dp.rounded_rectangle((90,250,990,500),30,fill=(255,255,255,int(235*a)))
    dp.multiline_text((540,375),txt,font=f,fill=(20,20,20,int(255*a)),anchor="mm",align="center",spacing=10); cv.alpha_composite(p)
    if t>=o(2.8):
        sc,aa=pop(t,o(2.8),o(3.3)); box_text(cv,"SERÁ MESMO?",590,int(78*sc),aa*a,fg=NAVY,bg=LBc)
els.append(Func(hook,0,o(3.3)))
# 2) reportagem no Botânico
def lower3(cv,t):
    t0,t1=o(3.6),o(11.3); a=ss(t0,t0+0.3,t)*(1-ss(t1-0.25,t1,t)); dx=(1-ss(t0,t0+0.35,t))*-200
    p=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle((50+dx,1120,140+dx,1166),10,fill=(10,132,255,int(255*a))); d.text((95+dx,1143),"HOJE",font=font("black",28),fill=W_+(int(255*a),),anchor="mm")
    d.rounded_rectangle((50+dx,1176,760+dx,1300),14,fill=NAVY+(int(235*a),))
    d.text((80+dx,1192),"BOTÂNICO SHOPPING",font=font("black",44),fill=W_+(int(255*a),),anchor="la")
    d.text((82+dx,1252),"BELVEDERE · BELO HORIZONTE",font=font("semi",28),fill=LBc+(int(255*a),),anchor="la"); cv.alpha_composite(p)
els.append(Func(lower3,o(3.6),o(11.3)))
els.append(Func(lambda cv,t: (lambda sc,a: box_text(cv,"MUSICAL DE NATAL",420,int(64*sc),a))(*pop(t,o(7.3),o(8.65))),o(7.3),o(8.65)))
els.append(Func(lambda cv,t: (lambda sc,a: box_text(cv,"LOTADO",620,int(150*sc),a,fg=W_,bg=(10,132,255)))(*pop(t,o(10.5),o(11.3))),o(10.5),o(11.3)))
def publico(cv,t):
    items=[(12.2,"CRIANÇAS"),(12.95,"ADULTOS"),(13.45,"CASAIS"),(13.95,"FAMÍLIAS"),(14.8,"GENTE PRA TODO LADO")]
    for k,(t0,s) in enumerate(items):
        if t<o(t0): continue
        sc,a=pop(t,o(t0),o(16.95)); box_text(cv,s,330+k*105,int(54*sc),a,fg=NAVY if k==4 else W_,bg=LBc if k==4 else NAVY)
els.append(Func(publico,o(12.2),o(16.95)))
# 3) dados do Botânico (fonte citada)
def dados(cv,t):
    t0,t1=o(17.9),o(23.4); a=ss(t0,t0+0.3,t)*(1-ss(t1-0.2,t1,t)); dy=(1-ss(t0,t0+0.35,t))*40-60
    p=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle((120,250+dy,960,640+dy),28,fill=NAVY+(int(235*a),),outline=LBc+(int(255*a),),width=3)
    d.text((540,300+dy),"BOTÂNICO SHOPPING",font=font("semi",34),fill=LBc+(int(255*a),),anchor="mm")
    pc=int(100*ss(t0+0.2,t0+1.1,t)); d.text((540,420+dy),f"{pc}%",font=font("black",110),fill=W_+(int(255*a),),anchor="mm")
    d.text((540,510+dy),"DAS LOJAS OCUPADAS EM 7 MESES",font=font("bold",34),fill=W_+(int(230*a),),anchor="mm")
    d.text((540,590+dy),"Fonte: Diário do Comércio",font=font("med",24),fill=(200,210,225,int(230*a)),anchor="mm"); cv.alpha_composite(p)
els.append(Func(dados,o(17.9),o(23.4)))
# 4) "muda tudo": lista com ícones (emoji via HTML)
CSS="<style>*{margin:0;padding:0}body{background:transparent}#root{display:inline-block;padding:10px}.p{display:inline-flex;align-items:center;gap:18px;background:rgba(11,37,69,.92);border:3px solid #5CB8FF;border-radius:26px;padding:14px 30px;font:900 48px 'Inter';color:#fff}.e{font-family:'Noto Color Emoji';font-size:52px}</style>"
MUDA=[(23.95,"☕","CAFÉ DA MANHÃ"),(24.85,"🍽️","ALMOÇO"),(25.55,"🌙","JANTAR"),(26.25,"❤️","DATE A DOIS"),(27.55,"👨‍👩‍👧","PASSEIO COM AS CRIANÇAS"),(29.75,"🐶","ATÉ O PASSEIO COM O CACHORRO")]
mimgs=[html_png(f'<html><head>{CSS}</head><body><div id="root"><div class="p"><span class="e">{e}</span>{s}</div></div></body></html>',f"{B}/m{k}.png",w=1080,h=200) for k,(t0,e,s) in enumerate(MUDA)]
for k,(t0,e,s) in enumerate(MUDA):
    els.append(Sprite(mimgs[k],o(t0),o(30.95),x=540,y=300+k*118,anchor="tc",pop=True,fout=True))
els.append(Func(lambda cv,t: (lambda sc,a: box_text(cv,"MUDA TUDO",210,int(66*sc),a,fg=NAVY,bg=LBc))(*pop(t,o(22.85),o(30.95))),o(22.85),o(30.95)))
# 5) modo investidor (tela azul + quadro virtual)
_grid=Image.new("RGBA",(W,H),(0,0,0,0)); _gd=ImageDraw.Draw(_grid)
for x in range(0,W,60): _gd.line((x,0,x,H),fill=(120,190,255,26),width=1)
for y in range(0,H,60): _gd.line((0,y,W,y),fill=(120,190,255,26),width=1)
def modo(cv,t):
    t0,t1=o(33.0),o(58.75); a=ss(t0,t0+0.4,t)*(1-ss(t1-0.4,t1,t))
    tint=Image.new("RGBA",(W,H),(6,22,48,int(95*a))); cv.alpha_composite(tint)
    if a>0: g=_grid.copy(); g.putalpha(g.getchannel("A").point(lambda v:int(v*a))); cv.alpha_composite(g)
    if t<o(36.0):
        u=ss(t0,t0+0.35,t); box_text(cv,"MODO INVESTIDOR",330,int(80*(1.3-0.3*u)),u*(1-ss(o(35.8),o(36.0),t)),fg=NAVY,bg=LBc)
els.append(Func(modo,o(33.0),o(58.75)))
def mapa(cv,t):   # MOVIMENTO -> ramificações
    t0,t1=o(36.6),o(47.95); a=ss(t0,t0+0.3,t)*(1-ss(t1-0.25,t1,t)); d=ImageDraw.Draw(cv)
    cx,cy=540,520; sc,_=pop(t,t0,t1)
    box_text(cv,"MOVIMENTO",cy,int(70*sc),a,fg=NAVY,bg=LBc)
    nodes=[(38.0,"COMÉRCIO",(250,760)),(39.0,"SERVIÇOS",(830,760)),(40.1,"EVENTOS",(250,940)),(40.9,"GENTE QUERENDO MORAR",(700,940))]
    for (tn,s,(x,y)) in nodes:
        if t<o(tn): continue
        u=ss(o(tn),o(tn)+0.3,t)*(1-ss(t1-0.25,t1,t))
        ex=cx+(x-cx)*u; ey=cy+40+(y-cy-40)*u
        d.line((cx,cy+45,ex,ey-35),fill=LBc+(int(220*u),),width=5)
        if u>0.6: box_text(cv,s,y,46,u,fg=W_,bg=NAVY,font_name="bold",anchor_x=x)
    if t>=o(44.9):
        sc2,a2=pop(t,o(44.9),t1); box_text(cv,"+ PROCURA PRA COMPRA E VENDA",1110,int(52*sc2),a2,fg=NAVY,bg=LBc)
els.append(Func(mapa,o(36.6),o(47.95)))
def regra(cv,t):  # A REGRA É CLARA
    t0,t1=o(51.6),o(58.75); a=ss(t0,t0+0.3,t)*(1-ss(t1-0.25,t1,t))
    box_text(cv,"A REGRA É CLARA",280,54,a,fg=LBc,bg=NAVY,font_name="bold")
    steps=[(53.1,"MOVIMENTO",430),(53.84,"DEMANDA",640),(55.22,"LIQUIDEZ",850)]
    d=ImageDraw.Draw(cv)
    for k,(ts_,s,y) in enumerate(steps):
        if t<o(ts_): continue
        sc,aa=pop(t,o(ts_),t1); aa*=a
        box_text(cv,s,y,int(92*sc),aa,fg=NAVY if k==2 else W_,bg=LBc if k==2 else NAVY)
        if k<2 and t>=o(steps[k+1][0])-0.15:
            u=ss(o(steps[k+1][0])-0.15,o(steps[k+1][0])+0.1,t)*a
            d.polygon([(520,y+70),(560,y+70),(560,y+100),(585,y+100),(540,y+135),(495,y+100),(520,y+100)],fill=LBc+(int(255*u),))
els.append(Func(regra,o(51.6),o(58.75)))
# 6) o shopping na porta: animação planta -> render
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
A0,A1=o(59.3),o(65.4)
anim=f"{B}/anim.mov"
if not os.path.exists(anim): subprocess.run(["python3","-I",f"{ENG}/../v7/anim.py",f"{BOOK}/mall.jpg",anim,f"{A1-A0:.3f}"],check=True)
els.append(AnimClip(anim,A0,A1,y=210))
els.append(Func(lambda cv,t: box_text(cv,"NA PORTA DA SUA CASA",700,52,ss(A0,A0+0.3,t)*(1-ss(A1-0.2,A1,t)),fg=NAVY,bg=LBc),A0,A1))
els.append(Card("04",[0,0,1,.765],o(65.4),o(68.3),top=320,maxw=1000,anim="zoom"))
els.append(Func(lambda cv,t: (lambda sc,a: box_text(cv,"VIEW ESTORIL",250,int(70*sc),a))(*pop(t,o(65.45),o(68.3))),o(65.45),o(68.3)))
# 7) CTA com imagens do View
els.append(Card("11",None,o(69.9),o(71.7),top=230,maxw=900,maxh=560,anim="zoom",fout=False))
els.append(Card("10",None,o(71.7),o(73.6),top=230,maxw=900,maxh=560,anim="left",fin=True,fout=True))
els.append(Func(lambda cv,t: (lambda sc,a: box_text(cv,"ANTES DE TODO MUNDO",1250,int(60*sc),a,fg=NAVY,bg=LBc))(*pop(t,o(71.0),o(74.9))),o(71.0),o(74.9)))
els.append(Func(lambda cv,t: (lambda sc,a: box_text(cv,"AS MELHORES UNIDADES",1350,int(48*sc),a))(*pop(t,o(73.6),o(74.9))),o(73.6),o(74.9)))
els.append(Func(lambda cv,t: (lambda sc,a: box_text(cv,"ME CHAMA AQUI",420,int(96*sc),a,fg=NAVY,bg=LBc))(*pop(t,o(75.0),VT)),o(75.0),VT))
els.append(Card("mall.jpg",None,VT,T,top=600,maxw=940,anim="rise",fout=False))
els.append(Func(lambda cv,t: box_text(cv,"ME CHAMA AQUI",1080,60,ss(VT+0.4,VT+0.7,t),fg=NAVY,bg=LBc),VT,T))
ov=f"{B}/overlay.mov"
if not os.path.exists(ov): render_overlay(els,T,ov)
# ---------- legendas ----------
words=load_words(f"{S}/b1/tr.json")
for w in words:
    if w[2].startswith("baixo") and w[0]<3: w[2]=w[2].replace("baixo","bairro")
def remap(ws):
    out=[]
    for s,e,x in ws:
        if any(a-0.02<=s<b for a,b in CUTS): continue
        out.append([o(s),o(e),x])
    return out
st=["Style: Cap,Inter ExtraBold,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,280,1",
    "Style: Big,Inter Display Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,2,0,1,4,4,8,80,80,0,1",
    "Style: Disc,Inter Medium,26,&H50FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,60,60,100,1"]
ev=word_captions(remap(words),"Cap","&HFFB85C&",VT)
def add(a,b,style,text,fx="{\\fad(200,200)}",layer=2): ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{fx}{text}")
add(A0,o(68.3),"Disc","Imagens meramente ilustrativas",fx="")
add(o(69.9),o(73.6),"Disc","Imagens meramente ilustrativas",fx="")
add(VT,T,"Big","VIEW ESTORIL",fx="{\\fad(300,0)\\pos(540,380)}")
add(VT,T,"Disc","Imagem meramente ilustrativa",fx="")
assf=f"{B}/v.ass"; open(assf,"w").write(ass_head(st)+"\n".join(ev)+"\n")
# ---------- trilha e composição ----------
mus=f"{B}/music.wav"
subprocess.run(["python3","-I",f"{ENG}/../v7/music3.py",mus,f"{T/SPEED:.3f}",f"{o(3.58)/SPEED:.3f}",f"{o(33.0)/SPEED:.3f}",f"{VT/SPEED:.3f}"],check=True)
ins=[]
for f in files+[f"{B}/endbg.mkv"]: ins+=["-i",f]
n=len(files)+1
fg=["".join(f"[{i}:v]" for i in range(n))+f"concat=n={n}:v=1:a=0[cv]",
    f"[{n}:v]format=yuva420p[ov]",f"[cv][ov]overlay=0:0:eof_action=pass[c2]",
    f"[c2]ass={assf},setpts=PTS/{SPEED},fps={FPS},format=yuv420p[vo]",
    f"[{n+1}:a]atempo={SPEED},highpass=f=100,afftdn=nr=5:nf=-45:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,equalizer=f=250:t=q:w=1.0:g=-3.5,equalizer=f=500:t=q:w=1.2:g=-2.5,equalizer=f=2500:t=q:w=1.2:g=4.5,equalizer=f=4500:t=q:w=1.2:g=5,treble=g=4:f=9000,deesser=i=0.2,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=180,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo,asplit[voz][key]",
    f"[{n+2}:a]atempo={SPEED},aformat=channel_layouts=stereo,volume=1.0[amb]",
    f"[{n+3}:a]volume=0.24,aformat=channel_layouts=stereo[mus]",
    "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[md]",
    "[voz][md][amb]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(ins+["-i",ov,"-i",f"{B}/voice.wav","-i",f"{B}/amb.wav","-i",mus,"-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
    "-c:v","libx264","-preset","medium","-crf","20","-maxrate","9M","-bufsize","18M","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{B}/final.mp4"])
light(f"{B}/final.mp4",f"{B}/final_leve.mp4")
json.dump({"KEEP":KEEP,"VT":VT,"T":T},open(f"{B}/timeline.json","w"))
print("ok",round(VT,2),round(T,2),round(T/SPEED,2),len(PIECES),"peças")
