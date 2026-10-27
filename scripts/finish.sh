#!/usr/bin/env bash
# Mix voice (-16 LUFS) with a very quiet music bed and mux onto build/video.mp4.
# Usage (from the project folder): bash <skill>/scripts/finish.sh out/<name>.mp4 [music.mp3]
set -e
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
CONF="$HOME/.kenh-khoa-hoc-short"   # user folder: .env + music/ (outside the skill folder)
OUT="${1:-out/final.mp4}"
MUSIC="${2:-$(ls "$CONF"/music/*.mp3 "$CONF"/music/*.wav "$CONF"/music/*.m4a "$SKILL"/assets/music/*.mp3 2>/dev/null | head -1)}"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 build/video.mp4)
FADE=$(python -c "print(max(0, $DUR - 3.5))")
mkdir -p "$(dirname "$OUT")"
if [ -z "$MUSIC" ]; then
  echo "no music file -> voice only"
  ffmpeg -v error -y -i voice.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" -t "$DUR" -c:a pcm_s16le build/mix.wav
else
# music: normalise to -24 LUFS then -14 dB => roughly 20 dB under the voice ("rất nhỏ")
ffmpeg -v error -y -i voice.mp3 -stream_loop -1 -i "$MUSIC" -filter_complex \
  "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[v];[1:a]atrim=0:$DUR,asetpts=PTS-STARTPTS,loudnorm=I=-24:TP=-6,volume=-14dB,aresample=48000,afade=t=in:d=1.5,afade=t=out:st=$FADE:d=3.5[m];[v][m]amix=inputs=2:duration=longest:normalize=0[a]" \
  -map "[a]" -t "$DUR" -c:a pcm_s16le build/mix.wav
fi
ffmpeg -v error -y -i build/video.mp4 -i build/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$OUT"
echo "done $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT") s)"
