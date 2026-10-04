import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

DB=Path('etenesh_business.db')
st.set_page_config(page_title='እቴነሽ ጌታው ፋሽን ዲዛይን',page_icon='👗',layout='wide')

def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
 c=conn(); c.executescript('''CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT, et_date TEXT, kind TEXT, description TEXT, revenue REAL DEFAULT 0, expense REAL DEFAULT 0, notes TEXT); CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, et_date TEXT, customer TEXT, product TEXT, qty INTEGER, price REAL, status TEXT, delivery_date TEXT, notes TEXT); CREATE TABLE IF NOT EXISTS loan(id INTEGER PRIMARY KEY AUTOINCREMENT, installment_no INTEGER, due_date TEXT, amount REAL, status TEXT DEFAULT 'ያልተከፈለ', paid_date TEXT);'''); c.commit(); c.close()

def seed():
 c=conn()
 if c.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]==0:
  data=[(1800,790,1010),(3500,2000,1500),(1600,700,900),(2600,1650,950),(3500,1450,2050),(3700,1800,1900),(4000,2875,1125),(3400,2000,1400),(2400,1650,750),(2400,1650,750),(1500,820,650),(2300,820,1480),(5100,2250,2850),(2000,1200,1300),(1200,575,625),(900,620,280),(1700,700,1000),(3800,1940,1860),(1500,900,600),(3000,1490,1510),(5700,2750,2240),(3800,2420,1320),(2400,1500,900),(3400,1590,1410),(1500,1050,440),(1500,1150,350),(3000,1450,1550),(1500,920,580),(1600,625,975),(1500,625,875),(2700,1540,1150),(1700,1150,550),(2900,1550,1350),(3200,1885,1915),(3900,2700,1200)]
  for i,(r,e,p) in enumerate(data,1): c.execute('INSERT INTO transactions(et_date,kind,description,revenue,expense,notes) VALUES(?,?,?,?,?,?)',('2017-2018','ታሪካዊ ግብይት',f'የታሪክ ግብይት #{i}',r,e,f'የተጻፈ ትርፍ: {p}; ሲስተሙ ገቢ-ወጪ ይሰላል'))
  setup=[('መኪና/ማሽን',45500),('ካውያ',3500),('መቀስ ቁጥር 11',1600),('መርገጫ የዚፕ',150),('ማጠፊያ',1000),('ጋይድ',1000),('መለኪያ',150),('የተሰሩ ልብሶች',8300),('የቢጃማ ጨርቅ',2350),('ብትን ጨርቅ 24ሜ',7850),('የሴት ቁምጣ',945),('ጥላ',500),('ክር ላስቲክ',650),('ብትን ጨርቅ ዝቅተኛ',4000),('ቀድሞ የተከፈለ ኪራይ',2220),('ቀለም እና አምፖል',1950),('ብትን ጨርቅ',5040)]
  for d,a in setup:c.execute('INSERT INTO transactions(et_date,kind,description,expense) VALUES(?,?,?,?,?)',('05/12/2017','መነሻ ወጪ',d,a))
  for d,a in [('ትራንስፖርት',550),('ምግብ',470),('ባንክ አገልግሎት',100.06)]:c.execute('INSERT INTO transactions(et_date,kind,description,expense) VALUES(?,?,?,?,?)',('25/12/2017','ስራ ማስኬጃ',d,a))
  c.commit()
 if c.execute('SELECT COUNT(*) FROM loan').fetchone()[0]==0:
  for i in range(1,21):c.execute('INSERT INTO loan(installment_no,due_date,amount) VALUES(?,?,?)',(i,f'ሰኔ 21/2017 + {(i-1)*3} ወራት',12600))
  c.commit()
 c.close()
init();seed()

st.title('👗 እቴነሽ ጌታው ፋሽን ዲዛይን')
st.caption('የንግድ አስተዳደር እና ኦፕሬሽን ስርዓት (Business Management & Operations System)')
menu=st.sidebar.radio('ምናሌ (Menu)',['ዋና ዳሽቦርድ (Dashboard)','ገቢና ወጪ (Income & Expense)','የደንበኛ ትዕዛዞች (Orders)','የብድር ክትትል (Loan)','የዋጋ ማስያ (Pricing Calculator)','ሪፖርቶች (Reports)','የቢዝነስ መገለጫ (Profile)'])
c=conn(); tx=pd.read_sql_query('SELECT * FROM transactions ORDER BY id DESC',c)
if menu.startswith('ዋና'):
 r=tx.revenue.sum();e=tx.expense.sum();p=r-e
 a,b,d,f=st.columns(4);a.metric('ጠቅላላ ገቢ',f'{r:,.2f} ብር');b.metric('ጠቅላላ ወጪ',f'{e:,.2f} ብር');d.metric('ትርፍ',f'{p:,.2f} ብር');f.metric('20 ሩብ ዓመት ክፍያ',f'{252000:,.0f} ብር')
 st.subheader('የገቢና ወጪ አዝማሚያ'); st.line_chart(tx[tx.kind=='ታሪካዊ ግብይት'][['revenue','expense']].reset_index(drop=True))
