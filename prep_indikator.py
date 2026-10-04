"""
prep_indikator.py
Gabungkan file mentah BPS (data/raw/) menjadi satu tabel indikator provinsi tahun 2022 (34 provinsi)
dan cetak laporan pengecekan. Sumber semua data: BPS (lihat data/processed/sumber_data.csv).
Cara pakai: python prep_indikator.py
"""
import csv, io, re
import pandas as pd

RAW = "data/raw/"
OUT = "data/processed/"

# ---- kamus nama provinsi: nama baku + kelompok pulau ----------------------------------------
KUNCI = [  # (nama baku, kelompok pulau)
 ("Aceh","Sumatera"),("Sumatera Utara","Sumatera"),("Sumatera Barat","Sumatera"),("Riau","Sumatera"),
 ("Jambi","Sumatera"),("Sumatera Selatan","Sumatera"),("Bengkulu","Sumatera"),("Lampung","Sumatera"),
 ("Kepulauan Bangka Belitung","Sumatera"),("Kepulauan Riau","Sumatera"),
 ("DKI Jakarta","Jawa"),("Jawa Barat","Jawa"),("Jawa Tengah","Jawa"),("DI Yogyakarta","Jawa"),
 ("Jawa Timur","Jawa"),("Banten","Jawa"),
 ("Bali","Bali dan Nusa Tenggara"),("Nusa Tenggara Barat","Bali dan Nusa Tenggara"),("Nusa Tenggara Timur","Bali dan Nusa Tenggara"),
 ("Kalimantan Barat","Kalimantan"),("Kalimantan Tengah","Kalimantan"),("Kalimantan Selatan","Kalimantan"),
 ("Kalimantan Timur","Kalimantan"),("Kalimantan Utara","Kalimantan"),
 ("Sulawesi Utara","Sulawesi"),("Sulawesi Tengah","Sulawesi"),("Sulawesi Selatan","Sulawesi"),
 ("Sulawesi Tenggara","Sulawesi"),("Gorontalo","Sulawesi"),("Sulawesi Barat","Sulawesi"),
 ("Maluku","Maluku dan Papua"),("Maluku Utara","Maluku dan Papua"),("Papua Barat","Maluku dan Papua"),("Papua","Maluku dan Papua"),
]
BAKU = [k for k, _ in KUNCI]
# varian penulisan yang ditemukan di file BPS / publikasi migrasi -> nama baku
VARIAN = {"kep. bangka belitung":"Kepulauan Bangka Belitung","bangka belitung":"Kepulauan Bangka Belitung",
          "d i yogyakarta":"DI Yogyakarta","di yogyakarta":"DI Yogyakarta","d.i. yogyakarta":"DI Yogyakarta",
          "dki jakarta":"DKI Jakarta","kep. riau":"Kepulauan Riau"}
def baku(nama):
    s = re.sub(r"\s+", " ", str(nama)).strip()
    k = s.lower()
    if k in VARIAN: return VARIAN[k]
    for b in BAKU:
        if b.lower() == k: return b
    return None

def num(x):
    """'...', '-', '–' dan kosong -> NaN; selain itu angka."""
    s = str(x).strip().replace("\u2013", "-")
    if s in ("", "...", "-", "nan"): return float("nan")
    return float(s.replace(" ", ""))

def read_table(fname):
    """Baca CSV BPS: berhenti pada baris kosong (sebelum 'Keterangan')."""
    txt = open(RAW + fname, encoding="utf-8-sig").read()
    rows = list(csv.reader(io.StringIO(txt)))
    return rows

def simple(fname, col_idx, nama_var):
    rows = read_table(fname)
    out = {}
    for r in rows[1:]:
        if not r or not r[0].strip() or r[0].strip().lower().startswith("keterangan"): break
        out[r[0].strip()] = num(r[col_idx])
    return out, nama_var

def dinamis(fname, col_idx):
    """Baca unduhan tabel dinamis BPS (baris provinsi = nama huruf besar). Kembalikan (dict provinsi->nilai, nilai nasional)."""
    rows = read_table(fname)
    out, nas = {}, float("nan")
    for r in rows:
        if len(r) > col_idx and r[0].strip():
            b = baku(r[0])
            if b is not None: out[b] = num(r[col_idx])
            elif r[0].strip().upper() == "INDONESIA": nas = num(r[col_idx])
    return out, nas

