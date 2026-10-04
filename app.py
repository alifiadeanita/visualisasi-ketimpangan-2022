# app.py : langkah 6. Tiga bagian: 1 hierarki, 2 multivariat (brushing dan linking), 3 aliran (Sankey + matriks OD).
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.cluster.hierarchy import fcluster, leaves_list, linkage
from scipy.spatial.distance import squareform

st.set_page_config(page_title="Ketimpangan Pembangunan Antarprovinsi 2022", layout="wide")

st.title("Jawa dan Luar Jawa: Seberapa Timpang Pembangunan Kita?")
st.caption("Data tahun 2022 untuk 34 provinsi. Sumber: BPS")


# ---------------------------------------------------------------- 1. MEMUAT DATA
@st.cache_data
def muat_data():
    ind = pd.read_csv("data/processed/indikator_provinsi_2022.csv")
    pdrb = pd.read_csv("data/processed/pdrb_lapangan_usaha_long_2022.csv")
    return ind, pdrb


ind, pdrb = muat_data()


# ---------------------------------------------------------------- 2. BAGIAN HIERARKI
def siapkan_node(ind, pdrb):
    """Menyusun daftar 'kotak' (node) hierarki: Indonesia > pulau > provinsi > lapangan usaha.
    Dipakai bersama oleh treemap dan sunburst, jadi kedua grafik pasti menampilkan data yang sama.
    Ukuran = PDRB (triliun Rp). Warna = PDRB per kapita (juta Rp)."""
    d = pdrb.merge(ind[["provinsi", "pdrb_kapita_ribu_rp"]], on="provinsi", how="left")
    d["nilai"] = d["nilai_miliar_rp"] / 1000                      # miliar -> triliun
    d["kapita"] = d["pdrb_kapita_ribu_rp"] / 1000                 # ribu -> juta rupiah

    # penduduk tersirat = total PDRB / PDRB per kapita (agar rata-rata pulau dihitung benar)
    prov = d.groupby(["kelompok_pulau", "provinsi"], as_index=False).agg(
        nilai=("nilai", "sum"), kapita=("kapita", "first"))
    prov["penduduk"] = prov["nilai"] * 1e12 / (prov["kapita"] * 1e6)
    pulau = prov.groupby("kelompok_pulau", as_index=False).agg(nilai=("nilai", "sum"), penduduk=("penduduk", "sum"))
    pulau["kapita"] = pulau["nilai"] * 1e12 / pulau["penduduk"] / 1e6
    root_nilai = pulau["nilai"].sum()
    root_kapita = root_nilai * 1e12 / pulau["penduduk"].sum() / 1e6

    ids, labels, parents, values, kapita = [], [], [], [], []
    ids.append("Indonesia"); labels.append("Indonesia"); parents.append(""); values.append(root_nilai); kapita.append(root_kapita)
    for _, r in pulau.iterrows():
        ids.append(r.kelompok_pulau); labels.append(r.kelompok_pulau); parents.append("Indonesia")
        values.append(r.nilai); kapita.append(r.kapita)
    for _, r in prov.iterrows():
        ids.append(f"{r.kelompok_pulau}/{r.provinsi}"); labels.append(r.provinsi); parents.append(r.kelompok_pulau)
        values.append(r.nilai); kapita.append(r.kapita)
    for _, r in d.iterrows():
        ids.append(f"{r.kelompok_pulau}/{r.provinsi}/{r.sektor}"); labels.append(r.sektor)
        parents.append(f"{r.kelompok_pulau}/{r.provinsi}"); values.append(r.nilai); kapita.append(r.kapita)
    return dict(ids=ids, labels=labels, parents=parents, values=values, kapita=kapita)


HOVER = ("<b>%{label}</b><br>PDRB: Rp %{value:,.1f} triliun"
         "<br>Porsi dari induk: %{percentParent:.1%}"
         "<br>PDRB per kapita (provinsi/pulau): Rp %{customdata:.1f} juta<extra></extra>")


def pengaturan_warna(kapita):
    """Warna = PDRB per kapita pada skala logaritmik (sebaran sangat miring). Palet Viridis ramah buta warna."""
    tick_asli = [25, 50, 100, 200, 300]
    return dict(colors=np.log10(kapita), colorscale="Viridis", cmin=np.log10(20), cmax=np.log10(300),
                colorbar=dict(title="PDRB per kapita<br>(juta Rp, skala log)",
                              tickvals=np.log10(tick_asli), ticktext=[str(t) for t in tick_asli]))


