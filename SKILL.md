---
name: kenh-khoa-hoc-short
description: Dựng video dọc 9:16 cho kênh khoa học kể chuyện — người dùng gửi một đoạn text (kèm link bài báo / tài liệu), AI viết bản đọc có cảm xúc, render giọng ElevenLabs (giọng Ba Luc), lấy hình từ archive.org + cắt hình trong bài báo tô vàng làm bằng chứng, dựng nền đen grain, hook cố định trên cùng chữ trắng-vàng kiểu cắt tay rung nhẹ, khung vuông bo góc phát sáng, caption chạy theo lời, sao lấp lánh hồng-xanh-vàng-trắng, nhạc nền piano rất nhỏ. Dùng khi người dùng gửi text và nói "làm video kênh khoa học", "dựng short kiểu nền đen sao lấp lánh", "làm tiếp video kênh", hoặc gọi /kenh-khoa-hoc-short.
---

# Kênh khoa học short

`SK` = thư mục gốc của skill này (đường dẫn ở dòng "Base directory for this skill" khi skill được nạp).
`CONF` = `~/.kenh-khoa-hoc-short/` — thư mục riêng của người dùng, giữ key và nhạc, nằm ngoài thư mục skill:
- `CONF/.env` — một dòng `ELEVENLABS_API_KEY=sk_...`
- `CONF/music/` — nhạc nền riêng (tuỳ chọn; file mp3/wav/m4a đầu tiên được dùng). Không có thì dùng nhạc mặc định `SK/assets/music/first_snow_piano.mp3`

Trả lời người dùng bằng tiếng Việt.

## Bước 0 — kiểm tra máy (lần đầu dùng, hoặc khi lệnh nào đó lỗi)
```
PYTHONIOENCODING=utf-8 python -X utf8 "$SK/scripts/check_setup.py"
```
Nếu có mục `[THIẾU]`: dừng lại, báo người dùng đúng danh sách thiếu kèm cách bổ sung (script đã in sẵn), rồi:
- **Python package** (`pillow numpy pymupdf faster-whisper yt-dlp`): hỏi người dùng có muốn mình cài giúp không → `python -m pip install <tên>`.
- **ffmpeg / Node.js**: đưa lệnh cài theo hệ điều hành (script đã in); cài xong phải mở lại terminal / Claude Code để PATH nhận.
- **ElevenLabs key**: hướng dẫn người dùng tự tạo key ở elevenlabs.io → Developers → API Keys (bật quyền Text to Speech + User read), rồi **tự** tạo file `CONF/.env`. Không yêu cầu người dùng dán key vào chat; nếu họ đã dán thì ghi vào file giúp và nhắc họ đó là bí mật. Không bao giờ in/cat file key.
- **Giọng Ba Luc**: nếu TTS báo `voice_not_found`, bảo người dùng mở ElevenLabs Voice Library, tìm "Ba Luc" (ID `KJmTHSk3TjHp87WObL98`) và bấm "Add to my voices". Giọng thư viện cần gói trả phí (Starter trở lên). Người dùng muốn giọng khác thì truyền voice ID làm tham số thứ 3 của `tts.mjs`.
Chạy lại `check_setup.py` đến khi báo "Máy đã đủ".

Lần đầu `words.py` chạy, faster-whisper tải model `medium` (~1,5 GB) — báo trước cho người dùng.

## Chốt cứng của phong cách (đừng tự đổi nếu người dùng không yêu cầu)
- **Giọng**: ElevenLabs, voice Ba Luc, model `eleven_v4`, `languageCode: vi`, stability 0.4 / similarity 0.75. Khoảng 700 credit cho 2.700 ký tự.
- **Hình**: chỉ footage **archive.org** (Prelinger, public domain) + **hình cắt từ bài báo/tài liệu** người dùng gửi. Không sinh clip AI.
- **Bố cục** 1080x1920: nền đen + grain động; hook 2 dòng căn giữa phía trên khung, **cố định suốt video**; khung vuông 940x940 bo góc 48 có quầng sáng ấm; caption IN HOA nằm trong phần dưới khung.
- **Chữ**: Nunito 900 ép hẹp 0.9, mép sần, từng chữ cái xê dịch/xoay nhẹ đổi 4 khung/lần ("run run nhẹ"). Hook cỡ 54, caption cỡ 50. **Chữ chỉ trắng + vàng**; hồng và xanh dương chỉ dùng cho **ngôi sao**.
- **Sao**: 4 cánh có glow, to nhỏ xen kẽ, lấp lánh.
- **Nhạc**: mặc định bản piano "I Will Go To You Like the First Snow" (`assets/music/first_snow_piano.mp3`), thấp hơn giọng ~20 dB. **Không dùng bản có lời** dưới giọng đọc. Người dùng nêu bài khác thì tìm bản piano bằng `yt-dlp -x --audio-format mp3 "ytsearch1:<tên> piano"` và nhắc họ tự kiểm tra bản quyền trước khi đăng.
- **Hình nghiên cứu = bằng chứng**: mỗi ảnh tô vàng (highlighter) đúng câu chính đang được đọc, cắt kiểu "zoom vào bằng chứng" (câu tô vàng ở giữa, thêm 2–3 dòng trên/dưới, mép trái/phải mờ dần), dưới khung ghi nguồn (`credit`). Câu tô vàng nên nằm gọn **1 dòng** để zoom được to; chỉ trang tiêu đề/tóm tắt mới cắt rộng.
- **Footage archive** ghi `"illus_label": "(Hình ảnh minh họa)"` trong `edit.json` → hiện dưới khung.
- Tự kiểm tra khung xem trước nội bộ rồi render thẳng bản đầy đủ, chỉ gửi người dùng file hoàn chỉnh.
- Không SFX trừ khi người dùng yêu cầu.

