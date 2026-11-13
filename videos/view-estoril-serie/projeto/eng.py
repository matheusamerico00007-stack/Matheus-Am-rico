# Motor de edição comum para a série View Estoril (4 vídeos, estilos diferentes)
import json, subprocess, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FPS=30; W=1080; H=1920; SPEED=1.1
BOOK="/tmp/claude-0/-home-user-Matheus-Am-rico/84db027f-5e51-5629-a38e-34cde6dcf53b/scratchpad/v7/hr"
FONTS={
 "black":"/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
 "bold":"/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
 "semi":"/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf",
 "med":"/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf",
 "serif_i":"/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf",
 "serif":"/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf",
 "mono_b":"/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf",
 "mono":"/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"}
_fc={}
def font(name,size):
    k=(name,size)
    if k not in _fc: _fc[k]=ImageFont.truetype(FONTS[name],size)
    return _fc[k]
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
def ss(e0,e1,x):
    t=min(1,max(0,(x-e0)/(e1-e0))) if e1!=e0 else (1 if x>=e1 else 0); return t*t*(3-2*t)
def ease_out_back(t,s=1.4):
    t=min(1,max(0,t)); return 1+(s+1)*(t-1)**3+s*(t-1)**2
# ---------- palavras ----------
FIX={"Buretis,":"Buritis,","Buritiz,":"Buritis,","Buriti":"Buritis","Rádio":"Raja","Gabalha,":"Gabaglia,","polidesportiva,":"poliesportiva,"}
def load_words(path):
    ws=[[s,e,t.strip()] for seg in json.load(open(path)) for s,e,t in seg["words"]]
    m=[]
    for w in ws:
        w[2]=FIX.get(w[2],w[2])
        if m and (w[2].startswith("$") or w[2].startswith("-")): m[-1]=[m[-1][0],w[1],m[-1][2]+w[2]]
        else: m.append(w)
    return m
# ---------- imagens do book (sempre INTEIRAS) ----------
_img={}
def book_img(name,rect=None):
    key=(name,tuple(rect) if rect else None)
    if key not in _img:
        p=name if name.startswith("/") else (f"{BOOK}/{name}" if "." in name else f"{BOOK}/p-{name}.png")
        im=Image.open(p).convert("RGB")
        if rect:
            SW,SH=im.size; im=im.crop((int(rect[0]*SW),int(rect[1]*SH),int(rect[2]*SW),int(rect[3]*SH)))
        _img[key]=im
    return _img[key]
_cards={}
def card_image(name,rect,maxw,maxh,radius=28,border=(150,214,255,130),bw=3,shadow=True):
    key=(name,tuple(rect) if rect else None,maxw,maxh,radius,border,bw,shadow)
    if key in _cards: return _cards[key]
    im=book_img(name,rect); s=min(maxw/im.width,maxh/im.height)
    cw,ch=int(im.width*s),int(im.height*s)
    pad=40 if shadow else 0
    out=Image.new("RGBA",(cw+2*pad,ch+2*pad),(0,0,0,0))
    if shadow:
        sh=Image.new("L",out.size,0); ImageDraw.Draw(sh).rounded_rectangle((pad,pad+14,pad+cw,pad+ch+14),radius,fill=165)
        sh=sh.filter(ImageFilter.GaussianBlur(20)); out.putalpha(sh)
        out=Image.composite(Image.new("RGBA",out.size,(0,0,0,255)),out,sh)
        out.putalpha(sh)
    c=im.resize((cw,ch),Image.LANCZOS).convert("RGBA")
    if bw: ImageDraw.Draw(c).rounded_rectangle((0,0,cw-1,ch-1),radius,outline=border,width=bw)
    mk=Image.new("L",(cw,ch),0); ImageDraw.Draw(mk).rounded_rectangle((0,0,cw-1,ch-1),radius,fill=255)
    c.putalpha(mk); out.alpha_composite(c,(pad,pad))
    _cards[key]=(out,pad,cw,ch); return _cards[key]
def paste_alpha(canvas,img,x,y,a=1.0):
    if a<=0: return
    if a<1:
        img=img.copy(); al=img.getchannel("A").point(lambda v:int(v*a)); img.putalpha(al)
    canvas.alpha_composite(img,(int(x),int(y)))