def buat_treemap(n):
    fig = go.Figure(go.Treemap(
        ids=n["ids"], labels=n["labels"], parents=n["parents"], values=n["values"],
        branchvalues="total", maxdepth=3, customdata=n["kapita"], hovertemplate=HOVER,
        marker=pengaturan_warna(n["kapita"]), pathbar=dict(visible=True)))
    fig.update_layout(margin=dict(t=40, l=5, r=5, b=5), height=620,
                      uniformtext=dict(minsize=9, mode="hide"))
    return fig


def buat_sunburst(n):
    fig = go.Figure(go.Sunburst(
        ids=n["ids"], labels=n["labels"], parents=n["parents"], values=n["values"],
        branchvalues="total", maxdepth=3, customdata=n["kapita"], hovertemplate=HOVER,
        marker=pengaturan_warna(n["kapita"]), insidetextorientation="radial"))
    fig.update_layout(margin=dict(t=10, l=5, r=5, b=5), height=620)
    return fig


st.header("1. Di mana ekonomi Indonesia terkumpul?")
st.write("Besar kotak atau busur menunjukkan PDRB atas dasar harga berlaku, dan warna menunjukkan PDRB per kapita. "
         "**Klik** sebuah bagian untuk masuk ke tingkat di bawahnya (pulau, provinsi, lalu lapangan usaha). "
         "Pada treemap, klik jalur di atas grafik untuk kembali. Pada sunburst, klik lingkaran di tengah.")

node = siapkan_node(ind, pdrb)
tab1, tab2 = st.tabs(["Treemap", "Sunburst"])
with tab1:
    st.plotly_chart(buat_treemap(node), width="stretch", key="treemap")
    st.caption("Treemap memudahkan membandingkan luas (besar PDRB) antar provinsi.")
with tab2:
    st.plotly_chart(buat_sunburst(node), width="stretch", key="sunburst")
    st.caption("Sunburst memperlihatkan struktur tingkatan (pulau, provinsi, lapangan usaha) secara radial.")

st.caption("Sumber: BPS, PDRB Provinsi-Provinsi di Indonesia Menurut Lapangan Usaha 2020-2024 (Tabel 87) dan PDRB per Kapita ADHB, 2022. "
           "Nilai per lapangan usaha dihitung dari persen distribusi x total PDRB provinsi.")


# ---------------------------------------------------------------- 3. BAGIAN MULTIVARIAT
# kolom di CSV -> nama lengkap (untuk legenda/tabel) dan nama singkat (untuk sumbu grafik)
VARIABEL = {
    "ipm": "IPM (indeks)",
    "miskin_pct_mar2022": "Penduduk miskin (%)",
    "tpt_agu2022": "TPT (%)",
    "rls_15plus_th": "Rata-rata lama sekolah 15+ (tahun)",
    "uhh_rata2_lp": "UHH rata-rata L dan P (tahun)",
    "pengeluaran_kapita_ribu_rp": "Pengeluaran per kapita (ribu Rp)",
    "gini_mar2022": "Gini ratio",
    "sanitasi_layak_pct": "Sanitasi layak (%)",
    "air_minum_layak_pct": "Air minum layak (%)",
    "pdrb_kapita_ribu_rp": "PDRB per kapita (ribu Rp)",
}
SINGKAT = {"ipm": "IPM", "miskin_pct_mar2022": "Miskin (%)", "tpt_agu2022": "TPT (%)", "rls_15plus_th": "Lama sekolah",
           "uhh_rata2_lp": "UHH", "pengeluaran_kapita_ribu_rp": "Pengeluaran", "gini_mar2022": "Gini",
           "sanitasi_layak_pct": "Sanitasi (%)", "air_minum_layak_pct": "Air minum (%)", "pdrb_kapita_ribu_rp": "PDRB/kapita"}
PALET = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#56B4E9"]   # Okabe-Ito: ramah buta warna
ABU = "rgba(150,150,150,0.35)"


