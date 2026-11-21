# Muat turun aplikasi Android

Pasang APK peralihan sekali di atas versi sebelumnya. Selepas itu, buka **Tetapan → Tentang & Kemas Kini** untuk menyemak kemas kini dalam app. Android meminta pengesahan pemasangan.

| Aplikasi | APK bertandatangan | Maklumat versi |
| --- | --- | --- |
| OM Content Tracker | [OM-Content-Tracker-1.4.5.apk](om-content-tracker/OM-Content-Tracker-1.4.5.apk?raw=true) | [Versi semasa](om-content-tracker/latest.json) |
| MyGood Finance | [MyGf-2.1.6.apk](mygf/MyGf-2.1.6.apk?raw=true) | [Versi semasa](mygf/latest.json) |

## Pengurusan keluaran

Log masuk sebagai owner dan buka [Urus keluaran Android](../../actions/workflows/urus-keluaran.yml). Pilih **Run workflow**, kekalkan cabang `main`, pilih kod app dan tindakan.

- **Semak** mengesahkan pakej, sijil dan checksum APK semasa.
- **Terbitkan** memilih APK bertandatangan yang sudah dimuat naik ke folder `mygf/` atau `om-content-tracker/`. Masukkan nama fail dan nota keluaran. Aliran kerja mengambil nombor versi daripada APK dan menyemak bahawa kodnya lebih tinggi.
- **Jeda** menghentikan tawaran kemas kini baharu bagi app tersebut. **Sambung** mengaktifkan semula keluaran yang sama selepas semakan APK.
- **Sejarah** tersedia dalam [rekod perubahan MyGood Finance](../../commits/main/mygf/latest.json) dan [rekod perubahan OM Content Tracker](../../commits/main/om-content-tracker/latest.json).

Untuk app baharu, daftarkan kod, ID pakej dan cap jari sijil dalam `.github/channels.json`. App perlu menggunakan kod yang sama apabila menyemak saluran ini.
