# Brief cho agent tìm footage archive.org

Copy nguyên khối dưới vào prompt của agent (`general-purpose`, chạy nền). Thay các chỗ `<...>`.
Khi chia việc cho 2 agent, mỗi agent nhận một nửa shot list và một tiền tố file riêng để không đè nhau.

---

Find and cut public-domain B-roll from archive.org for a Vietnamese vertical science short about: <chủ đề 1–2 câu>.

Output folder (create it): <project>/assets/archive/
Put raw downloads (if any full files) in a separate temp dir under <scratchpad>/archive_raw/ — never inside the project.
Do NOT install any repos/tools; use curl, ffmpeg, ffprobe, python (run python with -I) which are already installed. Windows machine, Git Bash.

How: use the archive.org advancedsearch API (https://archive.org/advancedsearch.php?q=...&fl[]=identifier,title,licenseurl,collection&rows=50&output=json) and the metadata API (https://archive.org/metadata/<id>). Strongly prefer the Prelinger Archives (collection:prelinger) and home movies (collection:home_movies, prelinger_home_movies) — public domain, nostalgic film look. Cut segments straight from the URL with ffmpeg seeking (ffmpeg -ss X -i https://archive.org/download/<id>/<file>.mp4 -t N ...) instead of downloading whole films where possible. Re-encode each cut to H.264 mp4, no audio (-an), keep original resolution, 8–12 s long, starting on a clean shot (no title cards, no text overlays, no scene cut in the first second). Check every cut visually: extract frames (start / 0.5 s / mid / end) and look at them; reject blurry, black, text-heavy, nude or off-topic shots.

Shot list (one clip each, filename prefix as given):
<a01_xxx — mô tả shot>
<a02_xxx — ...>
If one shot genuinely can't be found, substitute the closest thing and say so.

Also write/append assets/archive/sources.csv with columns: file,identifier,title,source_url,start_sec,duration,license. Only public domain or CC items.

Final report (concise): table file → what it shows → identifier, plus shots you couldn't find and any letterboxing/fps notes. Don't paste frame images or long logs.

---

## Kinh nghiệm đã gặp (26/10/2026)
- Phim gia đình chạy 16/18 fps, render.py tự chuẩn hoá về 30 fps.
- Một số clip 854x480 có viền đen hai bên; khung vuông 940x940 crop giữa nên viền tự mất.
- Không có montage "lớn lên qua các tuổi" sạch chữ; "Fundamentals of Filing" trên archive bị gắn nhầm file.
- Hoạt hình "The Human Brain" (Britannica, 0433_Human_Brain_The_01_05_28_00) có cảnh tủ hồ sơ trí nhớ và gia đình nhiều độ tuổi — dùng tốt cho chủ đề não/ký ức.
- Agent mất ~15 phút cho 14 shot; chia 2 agent × 7 shot để nhanh gấp đôi.