@st.cache_data
def analisis_multivariat(ind, k):
    """Standarisasi -> PCA (SVD) -> klaster hierarkis Ward. Juga urutan baris/kolom untuk heatmap terklaster."""
    X = ind[list(VARIABEL)].copy()
    X["pdrb_kapita_ribu_rp"] = np.log10(X["pdrb_kapita_ribu_rp"])          # sebaran miring -> log
    Z = (X - X.mean()) / X.std(ddof=0)                                       # z-score: tiap variabel setara
    U, S, Vt = np.linalg.svd(Z.values, full_matrices=False)
    varians = S ** 2 / (S ** 2).sum()
    skor, muatan = U[:, :2] * S[:2], Vt[:2].T
    if np.corrcoef(skor[:, 0], ind["ipm"])[0, 1] < 0:                         # tanda sumbu bebas; dibuat agar kanan = lebih maju
        skor[:, 0] *= -1
        muatan[:, 0] *= -1
    tree = linkage(Z.values, "ward")
    kl = fcluster(tree, k, "maxclust")
    urut = ind.groupby(kl)["ipm"].mean().sort_values(ascending=False).index.tolist()
    nama = {lama: f"Kelompok {i + 1}" for i, lama in enumerate(urut)}        # Kelompok 1 = IPM rata-rata tertinggi
    hasil = ind.copy()
    hasil["PC1"], hasil["PC2"] = skor[:, 0], skor[:, 1]
    hasil["kelompok"] = [nama[x] for x in kl]
    load = pd.DataFrame(muatan, index=[VARIABEL[v] for v in VARIABEL], columns=["PC1", "PC2"])
    # urutan heatmap: baris mengikuti pohon klaster; kolom diurutkan menurut kemiripan korelasi
    baris = leaves_list(tree)
    jarak_kol = squareform(1 - Z.corr().abs().values, checks=False)
    kolom = leaves_list(linkage(jarak_kol, "average"))
    return hasil, load, varians, Z.round(4), baris, kolom


def provinsi_dari_event(event, hasil):
    """Ambil nama provinsi dari titik yang diseleksi (brushing) pada scatter PCA."""
    try:
        titik = event.selection.points
    except Exception:
        return set()
    daftar = set(hasil["provinsi"])
    dipilih = set()
    for p in titik:
        cd = p.get("customdata") or []
        if cd and cd[0] in daftar:
            dipilih.add(cd[0])
        else:                                                              # cadangan: cocokkan lewat koordinat
            j = ((hasil["PC1"] - p["x"]) ** 2 + (hasil["PC2"] - p["y"]) ** 2).idxmin()
            dipilih.add(hasil.loc[j, "provinsi"])
    return dipilih


def buat_pca(hasil, varians, tampil_nama):
    urutan = sorted(hasil["kelompok"].unique())
    fig = px.scatter(
        hasil, x="PC1", y="PC2", color="kelompok", symbol="kelompok",
        category_orders={"kelompok": urutan}, color_discrete_sequence=PALET,
        text="provinsi" if tampil_nama else None, hover_name="provinsi", custom_data=["provinsi"],
        hover_data={"PC1": ":.2f", "PC2": ":.2f", "kelompok": False, "ipm": ":.2f",
                    "miskin_pct_mar2022": ":.2f", "pdrb_kapita_ribu_rp": ":,.0f"},
        labels={"PC1": f"PC1 ({varians[0] * 100:.1f}% varians): kanan = lebih maju",
                "PC2": f"PC2 ({varians[1] * 100:.1f}% varians)", "kelompok": "Kelompok",
                "ipm": "IPM", "miskin_pct_mar2022": "Miskin (%)", "pdrb_kapita_ribu_rp": "PDRB per kapita (ribu Rp)"})
    fig.update_traces(marker=dict(size=11, line=dict(width=0.5, color="white")), textposition="top center",
                      textfont=dict(size=10))
    fig.update_layout(height=560, margin=dict(t=10, l=5, r=5, b=5), legend=dict(orientation="h", y=-0.15),
                      dragmode="select")
    return fig


def buat_muatan(load):
    muat_long = load.reset_index(names="variabel").melt(id_vars="variabel", var_name="sumbu", value_name="muatan")
    fig = px.bar(muat_long, x="muatan", y="variabel", color="sumbu", barmode="group", orientation="h",
                 color_discrete_sequence=["#0072B2", "#E69F00"])
    fig.update_layout(height=520, margin=dict(t=10, l=5, r=5, b=5), yaxis_title=None, xaxis_title="Muatan",
                      legend=dict(orientation="h", y=-0.12, title=None))
    return fig


