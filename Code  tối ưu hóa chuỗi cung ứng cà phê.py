import os
import csv
import pulp as pl
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, to_hex

# 2. Tap chi so
VungTrong = ['DakLak', 'LamDong', 'GiaLai','KonTum']           # Vung trong
NoiThuMua = ['BuonMaThuot', 'DiLin', 'Pleiku']                   # Noi thu mua (nha may)
CoSoRangXay = ['HCM', 'DaNang', 'HaiPhong', 'QuangNam','CanTho']     # Co so rang xay (kho phan phoi)
CuaHang = ['HaNoi', 'HCM_store', 'DaNang_store', 'DaLat', 'NhaTrang','CaMau']  # Cua hang
ThoiGian = [1, 2, 3]                                   # Thoi gian (thang)

# Doi ten thanh cac tap chi so thong dung
G = VungTrong
S = NoiThuMua
P = CoSoRangXay
R = CuaHang
T = ThoiGian

# 3.Tham so_gan gia tri thuc te (don vi: kg cho khoi luong, nghin dong cho chi phi)

#Chi phi van chuyen(nghìn dong/ tan) vung trong->thu mua
chi_phi_gs = {
    ('DakLak','BuonMaThuot'): 9500,
    ('DakLak','DiLin'): 11000,
    ('DakLak','Pleiku'): 10500,
    ('LamDong','BuonMaThuot'): 10000,
    ('LamDong','DiLin'): 12000,
    ('LamDong','Pleiku'): 11500,
    ('GiaLai','BuonMaThuot'): 10000,
    ('GiaLai','DiLin'): 10500,
    ('GiaLai','Pleiku'): 9500,
    ('KonTum','BuonMaThuot'): 11500,
    ('KonTum','DiLin'): 12500,
    ('KonTum','Pleiku'): 9000,
}

#Chi phi van chuyen thu mua->rang xay
chi_phi_sp = {
    ('BuonMaThuot','HCM'): 4500,
    ('BuonMaThuot','DaNang'): 7000,
    ('BuonMaThuot','QuangNam'): 7200,
    ('BuonMaThuot','HaiPhong'): 15000,
    ('BuonMaThuot','CanTho'): 5000,
    ('DiLin','HCM'): 4800,
    ('DiLin','DaNang'): 6800,
    ('DiLin','QuangNam'): 7100,
    ('DiLin','HaiPhong'): 14800,
    ('DiLin','CanTho'): 5200,
    ('Pleiku','HCM'): 5000,
    ('Pleiku','DaNang'): 6500,
    ('Pleiku','QuangNam'): 6800,
    ('Pleiku','HaiPhong'): 14500,
    ('Pleiku','CanTho'): 5500,
}

#Chi phi van chuyen rang xay-> cua hang
chi_phi_pr = {
    ('HCM','HaNoi'): 12000,
    ('HCM','HCM_store'): 3000,
    ('HCM','DaNang_store'): 7500,
    ('HCM','DaLat'): 14000,
    ('HCM','NhaTrang'): 13000,
    ('HCM','CaMau'): 15000,
    ('DaNang','HaNoi'): 9000,
    ('DaNang','HCM_store'): 7200,
    ('DaNang','DaNang_store'): 3500,
    ('DaNang','DaLat'): 6500,
    ('DaNang','NhaTrang'): 6300,
    ('DaNang','CaMau'): 14000,
    ('HaiPhong','HaNoi'): 2000,
    ('HaiPhong','HCM_store'): 11000,
    ('HaiPhong','DaNang_store'): 8500,
    ('HaiPhong','DaLat'): 12000,
    ('HaiPhong','NhaTrang'): 11500,
    ('HaiPhong','CaMau'): 16000,
    ('QuangNam','HaNoi'): 8800,
    ('QuangNam','HCM_store'): 7400,
    ('QuangNam','DaNang_store'): 3600,
    ('QuangNam','DaLat'): 6700,
    ('QuangNam','NhaTrang'): 6500,
    ('QuangNam','CaMau'): 14500,
    ('CanTho','HaNoi'): 14000,
    ('CanTho','HCM_store'): 4000,
    ('CanTho','DaNang_store'): 8000,
    ('CanTho','DaLat'): 14500,
    ('CanTho','NhaTrang'): 12000,
    ('CanTho','CaMau'): 3000,
}