## Quy trình — chia việc song song cho nhanh nhất

Thư mục dự án: `<thư mục làm việc>/<yy.mm.dd> - <slug>/` với `assets/archive`, `assets/paper`, `build`, `out`. Mọi lệnh chạy từ thư mục dự án.

### Bước 1 — viết `script.txt` (làm ngay, ~2 phút)
Giữ nguyên lời người dùng, chỉ: bỏ `**`/markdown; số viết thành chữ ("năm hai nghìn không trăm hai mươi lăm", "hai mươi sáu em bé"); bỏ hoặc đọc hoá từ viết tắt khó ("fMRI" → "máy chụp cộng hưởng từ"); thêm thẻ cảm xúc tiếng Anh đầu câu cho đoạn chuyển ý: `[curious]` mở đầu, `[softly]`, `[thoughtful]`, `[excited]` khi đến phát hiện, `[mischievously]` cho câu "đoán xem…", `[impressed]`, `[gently]`/`[emotional]` đoạn kết; dùng `...` để ngắt nghỉ. Đồng thời soạn **shot list** 12–16 shot theo từng ý (tiền tố a01…).

### Bước 2 — bắn song song trong MỘT lượt tool
1. **Agent archive #1 và #2** (`general-purpose`, chạy nền): mỗi agent nửa shot list, prompt lấy từ `references/archive-brief.md`.
2. **Agent tài liệu** (`general-purpose`, chạy nền) nếu có link bài báo/tài liệu: tải PDF (Science/Nature hay chặn 403 → tìm bản PDF trên site lab tác giả / PMC / bioRxiv / arXiv), chạy `paper_figs.py pages`, xem trang, chọn 4–6 vùng đáng giá (trang tiêu đề + abstract, sơ đồ thí nghiệm, biểu đồ kết quả chính), chạy `paper_figs.py crop` ra `assets/paper/p_*.png`, báo lại mỗi file cho thấy gì + dòng nguồn "NGUỒN: <TÁC GIẢ> ET AL., <TẠP CHÍ> (<NĂM>)".
   Sau đó **mình** làm ảnh bằng chứng tô vàng theo từng ý lời đọc (agent chưa biết mốc câu): `paper_zoom.py` (spec câu cần tô) → `paper_figs.py crop` (phần tử thứ 6 của mỗi vùng = danh sách câu tô vàng) → `paper_zoom.py fade`. Đặt tên `h*_<ý>.png`.
3. **Mình**: render giọng + mốc chữ (chạy nền, không chờ agent):
   ```
   node --env-file="$HOME/.kenh-khoa-hoc-short/.env" "$SK/scripts/tts.mjs" script.txt voice.mp3
   PYTHONIOENCODING=utf-8 python -X utf8 "$SK/scripts/words.py" voice.mp3 script.txt build/words.json
   ```
   `words.py` in mốc từng câu — dùng để xếp timeline. Bóc băng ra phải đủ lời, không có chữ "curious/softly…" bị đọc thành tiếng.

### Bước 3 — `edit.json` (khi agent về)
```json
{
  "hook": [[["TẠI SAO BẠN ", "W"], ["KHÔNG THỂ", "Y"]],
           [["NHỚ ĐƯỢC ", "W"], ["THỜI THƠ ẤU", "Y"], ["?", "W"]]],
  "credit": "NGUỒN: YATES ET AL., SCIENCE (2025)",
  "illus_label": "(Hình ảnh minh họa)",
  "keep_case": ["fMRI"],
  "timeline": [[0.0, "assets/archive/a01_child.mp4", 0],
               [46.64, "assets/paper/p_title.png", 0]]
}
```
- Hook: câu hỏi/khẳng định gây tò mò của chính video, 2 dòng ngắn (≤ ~22 ký tự/dòng), từ khoá vàng.
- Timeline: mỗi đoạn bắt đầu ở mốc câu; **≤ 10 s mỗi hình**; hình bài báo đặt đúng lúc lời nhắc tới nghiên cứu/kết quả; clip ngắn hơn đoạn sẽ tự slow-mo nhẹ — tránh kéo quá 1.3x; tái dùng clip thì đổi `offset`.

### Bước 4 — xem trước rồi render
```
PYTHONIOENCODING=utf-8 python -X utf8 "$SK/scripts/render.py" @9   # 1 khung -> build/preview_9.png, Read để TỰ kiểm tra
PYTHONIOENCODING=utf-8 python -X utf8 "$SK/scripts/render.py"      # full (chạy nền) ~0.15–0.25 s/khung → 3 phút video ≈ 12–15 phút
bash "$SK/scripts/finish.sh" out/<slug>.mp4 [music.mp3]            # bỏ trống music = CONF/music/ nếu có, không thì nhạc mặc định
```
Kiểm tra cuối: trích 4 khung (đầu/hình bài báo/giữa/cuối), xem hook không tràn mép, caption không đè chữ trong hình bài báo, thời lượng video = audio.

## Bẫy đã vấp
- Windows: Python in tiếng Việt lỗi `cp1252` → luôn `PYTHONIOENCODING=utf-8 python -X utf8`.
- Lệnh chạy bằng Git Bash/bash (Windows: dùng Bash tool, không dùng PowerShell cho các lệnh `$SK`/`$HOME` ở trên).
- Font Rubik / Rubik Dirt **không có dấu tiếng Việt**; Nunito 900 là font gần mẫu nhất có đủ dấu.
- `render.py` đọc `edit.json` + `build/words.json` ở thư mục hiện tại; chạy 2 render cùng lúc thì mỗi bản chậm gấp đôi.
- Science.org trả 403 cho curl → tìm PDF trên trang lab tác giả hoặc PMC.