def buat_parallel(hasil, sorot):
    """Parallel coordinates: satu garis per provinsi. Tiap sumbu diskalakan min-maks (0-1); angka kecil = nilai asli.
    Jika ada provinsi tersorot (dari seleksi di scatter PCA), garis lain dipudarkan."""
    kolom = list(VARIABEL)
    mn, mx = hasil[kolom].min(), hasil[kolom].max()
    norm = (hasil[kolom] - mn) / (mx - mn)
    kelompok = sorted(hasil["kelompok"].unique())
    warna = {kel: PALET[i] for i, kel in enumerate(kelompok)}
    ada = len(sorot) > 0
    fig = go.Figure()
    urutan = [i for i in hasil.index if hasil.loc[i, "provinsi"] not in sorot] + \
             [i for i in hasil.index if hasil.loc[i, "provinsi"] in sorot]      # yang tersorot digambar terakhir (di atas)
    sudah = set()
    for i in urutan:
        prov, kel = hasil.loc[i, "provinsi"], hasil.loc[i, "kelompok"]
        pilih = prov in sorot
        redup = ada and not pilih
        fig.add_trace(go.Scatter(
            x=list(range(len(kolom))), y=norm.loc[i].values, mode="lines+text" if pilih else "lines",
            line=dict(color=ABU if redup else warna[kel], width=3.5 if pilih else (1 if redup else 1.8)),
            text=[""] * (len(kolom) - 1) + [prov] if pilih else None, textposition="middle right", textfont=dict(size=11),
            name=kel, legendgroup=kel, showlegend=kel not in sudah and not redup,
            customdata=[[SINGKAT[c], f"{hasil.loc[i, c]:,.2f}" if abs(hasil.loc[i, c]) < 1000 else f"{hasil.loc[i, c]:,.0f}"]
                        for c in kolom],
            hovertemplate=f"<b>{prov}</b> ({kel})<br>" + "%{customdata[0]}: %{customdata[1]}<extra></extra>"))
        if not redup:
            sudah.add(kel)
    for j, c in enumerate(kolom):                                              # nilai asli di ujung bawah dan atas sumbu
        fig.add_annotation(x=j, y=-0.04, text=f"{mn[c]:,.1f}" if mn[c] < 1000 else f"{mn[c]:,.0f}", showarrow=False,
                           font=dict(size=9, color="gray"), yanchor="top")
        fig.add_annotation(x=j, y=1.04, text=f"{mx[c]:,.1f}" if mx[c] < 1000 else f"{mx[c]:,.0f}", showarrow=False,
                           font=dict(size=9, color="gray"), yanchor="bottom")
    fig.update_xaxes(tickvals=list(range(len(kolom))), ticktext=[SINGKAT[c] for c in kolom], side="top",
                     showgrid=True, gridcolor="rgba(150,150,150,0.4)", range=[-0.3, len(kolom) - 0.2], fixedrange=True)
    fig.update_yaxes(visible=False, range=[-0.12, 1.12], fixedrange=True)
    fig.update_layout(height=520, margin=dict(t=60, l=5, r=120, b=30), legend=dict(orientation="h", y=-0.05, title=None))
    return fig


def buat_heatmap(hasil, Z, baris, kolom, sorot):
    """Heatmap terklaster: baris (provinsi) dan kolom (variabel) diurutkan menurut kemiripan. Warna = z-score."""
    prov_urut = hasil["provinsi"].values[baris]
    kol_urut = [list(VARIABEL)[j] for j in kolom]
    zm = Z.loc[:, kol_urut].values[baris]
    asli = hasil.loc[:, kol_urut].values[baris]
    ylabel = [f"{p} ({hasil.loc[hasil.provinsi == p, 'kelompok'].iloc[0].replace('Kelompok ', 'K')})" for p in prov_urut]
    fig = go.Figure(go.Heatmap(
        z=zm, x=[SINGKAT[c] for c in kol_urut], y=ylabel, zmid=0, zmin=-3, zmax=3, colorscale="RdBu_r",
        customdata=asli, colorbar=dict(title="z-score", tickvals=[-3, -2, -1, 0, 1, 2, 3]),
        hovertemplate="<b>%{y}</b><br>%{x}<br>z-score: %{z:.2f}<br>nilai asli: %{customdata:,.2f}<extra></extra>"))
    for i, p in enumerate(prov_urut):                                          # bingkai hitam pada provinsi tersorot
        if p in sorot:
            fig.add_shape(type="rect", x0=-0.5, x1=len(kol_urut) - 0.5, y0=i - 0.5, y1=i + 0.5,
                          line=dict(color="black", width=2.5))
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=10))
    fig.update_xaxes(side="top", tickangle=-30)
    fig.update_layout(height=700, margin=dict(t=70, l=5, r=5, b=5))
    return fig