#Chi phi san xuat tai noi thu mua
chi_phi_san_xuat = {
    ('BuonMaThuot', 1): 21000,
    ('BuonMaThuot', 2): 19500,
    ('BuonMaThuot', 3): 20000,
    ('DiLin', 1): 20500,
    ('DiLin', 2): 19800,
    ('DiLin', 3): 20200,
    ('Pleiku', 1): 20800,
    ('Pleiku', 2): 19700,
    ('Pleiku', 3): 20100,
}

# Nhu cau cua cua hang theo thoi gian tinh bang kg
nhu_cau = {
    ('HaNoi', 1): 94500,
    ('HaNoi', 2): 88200,
    ('HaNoi', 3): 91800,
    ('HCM_store', 1): 99000,
    ('HCM_store', 2): 103500,
    ('HCM_store', 3): 97200,
    ('DaNang_store', 1): 64800,
    ('DaNang_store', 2): 67500,
    ('DaNang_store', 3): 65700,
    ('DaLat', 1): 46800,
    ('DaLat', 2): 43200,
    ('DaLat', 3): 45000,
    ('NhaTrang', 1): 40500,
    ('NhaTrang', 2): 42300,
    ('NhaTrang', 3): 41400,
    ('CaMau', 1): 36000,
    ('CaMau', 2): 37800,
    ('CaMau', 3): 36900,
}

#Chi phi luu kho(nghin dong/tan/thang)
chi_phi_luu_kho_s = {
    ('BuonMaThuot', 1): 1100,
    ('BuonMaThuot', 2): 1000,
    ('BuonMaThuot', 3): 1050,
    ('DiLin', 1): 1000,
    ('DiLin', 2): 950,
    ('DiLin', 3): 1000,
    ('Pleiku', 1): 1050,
    ('Pleiku', 2): 980,
    ('Pleiku', 3): 1020,
}

chi_phi_luu_kho_p = {
    ('HCM', 1): 1300,
    ('HCM', 2): 1200,
    ('HCM', 3): 1250,
    ('DaNang', 1): 1150,
    ('DaNang', 2): 1100,
    ('DaNang', 3): 1120,
    ('HaiPhong', 1): 1200,
    ('HaiPhong', 2): 1150,
    ('HaiPhong', 3): 1180,
    ('QuangNam', 1): 1280,
    ('QuangNam', 2): 1230,
    ('QuangNam', 3): 1250,
    ('CanTho', 1): 1250,
    ('CanTho', 2): 1200,
    ('CanTho', 3): 1220,
}

chi_phi_luu_kho_r = {
    ('HaNoi', 1): 1600,
    ('HaNoi', 2): 1500,
    ('HaNoi', 3): 1550,
    ('HCM_store', 1): 1400,
    ('HCM_store', 2): 1350,
    ('HCM_store', 3): 1380,
    ('DaNang_store', 1): 1450,
    ('DaNang_store', 2): 1400,
    ('DaNang_store', 3): 1420,
    ('DaLat', 1): 1550,
    ('DaLat', 2): 1500,
    ('DaLat', 3): 1520,
    ('NhaTrang', 1): 1500,
    ('NhaTrang', 2): 1480,
    ('NhaTrang', 3): 1490,
    ('CaMau', 1): 1450,
    ('CaMau', 2): 1420,
    ('CaMau', 3): 1430,
}

# Cong suat toi da
cong_suat_s = {
    'BuonMaThuot': 480000,
    'DiLin': 450000,
    'Pleiku': 460000,
}

cong_suat_p = {
    'HCM': 420000,
    'DaNang': 400000,
    'HaiPhong': 380000,
    'QuangNam': 410000,
    'CanTho': 390000,
}

# San luong vung trong
san_luong = {
    ('DakLak', 1): 200000,
    ('DakLak', 2): 180000,
    ('DakLak', 3): 190000,
    ('LamDong', 1): 150000,
    ('LamDong', 2): 140000,
    ('LamDong', 3): 145000,
    ('GiaLai', 1): 160000,
    ('GiaLai', 2): 155000,
    ('GiaLai', 3): 158000,
    ('KonTum', 1): 120000,
    ('KonTum', 2): 115000,
    ('KonTum', 3): 118000,
}

# Chi phi lang phi
chi_phi_lang_phi_g = 5000
chi_phi_lang_phi_s = 10000
chi_phi_lang_phi_p = 15000

