#!/usr/bin/env bash
# Gabungkan video (tanpa audio) + voiceover (+ SFX/musik opsional), lalu verifikasi file hasil.
# Pakai: mix_and_verify.sh video_only.mp4 VO.mp3 output.mp4 [sfx_atau_musik.wav] [offset_detik=1]
# Durasi dan jumlah frame yang diharapkan diambil dari video_only.mp4 (bukan ditebak).
set -euo pipefail
V="$1"; VO="$2"; OUT="$3"; FX="${4:-}"; OFF="${5:-1}"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | awk '{printf "%d", $1+0.5}')
FRAMES=$((DUR*30)); OFFMS=$(awk -v o="$OFF" 'BEGIN{printf "%d", o*1000}')
if [ -n "$FX" ]; then
  ffmpeg -y -v error -i "$V" -i "$VO" -i "$FX" -filter_complex \
  "[1:a]aformat=channel_layouts=stereo,adelay=${OFFMS}|${OFFMS},apad=whole_dur=$DUR,atrim=0:$DUR,asetpts=PTS-STARTPTS[vo];\
[2:a]atrim=0:$DUR,asetpts=PTS-STARTPTS,volume=0.55[fx];\
[vo][fx]amix=inputs=2:duration=longest:dropout_transition=0,volume=2,alimiter=limit=0.95[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -ar 48000 -t $DUR -movflags +faststart "$OUT"
else
  ffmpeg -y -v error -i "$V" -i "$VO" -filter_complex \
  "[1:a]aformat=channel_layouts=stereo,adelay=${OFFMS}|${OFFMS},apad=whole_dur=$DUR,atrim=0:$DUR,asetpts=PTS-STARTPTS,alimiter=limit=0.95[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -ar 48000 -t $DUR -movflags +faststart "$OUT"
fi
echo "== metadata (harus: ${DUR}s, ${FRAMES} frame, 30 fps, h264+aac) =="
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate -of default=nw=1 "$OUT"
echo "frame terbaca: $(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$OUT")"
echo "== frame hitam =="; ffmpeg -i "$OUT" -vf blackdetect=d=0.1:pix_th=0.05 -an -f null - 2>&1 | grep black_ || echo "tidak ada"
echo "== senyap tak sengaja =="; ffmpeg -i "$OUT" -af silencedetect=noise=-50dB:d=0.5 -vn -f null - 2>&1 | grep silence_ || echo "tidak ada"
echo "== level volume =="; ffmpeg -i "$OUT" -af volumedetect -vn -f null - 2>&1 | grep -E "mean_volume|max_volume"
