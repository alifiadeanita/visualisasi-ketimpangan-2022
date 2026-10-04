"""
prep_migrasi.py
Ekstrak Tabel 5.3 (arus migrasi risen antarprovinsi, L+P) dan Tabel 7 (migrasi masuk/keluar/neto risen)
dari publikasi BPS 'Statistik Migrasi Indonesia Hasil Long Form SP2020'.
Keluaran: data/processed/*.csv
Sumber: BPS (2023), Statistik Migrasi Indonesia Hasil Long Form Sensus Penduduk 2020.
"""
import re, sys
import pdfplumber
import pandas as pd

PDF = sys.argv[1] if len(sys.argv) > 1 else "data/raw/statistik-migrasi-indonesia-hasil-long-form-sensus-penduduk-2020.pdf"
OUT = "data/processed/"

PROVS = ["Aceh","Sumatera Utara","Sumatera Barat","Riau","Jambi","Sumatera Selatan","Bengkulu","Lampung",
 "Kep. Bangka Belitung","Kepulauan Riau","DKI Jakarta","Jawa Barat","Jawa Tengah","DI Yogyakarta","Jawa Timur",
 "Banten","Bali","Nusa Tenggara Barat","Nusa Tenggara Timur","Kalimantan Barat","Kalimantan Tengah",
 "Kalimantan Selatan","Kalimantan Timur","Kalimantan Utara","Sulawesi Utara","Sulawesi Tengah","Sulawesi Selatan",
 "Sulawesi Tenggara","Gorontalo","Sulawesi Barat","Maluku","Maluku Utara","Papua Barat","Papua"]
TOTAL = "Jumlah/Total"

def to_int(tok):
    t = re.sub(r"[A-Za-z\.\/]", "", tok)          # buang sisa watermark yang menempel
    t = t.replace(" ", "")
    if t in ("-", ""): return 0 if tok.strip() == "-" else None
    return int(t) if re.fullmatch(r"-?\d+", t) else None

def read_rows(page, label_max_x=140, num_min_x=140, y_min=150, row_tol=4):
    """Kembalikan {label: [angka,...]} untuk satu halaman, berbasis koordinat."""
    words = page.extract_words()
    # halaman tanpa huruf: buang karakter watermark (huruf/titik) supaya bbox angka tidak membesar
    clean = page.filter(lambda o: o.get("object_type") != "char" or re.fullmatch(r"[0-9\-]", o["text"]))
    nwords = clean.extract_words()
    # 1) label baris: kelompokkan kata di zona kiri per baris (top)
    left = [w for w in words if w["x1"] < label_max_x and w["top"] > y_min]
    lines = {}
    for w in sorted(left, key=lambda w: (round(w["top"]), w["x0"])):
        key = next((k for k in lines if abs(k - w["top"]) < 2.5), None)
        lines.setdefault(key if key is not None else w["top"], []).append(w["text"])
    labels = {}
    for top, toks in lines.items():
        name = " ".join(toks).replace("Jumlah / Total", TOTAL)
        name = re.sub(r"\s*/\s*", "/", name) if "Jumlah" in name else name
        if name in PROVS or name.startswith("Jumlah"):
            labels[top] = TOTAL if name.startswith("Jumlah") else name
    # 2) angka tiap baris: kata di zona kanan pada top yang sama, digabung bila jaraknya kecil (pemisah ribuan)
    right = [w for w in nwords if w["x0"] >= num_min_x and w["top"] > y_min]
    out = {}
    for top, name in labels.items():
        ws = sorted([w for w in right if abs(w["top"] - top) < row_tol and re.search(r"\d|^-$", w["text"])],
                    key=lambda w: w["x0"])
        groups, cur, prev = [], [], None
        for w in ws:
            if prev is not None and w["x0"] - prev["x1"] > 10:
                groups.append(cur); cur = []
            cur.append(w["text"]); prev = w
        if cur: groups.append(cur)
        vals = [to_int(" ".join(g)) for g in groups]
        out[name] = vals
    return out

def main():
    pdf = pdfplumber.open(PDF)
    # ---------- Tabel 5.3 : halaman PDF 72-74 ----------
    blocks = [read_rows(pdf.pages[i]) for i in (71, 72, 73)]
    for b in blocks:
        assert len(b) == 35, f"jumlah baris {len(b)}"
        bad = {k: len(v) for k, v in b.items() if len(v) != 12 or None in v}
        assert not bad, bad
    full = {p: blocks[0][p] + blocks[1][p] + blocks[2][p] for p in PROVS + [TOTAL]}
    # urutan kolom: 34 provinsi + Lainnya/Luar Negeri + Total. Urutan kolom Papua Barat/Papua dicek lewat diagonal.
    colnames = PROVS + ["Lainnya/Luar Negeri", TOTAL]
    mat = pd.DataFrame({p: full[p] for p in PROVS + [TOTAL]}, index=colnames).T   # baris=tujuan, kolom=asal
    mat.index.name = "tujuan"
    mat.columns.name = "asal"
    # validasi diagonal
    for i, p in enumerate(PROVS):
        r = mat.loc[p, PROVS]
        if r.idxmax() != p:
            print("PERINGATAN diagonal:", p, "maks di", r.idxmax())
    mat.to_csv(OUT + "migrasi_risen_matriks_od_wide.csv")
    # format long, tanpa diagonal dan tanpa total
    long = (mat.loc[PROVS, PROVS].stack().rename("jumlah").reset_index())
    long.columns = ["provinsi_tujuan", "provinsi_asal", "jumlah"]
    long = long[long.provinsi_tujuan != long.provinsi_asal][["provinsi_asal", "provinsi_tujuan", "jumlah"]]
    long.to_csv(OUT + "migrasi_risen_od_long.csv", index=False)
    # dari luar negeri
    mat.loc[PROVS, ["Lainnya/Luar Negeri"]].rename(columns={"Lainnya/Luar Negeri": "jumlah"}).reset_index() \
       .rename(columns={"tujuan": "provinsi_tujuan"}).to_csv(OUT + "migrasi_risen_dari_luar_negeri.csv", index=False)

    # ---------- Tabel 7 : halaman PDF 76 ----------
    t7 = read_rows(pdf.pages[75], label_max_x=150, num_min_x=150, y_min=100)
    cols = ["masuk_L","masuk_P","masuk_LP","keluar_L","keluar_P","keluar_LP","neto_L","neto_P","neto_LP"]
    bad = {k: len(v) for k, v in t7.items() if len(v) != 9 or None in v}
    assert not bad, bad
    df7 = pd.DataFrame(t7, index=cols).T
    df7.index.name = "provinsi"
    df7.to_csv(OUT + "migrasi_risen_masuk_keluar_neto.csv")
    print("selesai. Tabel 5.3:", mat.shape, "| Tabel 7:", df7.shape)

if __name__ == "__main__":
    main()