# Ty le hao hut
ty_le_hao_hut_s = {
    'BuonMaThuot': 0.06,
    'DiLin': 0.05,
    'Pleiku': 0.055
}

ty_le_hao_hut_p = {
    'HCM': 0.12,
    'DaNang': 0.11,
    'HaiPhong': 0.10,
    'QuangNam': 0.10,
    'CanTho': 0.115
}

# 4. Tao mo hinh
model = pl.LpProblem("Toi_uu_hoa_chuoi_cung_ung_ca_phe", pl.LpMinimize)

# 5. Khai bao bien
x = pl.LpVariable.dicts("x", ((g,s,t) for g in VungTrong for s in NoiThuMua for t in ThoiGian), lowBound=0)
y = pl.LpVariable.dicts("y", ((s,p,t) for s in NoiThuMua for p in CoSoRangXay for t in ThoiGian), lowBound=0)
z = pl.LpVariable.dicts("z", ((p,r,t) for p in CoSoRangXay for r in CuaHang for t in ThoiGian), lowBound=0)
I_s = pl.LpVariable.dicts("I_s", ((s,t) for s in NoiThuMua for t in ThoiGian), lowBound=0)
I_p = pl.LpVariable.dicts("I_p", ((p,t) for p in CoSoRangXay for t in ThoiGian), lowBound=0)
I_r = pl.LpVariable.dicts("I_r", ((r,t) for r in CuaHang for t in ThoiGian), lowBound=0)

# Bien lang phi
waste_g = pl.LpVariable.dicts("waste_g", ((g,t) for g in VungTrong for t in ThoiGian), lowBound=0)  # Lãng phí tại vùng trồng
waste_s = pl.LpVariable.dicts("waste_s", ((s,t) for s in NoiThuMua for t in ThoiGian), lowBound=0)  # Lãng phí tại nơi thu mua
waste_p = pl.LpVariable.dicts("waste_p", ((p,t) for p in CoSoRangXay for t in ThoiGian), lowBound=0) # Lãng phí tại cơ sở rang xay

# 6. Ham muc tieu: toi thieu tong chi phi(bao gom ca chi phi lang phi)
model += (
    pl.lpSum(chi_phi_gs[g,s]*x[g,s,t]/1000 for g in VungTrong for s in NoiThuMua for t in ThoiGian) +   # Chia 1000 vi chi phi tren tan, x la kg
    pl.lpSum(chi_phi_sp[s,p]*y[s,p,t]/1000 for s in NoiThuMua for p in CoSoRangXay for t in ThoiGian) +
    pl.lpSum(chi_phi_pr[p,r]*z[p,r,t]/1000 for p in CoSoRangXay for r in CuaHang for t in ThoiGian) +
    pl.lpSum(chi_phi_san_xuat[s,t]*pl.lpSum(x[g,s,t] for g in VungTrong)/1000 for s in NoiThuMua for t in ThoiGian) +
    pl.lpSum(chi_phi_luu_kho_s[s,t]*I_s[s,t]/1000 for s in NoiThuMua for t in ThoiGian) +
    pl.lpSum(chi_phi_luu_kho_p[p,t]*I_p[p,t]/1000 for p in CoSoRangXay for t in ThoiGian) +
    pl.lpSum(chi_phi_luu_kho_r[r,t]*I_r[r,t]/1000 for r in CuaHang for t in ThoiGian) +
    pl.lpSum(chi_phi_lang_phi_g * waste_g[g,t]/1000 for g in VungTrong for t in ThoiGian) +  # Chi phí lãng phí tại vùng trồng
    pl.lpSum(chi_phi_lang_phi_s * waste_s[s,t]/1000 for s in NoiThuMua for t in ThoiGian) +  # Chi phí lãng phí tại nơi thu mua
    pl.lpSum(chi_phi_lang_phi_p * waste_p[p,t]/1000 for p in CoSoRangXay for t in ThoiGian)   # Chi phí lãng phí tại cơ sở rang xay
)

# 7. Rang buoc
# 7.1. Can bang hang hoa tai vung trong(bao gom lang phi)
for g in VungTrong:
    for t in ThoiGian:
        model += pl.lpSum(x[g,s,t] for s in NoiThuMua) + waste_g[g,t] == san_luong[g,t], f"can_bang_vung_trong_{g}_{t}"

