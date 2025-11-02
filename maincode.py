import streamlit as st
import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from nodevectors import Node2Vec
import hdbscan
from sklearn.manifold import TSNE
from datetime import datetime
import time
import openai
from collections import defaultdict

# === GLOBAL API KEYS & URLs ===
ETHERSCAN_API_KEY = "N3D8E5XJ2MUABPE5BST1I54IFSA5TKRDAW"
BASE_URL_ETH_V1 = "https://api.etherscan.io/v2/api"
BASE_URL_ETH_V2 = "https://api.etherscan.io/v2/api"
ESPLORA_URL = "https://blockstream.info/api"

# === UI Setup ===
st.set_page_config(page_title="Crypto Multi-Tool Dashboard", page_icon="🟦", layout="wide")

# ====== Currency Converter Section ======
def currency_convert(symbol="bitcoin", target_currency="usd", amount=1.0):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies={target_currency}"
        r = requests.get(url)
        price = r.json()[symbol][target_currency]
        return amount * price
    except Exception:
        return "-"

st.markdown("""
    <div style='text-align:center; margin-bottom:18px; margin-top:8px'>
        <span style='font-size:2.8em; color:#00BFFF; font-family:monospace; font-weight:900; letter-spacing:1.5px;'>
            PROJECT SN
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .module{background:#FFFFFF;border-radius:16px;padding:22px;box-shadow:0 2px 18px #0485c730;}
        .link-btn{border-radius:50%;width:62px;height:62px;display:inline-flex;align-items:center;justify-content:center;font-size:30px;font-weight:800;margin:12px;border:2.8px solid #1c3247;background:#00bfff;color:#191a22;text-decoration:none;transition:background 0.14s}
        .link-btn:hover{background:#FFD700;color:#191a22;border:3px solid #FFD700;text-decoration:none;}
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 2])
with col1:
    st.write("### BTC Currency Converter")
    amount_btc = st.number_input("Amount in BTC", min_value=0.0, value=0.1, key="btc_amt")
    tgt_cur1 = st.selectbox("To Currency", options=["inr", "usd", "eur", "gbp"], key="btc_curr")
    res_btc = currency_convert("bitcoin", tgt_cur1, amount_btc)
    st.success(f"{amount_btc} BTC = {res_btc if isinstance(res_btc, (int,float)) else res_btc} {tgt_cur1.upper()}")

with col2:
    st.write("### ETH Currency Converter")
    amount_eth = st.number_input("Amount in ETH", min_value=0.0, value=0.5, key="eth_amt")
    tgt_cur2 = st.selectbox("To Currency", options=["inr","usd","eur","gbp"], key="eth_curr")
    res_eth = currency_convert("ethereum", tgt_cur2, amount_eth)
    st.success(f"{amount_eth} ETH = {res_eth if isinstance(res_eth,(int,float)) else res_eth} {tgt_cur2.upper()}")

st.markdown("<hr>", unsafe_allow_html=True)

# new typed
from streamlit.components.v1 import html
import streamlit as st

PAGES = [
    {"title": "Ethereum Wallet Transaction Explorer", "icon": "https://cryptologos.cc/logos/ethereum-eth-logo.png?v=026", "color": "#00BFFF"},
    {"title": "Bitcoin Address Transaction Explorer", "icon": "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=026", "color": "#FFD700"},
    {"title": "Ethereum Bridge Transaction Finder", "icon": "https://cryptologos.cc/logos/ethereum-eth-logo.png?v=026", "color": "#4CB7FF"},
    {"title": "Bitcoin Bridge Transaction Finder", "icon": "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=026", "color": "#FDAA00"},
    {"title": "Ethereum Transaction Clustering", "icon": "https://cryptologos.cc/logos/ethereum-eth-logo.png?v=026", "color": "#00BFFF"},
    {"title": "Bitcoin Transaction Clustering", "icon": "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=026", "color": "#FFD700"},
    {"title": "Bitcoin Suspicious Transaction Analyzer", "icon": "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=026", "color": "#FDAA00"},
    {"title": "Ethereum Suspicious Transaction Analyzer", "icon": "https://cryptologos.cc/logos/ethereum-eth-logo.png?v=026", "color": "#00BFFF"},
]

st.sidebar.markdown("""
    <style>
        .sidebtn {
            display: flex;
            align-items: center;
            background: #181B2A;
            border-radius: 11px;
            padding: 13px 20px;
            margin-bottom: 11px;
            border: 2.2px solid #20244C;
            font-size: 1.1em;
            font-weight: 800;
            color: #FFFFFF !important;
            text-colour: #FFFFFF !important;
            cursor: pointer;
            transition: background 0.15s, border 0.15s;
        }
        .sidebtn.selected { background: #111426!important; border: 2.2px solid #00BFFF!important; color: #00FAFC!important; }
        .sidebtn:hover { background: #00BFFF; color: #191c22; }
        .sidebtn img { width:32px;height:32px;border-radius:50%;margin-right:15px;margin-left:1px;box-shadow:0 1px 2px #1113;}
    </style>
""", unsafe_allow_html=True)

if "sidebar_page" not in st.session_state: st.session_state.sidebar_page = 0

for idx, page in enumerate(PAGES):
    clicked = st.sidebar.button(
        f":blue[{page['title']}]",
        key=f"sidebtn{idx}"
    )
    is_selected = st.session_state.sidebar_page == idx
    icon_html = f"<img src='{page['icon']}' alt=''/>"
    color = page['color']
    container_class = "sidebtn selected" if is_selected else "sidebtn"
    text_color = "#00BFFF" if 'Ethereum' in page["title"] else "#FFD700" if 'Bitcoin' in page["title"] else color
    custom_html = f"<div class='{container_class}' style='border-left:8px solid {color}; color:{text_color}'>{icon_html}{page['title']}</div>"
    html(custom_html, height=48)
    if clicked:
        st.session_state.sidebar_page = idx


page = PAGES[st.session_state.sidebar_page]["title"]

page = PAGES[st.session_state.sidebar_page]["title"]



# -------- Ethereum Wallet Transaction Explorer (First Ethereum Module) --------
def eth_wallet_explorer():
    st.markdown("""
    <style>
    body, .stApp {background-color: #0E1117;}
    h1, h3, h4, h5, h6, .stText, .stMarkdown, .stDataFrame, .stTable, .stJson {color:#EAEAEA;}
    .stTextInput label div, .stTextInput label {color:#fff !important; font-size:17px;}
    .stTextInput > div > div > input {background: #1E222A !important; color: #fff; font-size: 16px;}
    .stButton>button {background-color: #00BFFF; color: #0E1117 !important; border: none; font-weight: 700; border-radius: 6px;}
    .stDataFrame, .stTable {background: #1E222A; color: #EAEAEA;}
    .stAlert {background: #FFD700; color: #0E1117;margin:10px;}
    .stDownloadButton>button {background: #FFD700;color: #0E1117;font-weight:bold;}
    hr {border: 1.5px solid #00BFFF;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:25px;">
        <img src="https://cryptologos.cc/logos/ethereum-eth-logo.png?v=026" width="58"/>
        <h1 style="color:#00BFFF; margin-bottom:0; font-family:monospace;">
            Ethereum Wallet Explorer
        </h1>
    </div>
    <hr/>
    """, unsafe_allow_html=True)
    st.markdown("<h4 style='color:#EAEAEA'>Track and analyze all Ethereum wallet transactions in full detail with a blockchain cyberstyle dashboard.</h4>", unsafe_allow_html=True)

    address = st.text_input("Enter Ethereum address (0x...)", value="0x1fD35bB2FFa949Fd90a47a945B5487575F24bfaB", max_chars=42)

    def fetch_all_transactions(address):
        PAGE_SIZE = 10000
        CHAIN_ID = 1
        def fetch_tx_list(module_action, address):
            startblock = 0
            endblock = 99999999
            all_tx = []
            while True:
                url = (
                    f"{BASE_URL_ETH_V1}?chainid={CHAIN_ID}"
                    f"&module=account"
                    f"&action={module_action}"
                    f"&address={address}"
                    f"&startblock={startblock}"
                    f"&endblock={endblock}"
                    f"&page=1"
                    f"&offset={PAGE_SIZE}"
                    f"&sort=asc"
                    f"&apikey={ETHERSCAN_API_KEY}"
                )
                r = requests.get(url)
                data = r.json()
                if data.get("status") != "1" or not data.get("result"):
                    break
                tx_list = data["result"]
                all_tx += tx_list
                if len(tx_list) < PAGE_SIZE:
                    break
                try:
                    startblock = int(tx_list[-1]['blockNumber']) + 1
                except Exception:
                    break
            return all_tx

        normal = fetch_tx_list("txlist", address)
        token = fetch_tx_list("tokentx", address)
        internal = fetch_tx_list("txlistinternal", address)
        all_txs = normal + token + internal
        seen = set()
        unique_txs = []
        for tx in all_txs:
            h = tx.get("hash")
            if h and h not in seen:
                seen.add(h)
                unique_txs.append(tx)
        return unique_txs

    requested_columns = [
        ("hash", "Transaction Hash"),
        ("blockNumber", "Block Number"),
        ("blockHash", "Block Hash"),
        ("timeStamp", "Timestamp"),
        ("from", "From Address"),
        ("to", "To Address"),
        ("value", "Value (Eth/Wei)"),
        ("gas", "Gas Limit"),
        ("gasUsed", "Gas Used"),
        ("gasPrice", "Gas Price"),
        ("maxFeePerGas", "Max Fee Per Gas"),
        ("maxPriorityFeePerGas", "Max Priority Fee Per Gas"),
        ("nonce", "Nonce"),
        ("input", "Input Data"),
        ("type", "Tx Type"),
        ("isError", "Status"),
        ("contractAddress", "Contract Address"),
        ("cumulativeGasUsed", "Cumulative Gas Used"),
        ("logIndex", "Logs Count"),
        ("logsBloom", "Logs Bloom"),
        ("methodId", "Method ID"),
        ("functionName", "Function Name"),
        ("chainId", "Chain ID"),
        ("transactionIndex", "Transaction Index"),
        ("r", "Signature R"),
        ("s", "Signature S"),
        ("v", "Signature V"),
        ("baseFeePerGas", "Base Fee Per Gas"),
        ("effectiveGasPrice", "Effective Gas Price"),
        ("miner", "Miner/Validator"),
        ("confirmations", "Confirmations Count")
    ]

    def highlight_cols(val):
        try:
            value = float(val)
            if value > 100 * 1e18:
                return 'background-color: #FFD700; color:#0E1117; font-weight:700;'
            elif value > 10*1e18:
                return 'background-color: #00FF88; color:#0E1117; font-weight:700;'
        except:
            pass
        return ''

    if st.button("Fetch & Display All Transactions - ETH", type="primary"):
        with st.spinner("Loading all transactions and metadata from chain..."):
            txs = fetch_all_transactions(address)
            if not txs:
                st.error("No transactions found or invalid address.")
            else:
                df = pd.DataFrame(txs)
                df["Date/Time"] = pd.to_datetime(df["timeStamp"], unit='s', utc=True).dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                if "value" in df:
                    df["Value (ETH)"] = pd.to_numeric(df["value"], errors="coerce") / 1e18
                display_cols = [(api, ui) for api, ui in requested_columns if api in df]
                col_renames = {api: ui for api, ui in display_cols}
                keep_cols = [api for api, ui in display_cols]
                table = df[keep_cols + (["Date/Time", "Value (ETH)"] if "value" in df else [])].rename(columns=col_renames)
                table.insert(0, "S. No.", range(1, 1+len(table)))
                if "Value (Eth/Wei)" in table:
                    table = table.style.applymap(highlight_cols, subset=["Value (Eth/Wei)"])
                st.dataframe(table, use_container_width=True, hide_index=True)
                st.markdown("<hr/><center><span style='color:#00BFFF;font-size:1.1em;'>Data provided by Etherscan API · Crypto Dashboard 2025</span></center>", unsafe_allow_html=True)

# -------- Bitcoin Address Transaction Explorer (First Bitcoin Module) --------
def btc_wallet_explorer():
    st.markdown("""
    <style>
    .stApp {background: #191c22;}
    h1, h4, .stMarkdown, .stDataFrame, .stTable {color: #fff;}
    .stTextInput label div, .stTextInput label {color:#fff !important; font-weight:650;}
    .stTextInput>div>div>input {background: #232732 !important; color: #00ffc3; font-size: 17px;}
    .stButton>button {background-color: #00BFFF; color: #191c22 !important; border: none; font-weight: 700;}
    .stDataFrame, .stTable, .css-1d391kg {background: #20222a; color: #fff;}
    hr {border: 1.5px solid #00BFFF;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:18px;">
        <img src="https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=026" width="38"/>
        <h1 style="color:#00BFFF; font-family:monospace;">Bitcoin Address Explorer</h1>
    </div>
    <hr>
    """, unsafe_allow_html=True)
    st.markdown("<h4 style='color:#EAEAEA'>Live BTC transaction analytics—just paste any Bitcoin address below.</h4>", unsafe_allow_html=True)

    address = st.text_input("Enter Bitcoin Address", value="bc1qfcmp4gmuz2uhkaazluexhwm32repaj78kc9jsw", max_chars=42)

    def fetch_txs(address):
        url = f"{ESPLORA_URL}/address/{address}/txs"
        r = requests.get(url)
        if r.status_code != 200:
            return []
        return r.json()

    def fetch_tx_details(txid):
        url = f"{ESPLORA_URL}/tx/{txid}"
        r = requests.get(url)
        if r.status_code != 200:
            return {}
        return r.json()

    def sat_to_btc(sat):
        return sat / 1e8

    def flatten_tx(tx):
        # Collect details
        txid = tx.get("txid")
        fee = sat_to_btc(tx.get("fee", 0))
        size = tx.get("size")
        weight = tx.get("weight")
        version = tx.get("version")
        locktime = tx.get("locktime")
        vsize = tx.get("vsize")
        confirmed = tx.get("status", {}).get("confirmed", False)
        block_hash = tx.get("status", {}).get("block_hash", "")
        block_height = tx.get("status", {}).get("block_height", "")
        block_time = tx.get("status", {}).get("block_time", "")
        timestamp = pd.to_datetime(block_time, unit='s', utc=True) if block_time else ""
        status = "confirmed" if confirmed else "unconfirmed"

        vin = tx.get("vin", [])
        vout = tx.get("vout", [])
        input_addresses = []
        output_addresses = []
        total_input_value = 0
        total_output_value = 0
        input_txids = []
        input_values = []
        output_values = []
        tx_types = set()
        for vin_item in vin:
            prev = vin_item.get("prevout", {})
            in_addr = prev.get("scriptpubkey_address", None)
            if in_addr:
                input_addresses.append(in_addr)
            input_txids.append(vin_item.get("txid"))
            input_values.append(sat_to_btc(prev.get("value", 0)))
            total_input_value += sat_to_btc(prev.get("value", 0))

        for vout_item in vout:
            out_addr = vout_item.get("scriptpubkey_address", None)
            out_type = vout_item.get("scriptpubkey_type", "")
            if out_addr:
                output_addresses.append(out_addr)
            output_values.append(sat_to_btc(vout_item.get("value", 0)))
            total_output_value += sat_to_btc(vout_item.get("value", 0))
            if out_type:
                tx_types.add(out_type)

        change_value = total_input_value - total_output_value
        tx_type = ",".join(tx_types)

        mempool_time = tx.get("mempool_time", "")
        replaced_by = tx.get("replaced_by", "")
        replaced_txids = tx.get("replaced_txids", "")
        fee_rate = (fee / size * 1e8) if size and size > 0 else None
        # Flatten witness/scripts for input/output for display
        scripts_in = "; ".join(str(v.get('script_sig', '')) for v in vin)
        scripts_out = "; ".join(str(v.get('scriptpubkey_asm', '')) for v in vout)
        input_count = len(vin)
        output_count = len(vout)
        return {
            "txid": txid,
            "version": version,
            "locktime": locktime,
            "size": size,
            "weight": weight,
            "vsize": vsize,
            "fee": fee,
            "fee_rate": fee_rate,
            "status": status,
            "block_hash": block_hash,
            "block_height": block_height,
            "timestamp": timestamp,
            "confirmed": confirmed,
            "input_count": input_count,
            "output_count": output_count,
            "input_txids": ", ".join(str(i) for i in input_txids if i),
            "input_addresses": ", ".join(input_addresses),
            "input_values": ", ".join([f"{v:.8f}" for v in input_values]),
            "output_addresses": ", ".join(output_addresses),
            "output_values": ", ".join([f"{v:.8f}" for v in output_values]),
            "change_value": f"{change_value:.8f}" if change_value else "",
            "total_input_value": f"{total_input_value:.8f}",
            "total_output_value": f"{total_output_value:.8f}",
            "transaction_type": tx_type,
            "scripts_in": scripts_in,
            "scripts_out": scripts_out,
            "replaced_by": replaced_by,
            "replaced_txids": ", ".join(str(x) for x in replaced_txids) if isinstance(replaced_txids, list) else replaced_txids,
            "mempool_time": mempool_time
        }

    if st.button("Fetch & Analyze - BTC"):
        with st.spinner("Loading data from Blockstream..."):
            txs = fetch_txs(address)
            if not txs:
                st.error("No transactions found or address invalid!")
            else:
                st.success(f"Found {len(txs)} transaction(s) for {address}")
                tx_table = []
                for tx in txs:
                    tx_details = fetch_tx_details(tx.get("txid"))
                    tx_table.append(flatten_tx(tx_details))
                table = pd.DataFrame(tx_table)
                table.index = range(1, len(table)+1)
                table.index.name = "S. No."
                st.dataframe(table, use_container_width=True)
                st.markdown("<hr/><center><span style='color:#00BFFF;font-size:1.1em;'>Powered by Blockstream Esplora API · Crypto Dashboard 2025</span></center>", unsafe_allow_html=True)

# -------- Ethereum Bridge Transaction Finder --------
def eth_bridge_finder():
    BRIDGE_CONTRACTS = [
        "0x98f3c9e6e3face36baad05fe09d375ef1464288b",  # Wormhole
        "0x8731d54e9d02c286767d56ac03e8037c07e01e98",  # Stargate
        "0x22d0f1f116b5752a7c0a002d5b09cc0e4a2c3c08",  # Celer
        "0x0d2f88d0a2d961447d5779f4d1ab6bc1cce4b300",  # Synapse
        "0x5aEa563B84a1e3932A1d960b08843F537bC7dB2a",  # Multichain example
    ]

    st.markdown("""
    <style>
    body, .stApp {background-color: #191c22;}
    h1, h4, .stMarkdown, .stDataFrame, .stTable {color: #fff;}
    .stTextInput label, .stTextInput label div {color:#fff !important; font-weight:650;}
    .stTextInput>div>div>input {background: #232732 !important; color: #00ffc3; font-size: 17px;}
    .stButton>button {background-color: #00BFFF; color: #191c22 !important; border: none; font-weight: 700;}
    .stDataFrame, .stTable {background: #20222a; color: #fff;}
    hr {border: 1.5px solid #00BFFF;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:18px;">
        <img src="https://cryptologos.cc/logos/ethereum-eth-logo.png?v=026" width="34"/>
        <h1 style="color:#00BFFF; font-family:monospace;">Ethereum Bridge Transaction Explorer</h1>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    wallet = st.text_input("Ethereum Wallet Address", value="0x1fD35bB2FFa949Fd90a47a945B5487575F24bfaB", max_chars=42)

    def fetch_all_txs(wallet):
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "txlist",
            "address": wallet,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "asc",
            "apikey": ETHERSCAN_API_KEY
        }
        txs = []
        resp = requests.get(url, params=params)
        data = resp.json()
        if data.get("status") == "1":
            txs = data["result"]
        return txs

    def filter_bridge_txs(txs, bridge_contracts):
        bridge_contracts = set([addr.lower() for addr in bridge_contracts])
        return [tx for tx in txs if tx["to"].lower() in bridge_contracts]

    if st.button("Find Bridge Transactions - ETH"):
        with st.spinner(f"Fetching and filtering transactions for {wallet}..."):
            txs = fetch_all_txs(wallet)
            bridge_txs = filter_bridge_txs(txs, BRIDGE_CONTRACTS)
            df = pd.DataFrame(bridge_txs)
            if not df.empty:
                columns = ["hash", "blockNumber", "timeStamp", "from", "to", "value", "input"]
                df = df[columns]
                df["time"] = pd.to_datetime(df["timeStamp"], unit='s', utc=True) if "timeStamp" in df else df["timeStamp"]
                df = df.rename(columns={"time":"UTC Time"})
                df.insert(0, "S. No.", range(1, 1+len(df)))
                st.success(f"Found {len(df)} bridge transactions!")
                st.dataframe(df, use_container_width=True)
                st.download_button("Download CSV", df.to_csv(index=False), "cross_bridge_transactions.csv")
            else:
                st.warning("No bridge transactions found for this wallet.")

# -------- Bitcoin Bridge Transaction Finder (Identical UI & Logic But BTC) --------
def btc_bridge_finder():
    BRIDGE_CONTRACTS = [  # Same as ETH example, adapt as needed
        "0x98f3c9e6e3face36baad05fe09d375ef1464288b",
        "0x8731d54e9d02c286767d56ac03e8037c07e01e98",
        "0x22d0f1f116b5752a7c0a002d5b09cc0e4a2c3c08",
        "0x0d2f88d0a2d961447d5779f4d1ab6bc1cce4b300",
        "0x5aEa563B84a1e3932A1d960b08843F537bC7dB2a",
    ]

    st.markdown("""
    <style>
    body, .stApp {background-color: #191c22;}
    h1, h4, .stMarkdown, .stDataFrame, .stTable {color: #fff;}
    .stTextInput label, .stTextInput label div {color:#fff !important; font-weight:650;}
    .stTextInput>div>div>input {background: #232732 !important; color: #00ffc3; font-size: 17px;}
    .stButton>button {background-color: #00BFFF; color: #191c22 !important; border: none; font-weight: 700;}
    .stDataFrame, .stTable {background: #20222a; color: #fff;}
    hr {border: 1.5px solid #00BFFF;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:18px;">
        <img src="https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=026" width="34"/>
        <h1 style="color:#00BFFF; font-family:monospace;">Bitcoin Bridge Transaction Explorer</h1>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    wallet = st.text_input("Bitcoin Wallet Address", value="bc1qfcmp4gmuz2uhkaazluexhwm32repaj78kc9jsw", max_chars=42)

    # Placeholder stub since Bitcoin bridges are different, implement if API available
    st.info("Bitcoin Bridge transaction finder not implemented yet.")

# -------- Ethereum Transaction Clustering --------
def eth_address_clustering():
    st.markdown('<h2 style="color:#00BFFF">Ethereum Address Clustering (Community Detection)</h2><hr>', unsafe_allow_html=True)
    wallet = st.text_input("Ethereum Wallet Address", value="", max_chars=42)

    def fetch_eth_txs(wallet):
        url = f"{BASE_URL_ETH_V2}?chainid=1&module=account&action=txlist&address={wallet}&page=1&offset=10000&sort=asc&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url)
        data = r.json()
        if data.get("status") == "1" and data.get("result"):
            return data["result"]
        else:
            return []

    def build_graph_from_txs(txs):
        G = nx.DiGraph()
        for tx in txs:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower() if tx.get("to") else None
            if from_addr and to_addr:
                G.add_edge(from_addr, to_addr)
        return G

    if st.button("Cluster & Visualize - ETH"):
        txs = fetch_eth_txs(wallet)
        G = build_graph_from_txs(txs)
        if G.number_of_nodes() == 0:
            st.warning("No data to analyze.")
            return
        communities = nx.algorithms.community.label_propagation_communities(G.to_undirected())
        clusters = {}
        for i, comm in enumerate(communities):
            for node in comm:
                clusters[node] = i
        color_map = [clusters.get(node, 0) for node in G.nodes()]
        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(14, 9))
        nx.draw(G, pos, with_labels=True, node_color=color_map, cmap="tab20", node_size=400, edge_color="gray")
        plt.title("Ethereum Address Clusters (NetworkX Label Propagation)")
        st.pyplot(plt)
        df = pd.DataFrame({"address": list(G.nodes()), "cluster": color_map})
        st.markdown("#### Address Clusters Table")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Address Clusters CSV", df.to_csv(index=False), "eth_address_clusters.csv")


# -------- Bitcoin Transaction Clustering --------
import streamlit as st
import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def btc_address_clustering():
    st.markdown('<h2 style="color:#00BFFF">Bitcoin Address Clustering (Community Detection)</h2><hr>', unsafe_allow_html=True)
    wallet = st.text_input("Bitcoin Wallet Address", value="", max_chars=42)
    MAX_TXS = 100

    def fetch_txs(address, max_count=MAX_TXS):
        url = f"{ESPLORA_URL}/address/{address}/txs"
        r = requests.get(url)
        if r.status_code != 200:
            return []
        return r.json()[:max_count]

    def build_graph_from_txs(txs):
        G = nx.DiGraph()
        for tx in txs:
            txid = tx.get("txid")
            tx_inputs = tx.get("vin", [])
            tx_outputs = tx.get("vout", [])
            in_addrs = set()
            for inp in tx_inputs:
                prev = inp.get("prevout")
                src = prev.get("scriptpubkey_address") if prev else None
                if src: in_addrs.add(src)
            value_map = {}
            for out in tx_outputs:
                dest = out.get("scriptpubkey_address")
                if dest:
                    value_map.setdefault(dest, 0)
            for src in in_addrs:
                for dest in value_map:
                    G.add_edge(src, dest)
        return G

    if st.button("Cluster & Visualize - BTC"):
        txs = fetch_txs(wallet)
        G = build_graph_from_txs(txs)
        if G.number_of_nodes() == 0:
            st.warning("No data to analyze.")
            return
        # Community detection (Label Propagation - works on directed and undirected)
        communities = nx.algorithms.community.label_propagation_communities(G.to_undirected())
        clusters = {}
        for i, comm in enumerate(communities):
            for node in comm:
                clusters[node] = i
        color_map = [clusters.get(node, 0) for node in G.nodes()]
        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(14, 9))
        nx.draw(G, pos, with_labels=True, node_color=color_map, cmap="tab20", node_size=400, edge_color="gray")
        plt.title("Bitcoin Address Clusters (NetworkX Label Propagation)")
        st.pyplot(plt)
        df = pd.DataFrame({"address": list(G.nodes()), "cluster": color_map})
        st.markdown("#### Address Clusters Table")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Address Clusters CSV", df.to_csv(index=False), "btc_address_clusters.csv")


# -------- Bitcoin Suspicious Transaction Analyzer --------
def btc_suspicious_analyzer():
    BLACKLISTED_ADDRESSES = {
        "1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
        "1CounterpartyXXXXXXXXXXXXXXXUWLpVr",
        "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
    }
    SUSPICIOUS_SCORE_THRESHOLD = 0.3
    BURST_WINDOW_SECONDS = 3600
    MAX_TXS = 250

    st.markdown("""
    <style>
    .stApp {background-color: #161622;}
    h1, h4, .stMarkdown, .stDataFrame, .stTable { color:#EAEAEA;}
    .stTextInput label div, .stTextInput label { color:#EAEAEA !important; font-weight:650;}
    .stTextInput>div>div>input {background: #1E222A !important; color: #00ffc3; font-size: 17px;}
    .stButton>button {background-color: #00BFFF; color: #191c22 !important; border: none; font-weight: 700;}
    .stDataFrame, .stTable {background: #1E222A; color: #fff;}
    hr {border: 1.5px solid #00BFFF;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:18px;">
        <img src="https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=026" width="38"/>
        <h1 style="color:#00BFFF; font-family:monospace;">Bitcoin Suspicious Transaction Analyzer (Advanced)</h1>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    address = st.text_input("Enter Bitcoin Address", value="bc1qfcmp4gmuz2uhkaazluexhwm32repaj78kc9jsw", max_chars=42)

    def fetch_txids(address, max_count=MAX_TXS):
        r = requests.get(f"{ESPLORA_URL}/address/{address}/txs")
        if r.status_code != 200:
            return []
        txs = r.json()
        return [tx["txid"] for tx in txs][:max_count]

    def fetch_tx(txid):
        r = requests.get(f"{ESPLORA_URL}/tx/{txid}")
        if r.status_code != 200:
            return {}
        return r.json()

    def sat_to_btc(sat):
        return sat / 1e8

    def burst_factor(timestamps):
        if len(timestamps) <= 1:
            return 0
        timestamps.sort()
        bursts = 0
        for i in range(len(timestamps)-1):
            if (timestamps[i+1] - timestamps[i]).total_seconds() <= BURST_WINDOW_SECONDS:
                bursts += 1
        return bursts

    def suspiciousness_score(total_value, freq, mixing, burst, blacklist_hit):
        score = total_value * (freq + 1) * (mixing + 1)
        score += burst * 0.05
        if blacklist_hit:
            score *= 5
        return score

    if st.button("Fetch & Analyze Suspicious BTC"):
        st.info(f"🔍 Fetching transactions for address: {address}")
        txids = fetch_txids(address)
        G = nx.DiGraph()
        edges_table = []
        node_data = defaultdict(lambda: {
            "total_received": 0,
            "freq": 0,
            "senders": set(),
            "timestamps": [],
            "blacklisted": False
        })

        for txid in txids:
            tx = fetch_tx(txid)
            ts = tx.get("status", {}).get("block_time", None)
            ts_human = datetime.utcfromtimestamp(ts) if ts else None
            vin = tx.get("vin", [])
            vout = tx.get("vout", [])

            sources = set()
            for inp in vin:
                prev = inp.get("prevout")
                src_addr = prev.get("scriptpubkey_address") if prev else None
                if src_addr:
                    sources.add(src_addr)

            for out in vout:
                dest = out.get("scriptpubkey_address")
                val_btc = sat_to_btc(out.get("value", 0))
                if not dest:
                    continue
                for src in sources:
                    G.add_edge(src, dest, value=val_btc, txid=txid, timestamp=ts_human)
                    edges_table.append({
                        "From": src,
                        "To": dest,
                        "Value (BTC)": val_btc,
                        "Time": ts_human,
                        "TxID": txid
                    })
                node = node_data[dest]
                node["total_received"] += val_btc
                node["freq"] += 1
                node["senders"].update(sources)
                if ts_human:
                    node["timestamps"].append(ts_human)
                if dest in BLACKLISTED_ADDRESSES:
                    node["blacklisted"] = True

        suspicious_list = []
        for addr, stats in node_data.items():
            burst = burst_factor(stats["timestamps"])
            score = suspiciousness_score(
                stats["total_received"],
                stats["freq"],
                len(stats["senders"]),
                burst,
                stats["blacklisted"]
            )
            suspicious_list.append({
                "Address": addr,
                "Total Received (BTC)": round(stats["total_received"], 8),
                "Frequency": stats["freq"],
                "Unique Senders": len(stats["senders"]),
                "Burst Count": burst,
                "Blacklisted": stats["blacklisted"],
                "Suspiciousness Score": score
            })

        df_suspicious = pd.DataFrame(suspicious_list).sort_values("Suspiciousness Score", ascending=False)
        flagged = df_suspicious[df_suspicious["Suspiciousness Score"] > SUSPICIOUS_SCORE_THRESHOLD]

        st.success(f"📊 Total Endpoints Analyzed: {len(df_suspicious)} | 🚨 Flagged Suspicious: {len(flagged)}")
        st.dataframe(flagged, use_container_width=True)

        suspicious_addrs = set(flagged['Address'])
        sub_edges = [(src, tgt) for src, tgt in G.edges() if tgt in suspicious_addrs]
        subG = G.edge_subgraph(sub_edges).copy()

        if subG.number_of_nodes() > 0:
            st.markdown("### 🕸️ Network Graph of Suspicious Cash-out Paths")
            node_colors = []
            for n in subG.nodes:
                if n in suspicious_addrs and n in BLACKLISTED_ADDRESSES:
                    node_colors.append("red")
                elif n in suspicious_addrs:
                    node_colors.append("orange")
                else:
                    node_colors.append("skyblue")
            plt.figure(figsize=(16, 11))
            pos = nx.spring_layout(subG, seed=42)
            nx.draw(subG, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=800, font_size=7)
            plt.title("Suspicious BTC Transactions — Advanced Heuristic Detection")
            st.pyplot(plt)
        else:
            st.warning("No suspicious endpoints found above threshold.")

        st.markdown("### 🧾 Raw Transaction Flows")
        df_edges = pd.DataFrame(edges_table)
        st.dataframe(df_edges, use_container_width=True)
        st.markdown("<hr/><center><span style='color:#00BFFF;font-size:1.1em;'>🚀 Powered by Blockstream Esplora API · Suspicious BTC Dashboard 2025</span></center>", unsafe_allow_html=True)

# -------- Ethereum Suspicious Transaction Analyzer --------
def eth_suspicious_analyzer():
    BLACKLISTED_ADDRESSES = {
        "0x0000000000000000000000000000000000000000",
    }
    SUSPICIOUS_SCORE_THRESHOLD = 10.0
    BURST_WINDOW_SECONDS = 3600
    MAX_PAGES = 10
    CHAIN_ID = 1
    PAGE_SIZE = 10000

    st.markdown("""
    <style>
    .stApp {background-color: #161622;}
    h1, h4, .stMarkdown, .stDataFrame, .stTable { color:#EAEAEA;}
    .stTextInput label div, .stTextInput label { color:#EAEAEA !important; font-weight:650;}
    .stTextInput>div>div>input {background: #1E222A !important; color: #00ffc3; font-size: 17px;}
    .stButton>button {background-color: #00BFFF; color: #191c22 !important; border: none; font-weight: 700;}
    .stDataFrame, .stTable {background: #1E222A; color: #fff;}
    hr {border: 1.5px solid #00BFFF;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:18px;">
        <img src="https://cryptologos.cc/logos/ethereum-eth-logo.png?v=026" width="38"/>
        <h1 style="color:#00BFFF; font-family:monospace;">Ethereum Suspicious Transaction Analyzer (Advanced)</h1>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    address = st.text_input("Enter Ethereum Address (0x...)",
                            value="0x1fD35bB2FFa949Fd90a47a945B5487575F24bfaB",
                            max_chars=42)
    analyze_btn = st.button("Fetch & Analyze Transactions")

    def fetch_tx_list(module_action, address):
        startblock = 0
        endblock = 99999999
        all_tx = []
        page = 1

        while True:
            url = (
                f"{BASE_URL_ETH_V2}?chainid={CHAIN_ID}"
                f"&module=account"
                f"&action={module_action}"
                f"&address={address}"
                f"&startblock={startblock}"
                f"&endblock={endblock}"
                f"&page=1"
                f"&offset={PAGE_SIZE}"
                f"&sort=asc"
                f"&apikey={ETHERSCAN_API_KEY}"
            )
            r = requests.get(url)
            try:
                data = r.json()
            except Exception:
                break

            if data.get("status") != "1" or not data.get("result"):
                break

            tx_list = data["result"]
            all_tx += tx_list

            if len(tx_list) < PAGE_SIZE:
                break

            try:
                startblock = int(tx_list[-1]['blockNumber']) + 1
            except Exception:
                break

            page += 1
            if page > MAX_PAGES:
                break
            time.sleep(0.2)

        return all_tx

    def fetch_all_transactions(address):
        normal = fetch_tx_list("txlist", address)
        token = fetch_tx_list("tokentx", address)
        internal = fetch_tx_list("txlistinternal", address)
        all_txs = normal + token + internal
        seen = set()
        unique_txs = []
        for tx in all_txs:
            h = tx.get("hash")
            if h and h not in seen:
                seen.add(h)
                unique_txs.append(tx)
        return unique_txs

    def calculate_suspicious_score(total_received, in_degree, mixing_factor, burst_factor, blacklist_flag):
        base = total_received * (in_degree + 1) * (mixing_factor + 1)
        if burst_factor:
            base *= 1.5
        if blacklist_flag:
            base *= 3
        return base

    def analyze_transactions(txs, score_threshold):
        G = nx.DiGraph()
        timestamps = {}
        for tx in txs:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower()
            if not from_addr or not to_addr:
                continue
            value = int(tx.get("value", "0")) / 1e18 if "value" in tx else 0
            symbol = tx.get("tokenSymbol", "ETH")
            G.add_edge(from_addr, to_addr, value=value, hash=tx.get("hash"), token=symbol)
            t = tx.get("timeStamp")
            if t:
                t = int(t)
                timestamps.setdefault(to_addr, []).append(t)
        node_stats = []
        for node in G.nodes():
            in_edges = list(G.in_edges(node, data=True))
            out_edges = list(G.out_edges(node, data=True))
            total_received = sum(d['value'] for _, _, d in in_edges)
            mixing_factor = len(set(a for a, _, _ in in_edges))
            in_degree = len(in_edges)
            out_degree = len(out_edges)
            blacklist_flag = node.lower() in BLACKLISTED_ADDRESSES
            burst_flag = False
            ts = sorted(timestamps.get(node, []))
            if len(ts) > 1:
                for i in range(len(ts) - 1):
                    if ts[i+1] - ts[i] <= BURST_WINDOW_SECONDS:
                        burst_flag = True
                        break
            suspicious_score = calculate_suspicious_score(
                total_received, in_degree, mixing_factor, burst_flag, blacklist_flag
            )
            node_stats.append({
                "address": node,
                "total_received": total_received,
                "total_sent": sum(d['value'] for _, _, d in out_edges),
                "num_incoming": in_degree,
                "num_outgoing": out_degree,
                "mixing_factor": mixing_factor,
                "burst_activity": burst_flag,
                "blacklisted": blacklist_flag,
                "suspicious_score": suspicious_score,
                "is_suspicious": suspicious_score >= score_threshold,
                "end_user": out_degree == 0
            })
        df_nodes = pd.DataFrame(node_stats).sort_values("suspicious_score", ascending=False)
        return df_nodes, G

    def visualize_graph(G, df_nodes):
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, seed=42)
        colors = []
        for node in G.nodes():
            row = df_nodes[df_nodes['address'] == node]
            if not row.empty:
                if row['blacklisted'].iloc[0]:
                    colors.append("red")
                elif row['is_suspicious'].iloc[0]:
                    colors.append("orange")
                else:
                    colors.append("skyblue")
            else:
                colors.append("skyblue")
        nx.draw(G, pos, with_labels=True, node_size=800, node_color=colors, edge_color="gray", font_size=8)
        plt.title("Suspicious ETH Transactions — Advanced Heuristic Detection")
        st.pyplot(plt)

    if analyze_btn:
        st.info(f"Fetching transactions for {address} ...")
        txs = fetch_all_transactions(address)
        st.success(f"Total transactions found: {len(txs)}")
        st.markdown("### 🧾 Raw Transactions")
        st.dataframe(pd.DataFrame(txs), use_container_width=True)
        st.markdown("### 🧮 Suspicious Score Analysis")
        df_nodes, G = analyze_transactions(txs, SUSPICIOUS_SCORE_THRESHOLD)
        st.dataframe(df_nodes, use_container_width=True)
        suspicious_nodes = df_nodes[df_nodes['is_suspicious']]
        if not suspicious_nodes.empty:
            st.markdown("### ⚠️ Suspicious Endpoints")
            st.dataframe(suspicious_nodes, use_container_width=True)
        st.markdown("### 🕸️ Transaction Graph")
        visualize_graph(G, df_nodes)
        st.markdown("<hr/><center><span style='color:#00BFFF;font-size:1.1em;'>Powered by Etherscan V2 API · Suspicious ETH Dashboard 2025</span></center>", unsafe_allow_html=True)

# === Main App Routing based on sidebar ===
if page == "Ethereum Wallet Transaction Explorer":
    eth_wallet_explorer()
elif page == "Bitcoin Address Transaction Explorer":
    btc_wallet_explorer()
elif page == "Ethereum Bridge Transaction Finder":
    eth_bridge_finder()
elif page == "Bitcoin Bridge Transaction Finder":
    btc_bridge_finder()
elif page == "Ethereum Transaction Clustering":
    eth_address_clustering()
elif page == "Bitcoin Transaction Clustering":
    btc_address_clustering()
elif page == "Bitcoin Suspicious Transaction Analyzer":
    btc_suspicious_analyzer()
elif page == "Ethereum Suspicious Transaction Analyzer":
    eth_suspicious_analyzer()
else:
    st.write("Select a module from the sidebar.")

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("© 2025 Crypto Multi-Utility Dashboard")


import openai

# Set your API key securely, for example from environment variable
openai.api_key = "YOUR_API_KEY"

def chat_with_gpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    while True:
        user_input = input("User: ")
        if user_input.lower() in {"exit", "quit"}:
            break
        messages.append({"role": "user", "content": user_input})
        assistant_reply = chat_with_gpt(messages)
        print(f"ChatGPT: {assistant_reply}")
        messages.append({"role": "assistant", "content": assistant_reply})