st.header("2. Apakah provinsi dengan ekonomi besar juga lebih sejahtera?")
st.write("Sepuluh indikator pembangunan diringkas dengan **PCA** (analisis komponen utama) menjadi dua sumbu. "
         "Provinsi yang berdekatan di grafik punya profil yang mirip. Warna dan bentuk titik menunjukkan **kelompok** "
         "hasil klaster hierarkis (Ward); Kelompok 1 adalah kelompok dengan IPM rata-rata tertinggi.")

k = st.slider("Jumlah kelompok (klaster)", min_value=2, max_value=6, value=4)
hasil, load, varians, Z, baris, kolom = analisis_multivariat(ind, k)

kol_kiri, kol_kanan = st.columns([3, 2])
with kol_kiri:
    tampil_nama = st.checkbox("Tampilkan nama provinsi", value=True)
    st.caption("**Seleksi** titik dengan menyeret kotak atau lasso pada grafik (ikon di pojok kanan atas grafik). "
               "Provinsi yang dipilih akan tersorot di grafik-grafik di bawahnya. Klik dua kali area kosong untuk menghapus seleksi.")
    event = st.plotly_chart(buat_pca(hasil, varians, tampil_nama), width="stretch", key="pca",
                            on_select="rerun", selection_mode=("box", "lasso", "points"))
with kol_kanan:
    st.markdown("**Muatan (loading): variabel apa yang membentuk tiap sumbu?**")
    st.plotly_chart(buat_muatan(load), width="stretch", key="muatan")

tambahan = st.multiselect("Atau pilih provinsi untuk disorot secara manual", options=sorted(hasil["provinsi"]))
sorot = provinsi_dari_event(event, hasil) | set(tambahan)
if sorot:
    st.info("Provinsi tersorot: " + ", ".join(sorted(sorot)))

st.subheader("Profil lengkap tiap provinsi: parallel coordinates")
st.caption("Satu garis = satu provinsi. Tiap sumbu diskalakan dari nilai terendah (bawah) ke tertinggi (atas); "
           "angka kecil di ujung sumbu adalah nilai aslinya. Arahkan kursor pada garis untuk melihat nilainya.")
st.plotly_chart(buat_parallel(hasil, sorot), width="stretch", key="parallel")

st.subheader("Pola kemiripan: heatmap terklaster")
st.caption("Baris dan kolom diurutkan menurut kemiripan (klaster hierarkis), sehingga provinsi dan indikator yang mirip berdekatan. "
           "Merah = di atas rata-rata 34 provinsi, biru = di bawah rata-rata (z-score). Huruf K di samping nama = kelompok.")
st.plotly_chart(buat_heatmap(hasil, Z, baris, kolom, sorot), width="stretch", key="heatmap")

with st.expander("Rata-rata indikator tiap kelompok dan anggotanya"):
    rata = hasil.groupby("kelompok")[list(VARIABEL)].mean().rename(columns=VARIABEL).round(2)
    rata.insert(0, "Jumlah provinsi", hasil.groupby("kelompok").size())
    st.dataframe(rata, width="stretch")
    for kel in sorted(hasil["kelompok"].unique()):
        st.write(f"**{kel}:** " + ", ".join(hasil.loc[hasil["kelompok"] == kel, "provinsi"]))

st.caption("Sumber: BPS, 2022 (IPM, kemiskinan Maret, TPT Agustus, rata-rata lama sekolah, UHH, pengeluaran per kapita, "
           "Gini Maret, sanitasi dan air minum layak, PDRB per kapita). Semua variabel distandarkan (z-score); "
           "PDRB per kapita ditransformasi log10 sebelum PCA dan heatmap.")


# ---------------------------------------------------------------- 4. BAGIAN ALIRAN (MIGRASI)
PULAU_URUT = ["Sumatera", "Jawa", "Bali & Nusa Tenggara", "Kalimantan", "Sulawesi", "Maluku & Papua"]
PALET_PULAU = ["#88CCEE", "#CC6677", "#DDCC77", "#117733", "#332288", "#AA4499"]   # palet 'Safe' (CARTO), ramah buta warna
WARNA_PULAU = dict(zip(PULAU_URUT, PALET_PULAU))
BAKU = {"Kep. Bangka Belitung": "Kepulauan Bangka Belitung"}                          # penyeragaman nama provinsi