# 7.2. Can bang hang hoa tai noi thu mua(bao gom lang phi)
for s in NoiThuMua:
    for t in ThoiGian:
        nhap = pl.lpSum(x[g,s,t] for g in VungTrong)
        xuat = pl.lpSum(y[s,p,t] for p in CoSoRangXay)
        ton_truoc = I_s[s,t-1] if t > 1 else 0
        model += waste_s[s, t] >= 0.9 * ty_le_hao_hut_s[s] * nhap
        model += waste_s[s, t] <= 1.1 * ty_le_hao_hut_s[s] * nhap
        model += nhap + ton_truoc == xuat + I_s[s,t] + waste_s[s,t], f"can_bang_nha_may_{s}_{t}"

# 7.3. Can bang hang hoa tai co so rang xay (bao gom lang phi)
for p in CoSoRangXay:
    for t in ThoiGian:
        nhap = pl.lpSum(y[s,p,t] for s in NoiThuMua)
        xuat = pl.lpSum(z[p,r,t] for r in CuaHang)
        ton_truoc = I_p[p,t-1] if t > 1 else 0
        model += waste_p[p, t] >= 0.9 * ty_le_hao_hut_p[p] * nhap
        model += waste_p[p, t] <= 1.1 * ty_le_hao_hut_p[p] * nhap

        model += nhap + ton_truoc == xuat + I_p[p,t] + waste_p[p,t], f"can_bang_kho_{p}_{t}"

# 7.4 Can bang hang hoa tai cua hang
for r in CuaHang:
    for t in ThoiGian:
        nhap = pl.lpSum(z[p,r,t] for p in CoSoRangXay)
        ton_truoc = I_r[r,t-1] if t > 1 else 0
        model += nhap + ton_truoc == nhu_cau[r,t] + I_r[r,t], f"can_bang_cua_hang_{r}_{t}"

# 7.5 Rang buoc cong suat noi thu mua
for s in NoiThuMua:
    for t in ThoiGian:
        model += pl.lpSum(x[g,s,t] for g in VungTrong) <= cong_suat_s[s], f"cs_nha_may_{s}_{t}"

# 7.6 Rang buoc cong suat rang xay
for p in CoSoRangXay:
    for t in ThoiGian:
        model += pl.lpSum(y[s,p,t] for s in NoiThuMua) <= cong_suat_p[p], f"cs_kho_{p}_{t}"

# 7.7 Rang buoc phan phoi dong deu cho noi thu mua
for s in S:
    tong_luong_s = pl.lpSum(x[g, s, t] for g in G for t in T)
    avg_s = pl.lpSum(x[g, ss, t] for g in G for ss in S for t in T) / len(S)
    model += tong_luong_s >= 0.5 * avg_s, f"Rang_buoc_min_s_{s}"
    model += tong_luong_s <= 1.5 * avg_s, f"Rang_buoc_max_s_{s}"

# 7.8 Rang buoc phan phoi dong deu cho co so rang xay
for p in P:
    tong_luong_p = pl.lpSum(y[s, p, t] for s in S for t in T)
    avg_p = pl.lpSum(y[s, pp, t] for s in S for pp in P for t in T) / len(P)
    model += tong_luong_p >= 0.8 * avg_p, f"Rang_buoc_min_p_{p}"
    model += tong_luong_p <= 1.2 * avg_p, f"Rang_buoc_max_p_{p}"

# 7.9 Rang buoc phan phoi dong deu cho cua hang ban le
for r in R:
    tong_luong_r = pl.lpSum(z[p, r, t] for p in P for t in T)
    avg_r = pl.lpSum(z[p, rr, t] for p in P for rr in R for t in T) / len(R)
    model += tong_luong_r >= 0.8 * avg_r, f"Rang_buoc_min_r_{r}"
    model += tong_luong_r <= 1.2 * avg_r, f"Rang_buoc_max_r_{r}"

# 8. Giai mo hinh
model.solve()

# 9. In ket qua
print("=== KET QUA TOI UU HOA ===")
print("Trang Thai:", pl.LpStatus[model.status])
print("Gia tri muc tieu (nghin dong):", round(pl.value(model.objective), 3))

# 10. In chi tiet ket qua cac bien quyet dinh(dang bang, lam tron)
import pandas as pd
print("\nChi tiet ket qua cac bien quyet dinh (chi in gia tri >= 0):\n")

