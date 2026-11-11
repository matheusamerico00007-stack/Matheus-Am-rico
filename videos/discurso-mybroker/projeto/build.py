import json, subprocess, sys, re
D = sys.argv[1]
words = [w for s in json.load(open(f"{D}/tr.json")) for w in s["words"]]
FIX = {"apuração":"oração","becico":"versículo","35.5":"37:5","Salmos":"Salmo","tá":"tá"}
CUTS = {
 "corte1_o-merito-nao-e-meu": dict(
   title="3 MESES DE MYBROKER.\nPÓDIO.\nE O MÉRITO NÃO É MEU.",
   segs=[(12.45,28.95),(29.60,61.95),(68.20,88.75)]),
 "corte2_eu-abandono-minha-fe": dict(
   title="\"SE VOCÊ NÃO SENTIR NADA,\nEU ABANDONO MINHA FÉ.\"",
   segs=[(111.45,130.45),(130.95,153.45)]),
}
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60
    return f"{h}:{m:02d}:{s:05.2f}"
HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,560,1
Style: Title,Inter ExtraBold,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB4000000,-1,0,0,0,100,100,1,0,3,22,0,8,90,90,230,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for name, c in CUTS.items():
    segs=c["segs"]; ev=[]; off=0; chunks=[]
    for a,b in segs:
        ws=[w for w in words if w[0]>=a-0.05 and w[1]<=b+0.3]
        cur=[]
        for w in ws:
            txt=w[2].strip()
            for k,v in FIX.items(): txt=txt.replace(k,v)
            cur.append((w[0]-a+off, w[1]-a+off, txt))
            end_punct = txt[-1:] in ".,?!"
            if len(cur)>=3 or end_punct or sum(len(x[2]) for x in cur)>14:
                chunks.append(cur); cur=[]
        if cur: chunks.append(cur)
        off += b-a
    total=off
    for i,ch in enumerate(chunks):
        st=ch[0][0]; en=chunks[i+1][0][0] if i+1<len(chunks) else ch[-1][1]+0.3
        en=min(en, ch[-1][1]+0.6)
        for j,(ws_,we,_) in enumerate(ch):
            wend = ch[j+1][0] if j+1<len(ch) else en
            parts=[]
            for k,(_,_,t) in enumerate(ch):
                t=t.rstrip(",.").upper()
                parts.append("{\\c&H33D6FF&}"+t+"{\\c&HFFFFFF&}" if k==j else t)
            ev.append(f"Dialogue: 0,{ts(max(ws_,st))},{ts(wend)},Cap,,0,0,0,,{{\\fscx100\\fscy100}}"+" ".join(parts))
    title=c["title"].replace("\n","\\N")
    ev.insert(0,f"Dialogue: 1,{ts(0)},{ts(3.8)},Title,,0,0,0,,{{\\fad(150,300)}}{title}")
    open(f"{D}/{name}.ass","w").write(HEAD+"\n".join(ev)+"\n")
    # filtergraph
    fg=[]; n=len(segs)
    for i,(a,b) in enumerate(segs):
        z = 1.0 if i%2==0 else 1.08
        crop = f",scale=iw*{z}:ih*{z},crop=1080:1920:(iw-1080)*0.45:(ih-1920)*0.3" if z>1 else ""
        fg.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS{crop},setsar=1[v{i}]")
        fg.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b-a-0.04}:d=0.04[a{i}]")
    fg.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[vc][ac]")
    fg.append(f"[vc]eq=contrast=1.05:saturation=1.08:gamma=0.98,ass={D}/{name}.ass,format=yuv420p[vo]")
    fg.append("[ac]highpass=f=90,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=3:attack=10:release=150,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[ao]")
    cmd=["ffmpeg","-v","error","-y","-i",f"{D}/dl/original.mov","-filter_complex",";".join(fg),
         "-map","[vo]","-map","[ao]","-c:v","libx264","-preset","medium","-crf","19","-r","30",
         "-c:a","aac","-b:a","192k","-ac","2","-movflags","+faststart",f"{D}/{name}.mp4"]
    print(name, f"{total:.1f}s"); subprocess.run(cmd, check=True)
