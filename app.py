import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, timedelta

DB="etenesh_business.db"
st.set_page_config(page_title="እቴነሽ ጌታው ፋሽን ዲዛይን",page_icon="🧵",layout="wide")

def conn(): return sqlite3.connect(DB, check_same_thread=False)

def init():
    c=conn(); x=c.cursor()
    x.execute("""CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT, trans_date TEXT, kind TEXT,
    description TEXT, revenue REAL, expense REAL, note TEXT)""")
    x.execute("""CREATE TABLE IF NOT EXISTS loan(
    id INTEGER PRIMARY KEY, due_date TEXT, amount REAL,
    status TEXT, paid_date TEXT, note TEXT)""")
    c.commit(); c.close()

def seed():
    c=conn(); x=c.cursor()
    if x.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]==0:
        rows=[(1800,790,1010),(3500,2000,1500),(1600,700,900),(2600,1650,950),
        (3500,1450,2050),(3700,1800,1900),(4000,2875,1125),(3400,2000,1400),
        (2400,1650,750),(2400,1650,750),(1500,820,650),(2300,820,1480),
        (5100,2250,2850),(2000,1200,1300),(1200,575,625),(900,620,280),
        (1700,700,1000),(3800,1940,1860),(1500,900,600),(3000,1490,1510),
        (5700,2750,2240),(3800,2420,1320),(2400,1500,900),(3400,1590,1410),
        (1500,1050,440),(1500,1150,350),(3000,1450,1550),(1500,920,580),
        (1600,625,975),(1500,625,875),(2700,1540,1150),(1700,1150,550),
        (2900,1550,1350),(3200,1885,1915),(3900,2700,1200)]
        for i,(r,e,p) in enumerate(rows,1):
            x.execute("""INSERT INTO transactions
            (trans_date,kind,description,revenue,expense,note)
            VALUES(?,?,?,?,?,?)""",("ቀን ያልተረጋገጠ","የቀድሞ ስራ",
            f"ታሪካዊ ግብይት #{i}",r,e,f"በመጀመሪያ የተሰጠ ትርፍ: {p} ብር"))
    if x.execute("SELECT COUNT(*) FROM loan").fetchone()[0]==0:
        start=date(2022,9,28)
        for i in range(20):
            x.execute("INSERT INTO loan VALUES(?,?,?,?,?,?)",
                      (i+1,(start+timedelta(days=91*i)).isoformat(),12600,"ያልተከፈለ",None,""))
    c.commit(); c.close()

init(); seed()
c=conn()

st.title("🧵 እቴነሽ ጌታው ፋሽን ዲዛይን")
st.caption("የቢዝነስ አስተዳደር ዳሽቦርድ (Business Management Dashboard)")
page=st.sidebar.radio("ምናሌ",["ዋና ዳሽቦርድ","ገቢና ወጪ","የብድር ክትትል","የዋጋ ማስያ","ሪፖርት","የቢዝነስ መረጃ"])

if page=="ዋና ዳሽቦርድ":
    df=pd.read_sql_query("SELECT * FROM transactions",c)
    r,e=df.revenue.sum(),df.expense.sum()
    a,b,d=st.columns(3); a.metric("ጠቅላላ ገቢ",f"{r:,.2f} ብር"); b.metric("ጠቅላላ ወጪ",f"{e:,.2f} ብር"); d.metric("ጠቅላላ ትርፍ",f"{r-e:,.2f} ብር")
    st.bar_chart(pd.DataFrame({"ገቢ":r,"ወጪ":e,"ትርፍ":r-e},index=["ድምር"]).T)
    st.subheader("የቋሚ ወጪ መነሻ")
    st.table(pd.DataFrame({"ወጪ":["ኪራይ","ዘበኛ","መብራት/ውሃ"],"ወርሃዊ ብር":[2000,500,"15–30"]}))