def in_ket_qua_bien(variables, mo_ta):
    du_lieu = [
        (*key, round(var.varValue, 2))
        for key, var in variables.items()
        if var.varValue is not None and var.varValue >= 0
    ]

    if du_lieu:
        so_chieu = len(du_lieu[0]) - 1  # số chiều khóa
        ten_cot_mac_dinh = ["g", "s", "p", "r", "t"]
        ten_cot = ten_cot_mac_dinh[:so_chieu] + ["Gia tri"]

        df = pd.DataFrame(du_lieu, columns=ten_cot)
        print(f"\n-- {mo_ta} --")
        print(df.to_string(index=False))
    else:
        print(f"\n-- {mo_ta} --")
        print("Không có biến nào có giá trị >= 0")

# 11. In tat ca cac bien
in_ket_qua_bien(x, "Luong van chuyen tu Vung Trong -> Noi Thu Mua (x[g,s,t])_Tinh bang kg")
in_ket_qua_bien(y, "Luong van chuyen tu Noi Thu Mua -> Rang Xay (y[s,p,t])_Tinh bang kg")
in_ket_qua_bien(z, "Luong van chuyen tu Rang Xay -> Cua Hang (z[p,r,t])_Tinh bang kg")
in_ket_qua_bien(I_s, "Ton kho tai Noi Thu Mua (I_s[s,t])_Tinh bang kg")
in_ket_qua_bien(I_p, "Ton kho tai Co so Rang Xay (I_p[p,t])_Tinh bang kg")
in_ket_qua_bien(I_r, "Ton kho tai Cua Hang (I_r[r,t])_Tinh bang kg")
in_ket_qua_bien(waste_g, "Lang phi tai Vung Trong (waste_g[g,t])_Tinh bang kg")
in_ket_qua_bien(waste_s, "Lang phi tai Noi Thu Mua (waste_s[s,t])_Tinh bang kg")
in_ket_qua_bien(waste_p, "Lang phi tai Co so Rang Xay (waste_p[p,t])_Tinh bang kg")

# 12. In bang chi phi
print("\n=== BANG CHI PHI (nghin dong) ===")

print("1. Van chuyen vung trong → thu mua:",
    round(sum(chi_phi_gs[g, s] * x[g, s, t].varValue / 1000
              for g in G for s in S for t in T if x[g, s, t].varValue), 3))

print("2. Van chuyen thu mua → rang xay:",
    round(sum(chi_phi_sp[s, p] * y[s, p, t].varValue / 1000
              for s in S for p in P for t in T if y[s, p, t].varValue), 3))

print("3. Van chuyen rang xay → cua hang:",
    round(sum(chi_phi_pr[p, r] * z[p, r, t].varValue / 1000
              for p in P for r in R for t in T if z[p, r, t].varValue), 3))

print("4. Chi phi san xuat tai noi thu mua:",
    round(sum(chi_phi_san_xuat[s, t] * sum(
        x[g, s, t].varValue for g in G if x[g, s, t].varValue) / 1000
              for s in S for t in T), 3))

print("5. Luu kho tai noi thu mua:",
    round(sum(chi_phi_luu_kho_s[s, t] * I_s[s, t].varValue / 1000
              for s in S for t in T if I_s[s, t].varValue), 3))

print("6. Luu kho tai co so rang xay:",
    round(sum(chi_phi_luu_kho_p[p, t] * I_p[p, t].varValue / 1000
              for p in P for t in T if I_p[p, t].varValue), 3))

print("7. Luu kho tai cua hang:",
    round(sum(chi_phi_luu_kho_r[r, t] * I_r[r, t].varValue / 1000
              for r in R for t in T if I_r[r, t].varValue), 3))

print("8. Lang phi tai vung trong:",
    round(sum(chi_phi_lang_phi_g * waste_g[g, t].varValue / 1000
              for g in G for t in T if waste_g[g, t].varValue), 3))

print("9. Lang phi tai diem thu mua:",
    round(sum(chi_phi_lang_phi_s * waste_s[s, t].varValue / 1000
              for s in S for t in T if waste_s[s, t].varValue), 3))

print("10. Lang phi tai rang xay:",
    round(sum(chi_phi_lang_phi_p * waste_p[p, t].varValue / 1000
              for p in P for t in T if waste_p[p, t].varValue), 3))