# ---------- elementos de sobreposição ----------
class Card:
    """Imagem inteira num cartão; entrada/saída suaves (slide/fade/escala) sem cortar a imagem"""
    def __init__(s,name,rect,t0,t1,cx=540,top=360,maxw=1000,maxh=840,anim="rise",fin=True,fout=True,radius=28,border=(150,214,255,130),bw=3):
        s.__dict__.update(locals()); del s.__dict__["s"]
    def draw(s,cv,t):
        if not (s.t0<=t<s.t1): return
        img,pad,cw,ch=card_image(s.name,s.rect,s.maxw,s.maxh,s.radius,s.border,s.bw)
        a=1.0; dx=dy=0; sc=1.0
        if s.fin:
            u=ss(s.t0,s.t0+0.28,t); a=min(a,u)
            if s.anim=="rise": dy=(1-u)*50
            elif s.anim=="left": dx=-(1-u)*120
            elif s.anim=="right": dx=(1-u)*120
            elif s.anim=="zoom": sc=0.9+0.1*ease_out_back((t-s.t0)/0.35)
        if s.fout:
            a=min(a,1-ss(s.t1-0.2,s.t1,t))
        yc=s.top+ch/2   # centro vertical do cartão (fixo)
        if sc!=1.0:
            img=img.resize((int(img.width*sc),int(img.height*sc)),Image.BICUBIC)
        paste_alpha(cv,img,s.cx-img.width/2+dx,yc-img.height/2+dy,a)
    def bottom(s):
        img,pad,cw,ch=card_image(s.name,s.rect,s.maxw,s.maxh,s.radius,s.border,s.bw); return s.top+ch
class Sprite:
    def __init__(s,img,t0,t1,x,y,pop=True,fout=True,anchor="tl"):
        s.__dict__.update(locals()); del s.__dict__["s"]
    def draw(s,cv,t):
        if not (s.t0<=t<s.t1): return
        im=s.img; a=1.0; sc=1.0
        if s.pop: u=(t-s.t0)/0.3; sc=0.6+0.4*ease_out_back(u); a=min(1,u*2.5)
        if s.fout: a=min(a,1-ss(s.t1-0.18,s.t1,t))
        if sc!=1.0: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BICUBIC)
        x,y=s.x,s.y
        if s.anchor=="tc": x-=im.width/2
        elif s.anchor=="tr": x-=im.width
        elif s.anchor=="c": x-=im.width/2; y-=im.height/2
        if s.anchor in ("tl","tr","tc") and sc!=1.0: y+= (s.img.height-im.height)/2
        paste_alpha(cv,im,x,y,a)
class Func:
    def __init__(s,fn,t0,t1): s.fn=fn; s.t0=t0; s.t1=t1
    def draw(s,cv,t):
        if s.t0<=t<s.t1: s.fn(cv,t)
def render_overlay(elements,T,out):
    n=round(T*FPS)
    p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","qtrle","-pix_fmt","argb",out],stdin=subprocess.PIPE)
    blank=Image.new("RGBA",(W,H),(0,0,0,0)).tobytes()
    for i in range(n):
        t=i/FPS
        act=[e for e in elements if e.t0<=t<e.t1]
        if not act: p.stdin.write(blank); continue
        cv=Image.new("RGBA",(W,H),(0,0,0,0))
        for e in act: e.draw(cv,t)
        p.stdin.write(cv.tobytes())
    p.stdin.close(); p.wait()
# ---------- HTML -> PNG transparente (balões, painéis) ----------
def html_png(html,out,w=1080,h=600):
    js=f"""const {{ chromium }} = require('playwright');
(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:{w},height:{h}}},deviceScaleFactor:1}});
await p.setContent({json.dumps(html)});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(150);
const el=await p.$('#root');await el.screenshot({{path:{json.dumps(out)},omitBackground:true}});await b.close();}})();"""
    jf=out+".js"; open(jf,"w").write(js); subprocess.run(["node",jf],check=True); os.remove(jf)
    return Image.open(out).convert("RGBA")
