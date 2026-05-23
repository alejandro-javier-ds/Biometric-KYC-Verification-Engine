import streamlit as st
import os

st.set_page_config(page_title="Sentinel KYC | SOC Dashboard", layout="wide")

def fetch_system_logs(log_dir: str, lines: int = 15) -> str:
    if not os.path.exists(log_dir):
        return "SYS_WARN: Audit directory offline or not found."
    
    log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
    if not log_files:
        return "SYS_WARN: No audit logs available."
        
    latest_log = max([os.path.join(log_dir, f) for f in log_files], key=os.path.getctime)
    try:
        with open(latest_log, "r") as f:
            return "".join(f.readlines()[-lines:])
    except Exception as e:
        return f"SYS_ERROR: Log parsing failed. {str(e)}"

def initialize_soc_dashboard() -> None:
    st.title("Sentinel: Enterprise Biometric Audit & KYC")
    st.markdown("---")
    
    vault_dir = "evidence_vault"
    log_dir = "audit_logs"
    
    col_vault, col_telemetry = st.columns([0.7, 0.3])

    with col_vault:
        st.subheader("Biometric Evidence Vault")
        if os.path.exists(vault_dir):
            evidence_files = [f for f in os.listdir(vault_dir) if f.endswith(".mp4")]
            evidence_files.sort(key=lambda x: os.path.getctime(os.path.join(vault_dir, x)), reverse=True)
            
            if evidence_files:
                grid = st.columns(3)
                for idx, video_file in enumerate(evidence_files[:12]):
                    with grid[idx % 3]:
                        st.video(os.path.join(vault_dir, video_file))
                        st.caption(f"AUDIT ID: {video_file}")
            else:
                st.info("SYSTEM_IDLE: Awaiting biometric telemetry streams.")
        else:
            st.warning("SYSTEM_FAULT: Evidence vault directory offline.")
            
    with col_telemetry:
        st.subheader("System Telemetry & Logs")
        logs = fetch_system_logs(log_dir)
        st.code(logs, language="log")
        
        if st.button("Refresh Telemetry"):
            st.rerun()

if __name__ == "__main__":
    initialize_soc_dashboard()