def main():
    laporan = []
    # 1) IPM
    ipm, _ = simple("Indeks_Pembangunan_Manusia_Menurut_Provinsi__2022.csv", 1, "ipm")
    # 2) Persentase penduduk miskin, Maret 2022 (kolom September berisi '...' pada file ini)
    miskin, _ = simple("Jumlah_dan_Persentase_Penduduk_Miskin_Menurut_Provinsi__2022.csv", 5, "miskin_pct")
    miskin_jml, _ = simple("Jumlah_dan_Persentase_Penduduk_Miskin_Menurut_Provinsi__2022.csv", 3, "miskin_ribu")
    # 3) TPT Agustus 2022
    tpt, _ = simple("Tingkat_Pengangguran_Terbuka__TPT__dan_Tingkat_Partisipasi_Angkatan_Kerja__TPAK__Menurut_Provinsi__2022.csv", 2, "tpt")
    # 4) PDRB per kapita ADHB (ribu rupiah)
    pdrb, _ = simple("Produk_Domestik_Regional_Bruto_per_Kapita_Atas_Dasar_Harga_Berlaku_Menurut_Provinsi__ribu_rupiah___2022.csv", 1, "pdrb_kapita")
    # 5) Pengeluaran per kapita disesuaikan: file berisi provinsi + kab/kota; ambil baris provinsi saja
    rows = read_table("_Metode_Baru__Pengeluaran_per_Kapita_Disesuaikan__2022.csv")
    peng = {}
    for r in rows[3:]:
        if len(r) >= 2 and r[0].strip():
            b = baku(r[0])
            if b is not None:            # hanya cocok bila baris itu nama provinsi (kab/kota tidak cocok)
                peng[b] = num(r[1])
    peng_nas = next(num(r[1]) for r in rows if r and r[0].strip().upper() == "INDONESIA")

    def ke_baku(d):
        o, tdk = {}, []
        for k, v in d.items():
            b = baku(k)
            (o.__setitem__(b, v) if b else tdk.append(k))
        return o, tdk
    kolom = {"ipm": ipm, "miskin_pct_mar2022": miskin, "miskin_ribu_mar2022": miskin_jml,
             "tpt_agu2022": tpt, "pdrb_kapita_ribu_rp": pdrb, "pengeluaran_kapita_ribu_rp": peng}
    df = pd.DataFrame(index=pd.Index(BAKU, name="provinsi"))
    df["kelompok_pulau"] = [p for _, p in KUNCI]
    for nama, d in kolom.items():
        d2, tdk = ke_baku(d)
        df[nama] = pd.Series(d2)
        laporan.append(f"[{nama}] baris tidak dikenali (dibuang, bukan 34 provinsi): {tdk}")
    nasional = {}
    baru = {
     "rls_15plus_th": ("Rata-Rata_Lama_Sekolah_Penduduk_Umur_15_Tahun_ke_Atas_Menurut_Provinsi__2022.csv", 1),
     "gini_mar2022": ("Gini_Ratio_Menurut_Provinsi_dan_Daerah__2022.csv", 7),          # Perkotaan+Perdesaan, Semester 1 (Maret)
     "sanitasi_layak_pct": ("Persentase_Rumah_Tangga_menurut_Provinsi_dan_Memiliki_Akses_terhadap_Sanitasi_Layak__2022.csv", 1),
     "air_minum_layak_pct": ("Persentase_Rumah_Tangga_yang_Memiliki_Akses_terhadap_Sumber_Air_Minum_Layak_Menurut_Provinsi_dan_Klasifikasi_Desa__2022.csv", 3),  # Perkotaan+Perdesaan
    }
    for nama, (fn, ci) in baru.items():
        d, nas = dinamis(fn, ci)
        df[nama] = pd.Series(d); nasional[nama] = nas
    # UHH saat lahir (hasil LF SP2020) per jenis kelamin; file xlsx unduhan BPS
    u = pd.read_excel(RAW + "uhh_provinsi_jenis_kelamin_2022.xlsx", header=None).iloc[4:]
    uhh = {}
    for _, r in u.iterrows():
        b = baku(r[0])
        if b: uhh[b] = (num(r[1]), num(r[2]))
        elif str(r[0]).strip().upper() == "INDONESIA": nasional["uhh_lk"], nasional["uhh_pr"] = num(r[1]), num(r[2])
    df["uhh_lk"] = pd.Series({k: v[0] for k, v in uhh.items()})
    df["uhh_pr"] = pd.Series({k: v[1] for k, v in uhh.items()})
    # BPS tidak menyediakan UHH gabungan pada unduhan ini -> rata-rata sederhana L dan P (aproksimasi, beri label jelas)
    df["uhh_rata2_lp"] = ((df.uhh_lk + df.uhh_pr) / 2).round(2)
    # urutan kolom rapi
    df = df[["kelompok_pulau","ipm","miskin_pct_mar2022","miskin_ribu_mar2022","tpt_agu2022","rls_15plus_th","uhh_lk","uhh_pr","uhh_rata2_lp",
             "pengeluaran_kapita_ribu_rp","gini_mar2022","sanitasi_layak_pct","air_minum_layak_pct","pdrb_kapita_ribu_rp"]]
    df.reset_index().to_csv(OUT + "indikator_provinsi_2022.csv", index=False)
    pd.DataFrame(KUNCI, columns=["provinsi", "kelompok_pulau"]).to_csv(OUT + "kunci_provinsi.csv", index=False)

    # ---------------- laporan pengecekan ----------------
    laporan.append(f"\nJumlah provinsi: {len(df)} (harus 34)")
    laporan.append("Nilai kosong per kolom:\n" + df.isna().sum().to_string())
    nas = {"ipm": ipm.get("Indonesia"), "miskin_pct": miskin.get("Indonesia"), "tpt_agu": tpt.get("Indonesia"),
           "pengeluaran_ribu_rp": peng_nas}
    laporan.append("\nAngka nasional di file (pembanding): " + str(nas))
    s = df["miskin_ribu_mar2022"].sum()
    laporan.append(f"Jumlah penduduk miskin 34 provinsi = {s:,.2f} ribu vs nasional {miskin_jml.get('Indonesia'):,.2f} ribu")
    laporan.append("\nRentang nilai:\n" + df.drop(columns=["kelompok_pulau"]).describe().loc[["min", "max"]].round(2).to_string())
    for c in ["ipm", "miskin_pct_mar2022", "tpt_agu2022", "pdrb_kapita_ribu_rp", "pengeluaran_kapita_ribu_rp"]:
        laporan.append(f"  {c}: tertinggi {df[c].idxmax()} ({df[c].max()}), terendah {df[c].idxmin()} ({df[c].min()})")
    pop = pd.read_excel(RAW + "penduduk_5plus_status_migrasi_2022.xlsx", header=None).iloc[5:40]
    pop = pop[pop[0].astype(str).str.match(r"^\d{2}\.")]
    pop["prov"] = pop[0].str.replace(r"^\d{2}\.\s*", "", regex=True).map(baku)
    w = pop.set_index("prov")[7].astype(float).reindex(df.index)
    laporan.append("\nPembanding: rata-rata 34 provinsi tertimbang penduduk 5+ vs angka nasional di file (selisih kecil = wajar)")
    for c, nv in [("rls_15plus_th", nasional["rls_15plus_th"]), ("sanitasi_layak_pct", nasional["sanitasi_layak_pct"]),
                  ("air_minum_layak_pct", nasional["air_minum_layak_pct"]), ("tpt_agu2022", nas["tpt_agu"]),
                  ("miskin_pct_mar2022", nas["miskin_pct"]), ("ipm", nas["ipm"])]:
        wm = (df[c] * w).sum() / w.sum()
        laporan.append(f"  {c}: tertimbang {wm:.2f} vs nasional {nv}")
    wm_u = (df.uhh_rata2_lp * w).sum() / w.sum()
    laporan.append(f"  uhh_rata2_lp (aproksimasi): tertimbang {wm_u:.2f}; nasional rata-rata L&P {(nasional['uhh_lk']+nasional['uhh_pr'])/2:.2f}; UHH resmi L+P 2022 = 73,70 (BRS BPS 2023)")
    laporan.append(f"  korelasi IPM vs UHH rata-rata: {df.ipm.corr(df.uhh_rata2_lp):.3f}; UHH perempuan - laki-laki: min {(df.uhh_pr-df.uhh_lk).min():.2f}, maks {(df.uhh_pr-df.uhh_lk).max():.2f}")
    laporan.append(f"  gini_mar2022: nasional di file {nasional['gini_mar2022']} (tidak bisa ditimbang)")
    laporan.append("Rentang variabel baru:\n" + df[list(baru)].describe().loc[["min","max"]].round(3).to_string())
    for c in baru:
        laporan.append(f"  {c}: tertinggi {df[c].idxmax()} ({df[c].max()}), terendah {df[c].idxmin()} ({df[c].min()})")
    laporan.append("Nilai kosong (semua kolom): " + str(int(df.isna().sum().sum())))

    # ---- migrasi per 1.000 penduduk 5+ (penyebut = penduduk 5+, sesuai definisi migrasi risen) ----
    t7 = pd.read_csv(OUT + "migrasi_risen_masuk_keluar_neto.csv"); t7["prov"] = t7.provinsi.map(baku)
    mg = pd.DataFrame({"penduduk_5plus": w}).join(t7.set_index("prov")[["masuk_LP", "keluar_LP", "neto_LP"]])
    mg.columns = ["penduduk_5plus", "migran_masuk", "migran_keluar", "migran_neto"]
    pop_mig = pop.set_index("prov")[8].astype(float).reindex(mg.index)
    laporan.append(f"\nMigran (file penduduk 5+) sama dengan migrasi masuk Tabel 7: {int((pop_mig == mg.migran_masuk).sum())}/34 provinsi")
    for k in ["masuk", "keluar", "neto"]:
        mg[f"{k}_per1000"] = (mg[f"migran_{k}"] / mg.penduduk_5plus * 1000).round(2)
    mg.reset_index().rename(columns={"prov": "provinsi"}).to_csv(OUT + "migrasi_rasio_provinsi_2022.csv", index=False)
    laporan.append("Neto per 1.000: tertinggi " + str(mg.neto_per1000.idxmax()) + f" ({mg.neto_per1000.max()}), terendah " + str(mg.neto_per1000.idxmin()) + f" ({mg.neto_per1000.min()})")

    # ---- PDRB menurut lapangan usaha (diisi manual pengguna dari publikasi) -> CSV long ----
    pl = pd.read_excel(RAW + "pdrb_provinsi_lapangan_usaha_2022.xlsx", sheet_name="PDRB_Long")
    pl.to_csv(OUT + "pdrb_lapangan_usaha_long_2022.csv", index=False)
    g = pl.groupby("provinsi").agg(persen=("persen", "sum"), nilai=("nilai_miliar_rp", "sum"), total=("total_pdrb_prov_miliar_rp", "first"))
    laporan.append(f"\nPDRB lapangan usaha: {pl.provinsi.nunique()} provinsi x {pl.sektor.nunique()} sektor = {len(pl)} baris (harapan 578)")
    laporan.append(f"  jumlah persen per provinsi: {g.persen.min():.4f}-{g.persen.max():.4f}; selisih nilai vs total maks {((g.nilai/g.total-1).abs().max()*100):.3f}%")
    laporan.append("  sektor terbesar per provinsi (cek logika): " + "; ".join(
        f"{p}={d.loc[d.persen.idxmax(),'sektor']}" for p, d in pl.groupby('provinsi') if p in
        ['Kalimantan Timur','Papua','DKI Jakarta','Bali','Jawa Barat','Sulawesi Tengah','Riau']))
    txt = "\n".join(laporan)
    open(OUT + "laporan_pengecekan.txt", "w", encoding="utf-8").write(txt)
    print(txt)

if __name__ == "__main__":
    main()
