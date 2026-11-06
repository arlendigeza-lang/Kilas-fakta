# KILAS FAKTA — Video pipeline

Pipeline ini menggunakan **Gemini Omni 1.2 Flash** untuk membuat klip sejarah bergerak, lalu FFmpeg menyatukannya dengan narasi menjadi video vertikal MP4.

## Yang sudah disiapkan
- Prompt 9 adegan Kekaisaran Mongol dalam gaya ilustrasi dokumenter sejarah.
- Pembuatan klip video vertikal 9:16, 720p, sekitar 10 detik per adegan.
- Penggabungan klip, audio narasi, watermark KILAS FAKTA, dan judul pembuka.
- Musik latar opsional dan subtitle SRT opsional.
- GitHub Actions untuk menjalankan render dari menu Actions.

## Sebelum bisa dijalankan
**Perlu API key berbayar Gemini.** Model video ini tidak menyediakan free tier untuk pembuatan video. Harga resmi yang diumumkan untuk Gemini Omni 1.2 Flash adalah sekitar **US$0,07 per detik video 720p**. Sembilan adegan x 10 detik berarti perkiraan sekitar **US$6,30** untuk video adegan, belum termasuk kemungkinan biaya input/permintaan lain. Periksa harga terbaru sebelum menjalankan.

1. Buat API key di [Google AI Studio](https://aistudio.google.com/apikey).
2. Di repository GitHub buka **Settings → Secrets and variables → Actions → New repository secret**.
3. Nama secret harus `GEMINI_API_KEY`; isi dengan API key tadi. Jangan menaruh key di file atau membagikannya di chat.
4. Upload audio narasi ke folder `assets` dengan nama `narration.mp3`. Format MP3 atau WAV didukung FFmpeg.
5. (Opsional) Upload musik latar sebagai `assets/music.mp3`.
6. (Opsional) Upload subtitle yang sudah disinkronkan sebagai `assets/subtitles.srt`.
7. Buka tab **Actions → Render KILAS FAKTA video → Run workflow**.
8. Setelah selesai, buka hasil run dan unduh artifact **KILAS-FAKTA-video**.

## Mengubah topik
Edit `pipeline/scenes.json`: ubah judul dan daftar prompt adegan. Setiap prompt sebaiknya menggambarkan satu adegan bergerak, bukan gambar diam. Durasi klip diatur pada `duration_seconds` (3–15 detik untuk model yang digunakan).

## Catatan penting
- Menambahkan kode ke GitHub belum berarti layanan AI sudah aktif. AI baru dipanggil saat workflow dijalankan dengan secret API key yang valid.
- Setiap adegan dibuat sebagai klip terpisah; hasil AI tetap perlu diperiksa untuk akurasi sejarah dan konsistensi visual.
- Audio bawaan dari klip AI sengaja dibuang agar tidak bertabrakan dengan narasi. Jika musik disediakan, musik dicampur pelan di bawah narasi.
- Pipeline tidak mengunggah video secara otomatis ke Facebook atau YouTube.
