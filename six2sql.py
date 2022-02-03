"""
Konversi data yg didownload dari akademik@itb ke format sql

$Id. six2sql
Date: 20210527
Author: jpatiani

Input data yang digunakan berupa data html dari menu user dosen > Tugas Akhir > 
Daftar Mahasiswa
Data html dibaca dengan pandas
Data yang terbaca dipilih untuk kolom tertentu
Data dikonversi dalam bentuk sql
"""

import pandas as pd
import numpy as np
import sqlite3 as sq
import sys
from pathlib import Path
import json

def createConnection(db_file):
    """ create a database connection """
    conn = None
    try:
        conn = sq.connect(db_file)
        print(sq.version)
    except sq.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def cekAcronim(v):
    """ simple check prodi code. manual edit of the output needed """
    ac          = ""
    frasa       = v.split()
    if len(frasa) == 1:
        ac = frasa[0][:2].upper()
    else:
        for kata in frasa:
            ac = ac + kata[0].upper()
    return ac

def createCode():
    from urllib.request import urlopen
    from bs4 import BeautifulSoup as BS

    http    = ["GANTI DENGAN FILE HASIL DOWNLOAD DARI SIX"]
    soup    = BS(urlopen(http).read())
    optfak  = list(soup.find("select", id="fakultas").stripped_strings)
    optgrp  = soup.find_all('optgroup')

    s       = lambda v: "S1" if str(v)[0] == "1" else ("S2" if str(v)[0] == "2" else ("S3" if str(v)[0] == "3" else "Profesi"))

    code    = {}

    for i, j in zip(optfak,optgrp):
        for k in list(j.stripped_strings):
            kd  = k.split("-")
            if len(kd) == 2:
                code[kd[0].strip()] = {"Nama": kd[1].strip(), "Akro": cekAcronim(kd[1]), "Jenjang": s(kd[0]), "Fakultas": i}
            else:
                nm = ""
                for ii, kk in enumerate(kd):
                    if ii >= 1:
                        nm = nm + kk.lstrip()

                code[kd[0].strip()] = {"Nama": nm, "Akro": cekAcronim(nm), "Jenjang": s(kd[0]), "Fakultas": i}

    with open("code.json","w") as f:
        json.dump(code, f, indent=4)

def statusAdvisor(v, **kwargs):
    w   = kwargs.get("target", ["GANTI DENGAN NAMA YANG INGIN DIPROSES"])
    if v.find(w) == 0:
        stat    = "Utama"
    else:
        stat    = "Pendamping"
    return stat

def createJenjang(v, **kwargs):
    kode        = kwargs.get("kode")
    prodi       = str(v)[:3]

    jenjang     = kode[prodi]["Jenjang"]
    akro        = kode[prodi]["Akro"]
    faklts      = kode[prodi]["Fakultas"]
    txtJenjang  = jenjang + " " + akro + "-" + faklts
    return txtJenjang

# Usage
print(len(sys.argv))
if len(sys.argv) < 2:
    print(" Usage: python six2sql.py <SIXInput.html> [<output.sql>]")
    quit(2)
elif len(sys.argv) == 2:
    sqlOutput = "bimbingan.sql"
    print("Default sql file name will be used")
else:
    sqlOutput = sys.argv[2]
    print("Processing... please wait")

# Check dependence file
cFile       = "code.json"
cF          = Path(cFile)
if not cF.is_file():
    print("Generating prodi code database ......")
    createCode()

with open(cFile) as f:
    code = json.load(f)

sixInput        = sys.argv[1]
tbl             = pd.read_html(sixInput)
df              = tbl[0]
"""
struct: nama, angkatan, tahun lulus, status pembimbing, jenjang, judul
"""
whoami          = ["GANTI DENGAN NAMA YANG INGIN DIPROSES"]
df["Angkatan"]  = df["NIM"].apply(lambda v: "20"+str(v)[3:5])
df["Lulus"]     = df["Tanggal Sidang"].apply(lambda v: str(v)[-4:])
df["Status"]    = df["Pembimbing"].apply(statusAdvisor, target=whoami)
df["Jenjang"]   = df["NIM"].apply(createJenjang, kode=code)
df["Strata"]    = df['NIM'].apply(lambda v: "S1" if str(v)[0] == "1" else ("S2" if str(v)[0] == "2" else ("S3" if str(v)[0] == "3" else "Profesi")))


for i in df.groupby("Strata").groups.keys():
    df.groupby(["Strata"]).get_group(i)[["Nama","Angkatan","Lulus","Status","Jenjang","Judul"]]

# Save to sql file
db_file         = "test.db"
conn            = sq.connect(db_file)
c               = conn.cursor()
c.execute('CREATE TABLE S1 (Nama text, Angkatan number, Lulus number, Pembimbing text, Jenjang text, Judul text)')
c.commit()
df.groupby(["Strata"]).get_group("S1")[["Nama","Angkatan","Lulus","Status","Jenjang","Judul"]].to_sql('S1', conn, if_exists='replace', index=False)
conn.close()