elif page=="ገቢና ወጪ":
    st.subheader("አዲስ ግብይት")
    with st.form("newtx"):
        d1,d2,d3=st.columns(3)
        dt=d1.date_input("ቀን"); kind=d2.selectbox("ዓይነት",["ትዕዛዝ/ሽያጭ","የተሰፋ ስራ","የዕቃ ሽያጭ","ግዥ","ሌላ ወጪ"])
        desc=d3.text_input("መግለጫ"); rev=d1.number_input("ገቢ",min_value=0.0); exp=d2.number_input("ወጪ",min_value=0.0); note=d3.text_input("ማስታወሻ")
        if st.form_submit_button("አስቀምጥ"):
            c.execute("INSERT INTO transactions(trans_date,kind,description,revenue,expense,note) VALUES(?,?,?,?,?,?)",(str(dt),kind,desc,rev,exp,note)); c.commit(); st.success("ተመዝግቧል።")
    df=pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC",c); df["የተሰላ ትርፍ"]=df.revenue-df.expense
    st.dataframe(df,use_container_width=True)
    st.download_button("CSV አውርድ",df.to_csv(index=False).encode("utf-8-sig"),"etenesh_transactions.csv","text/csv")

elif page=="የብድር ክትትል":
    st.subheader("20 ሩብ ዓመታት የብድር ክትትል")
    df=pd.read_sql_query("SELECT * FROM loan ORDER BY id",c)
    st.metric("ጠቅላላ የታቀደ ክፍያ",f"{df.amount.sum():,.0f} ብር")
    for _,q in df.iterrows():
        cols=st.columns([1,2,2,2]); cols[0].write(f"#{int(q.id)}"); cols[1].write(q.due_date); cols[2].write(f"{q.amount:,.0f} ብር")
        s=cols[3].selectbox("ሁኔታ",["ያልተከፈለ","የተከፈለ"],index=0 if q.status=="ያልተከፈለ" else 1,key=f"l{q.id}")
        if s!=q.status:
            c.execute("UPDATE loan SET status=?,paid_date=? WHERE id=?",(s,str(date.today()) if s=="የተከፈለ" else None,int(q.id))); c.commit()
    st.warning("የክፍያ ቀኖች ከዋናው የብድር ውል/የባንክ ሰነድ ጋር መረጋገጥ አለባቸው።")

elif page=="የዋጋ ማስያ":
    st.subheader("የምርት ወጪና የሽያጭ ዋጋ")
    a,b,d=st.columns(3); fabric=a.number_input("ጨርቅ",0.0); material=b.number_input("ክር/እቃ",0.0); labor=d.number_input("የስራ ዋጋ",0.0); overhead=a.number_input("የቋሚ ወጪ ድርሻ",0.0); margin=b.number_input("ትርፍ %",0.0,100.0,30.0)
    cost=fabric+material+labor+overhead; price=cost*(1+margin/100)
    a.metric("የምርት ወጪ",f"{cost:,.2f} ብር"); b.metric("የሚመከር ዋጋ",f"{price:,.2f} ብር")

elif page=="ሪፖርት":
    df=pd.read_sql_query("SELECT * FROM transactions",c); r,e=df.revenue.sum(),df.expense.sum()
    report=pd.DataFrame({"መለኪያ":["ገቢ","ወጪ","ትርፍ"],"ብር":[r,e,r-e]})
    st.subheader("የትርፍና ኪሳራ ሪፖርት"); st.table(report)
    st.download_button("ሪፖርት CSV አውርድ",report.to_csv(index=False).encode("utf-8-sig"),"etenesh_profit_loss.csv","text/csv")

else:
    st.subheader("የቢዝነስ መገለጫ")
    st.write("**ባለቤት:** እቴነሽ ጌታው")
    st.write("**መነሻ ገንዘብ:** 220,000 ብር — 20,000 ብር ቁጠባ + 200,000 ብር የወጣቶች ፈንድ ብድር")
    st.write("**የብድር ጊዜ:** 5 ዓመት (20 ሩብ ዓመታት); **ክፍያ:** 12,600 ብር/ሩብ ዓመት")
    st.write("**ምርቶች:** የሴቶች መደበኛ ቀሚስ እና ሽፎን ቀሚስ")
    st.write("**ዋና ችግሮች:** የገቢ/ወጪ መዝገብ፣ የምርት ወጪ፣ የብድር ጫና፣ ደንበኛ እጥረት፣ የጊዜ አጠቃቀም")

c.close()
