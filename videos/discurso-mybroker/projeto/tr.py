import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
import wave, numpy as np
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
segs, info = m.transcribe(a, language="pt", word_timestamps=True, vad_filter=False)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[[w.start,w.end,w.word] for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False)
