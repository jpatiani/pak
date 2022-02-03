"""
Konversi kode prodi

$Id. kode prodi
Date: 20210527
Author: jpatiani
"""

import pandas as pd

def cekAcronim(v):
    ac          = ""
    frasa       = v.split()
    if len(frasa) == 1:
        ac = frasa[0][:2].upper()
    else:
        for kata in frasa:
            ac = ac + kata[0].upper()
    return ac

c               = "/Users/jpatiani/Documents/Script/Data/Akademik/MahasiswaReguler-DitSTI.html"
tbl             = pd.read_html(c)
df              = tbl[0]
df.columns      = ["Kode","Nama"]
df.index        = df["Kode"].values
df["Akro"]      = df["Nama"].apply(cekAcronim)
df["Jenjang"]   = df['Kode'].apply(lambda v: "S1" if str(v)[0] == "1" else ("S2" if str(v)[0] == "2" else ("S3" if str(v)[0] == "3" else "Profesi")))

res             = df[["Nama","Akro","Jenjang"]].to_json("test.json","index",indent=4)
#results         = {}
#for key, df_gb in df.groupby("Kode Program Studi"):
#    results[key] = df_gb.to_dict('records')