tong_cp = (
    sum(chi_phi_gs[g, s] * x[g, s, t].varValue / 1000
        for g in G for s in S for t in T if x[g, s, t].varValue) +
    sum(chi_phi_sp[s, p] * y[s, p, t].varValue / 1000
        for s in S for p in P for t in T if y[s, p, t].varValue) +
    sum(chi_phi_pr[p, r] * z[p, r, t].varValue / 1000
        for p in P for r in R for t in T if z[p, r, t].varValue) +
    sum(chi_phi_san_xuat[s, t] * sum(
        x[g, s, t].varValue for g in G if x[g, s, t].varValue) / 1000
        for s in S for t in T) +
    sum(chi_phi_luu_kho_s[s, t] * I_s[s, t].varValue / 1000
        for s in S for t in T if I_s[s, t].varValue) +
    sum(chi_phi_luu_kho_p[p, t] * I_p[p, t].varValue / 1000
        for p in P for t in T if I_p[p, t].varValue) +
    sum(chi_phi_luu_kho_r[r, t] * I_r[r, t].varValue / 1000
        for r in R for t in T if I_r[r, t].varValue) +
    sum(chi_phi_lang_phi_g * waste_g[g, t].varValue / 1000
        for g in G for t in T if waste_g[g, t].varValue) +
    sum(chi_phi_lang_phi_s * waste_s[s, t].varValue / 1000
        for s in S for t in T if waste_s[s, t].varValue) +
    sum(chi_phi_lang_phi_p * waste_p[p, t].varValue / 1000
        for p in P for t in T if waste_p[p, t].varValue)
)

#13. In tong luong ca phe luu kho
print("\n=== TONG LUONG CA PHE LUU KHO (kg) ===")

tong_I_s = sum(I_s[s, t].varValue for s in S for t in T if I_s[s, t].varValue)
tong_I_p = sum(I_p[p, t].varValue for p in P for t in T if I_p[p, t].varValue)
tong_I_r = sum(I_r[r, t].varValue for r in R for t in T if I_r[r, t].varValue)

print(f"1. Tai noi thu mua (I_s): {round(tong_I_s, 2)} kg")
print(f"2. Tai co so rang xay (I_p): {round(tong_I_p, 2)} kg")
print(f"3. Tai cua hang (I_r): {round(tong_I_r, 2)} kg")

print(f"\nTong cong kiem tra lai: {round(tong_cp, 3)} nghin dong")
print(f"So sanh voi model.objective: {round(pl.value(model.objective), 3)} nghin dong")


#14. Ve bieu do chi phi
#14.1. Tinh toan tung khoan chi phi
chi_phi_items = [
    ("VC Trong→Thu mua", sum(chi_phi_gs[g, s] * x[g, s, t].varValue / 1000
                             for g in G for s in S for t in T if x[g, s, t].varValue)),
    ("VC Thu mua→Rang xay", sum(chi_phi_sp[s, p] * y[s, p, t].varValue / 1000
                                for s in S for p in P for t in T if y[s, p, t].varValue)),
    ("VC Rang xay→Cua hang", sum(chi_phi_pr[p, r] * z[p, r, t].varValue / 1000
                                 for p in P for r in R for t in T if z[p, r, t].varValue)),
    ("San xuat tai Thu mua", sum(chi_phi_san_xuat[s, t] * sum(
                                 x[g, s, t].varValue for g in G if x[g, s, t].varValue) / 1000
                                 for s in S for t in T)),
    ("Luu kho Thu mua", sum(chi_phi_luu_kho_s[s, t] * I_s[s, t].varValue / 1000
                            for s in S for t in T if I_s[s, t].varValue)),
    ("Luu kho Rang xay", sum(chi_phi_luu_kho_p[p, t] * I_p[p, t].varValue / 1000
                             for p in P for t in T if I_p[p, t].varValue)),
    ("Luu kho Cua hang", sum(chi_phi_luu_kho_r[r, t] * I_r[r, t].varValue / 1000
                             for r in R for t in T if I_r[r, t].varValue)),
    ("Lang phi tai Trong", sum(chi_phi_lang_phi_g * waste_g[g, t].varValue / 1000
                               for g in G for t in T if waste_g[g, t].varValue)),
    ("Lang phi tai Thu mua", sum(chi_phi_lang_phi_s * waste_s[s, t].varValue / 1000
                                 for s in S for t in T if waste_s[s, t].varValue)),
    ("Lang phi tai Rang xay", sum(chi_phi_lang_phi_p * waste_p[p, t].varValue / 1000
                                  for p in P for t in T if waste_p[p, t].varValue)),
]