elif menu.startswith('ገቢ'):
 st.subheader('አዲስ ገቢ/ወጪ መመዝገቢያ')
 with st.form('tx'):
  d=st.text_input('ቀን (የኢትዮጵያ ቀን)'); k=st.selectbox('ዓይነት',['ሽያጭ','ግዥ','የስራ ማስኬጃ ወጪ','ብድር ክፍያ','ሌላ']); desc=st.text_input('መግለጫ');r=st.number_input('ገቢ',0.0);e=st.number_input('ወጪ',0.0);n=st.text_area('ማስታወሻ')
  if st.form_submit_button('አስቀምጥ'):c.execute('INSERT INTO transactions(et_date,kind,description,revenue,expense,notes) VALUES(?,?,?,?,?,?)',(d,k,desc,r,e,n));c.commit();st.success('ተቀምጧል')
 st.dataframe(tx,use_container_width=True,hide_index=True);st.download_button('CSV አውርድ',tx.to_csv(index=False).encode('utf-8-sig'),'transactions.csv','text/csv')
elif menu.startswith('የደንበኛ'):
 st.subheader('የደንበኛ ትዕዛዞች')
 with st.form('order'):
  d=st.text_input('ቀን');customer=st.text_input('የደንበኛ ስም');product=st.selectbox('ምርት',['የሴቶች መደበኛ ቀሚስ','ሽፎን ቀሚስ','ቢጃማ','ጨርቅ','ሌላ']);q=st.number_input('ብዛት',1);price=st.number_input('ዋጋ',0.0);status=st.selectbox('ሁኔታ',['አዲስ','በስራ ላይ','ተጠናቋል','ተሰጥቷል','ተሰርዟል']);delivery=st.text_input('የመስጫ ቀን');notes=st.text_area('ማስታወሻ')
  if st.form_submit_button('አስቀምጥ'):c.execute('INSERT INTO orders(et_date,customer,product,qty,price,status,delivery_date,notes) VALUES(?,?,?,?,?,?,?,?)',(d,customer,product,q,price,status,delivery,notes));c.commit();st.success('ተመዝግቧል')
 st.dataframe(pd.read_sql_query('SELECT * FROM orders ORDER BY id DESC',c),use_container_width=True,hide_index=True)
elif menu.startswith('የብድር'):
 st.subheader('የብድር ክትትል');st.write('200,000 ብር | 5 ዓመት | 20 ሩብ ዓመታት | 12,600 ብር በሩብ ዓመት')
 df=pd.read_sql_query('SELECT * FROM loan ORDER BY installment_no',c)
 for _,row in df.iterrows():
  cols=st.columns([1,3,2,2,2]);cols[0].write(int(row.installment_no));cols[1].write(row.due_date);cols[2].write(f"{row.amount:,.0f} ብር");s=cols[3].selectbox('ሁኔታ',['ያልተከፈለ','ተከፍሏል'],index=0 if row.status=='ያልተከፈለ' else 1,key=f's{row.id}');pdte=cols[4].text_input('የክፍያ ቀን',row.paid_date or '',key=f'p{row.id}')
  if s!=row.status or pdte!=(row.paid_date or ''):c.execute('UPDATE loan SET status=?,paid_date=? WHERE id=?',(s,pdte,row.id));c.commit()
elif menu.startswith('የዋጋ'):
 st.subheader('የምርት ዋጋ ማስያ');a=st.number_input('የጨርቅ ወጪ',0.0);b=st.number_input('ክር/እቃ',0.0);d=st.number_input('የስራ ዋጋ',0.0);f=st.number_input('የተመደበ ቋሚ ወጪ',0.0);m=st.slider('የትርፍ መጠን (%)',0,100,30);cost=a+b+d+f;st.metric('ጠቅላላ ወጪ',f'{cost:,.2f} ብር');st.metric('የሚመከር ዋጋ',f'{cost*(1+m/100):,.2f} ብር')
elif menu.startswith('ሪፖርቶች'):
 r=tx.revenue.sum();e=tx.expense.sum();df=pd.DataFrame({'መለኪያ':['ጠቅላላ ገቢ','ጠቅላላ ወጪ','ትርፍ'],'መጠን':[r,e,r-e]});st.table(df);st.download_button('CSV አውርድ',df.to_csv(index=False).encode('utf-8-sig'),'report.csv','text/csv')
else:
 st.subheader('የቢዝነስ መገለጫ');st.markdown('**ባለቤት፦** እቴነሽ ጌታው\n\n**መነሻ ካፒታል፦** 220,000 ብር\n\n**የራስ ቁጠባ፦** 20,000 ብር\n\n**የወጣቶች ፈንድ ብድር፦** 200,000 ብር\n\n**ምርቶች፦** የሴቶች መደበኛ ቀሚስ፣ ሽፎን ቀሚስ')
 st.warning('የተረሱ የግዥ/ሽያጭ መረጃዎች በተለየ የታሪክ መረጃ ማጣሪያ መሰብሰብ ይገባል።')
c.close()
