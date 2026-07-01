import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime
import json
import os

st.set_page_config(page_title="ASX Market Tracker Engine", layout="wide")
st.title("📊 ASX Master Quantitative Command Center")

# --- TICKER TAPE UNIVERSE INDEX ---
components.html("""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{"symbols": [{"proName": "INDEX:XJO", "title": "ASX 200 Index"}, {"proName": "ASX:BHP", "title": "BHP Group"}, {"proName": "ASX:CBA", "title": "Commonwealth Bank"}, {"proName": "ASX:WBC", "title": "Westpac"}], "colorTheme": "light", "displayMode": "adaptive", "locale": "en"}
</script></div>""", height=50)

# --- UNIVERSE ARRAYS DEFINITION ---
ASX_50 = [
    "BHP.AX", "CBA.AX", "WBC.AX", "NAB.AX", "ANZ.AX", "MQG.AX", "WES.AX", "RIO.AX", "FMG.AX", "CSL.AX",
    "WDS.AX", "TLS.AX", "TCL.AX", "WOW.AX", "QBE.AX", "GMG.AX", "MIN.AX", "APA.AX", "QAN.AX", "SPK.AX",
    "REA.AX", "ALL.AX", "SHL.AX", "COH.AX", "IPL.AX", "BSL.AX", "PPT.AX", "WHC.AX", "ALQ.AX", "LYC.AX",
    "BEN.AX", "BOQ.AX", "BLD.AX", "CAR.AX", "SGP.AX", "DXS.AX", "CHC.AX", "GPT.AX", "MGR.AX", "VCX.AX",
    "AZJ.AX", "A2M.AX", "AMP.AX", "ANN.AX", "AST.AX", "ALX.AX", "EVN.AX", "IAG.AX", "MPL.AX", "SUN.AX"
]

ASX_100_ADDITIONS = [
    "ALU.AX", "ALX.AX", "AMP.AX", "ANN.AX", "APE.AX", "ARS.AX", "AWC.AX", "BEN.AX", "BKW.AX", "BOQ.AX", 
    "BSL.AX", "BWP.AX", "BXB.AX", "CAR.AX", "CGF.AX", "CHC.AX", "CIN.AX", "CLW.AX", "CNI.AX", "COH.AX", 
    "COL.AX", "CPU.AX", "CQR.AX", "CSR.AX", "CTC.AX", "CWN.AX", "CYP.AX", "DXS.AX", "EHE.AX", "ELD.AX", 
    "FLT.AX", "FPH.AX", "GEM.AX", "GOZ.AX", "GPT.AX", "HDN.AX", "HLI.AX", "HVN.AX", "IEL.AX", "IFL.AX", 
    "IFT.AX", "ILU.AX", "IPL.AX", "JBH.AX", "JHX.AX", "LLC.AX", "LNK.AX", "LYC.AX", "MGR.AX", "MND.AX"
]

ASX_200_ADDITIONS = [
    "A2B.AX", "ABG.AX", "AFI.AX", "AGL.AX", "AIN.AX", "ALK.AX", "AMI.AX", "AMP.AX", "ANG.AX", "AO1.AX",
    "APA.AX", "APE.AX", "API.AX", "APM.AX", "APX.AX", "ARB.AX", "ARE.AX", "ARG.AX", "ARU.AX", "ASB.AX",
    "ASM.AX", "ASG.AX", "AST.AX", "ASX.AX", "AUB.AX", "AVN.AX", "AVV.AX", "AWC.AX", "AWE.AX", "AWI.AX",
    "AX1.AX", "AZS.AX", "B4P.AX", "BAB.AX", "BAL.AX", "BAP.AX", "BCB.AX", "BCI.AX", "BFL.AX", "BGA.AX",
    "BGL.AX", "BGP.AX", "BHP.AX", "BIF.AX", "BKI.AX", "BKL.AX", "BKW.AX", "BLD.AX", "BLX.AX", "BML.AX",
    "BMT.AX", "BNA.AX", "BNL.AX", "BOA.AX", "BOQ.AX", "BOT.AX", "BOU.AX", "BPT.AX", "BRG.AX", "BRL.AX",
    "BRU.AX", "BSL.AX", "BTI.AX", "BTR.AX", "BVS.AX", "BWP.AX", "BXB.AX", "C6C.AX", "CAE.AX", "CAF.AX",
    "CAJ.AX", "CAR.AX", "CBA.AX", "CCV.AX", "CDA.AX", "CDD.AX", "CDP.AX", "CE1.AX", "CEL.AX", "CEN.AX",
    "CGC.AX", "CGF.AX", "CHC.AX", "CHH.AX", "CHL.AX", "CHR.AX", "CIE.AX", "CIM.AX", "CIN.AX", "CIP.AX",
    "CKF.AX", "CLA.AX", "CLH.AX", "CLQ.AX", "CLV.AX", "CL