#14.2. Tach ten va gia tri
labels, values = zip(*chi_phi_items)

#14.3 Gop cac chi phi nho <5% thanh "Khac"
threshold_pct = 5

total = sum(values)
labels_large = []
values_large = []
labels_small = []
values_small = []

for label, value in zip(labels, values):
    pct = value / total * 100
    if pct >= threshold_pct:
        labels_large.append(label)
        values_large.append(value)
    else:
        labels_small.append(label)
        values_small.append(value)

# Them muc "Khac"
if values_small:
    labels_large.append("Khác")
    values_large.append(sum(values_small))

# 14.4. Ve bieu do tron
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    values_large,
    labels=labels_large,
    autopct=lambda pct: f'{pct:.1f}%\n({pct * sum(values_large) / 100:.0f}k)',
    startangle=90,
    pctdistance=0.85,
    wedgeprops=dict(width=0.4, edgecolor='w')
)

# 14.5. Them ghi chu cho muc "Khac"
if labels_small:
    chi_tiet_khac = '\n'.join([f'• {label}' for label in labels_small])
    ax.text(1.2, -1.2, f"Khac gom:\n{chi_tiet_khac}",
            ha='left', va='top', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='black'))

#14.6.Tieu de va hien thi
ax.set_title("Co cau chi phi trong chuoi cung ung ca phe (nghin dong)", fontsize=14)
plt.tight_layout()
plt.show()

#15. Ve luong phan bo hang hoa
# 15.1. Ham tao bo cuc voi gian cach vua phai va duong noi gon hon
def get_pos_by_layer_dynamic(G_list, S_list, P_list, R_list, x_spacing=2.2):
    pos = {}
    max_len = max(len(G_list), len(S_list), len(P_list), len(R_list))

    def assign(layer_list, x_layer):
        step = 10 / max(len(layer_list), 1)
        return {name: (x_layer * x_spacing, -i * step) for i, name in enumerate(layer_list)}

    pos.update(assign(G_list, 0))
    pos.update(assign(S_list, 1))
    pos.update(assign(P_list, 2))
    pos.update(assign(R_list, 3))
    return pos

# 15.2. Lay du lieu flow tu bien x, y, z theo thang
flow_x_by_t = defaultdict(dict)
flow_y_by_t = defaultdict(dict)
flow_z_by_t = defaultdict(dict)

for (g, s, t), var in x.items():
    if var.varValue is not None and var.varValue > 0:
        flow_x_by_t[t][(g, s)] = round(var.varValue, 2)
for (s, p, t), var in y.items():
    if var.varValue is not None and var.varValue > 0:
        flow_y_by_t[t][(s, p)] = round(var.varValue, 2)
for (p, r, t), var in z.items():
    if var.varValue is not None and var.varValue > 0:
        flow_z_by_t[t][(p, r)] = round(var.varValue, 2)