# ---------- ASS ----------
def ts(x): x=max(0,x); return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
def ass_head(styles):
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            +"\n".join(styles)+"\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
def word_captions(words,style,hl,end_src,maxw=3,maxc=14,upper=True,phrase=False):
    ev=[]; chunks=[]; cur=[]
    for w in words:
        if w[0]>=end_src: break
        cur.append(w)
        if len(cur)>=maxw or w[2][-1:] in ".,?!" or sum(len(x[2]) for x in cur)>maxc: chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
    def fx(x): x=x.rstrip(",.?!"); return x.upper() if upper else x
    for i,ch in enumerate(chunks):
        nxt=chunks[i+1][0][0] if i+1<len(chunks) else end_src
        en=min(nxt,ch[-1][1]+0.5,end_src)
        if phrase:
            ev.append(f"Dialogue: 0,{ts(ch[0][0])},{ts(en)},{style},,0,0,0,,{{\\fad(90,90)}}"+" ".join(fx(x[2]) for x in ch)); continue
        for j,w in enumerate(ch):
            ws_=w[0]; we=ch[j+1][0] if j+1<len(ch) else en
            if we<=ws_: continue
            parts=[("{\\c"+hl+"}"+fx(x[2])+"{\\c&HFFFFFF&}") if k==j else fx(x[2]) for k,x in enumerate(ch)]
            ev.append(f"Dialogue: 0,{ts(ws_)},{ts(we)},{style},,0,0,0,,"+" ".join(parts))
    return ev
# ---------- base, cartela, composição ----------
def render_base(D,src,end_src,grade,out):
    if os.path.exists(out): return
    nf=round(end_src*FPS)
    v=(f"[0:v]fps={FPS}:start_time=0,trim=end_frame={nf},setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1,{grade}[v]")
    a=f"[0:a:0]atrim=0:{end_src},asetpts=PTS-STARTPTS,afade=t=out:st={end_src-0.08}:d=0.08,apad,atrim=0:{nf/FPS:.6f}[a]"
    run(["-i",src,"-filter_complex",v+";"+a,"-map","[v]","-map","[a]","-ac","1","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
def render_endbg(src,t_freeze,dur,grade,out,dark=-0.2,blur=10):
    if os.path.exists(out): return
    nf=round(dur*FPS)
    run(["-ss",str(t_freeze),"-i",src,"-f","lavfi","-i","anullsrc=r=48000:cl=mono","-filter_complex",
         f"[0:v]trim=end_frame=1,scale=1080:1920,setsar=1,{grade},eq=brightness={dark},gblur=sigma={blur},loop=loop={nf}:size=1,setpts=N/({FPS}*TB),trim=end_frame={nf},setpts=PTS-STARTPTS,format=yuv420p[v];[1:a]atrim=0:{nf/FPS:.6f}[a]",
         "-map","[v]","-map","[a]","-c:v","libx264","-crf","14","-preset","fast","-c:a","pcm_s16le",out])
VOICE=("highpass=f=90,afftdn=nr=8:nf=-40:tn=1,atrim=start=0.025,asetpts=PTS-STARTPTS,apad=pad_dur=0.05,"
       "deesser=i=0.3,equalizer=f=200:t=q:w=1:g=1.2,equalizer=f=3000:t=q:w=1.5:g=1.2,"
       "acompressor=threshold=-20dB:ratio=2.5:attack=15:release=200,loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")
def compose(D,base,endbg,overlay,assfile,music,out,music_vol=0.28,extra_vf=""):
    fg=[f"[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[cv][ca]",
        f"[2:v]format=yuva420p[ov]",
        f"[cv][ov]overlay=0:0:eof_action=pass{extra_vf}[c2]",
        f"[c2]ass={assfile},setpts=PTS/{SPEED},fps={FPS},format=yuv420p[vo]",
        f"[ca]atempo={SPEED},{VOICE},asplit[voz][key]",
        f"[3:a]volume={music_vol},aformat=channel_layouts=stereo[mus]",
        "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[md]",
        "[voz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
    run(["-i",base,"-i",endbg,"-i",overlay,"-i",music,"-filter_complex",";".join(fg),"-map","[vo]","-map","[ao]",
         "-c:v","libx264","-preset","medium","-crf","20","-maxrate","9M","-bufsize","18M","-c:a","aac","-b:a","192k","-movflags","+faststart",out])
def light(src,out):
    run(["-i",src,"-c:v","libx264","-profile:v","high","-level","4.1","-preset","slow","-crf","22","-maxrate","4.5M","-bufsize","9M",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","44100","-movflags","+faststart",out])
