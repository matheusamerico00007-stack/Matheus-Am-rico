import json, subprocess, sys
D=sys.argv[1]
words=[w for s in json.load(open(f"{D}/tr.json")) for w in s["words"]]
# (src_start, src_end, fade_in, fade_out, black_video)
SEGS=[(14.10,20.25,0,0,True),(20.80,28.95,0.7,0,False),(29.60,40.05,0,0,False),(40.08,46.65,0,0,False),
      (48.80,54.85,0,0,False),(55.30,57.20,0,0.35,False),(131.00,135.25,0.35,0,False),(74.50,88.70,0,0.6,False)]
END=4.9
KEY={"DEUS","PAI","SENHOR","SENHOR,","CONFIA","PÓDIO","SUSTENTA","CERTEZA","EXISTE","TUDO","CÉU","DESAFIO","CAMINHO","PRIMEIRO","LUGAR","CONFIANÇA"}
FIX={"apuração":"oração"}
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
GOLD="&H6EC3E6&"
HEAD="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display SemiBold,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,3,0,1,0,4,2,90,90,520,1
Style: Big,Inter Display ExtraBold,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,5,90,90,0,1
Style: Verse,Inter Display Medium,68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,110,110,0,1
Style: Ref,Inter Display SemiBold,46,&H006EC3E6,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,12,0,1,0,0,5,90,90,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
def fmt(ws):
    out=[]
    for w in ws:
        u=w.upper().rstrip(",.")
        out.append(f"{{\\c{GOLD}\\b1}}{u}{{\\c&HFFFFFF&\\b0}}" if u.rstrip(",") in KEY else u)
    return " ".join(out)
ev=[]; off=0
for i,(a,b,fi,fo,blk) in enumerate(SEGS):
    ws=[(w[0]-a+off,w[1]-a+off,FIX.get(w[2].strip(),w[2].strip())) for w in words if w[0]>=a-0.05 and w[1]<=b+0.3]
    if blk:
        groups=[];cur=[]
        for w in ws:
            cur.append(w)
            if w[2].endswith(","): groups.append(cur); cur=[]
        if cur: groups.append(cur)
        for k,g in enumerate(groups):
            st=g[0][0]-0.05; en=(groups[k+1][0][0]-0.05) if k+1<len(groups) else off+(b-a)-0.05
            ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Big,,0,0,0,,{{\\fad(180,220)\\blur0.6}}"+fmt([x[2] for x in g]).replace(" MÉRITOS","\\NMÉRITOS")+".")
    else:
        cur=[]; chunks=[]
        for w in ws:
            cur.append(w)
            if w[2][-1:] in ",." or len(cur)>=4: chunks.append(cur); cur=[]
        if cur: chunks.append(cur)
        for k,c in enumerate(chunks):
            st=c[0][0]-0.04; en=min(c[-1][1]+0.45, chunks[k+1][0][0]-0.04 if k+1<len(chunks) else off+(b-a))
            ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\fad(120,120)}}"+fmt([x[2] for x in c]))
    off+=b-a
VT=off; T=off+END
ev.append(f"Dialogue: 0,{ts(VT+0.5)},{ts(T-0.2)},Verse,,0,0,0,,{{\\fad(600,500)\\pos(540,900)}}\"ENTREGA O TEU CAMINHO\\NAO SENHOR, CONFIA NELE,\\NE O MAIS ELE FARÁ.\"")
ev.append(f"Dialogue: 0,{ts(VT+1.3)},{ts(T-0.2)},Ref,,0,0,0,,{{\\fad(600,500)\\pos(540,1130)}}SALMO 37:5")
open(f"{D}/motiv.ass","w").write(HEAD+"\n".join(ev)+"\n")
print("voz",round(VT,2),"total",round(T,2))
n=len(SEGS)
GRADE="eq=contrast=1.14:saturation=0.72:brightness=-0.02:gamma=0.97,colorbalance=rs=-0.04:bs=0.07:rm=0.02:rh=0.07:gh=0.02:bh=-0.06"
def run(c): subprocess.run(["ffmpeg","-v","error","-y"]+c,check=True)
for i,(a,b,fi,fo,blk) in enumerate(SEGS):
    L=b-a; o=f"{D}/seg{i}.mkv"
    import os
    if os.path.exists(o): continue
    af=f"afade=t=in:d=0.04,afade=t=out:st={L-0.06}:d=0.06"
    if blk:
        run(["-f","lavfi","-i",f"color=c=black:s=1080x1920:r=30:d={L}","-ss",str(a),"-t",str(L),"-i",f"{D}/dl/original.mov",
             "-map","0:v","-map","1:a","-af",af,"-c:v","libx264","-crf","12","-preset","fast","-c:a","pcm_s16le","-shortest",o]); continue
    z=f"1.0+0.06*t/{L}" if i%2 else f"1.06-0.06*t/{L}"
    v=(f"fps=30,{GRADE},scale=w='trunc(1080*({z})/2)*2':h='trunc(1920*({z})/2)*2':eval=frame:flags=bicubic,"
       f"crop=1080:1920:(iw-1080)/2:(ih-1920)*0.35,setsar=1")
    if fi: v+=f",fade=t=in:st=0:d={fi}"
    if fo: v+=f",fade=t=out:st={L-fo}:d={fo}"
    run(["-ss",str(a),"-t",str(L),"-i",f"{D}/dl/original.mov","-vf",v,"-af",af,"-map","0:v","-map","0:a",
         "-c:v","libx264","-crf","12","-preset","fast","-c:a","pcm_s16le",o])
run(["-f","lavfi","-i",f"color=c=black:s=1080x1920:r=30:d={END}","-f","lavfi","-i",f"anullsrc=r=48000:cl=mono","-t",str(END),
     "-c:v","libx264","-crf","12","-preset","fast","-c:a","pcm_s16le",f"{D}/seg{n}.mkv"])
open(f"{D}/list.txt","w").write("".join(f"file 'seg{i}.mkv'\n" for i in range(n+1)))
fg=[f"[0:v]vignette=angle=PI/4.2,noise=alls=5:allf=t,ass={D}/motiv.ass,format=yuv420p[vo]",
 "[0:a]highpass=f=90,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=3:attack=10:release=150,equalizer=f=3500:t=q:w=1:g=2,loudnorm=I=-15:TP=-2:LRA=8,aresample=48000,aformat=channel_layouts=stereo,asplit[voz][key]",
 "[1:a]volume=0.42,aformat=channel_layouts=stereo[mus]",
 "[mus][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=40:release=500:makeup=1[mduck]",
 "[voz][mduck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[ao]"]
run(["-f","concat","-safe","0","-i",f"{D}/list.txt","-i",f"{D}/trilha.wav","-filter_complex",";".join(fg),
  "-map","[vo]","-map","[ao]","-c:v","libx264","-preset","medium","-crf","20","-maxrate","12M","-bufsize","24M","-c:a","aac","-b:a","192k",
  "-movflags","+faststart",f"{D}/motivacional.mp4"])