@st.cache_data
def muat_migrasi():
    od = pd.read_csv("data/processed/migrasi_risen_od_long.csv")
    for kol in ("provinsi_asal", "provinsi_tujuan"):
        od[kol] = od[kol].replace(BAKU)
    rasio = pd.read_csv("data/processed/migrasi_rasio_provinsi_2022.csv")
    rasio["provinsi"] = rasio["provinsi"].replace(BAKU)
    # aliran ANTARPROVINSI saja (tanpa migran dari luar negeri), dihitung dari matriks OD
    rasio = rasio.set_index("provinsi")
    rasio["migran_masuk"] = od.groupby("provinsi_tujuan")["jumlah"].sum().reindex(rasio.index)
    rasio["migran_keluar"] = od.groupby("provinsi_asal")["jumlah"].sum().reindex(rasio.index)
    rasio["neto_per1000"] = ((rasio["migran_masuk"] - rasio["migran_keluar"]) / rasio["penduduk_5plus"] * 1000).round(2)
    return od, rasio.reset_index()


def hex_ke_rgba(hex_, alpha):
    h = hex_.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


def buat_sankey(od, pulau_of, tingkat, asal_f, tujuan_f, top_n):
    """Sankey migrasi risen: kolom kiri = asal (Juni 2017), kolom kanan = tujuan (Juni 2022). Lebar pita = jumlah migran."""
    d = od.copy()
    if tingkat == "pulau":
        d["asal"], d["tujuan"] = d["provinsi_asal"].map(pulau_of), d["provinsi_tujuan"].map(pulau_of)
        d = d[d["asal"] != d["tujuan"]].groupby(["asal", "tujuan"], as_index=False)["jumlah"].sum()   # antar pulau saja
        kunci_pulau = lambda nama: nama
    else:
        if asal_f:
            d = d[d["provinsi_asal"].isin(asal_f)]
        if tujuan_f:
            d = d[d["provinsi_tujuan"].isin(tujuan_f)]
        d = d.nlargest(top_n, "jumlah").rename(columns={"provinsi_asal": "asal", "provinsi_tujuan": "tujuan"})
        kunci_pulau = lambda nama: pulau_of[nama]
    d = d[d["jumlah"] > 0]
    if d.empty:
        return None, d

    def urut(kolom):
        total = d.groupby(kolom)["jumlah"].sum()
        return sorted(total.index, key=lambda n: (PULAU_URUT.index(kunci_pulau(n)), -total[n]))

    asal_n, tujuan_n = urut("asal"), urut("tujuan")
    idx_a = {n: i for i, n in enumerate(asal_n)}
    idx_t = {n: i + len(asal_n) for i, n in enumerate(tujuan_n)}
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=asal_n + tujuan_n, pad=12, thickness=16, line=dict(color="white", width=0.5),
                  color=[WARNA_PULAU[kunci_pulau(n)] for n in asal_n + tujuan_n],
                  hovertemplate="%{label}<br>Total aliran: %{value:,.0f} orang<extra></extra>"),
        link=dict(source=[idx_a[a] for a in d["asal"]], target=[idx_t[t] for t in d["tujuan"]], value=d["jumlah"],
                  color=[hex_ke_rgba(WARNA_PULAU[kunci_pulau(a)], 0.5) for a in d["asal"]],
                  hovertemplate="%{source.label} \u2192 %{target.label}<br>%{value:,.0f} orang<extra></extra>")))
    fig.add_annotation(x=0, y=1.07, xref="paper", yref="paper", text="<b>ASAL</b> (tinggal Juni 2017)", showarrow=False, xanchor="left")
    fig.add_annotation(x=1, y=1.07, xref="paper", yref="paper", text="<b>TUJUAN</b> (tinggal Juni 2022)", showarrow=False, xanchor="right")
    fig.update_layout(height=480 if tingkat == "pulau" else 760, margin=dict(t=50, l=5, r=5, b=5))
    return fig, d


