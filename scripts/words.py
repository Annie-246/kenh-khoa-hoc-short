# Word timestamps from faster-whisper, with the words replaced by the script text (ground truth).
# Also prints sentence timings to plan the media timeline.
# Usage (from the project folder): python -I -X utf8 <skill>/scripts/words.py voice.mp3 script.txt build/words.json
import json, os, re, sys, difflib
from faster_whisper import WhisperModel

audio, script_file, out_file = (sys.argv[1:4] + ["voice.mp3", "script.txt", "build/words.json"][len(sys.argv) - 1:])[:3]
os.makedirs(os.path.dirname(out_file) or ".", exist_ok=True)

m = WhisperModel("medium", device="cpu", compute_type="int8")
segs, _ = m.transcribe(audio, language="vi", word_timestamps=True, beam_size=5)
heard = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]

script = re.sub(r"\[[^\]]*\]", "", open(script_file, encoding="utf-8").read())  # drop [emotion] tags
truth = script.split()
norm = lambda t: re.sub(r"[^\w]", "", t.lower())

sm = difflib.SequenceMatcher(a=[norm(h[0]) for h in heard], b=[norm(t) for t in truth], autojunk=False)
out = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if j1 == j2:
        continue
    if i1 == i2:  # script words whisper missed: squeeze in after previous word
        t = out[-1]["end"] if out else 0.0
        out += [{"w": truth[j], "start": t, "end": t} for j in range(j1, j2)]
        continue
    s, e = heard[i1][1], heard[i2 - 1][2]
    n = j2 - j1
    for k, j in enumerate(range(j1, j2)):
        out.append({"w": truth[j], "start": s + (e - s) * k / n, "end": s + (e - s) * (k + 1) / n})
json.dump(out, open(out_file, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

line, st = [], None
for x in out:
    st = x["start"] if st is None else st
    line.append(x["w"])
    if x["w"][-1] in ".?!":
        print(f"{st:7.2f}-{x['end']:7.2f} {' '.join(line)[:90]}")
        line, st = [], None
print(f"words heard {len(heard)} / script {len(truth)} -> {out_file}")
