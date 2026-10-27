# Kênh khoa học short — skill Claude Code

Gửi cho Claude một đoạn text (kèm link bài báo nếu có), nhận về video dọc 9:16 kiểu kênh khoa học kể chuyện:
giọng đọc tiếng Việt có cảm xúc (ElevenLabs), footage cũ từ archive.org, hình trong bài báo được tô vàng làm bằng chứng,
nền đen grain, hook chữ trắng-vàng rung nhẹ, caption chạy theo lời, sao lấp lánh, nhạc piano nhỏ.

## 1. Cài đặt — dán prompt này vào Claude Code

```
Cài giúp mình skill kenh-khoa-hoc-short: chạy
git clone https://github.com/Annie-246/kenh-khoa-hoc-short ~/.claude/skills/kenh-khoa-hoc-short
Xong thì chạy scripts/check_setup.py trong thư mục đó để kiểm tra máy mình còn thiếu gì,
cài giúp những gì cài được và hướng dẫn mình phần còn lại.
```

Hoặc tự chạy trong terminal:

```
git clone https://github.com/Annie-246/kenh-khoa-hoc-short ~/.claude/skills/kenh-khoa-hoc-short
```

Cài xong **khởi động lại Claude Code** để skill được nạp.

## 2. Cần có trên máy

Lần đầu bạn gọi skill, Claude sẽ tự kiểm tra và báo thiếu gì. Danh sách đầy đủ:

| Thứ cần | Cách cài |
|---|---|
| Git | git-scm.com (Windows cần Git for Windows, Claude chạy lệnh qua Git Bash) |
| Python 3.10+ | python.org |
| ffmpeg | Windows: `winget install Gyan.FFmpeg` · macOS: `brew install ffmpeg` |
| Node.js 20+ | nodejs.org (Windows: `winget install OpenJS.NodeJS.LTS`) |
| Thư viện Python | `python -m pip install pillow numpy pymupdf faster-whisper yt-dlp` |
| Key ElevenLabs | xem mục 3 |

Lần đầu bóc băng, faster-whisper tải model khoảng 1,5 GB.

## 3. Key ElevenLabs và giọng đọc

1. Đăng ký [elevenlabs.io](https://elevenlabs.io). Cần gói trả phí (Starter trở lên) mới dùng được giọng trong Voice Library.
2. Vào **Developers → API Keys**, tạo key (bật quyền Text to Speech và User → Read).
3. Tạo file `~/.kenh-khoa-hoc-short/.env` (Windows: `C:\Users\<tên>\.kenh-khoa-hoc-short\.env`), nội dung một dòng:
   ```
   ELEVENLABS_API_KEY=sk_xxxxxxxx
   ```
4. Vào **Voice Library**, tìm giọng **Ba Luc** (ID `KJmTHSk3TjHp87WObL98`), bấm **Add to my voices**.

Đừng dán key lên chat công khai hay commit lên GitHub. Video 3 phút (~2.700 ký tự) tốn khoảng 700 credit.

## 4. Dùng

Trong Claude Code, mở thư mục bạn muốn chứa video rồi gõ:

```
/kenh-khoa-hoc-short
<dán đoạn text kể chuyện>
Link bài báo: https://...
```

Hoặc nói tự nhiên: "làm video kênh khoa học từ đoạn này…". Video xong nằm ở `<ngày> - <slug>/out/<slug>.mp4`.
Một video 3 phút mất khoảng 20–30 phút (tìm footage + render).

**Nhạc nền riêng (tuỳ chọn):** chép một file mp3 vào `~/.kenh-khoa-hoc-short/music/`. Không có thì skill dùng bản piano mặc định.

## 5. Không nhận chỉnh sửa — muốn custom thì tự sửa bản của bạn

**Repo này không nhận chỉnh sửa từ người khác:** không nhận Pull Request, không nhận yêu cầu đổi style.
Skill được giữ đúng phong cách gốc của kênh.

Bản bạn đã clone về máy là của bạn, cứ sửa thoải mái (giọng, font, màu, bố cục…). Dán prompt này vào Claude Code:

```
Mở skill ~/.claude/skills/kenh-khoa-hoc-short, đọc SKILL.md và scripts/render.py,
rồi sửa giúp mình theo ý: <mô tả thay đổi bạn muốn>.
```

## Bản quyền

- Code: MIT. Font Nunito: SIL OFL 1.1.
- Footage lấy từ archive.org (Prelinger, public domain). Hình bài báo: luôn ghi nguồn như skill làm sẵn.
- Nhạc mặc định là bản piano cover của bài "I Will Go To You Like the First Snow". Bài này có bản quyền; nếu đăng video kiếm tiền, nên thay bằng nhạc bạn có quyền dùng (YouTube Audio Library, Pixabay Music…).