def buat_matriks_od(od, urutan, pulau_of, tampil, sorot):
    """Matriks asal-tujuan (OD). Baris = provinsi asal, kolom = provinsi tujuan, diurutkan per kelompok pulau."""
    mat = od.pivot(index="provinsi_asal", columns="provinsi_tujuan", values="jumlah").reindex(index=urutan, columns=urutan)
    keluar = mat.sum(axis=1)
    persen = mat.div(keluar, axis=0) * 100
    teks = np.empty(mat.shape, dtype=object)
    for i, a in enumerate(urutan):
        for j, t in enumerate(urutan):
            teks[i, j] = (f"<b>{a} \u2192 {t}</b><br>{mat.iloc[i, j]:,.0f} orang"
                          f"<br>{persen.iloc[i, j]:.1f}% dari migran keluar {a}") if i != j else f"{a} (tidak berpindah)"
    if tampil == "jumlah":
        z = np.log10(mat.where(mat > 0))
        zmin, zmax = float(np.nanmin(z.values)), float(np.nanmax(z.values))
        ticks = [v for v in (10, 100, 1000, 10000, 100000) if zmin <= np.log10(v) <= zmax]
        cb = dict(title="Jumlah migran<br>(skala log)", tickvals=np.log10(ticks), ticktext=[f"{t:,}" for t in ticks])
    else:
        z = persen.where(mat > 0)
        zmin, zmax = 0.0, float(np.nanpercentile(z.values, 97))
        cb = dict(title="% dari migran<br>keluar asal")
    fig = go.Figure(go.Heatmap(z=z.values, x=urutan, y=urutan, text=teks, hovertemplate="%{text}<extra></extra>",
                               zmin=zmin, zmax=zmax, colorscale="Cividis", colorbar=cb, xgap=0, ygap=0))
    batas = np.cumsum([sum(1 for p in urutan if pulau_of[p] == pl) for pl in PULAU_URUT])[:-1]   # garis pemisah pulau
    for b in batas:
        fig.add_shape(type="line", x0=b - 0.5, x1=b - 0.5, y0=-0.5, y1=len(urutan) - 0.5, line=dict(color="white", width=1.5))
        fig.add_shape(type="line", y0=b - 0.5, y1=b - 0.5, x0=-0.5, x1=len(urutan) - 0.5, line=dict(color="white", width=1.5))
    for p in sorot:                                                          # bingkai: baris = asal, kolom = tujuan
        i = urutan.index(p)
        fig.add_shape(type="rect", x0=-0.5, x1=len(urutan) - 0.5, y0=i - 0.5, y1=i + 0.5, line=dict(color="#D55E00", width=2))
        fig.add_shape(type="rect", y0=-0.5, y1=len(urutan) - 0.5, x0=i - 0.5, x1=i + 0.5, line=dict(color="#D55E00", width=2))
    fig.update_xaxes(side="top", tickangle=-90, tickfont=dict(size=9), title="Provinsi tujuan (tinggal Juni 2022)")
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=9), title="Provinsi asal (tinggal Juni 2017)")
    fig.update_layout(height=760, margin=dict(t=120, l=5, r=5, b=5))
    return fig


def buat_neto(rasio, hasil, sorot):
    """Batang migrasi neto per 1.000 penduduk 5+, diurutkan. Biru = penerima neto, oranye = pengirim neto."""
    d = rasio.merge(hasil[["provinsi", "kelompok"]], on="provinsi").sort_values("neto_per1000")
    teks = [f"<b>{r.provinsi}</b> ({r.kelompok})<br>Neto: {r.neto_per1000:+.1f} per 1.000 penduduk 5+"
            f"<br>Masuk dari provinsi lain: {r.migran_masuk:,.0f} | Keluar ke provinsi lain: {r.migran_keluar:,.0f}" for r in d.itertuples()]
    fig = go.Figure(go.Bar(
        x=d["neto_per1000"], y=d["provinsi"], orientation="h",
        marker=dict(color=["#0072B2" if v >= 0 else "#D55E00" for v in d["neto_per1000"]],
                    line=dict(color="black", width=[2.5 if p in sorot else 0 for p in d["provinsi"]])),
        hovertext=teks, hovertemplate="%{hovertext}<extra></extra>"))
    fig.update_layout(height=780, margin=dict(t=10, l=5, r=5, b=40), xaxis_title="Migrasi neto per 1.000 penduduk berumur 5+ tahun",
                      yaxis=dict(tickfont=dict(size=10)))
    return fig


od, rasio = muat_migrasi()
pulau_of = dict(zip(pdrb["provinsi"], pdrb["kelompok_pulau"]))
urutan_prov = sorted(hasil["provinsi"], key=lambda p: (PULAU_URUT.index(pulau_of[p]), p))

st.header("3. Ke mana orang berpindah?")
st.write("Migran risen adalah penduduk berumur 5 tahun ke atas yang lima tahun sebelum pencacahan (Juni 2017) tinggal di provinsi "
         "yang berbeda dengan tempat tinggalnya sekarang (Juni 2022). Lebar pita menunjukkan jumlah migran, dan warna pita "
         "menunjukkan kelompok pulau asal.")