# 15.3. Ve so do theo tung thang
for t in T:
    flow_data = {}
    flow_data.update(flow_x_by_t[t])
    flow_data.update(flow_y_by_t[t])
    flow_data.update(flow_z_by_t[t])

    G_flow = nx.DiGraph()
    for (u, v), w in flow_data.items():
        G_flow.add_edge(u, v, weight=w)

    pos = get_pos_by_layer_dynamic(G, S, P, R, x_spacing=2.2)

    plt.figure(figsize=(20, 11))
    nx.draw_networkx_nodes(G_flow, pos, node_size=3000, node_color='lightyellow', edgecolors='black')
    nx.draw_networkx_labels(G_flow, pos, font_size=11, font_weight='bold')
    nx.draw_networkx_edges(G_flow, pos, arrows=True, width=1.2, connectionstyle='arc3,rad=0.05')

    edge_labels = {(u, v): f"{w:,.0f}" for (u, v), w in flow_data.items()}
    nx.draw_networkx_edge_labels(
        G_flow,
        pos,
        edge_labels=edge_labels,
        font_size=10,
        label_pos=0.52,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.85),
    )

    plt.title(f"Luong phan phoi hang theo thang {t} (G → S → P → R)", fontsize=16, weight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# 15.3.Ve so do van chuyen (tấn, triệu, tỷ)
from collections import defaultdict

# === 1. Tong luong van chuyen ===
flow_all = defaultdict(float)
for (g, s, t), var in x.items():
    if var.varValue:
        flow_all[(g, s)] += var.varValue
for (s, p, t), var in y.items():
    if var.varValue:
        flow_all[(s, p)] += var.varValue
for (p, r, t), var in z.items():
    if var.varValue:
        flow_all[(p, r)] += var.varValue

# === 2. Tính chi phí khac: lang phi + san xuat + luu kho ===
chi_phi_khac = defaultdict(float)
ton_kho_nut = defaultdict(float)

# G:
for g in G:
    for t in T:
        if waste_g[g, t].varValue:
            chi_phi_khac[g] += waste_g[g, t].varValue * chi_phi_lang_phi_g / 1000

# S:
for s in S:
    for t in T:
        if waste_s[s, t].varValue:
            chi_phi_khac[s] += waste_s[s, t].varValue * chi_phi_lang_phi_s / 1000
        chi_phi_khac[s] += sum(
            x[g, s, t].varValue * chi_phi_san_xuat[s, t] / 1000
            for g in G if x[g, s, t].varValue
        )
        if I_s[s, t].varValue:
            ton_kho_nut[s] += I_s[s, t].varValue
            chi_phi_khac[s] += I_s[s, t].varValue * chi_phi_luu_kho_s[s, t] / 1000

# P:
for p in P:
    for t in T:
        if waste_p[p, t].varValue:
            chi_phi_khac[p] += waste_p[p, t].varValue * chi_phi_lang_phi_p / 1000
        if I_p[p, t].varValue:
            ton_kho_nut[p] += I_p[p, t].varValue
            chi_phi_khac[p] += I_p[p, t].varValue * chi_phi_luu_kho_p[p, t] / 1000

# R:
for r in R:
    for t in T:
        if I_r[r, t].varValue:
            ton_kho_nut[r] += I_r[r, t].varValue
            chi_phi_khac[r] += I_r[r, t].varValue * chi_phi_luu_kho_r[r, t] / 1000

# === 3. Dinh dang tien ===
def dinh_dang_tien(val):
    if val >= 1_000_000:
        return f"{round(val / 1_000_000)}B"
    elif val >= 1_000:
        return f"{round(val / 1_000)}M"
    else:
        return f"{round(val)}k"

# === 4. Ve do thi ===
G_flow = nx.DiGraph()
for (u, v), w in flow_all.items():
    G_flow.add_edge(u, v, weight=w)

pos = get_pos_by_layer_dynamic(G, S, P, R, x_spacing=2.2)
plt.figure(figsize=(22, 12))
nx.draw_networkx_nodes(G_flow, pos, node_size=3000, node_color='lightyellow', edgecolors='black')

# === 5. Ghi nhan tung nut ===
labels_with_cost = {}
for node in G_flow.nodes:
    chi_phi = dinh_dang_tien(chi_phi_khac[node])
    ton_kho = round(ton_kho_nut[node] / 1000)
    labels_with_cost[node] = f"{node}\nChi phí khác: {chi_phi}\nTồn kho: {ton_kho} tấn"

nx.draw_networkx_labels(G_flow, pos, labels=labels_with_cost, font_size=11, font_weight='bold')

# === 6. NHan mui ten: chi phi VC + so tan (lam tron) ===
edge_labels = {}
for (u, v), w in flow_all.items():
    w_tan = round(w / 1000)
    if (u, v) in chi_phi_gs:
        cost = w * chi_phi_gs[(u, v)] / 1000
    elif (u, v) in chi_phi_sp:
        cost = w * chi_phi_sp[(u, v)] / 1000
    elif (u, v) in chi_phi_pr:
        cost = w * chi_phi_pr[(u, v)] / 1000
    else:
        cost = 0
    edge_labels[(u, v)] = f"Chi phi VC: {dinh_dang_tien(cost)}\nSo tan: {w_tan} tan"

nx.draw_networkx_edges(G_flow, pos, arrows=True, width=1.2, connectionstyle='arc3,rad=0.05')
nx.draw_networkx_edge_labels(
    G_flow, pos, edge_labels=edge_labels, font_size=10, label_pos=0.52,
    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.85),
)
plt.title("So do chuoi cug ung: Van chuyen, Chi phi khac va Ton kho", fontsize=16, weight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()






















