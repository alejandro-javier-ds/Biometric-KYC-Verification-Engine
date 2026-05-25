import streamlit as st
import os
import pyodbc
import pandas as pd
from config import get_pyodbc_string
from vision_engine import run_live_sensor

st.set_page_config(page_title="Sentinel SOC | Modular Engine", layout="wide")

VAULT_DIR = "evidence_vault"

@st.cache_data(ttl=2)
def fetch_audit_telemetry() -> pd.DataFrame:
    try:
        conn = pyodbc.connect(get_pyodbc_string())
        query = """
            SELECT EventID, CaptureTimestamp, VerificationStatus, ConfidenceScore, 
                   RawVideoFilename, MeshVideoFilename, HardwareSource
            FROM BiometricAudit ORDER BY CaptureTimestamp DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

st.title("Sentinel: Modular Biometric Verification SOC")
st.markdown("---")

tab1, tab2 = st.tabs(["Live Biometric Sensor", "Forensic Evidence Vault"])

with tab1:
    st.markdown("### Escaner Optico Integrado")
    if st.button("Encender Motor de Vision", type="primary"):
        video_placeholder = st.empty()
        run_live_sensor(video_placeholder)
        st.success("EVIDENCIA CAPTURADA. Sincronizando con Base de Datos...")
        st.rerun()

with tab2:
    st.markdown("### Historial de Auditorias")
    df = fetch_audit_telemetry()
    
    if df.empty:
        st.info("La boveda esta vacia. Ve a la primera pestana y captura tu rostro.")
    else:
        for index, row in df.iterrows():
            status_icon = "SUCCESS" if row['VerificationStatus'] == 'SUCCESS' else "FAILED"
            confidence_pct = row['ConfidenceScore'] * 100
            
            with st.expander(f"[{status_icon}] AUDIT ID: #{row['EventID']} | MATCH: {confidence_pct:.2f}% | DATE: {row['CaptureTimestamp']}"):
                vid_col1, vid_col2, meta_col = st.columns([0.4, 0.4, 0.2])
                
                raw_path = os.path.join(VAULT_DIR, row['RawVideoFilename'])
                mesh_path = os.path.join(VAULT_DIR, row['MeshVideoFilename'])

                with vid_col1:
                    st.caption("OPTICAL SENSOR (RAW)")
                    if os.path.exists(raw_path):
                        st.video(raw_path)
                    else:
                        st.error("Archivo no encontrado")

                with vid_col2:
                    st.caption("BIOMETRIC MESH (ALGORITHMIC)")
                    if os.path.exists(mesh_path):
                        st.video(mesh_path)
                    else:
                        st.error("Archivo no encontrado")

                with meta_col:
                    st.markdown("**Telemetry Data**")
                    st.markdown(f"- **Event ID:** `#{row['EventID']}`")
                    st.markdown(f"- **Confidence:** `{row['ConfidenceScore']}`")