tingkat_label = st.radio("Tingkat aliran", ["Antar kelompok pulau", "Antar provinsi (aliran terbesar)"], horizontal=True)
tingkat = "pulau" if tingkat_label.startswith("Antar kelompok") else "provinsi"
asal_f, tujuan_f, top_n = [], [], 30
if tingkat == "provinsi":
    c1, c2, c3 = st.columns(3)
    asal_f = c1.multiselect("Filter provinsi asal (kosong = semua)", options=urutan_prov)
    tujuan_f = c2.multiselect("Filter provinsi tujuan (kosong = semua)", options=urutan_prov)
    top_n = c3.slider("Tampilkan N aliran terbesar", min_value=10, max_value=80, value=30, step=5)

fig_sankey, d_sankey = buat_sankey(od, pulau_of, tingkat, asal_f, tujuan_f, top_n)
if fig_sankey is None:
    st.warning("Tidak ada aliran yang cocok dengan filter ini. Ubah atau kosongkan filter asal dan tujuan.")
else:
    st.plotly_chart(fig_sankey, width="stretch", key="sankey")
    if tingkat == "pulau":
        st.caption("Hanya perpindahan antar kelompok pulau yang ditampilkan; perpindahan antar provinsi dalam pulau yang sama tidak termasuk.")
    else:
        st.caption(f"Menampilkan {len(d_sankey)} aliran terbesar yang memenuhi filter, total {d_sankey['jumlah'].sum():,.0f} orang.")

st.subheader("Matriks asal-tujuan (OD)")
tampil_label = st.radio("Warna sel menunjukkan", ["Jumlah migran", "Persen dari migran keluar provinsi asal"], horizontal=True)
st.caption("Baris = provinsi asal, kolom = provinsi tujuan. Garis putih memisahkan kelompok pulau. "
           "Bingkai oranye menandai provinsi yang disorot di bagian 2 (sebagai asal pada baris dan sebagai tujuan pada kolom).")
st.plotly_chart(buat_matriks_od(od, urutan_prov, pulau_of, "jumlah" if tampil_label == "Jumlah migran" else "persen", sorot),
                width="stretch", key="od")

st.subheader("Siapa penerima dan pengirim migran netto?")
st.caption("Migrasi neto = migran masuk dari provinsi lain dikurangi migran keluar ke provinsi lain, dibagi penduduk berumur 5+ tahun, "
           "per 1.000 penduduk. Migran dari luar negeri tidak dihitung agar sejalan dengan Sankey dan matriks di atas.")
st.plotly_chart(buat_neto(rasio, hasil, sorot), width="stretch", key="neto")

ringkas = rasio.merge(hasil[["provinsi", "kelompok"]], on="provinsi").groupby("kelompok").agg(
    provinsi=("provinsi", "count"), penduduk=("penduduk_5plus", "sum"), masuk=("migran_masuk", "sum"), keluar=("migran_keluar", "sum"))
ringkas["Masuk per 1.000"] = (ringkas["masuk"] / ringkas["penduduk"] * 1000).round(1)
ringkas["Keluar per 1.000"] = (ringkas["keluar"] / ringkas["penduduk"] * 1000).round(1)
ringkas["Neto per 1.000"] = ((ringkas["masuk"] - ringkas["keluar"]) / ringkas["penduduk"] * 1000).round(1)
st.markdown("**Apakah orang berpindah ke provinsi yang lebih maju?** Ringkasan menurut kelompok dari bagian 2 "
            "(ikut berubah bila jumlah kelompok pada slider diubah):")
st.dataframe(ringkas.rename(columns={"provinsi": "Jumlah provinsi", "penduduk": "Penduduk 5+", "masuk": "Migran masuk",
                                     "keluar": "Migran keluar"}), width="stretch")

top = od.nlargest(1, "jumlah").iloc[0]
net = rasio.sort_values("neto_per1000")
st.info(f"Aliran antarprovinsi terbesar: **{top.provinsi_asal} \u2192 {top.provinsi_tujuan}** ({top.jumlah:,.0f} orang). "
        f"Penerima neto tertinggi per 1.000 penduduk: **{net.iloc[-1].provinsi}** ({net.iloc[-1].neto_per1000:+.1f}); "
        f"pengirim neto tertinggi: **{net.iloc[0].provinsi}** ({net.iloc[0].neto_per1000:+.1f}).")

st.caption("Sumber: BPS (2023), Statistik Migrasi Indonesia Hasil Long Form Sensus Penduduk 2020 (Tabel 5.3 dan 7); penduduk berumur 5+ tahun "
           "menurut migrasi risen, 2022. Data berasal dari sampel rumah tangga (dicacah Juni 2022), sehingga merupakan estimasi.")
