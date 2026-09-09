from datetime import date, datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from services.api_football import APIFootball, APIError
from services.analytics import poisson_matrix, market_probs, outcome_probs

st.set_page_config(page_title="TITAN Racha", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
:root{color-scheme:dark}.stApp{background:#0b0c0f}.block-container{max-width:1200px;padding-top:1rem;padding-bottom:5rem}.brand{font-size:1.7rem;font-weight:900}.brand b{color:#ff9d1b}.sub{color:#8f939d}.card{background:linear-gradient(180deg,#17191e,#101115);border:1px solid #292d35;border-radius:18px;padding:16px;margin:8px 0}.tag{display:inline-block;background:#20242b;border-radius:999px;padding:4px 9px;margin-right:5px;font-size:.78rem}.accent{color:#ff9d1b}.green{color:#54d38b}.red{color:#ff6875}.small{font-size:.82rem;color:#9da2ad}.match{font-size:1.4rem;font-weight:850}.stButton>button{border-radius:12px}
</style>""", unsafe_allow_html=True)


def local_time(s):
    try: return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(ZoneInfo("America/Bogota")).strftime("%d/%m %H:%M")
    except Exception: return (s or "")[:16].replace("T"," ")

def rows(fixtures):
    out=[]
    for f in fixtures:
        fx=f.get("fixture",{}); teams=f.get("teams",{}); goals=f.get("goals",{})
        out.append({"ID":fx.get("id"),"Liga":f.get("league",{}).get("name","—"),"Hora":local_time(fx.get("date","")),"Local":teams.get("home",{}).get("name","—"),"Visitante":teams.get("away",{}).get("name","—"),"Estado":fx.get("status",{}).get("short","—"),"Marcador":f"{goals.get('home','-')} - {goals.get('away','-')}"})
    return pd.DataFrame(out)

def pct(x): return f"{x:.1%}" if x is not None else "—"

api=APIFootball()
if not api.configured:
    st.markdown('<div class="brand">🔥 TITAN <b>RACHA</b></div>',unsafe_allow_html=True)
    st.warning("Configura API_FOOTBALL_KEY en .env. No pegues tu clave en el código.")
    st.code("API_FOOTBALL_KEY=TU_CLAVE_AQUI")
    st.stop()

with st.sidebar:
    st.markdown("### ⚙️ TITAN Racha")
    if st.button("🔄 Limpiar caché / actualizar", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.caption("Hora mostrada: Colombia (UTC-5).")
    st.caption("Datos: API-Football. Los modelos son estimaciones, no garantías.")

st.markdown('<div class="brand">🔥 TITAN <b>RACHA</b></div>',unsafe_allow_html=True)
st.markdown('<div class="sub">Partidos · Tendencias · Ligas · Props · análisis cuantitativo</div>',unsafe_allow_html=True)
tabs=st.tabs(["⚽ Partidos","📈 Tendencias","🏆 Ligas","👤 Props"])

# PARTIDOS
with tabs[0]:
    c1,c2,c3,c4=st.columns([1,1,1.1,1.5])
    d=c1.date_input("Fecha",date.today(),format="DD/MM/YYYY")
    view=c2.selectbox("Estado",["Todos","En vivo","Finalizados","Próximos"])
    league=c3.text_input("Liga",placeholder="Premier, Colombia…")
    team=c4.text_input("Equipo",placeholder="Barcelona, Nacional…")
    try: data=api.fixtures_by_date(d.isoformat())
    except APIError as e: st.error(str(e)); data=[]
    df=rows(data)
    if not df.empty:
        live={"1H","HT","2H","ET","BT","P"}; final={"FT","AET","PEN"}
        if view=="En vivo": df=df[df.Estado.isin(live)]
        if view=="Finalizados": df=df[df.Estado.isin(final)]
        if view=="Próximos": df=df[~df.Estado.isin(live|final)]
        if league: df=df[df.Liga.str.contains(league,case=False,na=False)]
        if team: df=df[df.Local.str.contains(team,case=False,na=False)|df.Visitante.str.contains(team,case=False,na=False)]
    st.markdown(f"**Partidos encontrados:** {len(df)}")
    if df.empty: st.info("No hay partidos con esos filtros.")
    else:
        options=df.ID.tolist(); labels={r.ID:f"{r.Local} vs {r.Visitante} · {r.Liga}" for r in df.itertuples()}
        fid=st.selectbox("Abrir ficha",options,format_func=lambda x:labels[x])
        st.dataframe(df.drop(columns=["ID"]),hide_index=True,use_container_width=True)
        try:
            detail=api.fixture_detail(int(fid))[0]; pred=api.predictions(int(fid)); stats=api.fixture_statistics(int(fid)); events=api.fixture_events(int(fid)); lineups=api.lineups(int(fid)); injuries=api.injuries(int(fid)); odds=api.odds(int(fid))
            home=detail["teams"]["home"]; away=detail["teams"]["away"]
            st.markdown(f'<div class="card"><div class="small">{detail.get("league",{}).get("name")} · {detail.get("league",{}).get("round","")}</div><div class="match">{home["name"]} <span class="sub">VS</span> {away["name"]}</div><div class="small">{local_time(detail.get("fixture",{}).get("date",""))} · {detail.get("fixture",{}).get("status",{}).get("long","")}</div></div>',unsafe_allow_html=True)
            ph,pd,pa=outcome_probs(pred)
            a,b,c=st.columns(3); a.metric("1 · Local",pct(ph/100)); b.metric("X · Empate",pct(pd/100)); c.metric("2 · Visitante",pct(pa/100))
            pscore=pred[0].get("predictions",{}).get("score",{}) if pred else {}; st.caption(f"Predicción API: {pscore.get('fulltime',{}).get('home','—')} - {pscore.get('fulltime',{}).get('away','—')}")
            lamh=max(.25,ph/45); lama=max(.25,pa/45); mat=poisson_matrix(lamh,lama,5); mp=market_probs(mat)
            st.markdown("### 🎯 Poisson + mercados derivados")
            a,b,c,d4,e=st.columns(5); a.metric("Over 2.5",pct(mp["over25"])); b.metric("Under 2.5",pct(mp["under25"])); c.metric("BTTS",pct(mp["btts"])); d4.metric("Local",pct(mp["home"])); e.metric("Visitante",pct(mp["away"]))
            mdf=pd.DataFrame(mat,index=[f"{i}" for i in range(6)],columns=[f"{i}" for i in range(6)]); st.dataframe(mdf.style.format("{:.1%}"),use_container_width=True)
            t1,t2,t3,t4,t5=st.tabs(["📊 Estadísticas","⚡ Eventos","👥 Alineaciones","🚑 Bajas","💰 Cuotas"])
            with t1:
                sr=[]
                for block in stats:
                    vals={x.get("type"):x.get("value") for x in block.get("statistics",[])}; sr.append({"Equipo":block.get("team",{}).get("name"),"Posesión":vals.get("Ball Possession"),"Tiros":vals.get("Total Shots"),"A puerta":vals.get("Shots on Goal"),"Córners":vals.get("Corner Kicks"),"Faltas":vals.get("Fouls"),"Amarillas":vals.get("Yellow Cards"),"Paradas":vals.get("Goalkeeper Saves")})
                st.dataframe(pd.DataFrame(sr),hide_index=True,use_container_width=True)
            with t2:
                er=[]
                for x in events: er.append({"Min":x.get("time",{}).get("elapsed"),"Equipo":x.get("team",{}).get("name"),"Tipo":x.get("type"),"Detalle":x.get("detail"),"Jugador":x.get("player",{}).get("name")})
                st.dataframe(pd.DataFrame(er),hide_index=True,use_container_width=True)
            with t3:
                lr=[]
                for x in lineups:
                    for p in x.get("startXI",[]): lr.append({"Equipo":x.get("team",{}).get("name"),"Jugador":p.get("player",{}).get("name"),"Pos":p.get("player",{}).get("pos"),"Titular":"Sí"})
                st.dataframe(pd.DataFrame(lr),hide_index=True,use_container_width=True)
            with t4:
                ir=[{"Jugador":x.get("player",{}).get("name"),"Equipo":x.get("team",{}).get("name"),"Tipo":x.get("player",{}).get("type"),"Razón":x.get("player",{}).get("reason")} for x in injuries]
                st.dataframe(pd.DataFrame(ir),hide_index=True,use_container_width=True)
            with t5:
                if odds: st.json(odds[0] if len(odds)==1 else odds[:3])
                else: st.info("Sin cuotas disponibles para este partido/plan.")
        except APIError as e: st.error(str(e))

# TENDENCIAS
with tabs[1]:
    st.markdown("### 📈 Tendencias de la fecha")
    td=st.date_input("Fecha de tendencias",date.today(),format="DD/MM/YYYY",key="td")
    try: fx=api.fixtures_by_date(td.isoformat())
    except APIError as e: st.error(str(e)); fx=[]
    done=[f for f in fx if f.get("fixture",{}).get("status",{}).get("short") in {"FT","AET","PEN"}]
    tr=[]
    for f in done:
        gh=f.get("goals",{}).get("home"); ga=f.get("goals",{}).get("away")
        if gh is not None and ga is not None: tr.append({"Liga":f.get("league",{}).get("name"),"Local":f.get("teams",{}).get("home",{}).get("name"),"Visitante":f.get("teams",{}).get("away",{}).get("name"),"Goles":gh+ga,"BTTS":"Sí" if gh>0 and ga>0 else "No"})
    st.dataframe(pd.DataFrame(tr),hide_index=True,use_container_width=True)

# LIGAS
with tabs[2]:
    st.markdown("### 🏆 Ligas y clasificación")
    q=st.text_input("Buscar liga",placeholder="Premier League, Colombia…")
    try: ls=api.leagues(q=q or None)
    except APIError as e: st.error(str(e)); ls=[]
    lr=[{"ID":x.get("league",{}).get("id"),"Competición":x.get("league",{}).get("name"),"País":x.get("country",{}).get("name"),"Tipo":x.get("league",{}).get("type")} for x in ls[:80]]
    st.dataframe(pd.DataFrame(lr),hide_index=True,use_container_width=True)
    if lr:
        lid=st.number_input("League ID para standings",min_value=1,value=int(lr[0]["ID"]))
        season=st.number_input("Temporada",min_value=2020,max_value=2030,value=2026)
        try:
            s=api.standings(int(lid),int(season)); table=((s[0].get("league",{}).get("standings") or [[]])[0]) if s else []
            st.dataframe(pd.DataFrame([{"#":x.get("rank"),"Equipo":x.get("team",{}).get("name"),"PJ":x.get("all",{}).get("played"),"G":x.get("all",{}).get("win"),"E":x.get("all",{}).get("draw"),"P":x.get("all",{}).get("lose"),"GF":x.get("all",{}).get("goals",{}).get("for"),"GC":x.get("all",{}).get("goals",{}).get("against"),"Pts":x.get("points")} for x in table]),hide_index=True,use_container_width=True)
        except APIError as e: st.warning(str(e))

# PROPS
with tabs[3]:
    st.markdown("### 👤 Props de jugadores")
    c1,c2,c3=st.columns(3); pq=c1.text_input("Jugador",placeholder="Mbappé"); lid=c2.number_input("League ID",1,9999,39); sea=c3.number_input("Temporada",2020,2030,2026)
    if st.button("Buscar jugador",type="primary"):
        try:
            ps=api.players(pq,int(lid),int(sea)); rr=[]
            for x in ps[:50]:
                p=x.get("player",{}); stt=(x.get("statistics") or [{}])[0]; games=stt.get("games",{}); goals=stt.get("goals",{}); shots=stt.get("shots",{})
                rr.append({"Jugador":p.get("name"),"ID":p.get("id"),"Posición":games.get("position"),"PJ":games.get("appearences"),"Min":games.get("minutes"),"Goles":goals.get("total"),"Asist":goals.get("assists"),"Tiros":shots.get("total"),"A puerta":shots.get("on")})
            st.dataframe(pd.DataFrame(rr),hide_index=True,use_container_width=True)
        except APIError as e: st.error(str(e))

st.caption("TITAN Racha · implementación propia inspirada en funcionalidades observables públicamente en Racha Sports; no utiliza código propietario ni credenciales de terceros. Fuente de datos: API-Football.")
