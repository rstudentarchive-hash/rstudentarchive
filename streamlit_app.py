# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
import base64
import re
import msoffcrypto
import os

def try_load_excel():
    # فك تشفير ملف الإكسل المحمي بكلمة مرور
    decrypted = BytesIO()
    with open(XLSX_PATH, "rb") as f:
        officefile = msoffcrypto.OfficeFile(f)
        officefile.load_key(password="61206120")  # كلمة المرور
        officefile.decrypt(decrypted)
    decrypted.seek(0)
    try:
        return pd.read_excel(decrypted, sheet_name="query")
    except Exception:
        decrypted.seek(0)
        return pd.read_excel(decrypted)

st.set_page_config(page_title="📘 ملف الطالب — لوحة احترافية", page_icon="🎓", layout="wide")
st.markdown("""
<style>
.card {
    font-size: 1.3rem !important;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)
# كلمة المرور المطلوبة
PASSWORD = "RS123"

# مربع إدخال كلمة المرور
password_input = st.text_input("🔒 أدخل كلمة المرور لعرض الصفحة", type="password")

# تحقق من كلمة المرور
if password_input != PASSWORD:
    st.warning("⚠️ الرجاء إدخال كلمة المرور الصحيحة لعرض المحتوى.")
    st.stop()  # يوقف تنفيذ باقي الصفحة

st.markdown("""
<style>
/* عمود منصات القراءة: صغّر البطاقات واثبت محاذاتها من الأعلى لليمين */
.rcol .card {
  transform: scale(.92);
  transform-origin: top right;
  padding: 10px;
  border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* شريط بطاقات الاختبارات الخارجية */
.exrow{
  display:flex;
  gap:10px;
  align-items:stretch;
  overflow-x:auto;
  padding:6px 4px;
  white-space:nowrap;
}

/* بطاقة الاختبارات الخارجية (مكبرة قليلاً) */
.excard{
  background:#EAF2FF !important;     /* أزرق فاتح */
  border:1px solid #CFE1FF !important;
  border-radius:12px !important;
  padding:12px 14px !important;      /* أكبر ≈15% */
  min-width:160px;                   /* زوّد العرض قليلاً */
  flex:0 0 auto;
  box-shadow:0 2px 6px rgba(0,0,0,.05);
}

.excard .k{
  font-size:1.04rem;   /* أكبر ≈30% من 0.8rem */
  color:#334155;
  font-weight:700;
  margin-bottom:4px;
}
.excard .v{
  font-size:1.24rem;   /* أكبر ≈30% من 0.95rem */
  font-weight:900;
  color:#0F172A;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* بطاقة الأكاديمية (أخضر فاتح) */
.kpi-a{
  border-radius:12px; padding:10px 12px;
  background:#E8F9EE !important; border:1px solid #BFE3CC;
  text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.05);
}
.kpi-a h4{ margin:0; font-size:.9rem; font-weight:700; color:#166534; }
.kpi-a .val{ font-size:1.15rem; font-weight:900; }

/* بطاقة منصات القراءة */
.kpi-r{
  border-radius:12px; padding:10px 12px;
  background:#ffffff !important; border:1px solid #e5e7eb;
  text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.05);
}
.kpi-r h4{ margin:0; font-size:.9rem; font-weight:700; color:#334155; }
.kpi-r .val{ font-size:1.15rem; font-weight:900; color:#0f172a; }

/* ألوان الأكاديمية (مخصّصة ولن تتأثر بأي ستايل آخر) */
.kpi-a .val.acad-low  { color:#dc2626 !important; }  /* <60 */
.kpi-a .val.acad-mid  { color:#b45309 !important; }  /* 60–70 */
.kpi-a .val.acad-high { color:#065f46 !important; }  /* >70 */
</style>
""", unsafe_allow_html=True)

def acad_class(v):
    s = str(v).strip().replace("٪","").replace("%","").replace(",", ".")
    try:
        x = float(s)
    except:
        return "acad-high"
    if x < 60:  return "acad-low"
    if x < 70:  return "acad-mid"
    return "acad-high"

st.markdown("""
<style>
/* عناوين البطاقات */
.kpi-a h4, .kpi-r h4{
  font-size: 1.125rem !important;   /* كان ~0.9rem → +25% */
}

/* القيم داخل البطاقات */
.kpi-a .val, .kpi-r .val{
  font-size: 1.44rem !important;    /* كان ~1.15rem → +25% */
  line-height: 1.15;                 /* تماسك عمودي */
}

/* (اختياري) زيادة طفيفة في الحشوة للموازنة مع كِبر الخط */
.kpi-a, .kpi-r{
  padding: 12px 14px !important;     /* كان 10px 12px */
}
</style>
""", unsafe_allow_html=True)



# ====================== مصادر الملفات ======================
BASE_DIR = Path(__file__).resolve().parent
XLSX_PATH = BASE_DIR / "بيانات الطلاب.xlsx"
LOGO_PATH = BASE_DIR / "شعار المدارس.jpg"  # اختياري

# ====================== قراءة البيانات ======================
def try_load_excel():
    # جرّب ورقة "query" أولًا، وإن لم توجد خذ أول ورقة
    try:
        return pd.read_excel(XLSX_PATH, sheet_name="query")
    except Exception:
        return pd.read_excel(XLSX_PATH)  # أول شيت

raw = try_load_excel()

# ========== أدوات أسماء الأعمدة ==========
def split_group_suffix(name: str):
    s = str(name)
    if "-" in s:
        group, suffix = s.split("-", 1)
        return group.strip(), suffix.strip()
    return None, s.strip()

def canon(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()

# نبني:
# 1) df موحد الأعمدة بالـ suffix فقط (مع دمج أول قيمة غير فارغة)
# 2) قاموس by_group للاحتفاظ بقيم مجموعات محددة مثل External / Behavior / reading platform
def normalize(raw: pd.DataFrame):
    by_group = {}  # (group_lower or None, suffix_lower) -> Series
    out = pd.DataFrame(index=raw.index)
    for col in raw.columns:
        group, suffix = split_group_suffix(col)
        gkey = (canon(group).lower() if group else None)
        skey = canon(suffix).lower()

        ser = raw[col]  # لا تحوّل لأنواع نصية الآن للحفاظ على الأرقام
        by_group[(gkey, skey)] = ser

        human_suffix = canon(suffix)
        if human_suffix not in out.columns:
            out[human_suffix] = ser
        else:
            left = out[human_suffix]
            right = ser
            is_empty = left.isna() | (left.astype(str).str.strip() == "")
            out[human_suffix] = left.mask(is_empty, right)
    return out, by_group

df, by_group = normalize(raw)

# بعض الأعمدة المهمة كنص لضمان البحث (بدون ضياع أصفار)
for col in ["ID2", "Name", "Arabicname", "Year", "Class"]:
    if col in df.columns:
        try:
            df[col] = df[col].astype("string")
        except Exception:
            pass

# ====================== أدوات مساعدِة لالتقاط القيم ======================
def norm_key(s: str) -> str:
    # للتطابق المرن: نهمل المسافات والنقاط والحالة
    return re.sub(r"[^0-9A-Za-z\u0600-\u06FF]+", "", str(s)).lower()

def get_val_by_partial(row, partial_col_name):
    """إرجاع قيمة من الصف بناءً على جزء من اسم العمود"""
    for col in row.index:
        if partial_col_name.lower() in col.lower():
            return row[col]
    return ""

def find_suffix_column(cols, wanted: str):
    wanted_norm = norm_key(wanted)
    lowmap = {norm_key(c): c for c in cols}
    # محاولات مع/بدون 1
    cands = [wanted_norm]
    if not wanted_norm.endswith("1"):
        cands.append(wanted_norm + "1")
    else:
        cands.append(wanted_norm[:-1])
    for c in cands:
        if c in lowmap:
            return lowmap[c]
    # يحتوي
    for k, orig in lowmap.items():
        if wanted_norm in k:
            return orig
    return None

def gv_row(row: pd.Series, key: str, default="—"):
    col = find_suffix_column(row.index, key)
    if not col:
        return default
    val = row[col]
    if pd.isna(val) or str(val).strip() == "":
        return default
    return str(val)

def gv_group(index: int, suffix_like: str, group_names, default="—"):
    """القراءة من مجموعة محددة (مثل External/Behavior/reading platform)."""
    c_suffix = canon(suffix_like).lower()
    groups = [canon(g).lower() for g in group_names if g]
    # تطابق مباشر
    for g in groups:
        ser = by_group.get((g or None, c_suffix))
        if ser is not None:
            v = ser.iloc[index]
            return default if pd.isna(v) or str(v).strip() == "" else str(v)
    # تطابق يحتوي
    for (g, sfx), ser in by_group.items():
        if g in groups and c_suffix in sfx:
            v = ser.iloc[index]
            if not (pd.isna(v) or str(v).strip()==""):
                return str(v)
    return default

# مرادفات المجموعات
G_ATT = ["attendance", "attend", "att", "attandance"]
G_BEH = ["behavior", "behaviour", "behavoir", "behavioir", "beh"]
G_EXT = ["external", "external exams", "ext", "map"]  # تشمل MAP ضمن الخارجية
G_READPLAT = ["reading platform", "reading platforms", "iread", "raz", "reading"]

# =============== تنسيق واجهة فاتح + كروت ===============
st.markdown("""
<style>
:root{
  --bg:#f7fafc;
  --text:#1f2937;
  --muted:#6b7280;
  --card:#ffffff;
  --border:#e5e7eb;
  --accent:#2563eb;
  --accent2:#16a34a;
  --accent3:#f59e0b;
}
html, body, [data-testid="stAppViewContainer"]{
  background: var(--bg);
  color: var(--text);
}
h1,h2,h3,h4{ color: var(--text); }
.badge{
  display:inline-block; padding:.25rem .5rem; border:1px solid var(--border); border-radius:10px;
  background:#fff; color:#111827; font-weight:700; font-size:.85rem;
}
.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,.05);
}
/* صف السطر داخل البطاقة */
/* صفّ البطاقة */
.kv{
  display:flex;
  flex-wrap: wrap;                 /* ✅ اسمح باللف داخل البطاقة */
  gap:.6rem;
  align-items:flex-start;
  margin:.35rem 0;
}

/* عنوان الحقل */
.kv .k{
  color:#374151;
  font-weight:600;
  flex: 0 0 auto;                  /* لا تتمدّد */
  min-width:auto;                  /* لا تجبر عرض كبير */
  max-width:100%;
  text-align:left;
  white-space:normal;              /* اسمح بكسر السطر */
  word-break:keep-all;             /* لا تكسر الحروف */
}

/* قيمة الحقل */
.kv .v{
  color:#111827;
  font-weight:700;
  flex: 1 0 100%;                  /* ✅ خذ سطرًا كاملاً تحت العنوان */
  min-width:0;                     /* مهم للّف داخل flex */
  white-space:normal;              /* لف طبيعي على مستوى الكلمات */
  overflow-wrap:break-word;        /* اكسر عند حدود الكلمة عند الحاجة */
  word-break:normal;               /* لا تقسّم كل حرف */
  text-align:left;
}


.kpi{
  display:flex; flex-direction:column; gap:.25rem; align-items:flex-start;
  padding:12px 14px; border-radius:14px; border:1px solid var(--border);
  background:linear-gradient(180deg,#ffffff, #f9fafb);
}
.kpi h4{ margin:0; font-size:.95rem; color:#374151; font-weight:700; }
.kpi .val{ font-size:1.3rem; font-weight:900; color:#111827;}
.section-title{ font-weight:800; text-transform:uppercase; letter-spacing:.3px; margin:.25rem 0 .5rem; }
.divider{ height:1px; background:linear-gradient(90deg,transparent, #e5e7eb, transparent); margin:.7rem 0 .9rem;}
.suggestion{ font-size:.92rem; color:#111827; }
.print-btn{ padding:.45rem .8rem; border-radius:10px; background:#111827; color:#fff; border:0; font-weight:700; }
.excel-btn{ padding:.45rem .8rem; border-radius:10px; background:#2563eb; color:#fff; border:0; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# =============== شريط علوي: شعار + فلاتر السنة والبحث ===============
top1, top2 = st.columns([1, 7])
with top1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=110)
with top2:
        st.markdown(
           """
           <h2 style='text-align:center; color:green;'>
                أرشيف الطالب - المرحلة الابتدائية<br>
                Student Archive - ESB
           </h2>
           """,
            unsafe_allow_html=True  
        )



# فلتر السنة
years = sorted(df["Year"].dropna().astype(str).unique()) if "Year" in df.columns else []
colY, colSearchMode, colQuery = st.columns([1.2, 1.2, 3])
with colY:
    year = st.selectbox("السنة الدراسية", ["الكل"] + years, index=0)
with colSearchMode:
    search_mode = st.selectbox("البحث بـ", ["ID2", "Name", "Arabicname"])
with colQuery:
    query = st.text_input("اكتب جزءًا من الاسم أو الهوية…", "")

# تطبيق فلتر السنة
filtered = df.copy()
if year != "الكل" and "Year" in filtered.columns:
    filtered = filtered[filtered["Year"].astype(str) == year]

# اقتراحات البحث الفورية (على ID2/Name/Arabicname)
def build_suggestions(q: str, data: pd.DataFrame, col: str):
    if not q or col not in data.columns:
        return []
    m = data[col].astype(str).str.contains(q, case=False, na=False)
    # نعرض حتى 20 اقتراحًا: الاسم العربي — الاسم الإنجليزي — ID
    out = []
    for _, r in data[m].head(20).iterrows():
        ar = r.get("Arabicname", "")
        en = r.get("Name", "")
        id2 = r.get("ID2", "")
        label = f"{ar} — {en} — ID:{id2}"
        out.append((label, r.name))  # (عرض، index)
    return out

suggestions = build_suggestions(query, filtered, search_mode)
selected_idx = None
if suggestions:
    labels = [s[0] for s in suggestions]
    pick = st.selectbox("نتائج مطابقة:", labels, index=0)
    # استرجاع index
    selected_idx = dict(suggestions)[pick]

# إن لم يكتب بحثًا، اسمح باختيار يدوي من القائمة (مثل النسخة القديمة)
if not selected_idx:
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.caption("أو اختر يدويًا من النتائج المفلترة أدناه:")
    selected_idx = st.selectbox(
        "اختر الطالب",
        options=filtered.index,
        format_func=lambda i: f"{filtered.loc[i].get('Arabicname','')} — {filtered.loc[i].get('Name','')} — ID:{filtered.loc[i].get('ID2','')}"
    )

row = filtered.loc[selected_idx]
row_index = selected_idx if isinstance(selected_idx, int) else df.index.get_loc(selected_idx)

# دالة لإيجاد العمود بالبحث الجزئي
def get_val_by_partial(row, keyword):
    for col in row.index:
        if keyword.lower() in col.lower():
            return row[col]
    return ""

# =============== الكروت: معلومات أساسية ===============
st.markdown("<div class='section-title'>👤 Personal information</div>", unsafe_allow_html=True)
cA, cB, cC, cD, cE, cF, cG, cH = st.columns([1.2,1.2,1,1,1,1,1,1])

with cA:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">الاسم (AR)</div><div class="v">{gv_row(row,"Arabicname")}</div></div></div>', unsafe_allow_html=True)
with cB:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">Name (EN)</div><div class="v">{gv_row(row,"Name")}</div></div></div>', unsafe_allow_html=True)
with cC:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">Class</div><div class="v">{gv_row(row,"Class")}</div></div></div>', unsafe_allow_html=True)
with cD:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">Mobile</div><div class="v">{gv_row(row,"Mobile")}</div></div></div>', unsafe_allow_html=True)
with cE:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">Login</div><div class="v">{gv_row(row,"login")}</div></div></div>', unsafe_allow_html=True)
with cF:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">Password</div><div class="v">{gv_row(row,"Password")}</div></div></div>', unsafe_allow_html=True)
with cG:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">Mawhiba / Competition</div><div class="v">{get_val_by_partial(row, "Mawhiba")}</div></div></div>', unsafe_allow_html=True)
with cH:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">Year</div><div class="v">{gv_row(row,"Year")}</div></div></div>', unsafe_allow_html=True)



# دالة مساعدة قبل أي with
def get_val_by_partial(row, partial_name):
    for col in row.index:
        if partial_name.lower() in col.lower():
            val = row[col]
            if pd.isna(val) or str(val).strip() == "":
                return "—"
            return str(val)
    return "—"

# =============== الكروت: الحضور والسلوك ===============
# ✅ أضف هذا في بداية الملف بعد st.set_page_config(...)
st.markdown("""
<style>
.big-text {
    font-size: 1.4rem !important;   /* حجم النصوص */
    font-weight: bold;
}
.section-title {
    font-size: 1.6rem !important;   /* تكبير العناوين */
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# =============== عمودان: يسار (البيانات الأكاديمية) / يمين (منصات القراءة مصغّرة) ===============
def rp_val(provider: str, kind: str):
    """
    provider: 'iread' أو 'raz'
    kind: 'books' أو 'levels'
    ترجع القيمة الصحيحة مع تحمّل أخطاء الكتابة مثل 'leves'
    """
    prov = norm_key(provider)
    kind_norm = norm_key(kind)
    # مرادفات/أخطاء مطبعية
    kind_keys = { "books": ["books", "book"], "levels": ["levels", "level", "leves"] }
    wanted_kinds = [norm_key(k) for k in kind_keys.get(kind_norm, [kind])]

    for (g, sfx), ser in by_group.items():
        if g in [canon(x).lower() for x in G_EXT]:
            continue
        s_norm = norm_key(sfx)
        if prov in s_norm and any(kk in s_norm for kk in wanted_kinds):
            val = ser.iloc[row_index]
            if not (pd.isna(val) or str(val).strip() == ""):
                return str(val)
    return "—"
# عمودان للسطر: يسار أكاديمية (5 بطاقات أفقياً)، يمين منصات القراءة (4 بطاقات أفقياً)
left_col, right_col = st.columns([2, 1])

# ── الأكاديمية (يسار) — صف أفقي واحد من 5 أعمدة
with left_col:
    st.markdown("<div class='section-title'>📚 Academic Data</div>", unsafe_allow_html=True)
    subs = [("Math","Math1"),("English","English1"),("Science","Science1"),("Arabic","Arabic1"),("Islamic","Islamic1")]
    ac_cols = st.columns(len(subs))
    for (label, key), c in zip(subs, ac_cols):
        val = gv_row(row, key)
        c.markdown(
            f"""<div class="kpi-a">
                    <h4>{label}</h4>
                    <div class="val {acad_class(val)}">{val}</div>
                </div>""",
            unsafe_allow_html=True
        )

# ── منصات القراءة (يمين) — صف أفقي واحد من 4 أعمدة
with right_col:
    st.markdown("<div class='section-title'>📖 Reading Platforms</div>", unsafe_allow_html=True)
    r_items = [("Iread-Levels","iread","levels"),
               ("Iread-Books","iread","books"),
               ("RAZ-Levels","raz","levels"),
               ("RAZ-Books","raz","books")]
    rp_cols = st.columns(len(r_items))
    for (label, prov, kind), c in zip(r_items, rp_cols):
        c.markdown(
            f"""<div class="kpi-r">
                    <h4>{label}</h4>
                    <div class="val">{rp_val(prov, kind)}</div>
                </div>""",
            unsafe_allow_html=True
        )


# =============== الكروت: الاختبارات الخارجية (تشمل MAP) ===============
st.markdown("<div class='section-title'>🧪 External Exams (incl. MAP)</div>", unsafe_allow_html=True)

ext_items = []
for (g, sfx), ser in by_group.items():
    if g in [canon(x).lower() for x in G_EXT]:
        val = ser.iloc[row_index]
        lab = canon(sfx)
        ext_items.append((lab, "—" if pd.isna(val) or str(val).strip()=="" else str(val)))

ext_items.sort()

if ext_items:
    # CSS للألوان
    st.markdown("""
    <style>
    .val-low   { color:#dc2626 !important; }   /* أحمر */
    .val-high  { color:#1d4ed8 !important; }   /* أزرق */
    .val-norm  { color:#0F172A !important; }   /* عادي */
    </style>
    """, unsafe_allow_html=True)

    # ابني البطاقات مع الشروط
    html = ["<div class='exrow'>"]
    threshold = 180  # المعدل الذي نقارن به
    for lab, val in ext_items:
        cls = "val-norm"
        try:
            num = float(val)
            if num < threshold:
                cls = "val-low"
            elif num > threshold + 20:
                cls = "val-high"
        except:
            pass  # إذا ليست قيمة رقمية

        html.append(
            f"<div class='excard'><div class='k'>{lab}</div><div class='v {cls}'>{val}</div></div>"
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)
else:
    st.caption("لا توجد أعمدة للاختبارات الخارجية لهذا الطالب.")

    # =============== الكروت: ILP ===============
st.markdown("<div class='section-title'>📌 ILP (Individual Learning Plan)</div>", unsafe_allow_html=True)
i1,i2,i3 = st.columns(3)
with i1:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">ILP-English</div><div class="v">{gv_row(row,"ILP English1")}</div></div></div>', unsafe_allow_html=True)
with i2:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">ILP-Math</div><div class="v">{gv_row(row,"ILP Math1")}</div></div></div>', unsafe_allow_html=True)
with i3:
    st.markdown(f'<div class="card"><div class="kv"><div class="k">ILP-Arabic</div><div class="v">{gv_row(row,"ILP Arabic1")}</div></div></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =============== الكروت: الحضور والسلوك ===============
col1, col2, col3 = st.columns(3)

# 🕒 Attendance
with col1:
    st.markdown("<div class='section-title'>🕒 Attendance</div>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    e_val = get_val_by_partial(row, "E. absence")
    a_val = get_val_by_partial(row, "Unexcused absence")
    l_val = get_val_by_partial(row, "Lateness")

    st.markdown(f"<div class='big-text'><b>Excused (E):</b> {e_val}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-text'><b>Unexcused (A):</b> {a_val}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-text'><b>Lateness (L):</b> {l_val}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# 🧭 Behavior
with col2:
    st.markdown("<div class='section-title'>🧭 Behavior</div>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    beh_items = []
    for (g, sfx), ser in by_group.items():
        if g in [canon(x).lower() for x in G_BEH]:
            val = ser.iloc[row_index]
            label = canon(sfx)
            beh_items.append((label, "—" if pd.isna(val) or str(val).strip()=="" else str(val)))
    if beh_items:
        beh_items.sort()
        for lab, val in beh_items:
            st.markdown(f"<div class='big-text'><b>{lab}:</b> {val}</div>", unsafe_allow_html=True)
    else:
        st.caption("لا توجد أعمدة سلوك لهذا الطالب.")
    st.markdown('</div>', unsafe_allow_html=True)

# 🩺 Healthy & 🤝 Social
with col3:
    st.markdown("<div class='section-title'>🩺 Healthy & 🤝 Social</div>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<div class='big-text'><b>Healthy:</b> {gv_row(row,'Healthy')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-text'><b>Social:</b> {gv_row(row,'Social')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =============== قسم "كل الأعمدة" للتأكيد (اختياري) ===============
with st.expander("🗂️ عرض كل الأعمدة (تأكيدًا على عدم فقد أي عمود)"):
    all_cols = []
    for c in row.index:
        all_cols.append((c, "—" if pd.isna(row[c]) or str(row[c]).strip()=="" else str(row[c])))
    df_all = pd.DataFrame(all_cols, columns=["Field", "Value"])
    st.dataframe(df_all, use_container_width=True)

# =============== أزرار الطباعة والتصدير ===============

def build_print_html():
    # شعار
    logo_tag = ""
    if LOGO_PATH.exists():
        b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
        logo_tag = f'<img src="data:image/jpeg;base64,{b64}" style="height:64px;"/>'

    # عناصر الاختبارات الخارجية
    ext_items = []
    for (g, sfx), ser in by_group.items():
        if g in [canon(x).lower() for x in G_EXT]:
            v = ser.iloc[row_index]
            lab = canon(sfx)
            val = "—" if pd.isna(v) or str(v).strip()=="" else str(v)
            ext_items.append((lab, val))
    ext_items.sort()

    # تلوين الأكاديمية
    def acad_class(v):
        s = str(v).strip().replace("٪","").replace("%","").replace(",", ".")
        try:
            x = float(s)
        except:
            return "acad-high"
        if x < 60:  return "acad-low"
        if x < 70:  return "acad-mid"
        return "acad-high"

    # HTML للطباعة بنفس شكل اللوحة (A4 أفقي)
    return f"""
<!doctype html>
<html lang="ar" dir="auto">
<head>
<meta charset="utf-8"/>
<title>تقرير الطالب</title>
<style>
  @page {{ size: A4 landscape; margin: 10mm; }}
  html,body{{ margin:0; padding:0; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  body{{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, "Noto Sans", "Helvetica Neue", sans-serif; color:#111827; }}
  .page{{ max-width: 1200px; margin: 0 auto; }}

  h2.section-title{{ margin:4px 0 10px; font-size:18px; font-weight:800; color:#0f172a; }}
  .row{{ display:flex; gap:10px; flex-wrap:wrap; }}
  .grid-8{{ display:grid; grid-template-columns: repeat(8,1fr); gap:10px; }}
  .grid-3{{ display:grid; grid-template-columns: repeat(3,1fr); gap:10px; }}
  .two-cols{{ display:grid; grid-template-columns: 2fr 1fr; gap:14px; align-items:start; }}

  .card{{ background:#fff; border:1px solid #e5e7eb; border-radius:14px; padding:10px 12px; box-shadow:0 2px 6px rgba(0,0,0,.04); }}
  .kv .k{{ color:#374151; font-weight:700; font-size:13px; }}
  .kv .v{{ color:#0f172a; font-weight:800; font-size:15px; margin-top:4px; }}

  .kpi-a{{ border-radius:12px; padding:12px 14px; background:#E8F9EE !important; border:1px solid #BFE3CC; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.05); }}
  .kpi-a h4{{ margin:0; font-size:1.125rem; font-weight:700; color:#166534; }}
  .kpi-a .val{{ font-size:1.44rem; font-weight:900; }}
  .kpi-a .val.acad-low  {{ color:#dc2626 !important; }}
  .kpi-a .val.acad-mid  {{ color:#b45309 !important; }}
  .kpi-a .val.acad-high {{ color:#065f46 !important; }}

  .kpi-r{{ border-radius:12px; padding:12px 14px; background:#ffffff !important; border:1px solid #e5e7eb; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,.05); }}
  .kpi-r h4{{ margin:0; font-size:1.125rem; font-weight:700; color:#334155; }}
  .kpi-r .val{{ font-size:1.44rem; font-weight:900; color:#0f172a; }}

  .ex-wrap{{ display:flex; flex-wrap:wrap; gap:8px; }}
  .ex{{ background:#EAF2FF; border:1px solid #CFE1FF; border-radius:10px; padding:8px 10px; min-width:150px; }}
  .ex .k{{ font-size:13px; color:#334155; font-weight:700; }}
  .ex .v{{ font-size:15px; font-weight:900; color:#0f172a; }}

  .section{{ page-break-inside: avoid; }}
  @media print {{ .page{{ zoom:0.90; }} }}
</style>
</head>
<body onload="window.print()">
  <div class="page">
    <div style="display:flex; align-items:center; gap:12px; margin:0 0 8px;">
      {logo_tag}
      <h1 style="margin:0; font-size:22px;">تقرير الطالب — {row.get('Arabicname','')} — ID: {row.get('ID2','')}</h1>
    </div>

    <div class="section grid-8" style="margin-bottom:10px;">
      <div class="card"><div class="kv"><div class="k">الاسم (AR)</div><div class="v">{gv_row(row,'Arabicname')}</div></div></div>
      <div class="card"><div class="kv"><div class="k">Name (EN)</div><div class="v">{gv_row(row,'Name')}</div></div></div>
      <div class="card"><div class="kv"><div class="k">Class</div><div class="v">{gv_row(row,'Class')}</div></div></div>
      <div class="card"><div class="kv"><div class="k">Mobile</div><div class="v">{gv_row(row,'Mobile')}</div></div></div>
      <div class="card"><div class="kv"><div class="k">Login</div><div class="v">{gv_row(row,'login')}</div></div></div>
      <div class="card"><div class="kv"><div class="k">Password</div><div class="v">{gv_row(row,'Password')}</div></div></div>
      <div class="card"><div class="kv"><div class="k">Mawhiba / Competition</div><div class="v">{get_val_by_partial(row,'Mawhiba')}</div></div></div>
      <div class="card"><div class="kv"><div class="k">Year</div><div class="v">{gv_row(row,'Year')}</div></div></div>
    </div>

    <div class="section two-cols" style="margin-bottom:10px;">
      <div>
        <h2 class="section-title">📚 Academic Data</h2>
        <div class="row">
          {"".join([
            f'''<div class="kpi-a"><h4>{lbl}</h4><div class="val {acad_class(gv_row(row,key))}">{gv_row(row,key)}</div></div>'''
            for (lbl,key) in [("Math","Math1"),("English","English1"),("Science","Science1"),("Arabic","Arabic1"),("Islamic","Islamic1")]
          ])}
        </div>
      </div>
      <div>
        <h2 class="section-title">📖 Reading Platforms</h2>
        <div class="row">
          {"".join([
            f'''<div class="kpi-r"><h4>{lbl}</h4><div class="val">{rp_val(p,k)}</div></div>'''
            for (lbl,p,k) in [("Iread-Levels","iread","levels"),("Iread-Books","iread","books"),("RAZ-Levels","raz","levels"),("RAZ-Books","raz","books")]
          ])}
        </div>
      </div>
    </div>

    <div class="section" style="margin-bottom:10px;">
      <h2 class="section-title">🧪 External Exams (incl. MAP)</h2>
      <div class="ex-wrap">
        {"".join([
          f'''<div class="ex"><div class="k">{lab}</div><div class="v">{val}</div></div>'''
          for (lab,val) in ext_items
        ])}
      </div>
    </div>

    <div class="section" style="margin-bottom:10px;">
      <h2 class="section-title">📌 ILP (Individual Learning Plan)</h2>
      <div class="grid-3">
        <div class="card"><div class="kv"><div class="k">ILP-English</div><div class="v">{gv_row(row,"ILP English1")}</div></div></div>
        <div class="card"><div class="kv"><div class="k">ILP-Math</div><div class="v">{gv_row(row,"ILP Math1")}</div></div></div>
        <div class="card"><div class="kv"><div class="k">ILP-Arabic</div><div class="v">{gv_row(row,"ILP Arabic1")}</div></div></div>
      </div>
    </div>

    <div class="section">
      <div class="grid-3">
        <div class="card">
          <h2 class="section-title" style="margin:0 0 6px;">🕒 Attendance</h2>
          <div class="kv"><div class="k">Excused (E)</div><div class="v">{get_val_by_partial(row,"E. absence")}</div></div>
          <div class="kv"><div class="k">Unexcused (A)</div><div class="v">{get_val_by_partial(row,"Unexcused absence")}</div></div>
          <div class="kv"><div class="k">Lateness (L)</div><div class="v">{get_val_by_partial(row,"Lateness")}</div></div>
        </div>
        <div class="card">
          <h2 class="section-title" style="margin:0 0 6px;">🧭 Behavior</h2>
          <div class="kv"><div class="k">Positives</div><div class="v">{gv_group(row_index,"positives",G_BEH)}</div></div>
          <div class="kv"><div class="k">Negatives</div><div class="v">{gv_group(row_index,"negatives",G_BEH)}</div></div>
          <div class="kv"><div class="k">Behavioral level</div><div class="v">{gv_group(row_index,"behavioral level",G_BEH)}</div></div>
        </div>
        <div class="card">
          <h2 class="section-title" style="margin:0 0 6px;">🩺 Healthy & 🤝 Social</h2>
          <div class="kv"><div class="k">Healthy</div><div class="v">{gv_row(row,"Healthy")}</div></div>
          <div class="kv"><div class="k">Social</div><div class="v">{gv_row(row,"Social")}</div></div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""
EXCEL_FILE = "بيانات الطلاب.xlsx"

# إدخال كلمة المرور
password_input = st.text_input("🔑 أدخل كلمة المرور لإظهار تحديث الإكسل:", type="password")

if password_input == "61206120":
    uploaded_file = st.file_uploader("📤 اختر ملف Excel جديد لتحديث البيانات", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # قراءة الملف الحالي والجديد
            current_df = pd.read_excel(EXCEL_FILE)
            new_df = pd.read_excel(uploaded_file)

            # التحقق من تطابق الأعمدة
            if list(current_df.columns) == list(new_df.columns):
                new_df.to_excel(EXCEL_FILE, index=False)
                st.success("✅ تم تحديث ملف الإكسل بنجاح.")
            else:
                st.error("❌ فشل التحديث: الأعمدة في الملف الجديد لا تطابق الأعمدة الحالية.")
        except Exception as e:
            st.error(f"⚠️ حدث خطأ أثناء التحديث: {e}")
else:
    if password_input:  # إذا كتب أي كلمة مرور خطأ
        st.error("❌ كلمة المرور غير صحيحة.")
        
colP, colX = st.columns([1, 3])
with colP:
    # زر يفتح نافذة جديدة للطباعة عبر رابط data: URI
    html_str = build_print_html()
    b64_html = base64.b64encode(html_str.encode("utf-8")).decode("utf-8")
    st.markdown(
        f"""
        <a class="print-btn" href="data:text/html;base64,{b64_html}" target="_blank">🖨️ فتح صفحة الطباعة</a>
        """,
        unsafe_allow_html=True
    )

with colX:
    # تصدير بيانات الطالب المحدد إلى Excel
    one = pd.DataFrame([row])
    buff = BytesIO()
    one.to_excel(buff, index=False)
    buff.seek(0)
 
    st.download_button(
         label="📥 تنزيل بيانات الطالب (Excel)",
         data=buff,
         file_name=f"student_{row.get('ID2','')}.xlsx",
         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         key=f"dl_student_excel_{row_index}"   # مفتاح فريد   
    )

