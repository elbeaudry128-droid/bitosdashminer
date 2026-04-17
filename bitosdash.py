#!/usr/bin/env python3
# BitOS Cloud Dashboard v3 — READY-TO-USE single-file build
# Only needs app.js alongside. Run: python3 bitosdash.py
import argparse, getpass, hashlib, http.server, json, os, platform, secrets
import socket, ssl, subprocess, sys, threading, time
import urllib.parse, urllib.request, urllib.error
from http.cookies import SimpleCookie
from pathlib import Path


# ══ EMBEDDED STATIC ASSETS ══════════════════════════════════════════
EMBEDDED_INDEX_HTML = r'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=5,user-scalable=yes,viewport-fit=cover">
<meta name="theme-color" content="#080c14">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
<title>BitOS Cloud v3 — Mining Dashboard</title>
<link rel="manifest" href="manifest.json">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%2300e5ff'/%3E%3Ctext x='50' y='68' font-size='60' font-weight='800' text-anchor='middle' fill='%23080c14' font-family='monospace'%3EB%3C/text%3E%3C/svg%3E">
<style>
:root{
  --bg:#080c14;--panel:#0d1421;--panel2:#111a2e;--border:#1e2d47;
  --text:#e8f0fe;--muted:#5a7090;--accent:#00e5ff;--accent2:#7c3aed;
  --green:#00d97e;--red:#ff2d55;--yellow:#ffb800;--orange:#ff7a00;
  --mono:'SF Mono',Monaco,'Cascadia Code',monospace;
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{background:var(--bg);color:var(--text);font-family:-apple-system,system-ui,sans-serif;min-height:100vh}
body{padding:env(safe-area-inset-top) env(safe-area-inset-right) calc(env(safe-area-inset-bottom)+64px) env(safe-area-inset-left);overflow-x:hidden}
a{color:var(--accent);text-decoration:none}
button{cursor:pointer;font-family:inherit;background:none;border:none;color:inherit}
input,select,textarea{font-family:inherit;background:var(--panel2);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:10px 12px;outline:none;width:100%}
input:focus,select:focus,textarea:focus{border-color:var(--accent)}

/* Topbar */
.topbar{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;background:var(--panel);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}
.tb-left{display:flex;align-items:center;gap:10px}
.menu-btn{width:36px;height:36px;border-radius:8px;background:var(--panel2);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:18px}
.tb-title{font-size:15px;font-weight:700}
.tb-right{display:flex;gap:6px;align-items:center}
.tb-badge{font-size:10px;padding:3px 8px;border-radius:6px;background:var(--panel2);border:1px solid var(--border);color:var(--muted);font-family:var(--mono)}

/* Sidebar */
.sidebar{position:fixed;top:0;left:0;width:260px;height:100vh;background:var(--panel);border-right:1px solid var(--border);transform:translateX(-100%);transition:transform .25s;z-index:1000;overflow-y:auto;padding:16px}
.sidebar.open{transform:translateX(0)}
.sb-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:999;display:none}
.sb-overlay.open{display:block}
.sb-item{padding:12px 14px;border-radius:10px;display:flex;align-items:center;gap:10px;cursor:pointer;font-size:13px;color:var(--muted);margin-bottom:4px}
.sb-item:hover{background:var(--panel2);color:var(--text)}
.sb-item.active{background:var(--accent);color:var(--bg);font-weight:700}

/* Container */
.container{max-width:1400px;margin:0 auto;padding:16px}

/* Card */
.card{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:12px}
.card-title{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:var(--mono);margin-bottom:10px}
.card-value{font-size:24px;font-weight:800}
.card-sub{font-size:11px;color:var(--muted);font-family:var(--mono);margin-top:2px}

.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.grid-2{grid-template-columns:repeat(2,1fr)}

/* KPI bar */
.kpi-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
.kpi-bar .card{text-align:center;padding:12px 8px;margin:0}
.kpi-bar .card-value{font-size:16px}
.kpi-bar .card-title{font-size:9px;margin-bottom:4px}

/* Wallet strip */
.dws{background:linear-gradient(135deg,var(--accent)15,var(--accent2)15);border:1px solid var(--border);border-radius:14px;padding:18px;margin-bottom:14px}
.dws-total{font-size:32px;font-weight:800;margin-bottom:10px}
.dws-split{display:flex;gap:16px;font-size:12px;color:var(--muted);font-family:var(--mono)}

/* Coin rows */
.coin-row{display:flex;align-items:center;gap:12px;padding:12px 14px;background:var(--panel);border:1px solid var(--border);border-radius:12px;margin-bottom:8px}
.coin-row .dot{width:10px;height:10px;border-radius:50%;background:var(--accent)}
.coin-row.kas .dot{background:#70eea6}
.coin-name{font-weight:700;font-size:13px}
.coin-hr{font-size:11px;color:var(--muted);font-family:var(--mono)}
.coin-rev{margin-left:auto;font-weight:700;color:var(--green);font-size:13px;font-family:var(--mono)}
.pbar{flex:1;height:6px;background:var(--panel2);border-radius:3px;overflow:hidden;margin:0 8px}
.pbar-fill{height:100%;background:var(--accent);border-radius:3px;transition:width .4s}

/* Rig mini */
.rig-mini{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid rgba(30,45,71,.4)}
.rig-mini:last-child{border-bottom:none}
.rig-mini-dot{width:8px;height:8px;border-radius:50%}
.dot-online{background:var(--green)}
.dot-warning{background:var(--yellow)}
.dot-offline{background:var(--muted)}
.rig-mini-name{flex:1;font-size:12px;font-weight:600}
.rig-mini-info{display:flex;flex-direction:column;align-items:flex-end;font-size:10px;color:var(--muted);font-family:var(--mono)}

/* Bottom nav */
.bottom-nav{position:fixed;bottom:0;left:0;right:0;height:60px;background:var(--panel);border-top:1px solid var(--border);display:flex;justify-content:space-around;align-items:center;z-index:500;padding-bottom:env(safe-area-inset-bottom)}
.bn-item{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:10px;color:var(--muted);gap:2px;padding:6px 2px;position:relative;font-weight:600}
.bn-item .bn-ico{font-size:18px}
.bn-item.active{color:var(--accent)}
.bn-item.active::before{content:'';position:absolute;top:0;left:30%;right:30%;height:2px;background:var(--accent);border-radius:0 0 3px 3px}
.bn-badge{position:absolute;top:4px;right:16%;background:var(--red);color:#fff;border-radius:9px;padding:1px 5px;font-size:9px;font-weight:800;min-width:14px;text-align:center}

/* Pages */
.page{display:none}
.page.active{display:block;animation:fadeIn .2s}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}

/* Sections inside pages (default content) */
.empty-hint{background:var(--panel);border:1px dashed var(--border);border-radius:12px;padding:24px;text-align:center;color:var(--muted);font-size:12px}
.empty-hint b{display:block;color:var(--text);margin-bottom:6px}

/* Buttons */
.btn{padding:10px 16px;border-radius:10px;font-size:13px;font-weight:700;border:1px solid var(--border);background:var(--panel2);color:var(--text);transition:opacity .15s;display:inline-flex;align-items:center;gap:6px;justify-content:center}
.btn-primary{background:var(--accent);color:var(--bg);border-color:var(--accent)}
.btn-danger{background:var(--red);color:#fff;border-color:var(--red)}
.btn-success{background:var(--green);color:var(--bg);border-color:var(--green)}
.btn-sm{padding:6px 10px;font-size:11px}
.btn:hover{opacity:.88}

/* Modals */
.modal{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:2000;display:none;align-items:center;justify-content:center;padding:16px}
.modal.show{display:flex;animation:fadeIn .2s}
.modal-box{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:20px;width:100%;max-width:460px;max-height:90vh;overflow-y:auto;position:relative}
.modal-hdr{font-size:16px;font-weight:800;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between}
.modal-close{width:32px;height:32px;border-radius:8px;background:var(--panel2);border:1px solid var(--border);color:var(--text);font-size:16px}

/* Toast */
#toast-wrap{position:fixed;top:14px;right:14px;z-index:3000;display:flex;flex-direction:column;gap:8px;max-width:340px}
.toast{background:var(--panel);border:1px solid var(--border);border-radius:10px;font-size:12px;box-shadow:0 8px 24px rgba(0,0,0,.5);transition:opacity .3s}

/* PWA install */
.pwa-install{position:fixed;bottom:80px;right:16px;background:var(--accent);color:var(--bg);border:none;border-radius:50%;width:52px;height:52px;font-size:22px;display:none;align-items:center;justify-content:center;box-shadow:0 4px 18px rgba(0,229,255,.5);z-index:499;font-weight:800}

/* Tables */
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--border)}
th{color:var(--muted);font-weight:600;font-size:10px;text-transform:uppercase}

@media(max-width:640px){
  .kpi-bar{grid-template-columns:repeat(2,1fr)}
  .dws-total{font-size:26px}
  .container{padding:12px}
}
@media(min-width:900px){
  .sidebar{transform:translateX(0);position:sticky;height:auto}
  .sb-overlay{display:none!important}
  .menu-btn{display:none}
}
</style>
</head>
<body>

<!-- Topbar -->
<header class="topbar">
  <div class="tb-left">
    <button class="menu-btn" onclick="toggleSidebar()">☰</button>
    <div class="tb-title" id="topbar-title">Dashboard</div>
  </div>
  <div class="tb-right">
    <div class="tb-badge" id="hive-badge-txt">HiveOS —</div>
    <div class="tb-badge" id="connectivity-badge">●</div>
    <div class="tb-badge" id="alerts-badge">0</div>
  </div>
</header>

<!-- Sidebar -->
<aside class="sidebar" id="sidebar">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;padding:8px 0">
    <div style="width:40px;height:40px;background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:var(--bg);font-family:var(--mono)">B</div>
    <div>
      <div style="font-weight:800">BitOS</div>
      <div style="font-size:10px;color:var(--muted);font-family:var(--mono)">Cloud v3.4.1</div>
    </div>
  </div>
  <div class="sb-item active" onclick="showPage('dashboard');closeSidebar()">🏠 Dashboard</div>
  <div class="sb-item" onclick="showPage('xmr');closeSidebar()">⛏ Monero (XMR)</div>
  <div class="sb-item" onclick="showPage('kas');closeSidebar()">💎 Kaspa (KAS)</div>
  <div class="sb-item" onclick="showPage('rigs');closeSidebar()">🖥 Mes Rigs</div>
  <div class="sb-item" onclick="showPage('wallet');closeSidebar()">💼 Portefeuille</div>
  <div class="sb-item" onclick="showPage('monitoring');closeSidebar()">📊 Monitoring</div>
  <div class="sb-item" onclick="showPage('historique');closeSidebar()">📜 Historique</div>
  <div class="sb-item" onclick="showPage('alertes');closeSidebar()">🔔 Alertes <span class="bn-badge" id="nb-alerts" style="position:static;margin-left:auto">0</span></div>
  <div class="sb-item" onclick="showPage('settings');closeSidebar()">⚙ Paramètres</div>
</aside>
<div class="sb-overlay" id="sb-overlay" onclick="closeSidebar()"></div>

<div class="container">

  <!-- DASHBOARD -->
  <div id="page-dashboard" class="page active">
    <div class="dws">
      <div class="card-title">Solde total</div>
      <div class="dws-total" id="dws-total">$ —</div>
      <div class="dws-split">
        <div id="dws-xmr">— XMR</div>
        <div id="dws-kas">— KAS</div>
      </div>
    </div>

    <div class="kpi-bar">
      <div class="card"><div class="card-title">Hashrate</div><div class="card-value" id="s-hash">—</div></div>
      <div class="card"><div class="card-title">Revenu/j</div><div class="card-value" id="s-rev">$ —</div></div>
      <div class="card"><div class="card-title">Temp. moy</div><div class="card-value" id="s-temp">—</div></div>
      <div class="card"><div class="card-title">Watts</div><div class="card-value" id="s-watt">—</div></div>
    </div>

    <div class="card">
      <div class="card-title">Pools actifs</div>
      <div class="coin-row">
        <div class="dot"></div>
        <div>
          <div class="coin-name">XMR</div>
          <div class="coin-hr" id="d-xmr-hr">— KH/s</div>
        </div>
        <div class="pbar"><div class="pbar-fill" id="d-xmr-bar" style="width:0%"></div></div>
        <div class="coin-rev" id="d-xmr-rev">+$—/j</div>
      </div>
      <div class="coin-row kas">
        <div class="dot"></div>
        <div>
          <div class="coin-name">KAS</div>
          <div class="coin-hr" id="d-kas-hr">— GH/s</div>
        </div>
        <div class="pbar"><div class="pbar-fill" id="d-kas-bar" style="width:0%;background:#70eea6"></div></div>
        <div class="coin-rev" id="d-kas-rev">+$—/j</div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <div class="card-title">Revenu mensuel estimé</div>
        <div class="card-value" id="d-monthly">$ —</div>
        <div class="card-sub" id="d-monthly-sub">—</div>
      </div>
      <div class="card">
        <div class="card-title">Alertes <span id="d-alert-badge" style="background:var(--red);color:#fff;border-radius:9px;padding:1px 6px;font-size:9px;display:none">0</span></div>
        <div id="al-dash"><div style="color:var(--muted);font-size:11px">Chargement...</div></div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <div class="card-title">Rigs actifs</div>
        <div id="rig-dash"><div style="color:var(--muted);font-size:11px">Aucun rig configuré</div></div>
      </div>
      <div class="card">
        <div class="card-title">Charge GPU</div>
        <div id="gpu-dash"><div style="color:var(--muted);font-size:11px">—</div></div>
      </div>
    </div>

    <div id="install-banner" style="display:none"></div>
    <div id="ghpages-info-banner" style="display:none"></div>
  </div>

  <!-- XMR PAGE -->
  <div id="page-xmr" class="page">
    <div class="card">
      <div class="card-title">Monero — XMR</div>
      <div class="card-value" id="xmr-total">— XMR</div>
      <div class="card-sub">Pool · SupportXMR</div>
    </div>
    <div class="grid grid-2">
      <div class="card"><div class="card-title">Hashrate pool</div><div class="card-value" id="xmr-pool-hr">—</div></div>
      <div class="card"><div class="card-title">Shares</div><div class="card-value" id="xmr-shares">—</div></div>
      <div class="card"><div class="card-title">En attente</div><div class="card-value" id="xmr-pending">—</div></div>
      <div class="card"><div class="card-title">Dernier paiement</div><div class="card-value" id="xmr-last-pay">—</div></div>
    </div>
  </div>

  <!-- KAS PAGE -->
  <div id="page-kas" class="page">
    <div class="card">
      <div class="card-title">Kaspa — KAS</div>
      <div class="card-value" id="kas-total">— KAS</div>
      <div class="card-sub">Pool · K1Pool</div>
    </div>
    <div class="grid grid-2">
      <div class="card"><div class="card-title">Hashrate pool</div><div class="card-value" id="kas-pool-hr">—</div></div>
      <div class="card"><div class="card-title">En attente</div><div class="card-value" id="kas-pending">—</div></div>
    </div>
  </div>

  <!-- RIGS PAGE -->
  <div id="page-rigs" class="page">
    <div class="card">
      <div class="card-title">Workers (HiveOS)</div>
      <div id="rigs-list"><div class="empty-hint"><b>Aucun rig</b>Configurez votre token HiveOS dans Paramètres</div></div>
    </div>
  </div>

  <!-- WALLET PAGE -->
  <div id="page-wallet" class="page">
    <div class="card">
      <div class="card-title">Portefeuille global</div>
      <div class="card-value" id="w-total">$ —</div>
    </div>
    <div class="grid grid-2">
      <div class="card">
        <div class="card-title">XMR</div>
        <div class="card-value" id="w-xmr-a">—</div>
        <div class="card-sub" id="w-xmr-u">$ —</div>
      </div>
      <div class="card">
        <div class="card-title">KAS</div>
        <div class="card-value" id="w-kas-a">—</div>
        <div class="card-sub" id="w-kas-u">$ —</div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Actions</div>
      <button class="btn btn-primary" onclick="openModal('modal-send')">Envoyer</button>
      <button class="btn" onclick="openModal('modal-receive')">Recevoir</button>
      <button class="btn" onclick="openModal('modal-convert')">Convertir USDT</button>
    </div>
    <div class="card">
      <div class="card-title">Wallets externes</div>
      <div id="ext-wallets-list"><div class="empty-hint">Aucun wallet externe</div></div>
    </div>
  </div>

  <!-- MONITORING -->
  <div id="page-monitoring" class="page">
    <div class="card"><div class="card-title">Monitoring en temps réel</div><div class="empty-hint">Graphiques & stats live</div></div>
  </div>

  <!-- HISTORIQUE -->
  <div id="page-historique" class="page">
    <div class="card">
      <div class="card-title">Historique des snapshots</div>
      <input type="search" id="hist-search" placeholder="Rechercher...">
      <div id="hist-list" style="margin-top:12px"></div>
      <div id="hist-empty" class="empty-hint">Aucun snapshot enregistré</div>
    </div>
  </div>

  <!-- ALERTES -->
  <div id="page-alertes" class="page">
    <div class="card">
      <div class="card-title">Alertes <span id="alert-count"></span></div>
      <div id="alertes-list"><div class="empty-hint">✓ Aucune alerte</div></div>
    </div>
  </div>

  <!-- SETTINGS -->
  <div id="page-settings" class="page">
    <div class="card">
      <div class="card-title">HiveOS API</div>
      <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:4px">Farm ID</label>
      <input id="hive-farm-input" placeholder="12345">
      <label style="font-size:11px;color:var(--muted);display:block;margin:10px 0 4px">Token personnel</label>
      <input id="hive-token-input" type="password" placeholder="Bearer token">
      <div style="display:flex;gap:8px;margin-top:10px">
        <button class="btn btn-primary" id="hive-discover-btn">Tester</button>
        <button class="btn" onclick="openModal('modal-change-pin')">Changer PIN</button>
      </div>
      <div id="hive-conn-stats" style="margin-top:10px;font-size:11px;color:var(--muted);font-family:var(--mono)"></div>
      <div id="hive-debug-log" style="margin-top:8px;font-size:10px;color:var(--muted);font-family:var(--mono);max-height:200px;overflow-y:auto"></div>
    </div>
    <div class="card">
      <div class="card-title">Préférences</div>
      <div style="font-size:12px;color:var(--muted)">Langue, devise, thème — en développement</div>
    </div>
  </div>

  <!-- ACTIONS -->
  <div id="page-actions" class="page">
    <div class="card"><div class="card-title">Actions recommandées</div><div id="action-list-container"><div class="empty-hint">Aucune action</div></div></div>
  </div>

</div>

<!-- Bottom nav -->
<nav class="bottom-nav">
  <button class="bn-item active" id="bn-dashboard" onclick="showPage('dashboard')"><span class="bn-ico">🏠</span><span>Dash</span></button>
  <button class="bn-item" id="bn-wallet" onclick="showPage('wallet')"><span class="bn-ico">💼</span><span>Wallet</span></button>
  <button class="bn-item" id="bn-xmr" onclick="showPage('xmr')"><span class="bn-ico">⛏</span><span>XMR</span></button>
  <button class="bn-item" id="bn-kas" onclick="showPage('kas')"><span class="bn-ico">💎</span><span>KAS</span></button>
  <button class="bn-item" id="bn-alertes" onclick="showPage('alertes')"><span class="bn-ico">🔔</span><span>Alertes</span><span class="bn-badge" id="bn-badge" style="display:none">0</span></button>
  <button class="bn-item" id="bn-settings" onclick="showPage('settings')"><span class="bn-ico">⚙</span><span>Réglages</span></button>
</nav>

<!-- Modals (minimaux) -->
<div class="modal" id="modal-send"><div class="modal-box">
  <div class="modal-hdr" id="send-title">Envoyer</div>
  <div>Disponible: <span id="send-avail">—</span></div>
  <button class="modal-close" onclick="closeModal('modal-send')">×</button>
</div></div>

<div class="modal" id="modal-receive"><div class="modal-box">
  <div class="modal-hdr" id="recv-title">Recevoir</div>
  <div id="recv-qr" style="text-align:center;margin:16px 0"></div>
  <button class="modal-close" onclick="closeModal('modal-receive')" style="position:absolute;top:16px;right:16px">×</button>
</div></div>

<div class="modal" id="modal-convert"><div class="modal-box">
  <div class="modal-hdr">Convertir</div>
  <button id="conv-btn-xmr" class="btn">XMR</button>
  <button id="conv-btn-kas" class="btn">KAS</button>
  <input id="conv-amount" type="number" placeholder="Montant" style="margin-top:10px">
  <input id="conv-addr" placeholder="Adresse USDT" style="margin-top:6px">
  <div id="conv-result-box" style="display:none;margin-top:10px"></div>
  <button id="btn-conv-go" class="btn btn-primary" style="margin-top:10px" disabled>Convertir</button>
  <button class="modal-close" onclick="closeModal('modal-convert')" style="position:absolute;top:16px;right:16px">×</button>
</div></div>

<div class="modal" id="modal-pin"><div class="modal-box">
  <div class="modal-hdr">Code PIN</div>
  <input id="pin-input" type="password" maxlength="6" placeholder="••••">
  <div id="pin-err" style="color:var(--red);font-size:11px;margin-top:6px"></div>
  <button class="btn btn-primary" onclick="closeModal('modal-pin')" style="margin-top:10px;width:100%">Valider</button>
</div></div>

<div class="modal" id="modal-change-pin"><div class="modal-box">
  <div class="modal-hdr">Changer le PIN</div>
  <input id="cp-old" type="password" placeholder="Ancien PIN">
  <input id="cp-new" type="password" placeholder="Nouveau PIN" style="margin-top:6px">
  <input id="cp-conf" type="password" placeholder="Confirmer" style="margin-top:6px">
  <button class="btn btn-primary" onclick="closeModal('modal-change-pin')" style="margin-top:10px;width:100%">Valider</button>
</div></div>

<div class="modal" id="modal-success"><div class="modal-box">
  <div class="modal-hdr">Succès</div>
  <div id="swb-sub-text">Opération réussie</div>
  <button class="btn btn-primary" onclick="closeModal('modal-success')" style="margin-top:10px;width:100%">OK</button>
</div></div>

<div id="toast-wrap"></div>
<button class="pwa-install" id="pwa-install-btn" onclick="installPWA()">+</button>

<script>
/* Minimal bootstrap helpers that app.js expects from the HTML */
function toggleSidebar(){
  var s=document.getElementById('sidebar'), o=document.getElementById('sb-overlay');
  if(s) s.classList.toggle('open');
  if(o) o.classList.toggle('open');
}
function closeSidebar(){
  var s=document.getElementById('sidebar'), o=document.getElementById('sb-overlay');
  if(s) s.classList.remove('open');
  if(o) o.classList.remove('open');
}
function openModal(id){
  var m=document.getElementById(id);
  if(m) m.classList.add('show');
}
function closeModal(id){
  var m=document.getElementById(id);
  if(m) m.classList.remove('show');
}
/* Close modals on backdrop click */
document.addEventListener('click', function(e){
  if(e.target.classList && e.target.classList.contains('modal')){
    e.target.classList.remove('show');
  }
});

/* Service worker */
if('serviceWorker' in navigator){
  window.addEventListener('load', function(){
    navigator.serviceWorker.register('sw.js').catch(function(e){console.warn('SW:',e);});
  });
}
</script>
<script defer src="app.js"></script>
<script defer>
window.addEventListener('load', function(){
  setTimeout(function(){
    if(typeof renderDash === 'function'){
      try { renderDash(); } catch(e){ console.warn('[BitOS] renderDash:', e.message); }
    } else {
      console.warn('[BitOS] app.js non chargé');
    }
  }, 300);
});
</script>
</body>
</html>
'''

EMBEDDED_MANIFEST_JSON = r'''{
  "name": "BitOS Cloud Dashboard",
  "short_name": "BitOS",
  "description": "Mining dashboard for XMR & KAS with HiveOS integration",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#080c14",
  "theme_color": "#080c14",
  "lang": "fr",
  "categories": ["finance", "utilities", "productivity"],
  "icons": [
    {
      "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'%3E%3Crect width='192' height='192' rx='38' fill='%2300e5ff'/%3E%3Ctext x='96' y='130' font-size='115' font-weight='800' text-anchor='middle' fill='%23080c14' font-family='monospace'%3EB%3C/text%3E%3C/svg%3E",
      "sizes": "192x192",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    },
    {
      "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='100' fill='%2300e5ff'/%3E%3Ctext x='256' y='350' font-size='310' font-weight='800' text-anchor='middle' fill='%23080c14' font-family='monospace'%3EB%3C/text%3E%3C/svg%3E",
      "sizes": "512x512",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
'''

EMBEDDED_SW_JS = r'''// BitOS Cloud v3 — Service Worker (offline + stale-while-revalidate)
const CACHE = 'bitos-v3.4.0';
const ASSETS = ['/', '/index.html', '/app.js', '/manifest.json'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS).catch(()=>{})));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // Ne jamais cacher les proxy API ni l'auth
  if (url.pathname.startsWith('/proxy/') ||
      url.pathname.startsWith('/api/') ||
      url.pathname === '/login' ||
      url.pathname === '/logout') {
    return; // passthrough
  }
  if (e.request.method !== 'GET') return;

  // Stale-while-revalidate
  e.respondWith(
    caches.open(CACHE).then(cache =>
      cache.match(e.request).then(cached => {
        const fetchPromise = fetch(e.request).then(resp => {
          if (resp && resp.status === 200 && resp.type === 'basic') {
            cache.put(e.request, resp.clone());
          }
          return resp;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    )
  );
});

self.addEventListener('message', e => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});
'''

EMBEDDED_ASSETS = {
    'index.html':   ('text/html; charset=utf-8',       EMBEDDED_INDEX_HTML),
    'manifest.json':('application/json',               EMBEDDED_MANIFEST_JSON),
    'sw.js':        ('application/javascript; charset=utf-8', EMBEDDED_SW_JS),
}

DASHBOARD_FILE = 'index.html'
DEFAULT_PORT   = 8765
VERSION = '3.4.2-ready'

PROXY_RULES = {
    '/proxy/hiveos':    'https://api2.hiveos.farm/api/v2',
    '/proxy/coingecko': 'https://api.coingecko.com/api/v3',
    '/proxy/kaspa':     'https://api.kaspa.org',
    '/proxy/xmr-pool':  'https://supportxmr.com/api',
    '/proxy/kas-pool':  'https://api-kas.k1pool.com/api',
    '/proxy/xmrchain':  'https://xmrchain.net/api',
}

BANNER = r"""
  ╔══════════════════════════════════════════════════════════╗
  ║   BitOS Cloud v3 — Dashboard Server                      ║
  ╚══════════════════════════════════════════════════════════╝
"""

START_TIME = time.time()
AUTH_ENABLED = False
AUTH_PASS_HASH = ''
AUTH_TOKENS = set()
AUTH_FAIL_COUNT = {}
AUTH_FAIL_LOCK = 5
AUTH_LOCK_TIME = 300
AUTH_FAIL_TIMES = {}

def hash_password(pwd): return hashlib.sha256(pwd.encode('utf-8')).hexdigest()
def generate_token(): return secrets.token_urlsafe(32)

def is_locked(ip):
    if ip not in AUTH_FAIL_COUNT: return False
    if AUTH_FAIL_COUNT[ip] >= AUTH_FAIL_LOCK:
        first_fail = AUTH_FAIL_TIMES.get(ip, 0)
        if time.time() - first_fail < AUTH_LOCK_TIME: return True
        AUTH_FAIL_COUNT.pop(ip, None); AUTH_FAIL_TIMES.pop(ip, None)
    return False

def record_fail(ip):
    AUTH_FAIL_COUNT[ip] = AUTH_FAIL_COUNT.get(ip, 0) + 1
    if ip not in AUTH_FAIL_TIMES: AUTH_FAIL_TIMES[ip] = time.time()

def reset_fails(ip):
    AUTH_FAIL_COUNT.pop(ip, None); AUTH_FAIL_TIMES.pop(ip, None)

LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BitOS — Connexion</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080c14;color:#e8f0fe;font-family:system-ui,sans-serif;
  display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#0d1421;border:1px solid #1e2d47;border-radius:16px;
  padding:40px 32px;width:100%;max-width:380px;text-align:center}
.logo{width:56px;height:56px;background:linear-gradient(135deg,#00e5ff,#7c3aed);
  border-radius:14px;display:flex;align-items:center;justify-content:center;
  font-size:24px;font-weight:800;color:#fff;margin:0 auto 20px}
h1{font-size:20px;font-weight:800;margin-bottom:6px}
.sub{color:#5a7090;font-size:12px;margin-bottom:28px}
input{width:100%;background:#111a2e;border:1px solid #1e2d47;border-radius:10px;
  padding:14px 16px;color:#e8f0fe;font-size:16px;outline:none;margin-bottom:16px}
input:focus{border-color:#00e5ff}
button{width:100%;background:#00e5ff;color:#080c14;border:none;border-radius:10px;
  padding:14px;font-size:14px;font-weight:800;cursor:pointer}
.err{color:#ff2d55;font-size:12px;margin-top:12px;min-height:18px}
</style></head><body>
<div class="box"><div class="logo">B</div><h1>BitOS Cloud</h1>
<div class="sub">Authentification requise</div>
<form id="f" onsubmit="return go()">
<input type="password" id="p" placeholder="Mot de passe" autofocus>
<button type="submit">Se connecter</button></form>
<div class="err" id="err"><!--ERR--></div></div>
<script>
async function go(){var p=document.getElementById('p').value;if(!p)return false;
try{var r=await fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({password:p})});var d=await r.json();
if(d.ok){window.location.href=d.redirect||'/';}
else{document.getElementById('err').textContent=d.error||'Mot de passe incorrect';
document.getElementById('p').value='';document.getElementById('p').focus();}}
catch(e){document.getElementById('err').textContent='Erreur reseau';}return false;}
</script></body></html>'''

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    log_file = None

    def log_message(self, fmt, *args):
        msg = f"[{self.address_string()}] {fmt % args}"
        if self.log_file:
            with open(self.log_file, 'a') as f: f.write(msg + '\n')
        if '/proxy/' not in (fmt % args):
            print(f"  \033[90m{msg}\033[0m")

    def _check_auth(self):
        if not AUTH_ENABLED: return True
        ip = self.client_address[0]
        if ip in ('127.0.0.1', '::1', 'localhost'): return True
        if is_locked(ip): return False
        ch = self.headers.get('Cookie', '')
        if ch:
            c = SimpleCookie(ch)
            if 'bitosdash_token' in c and c['bitosdash_token'].value in AUTH_TOKENS:
                return True
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'token' in qs and qs['token'][0] in AUTH_TOKENS: return True
        return False

    def _send_401(self):
        path = self.path.split('?')[0]
        if path.startswith('/proxy/') or path.startswith('/api/'):
            data = json.dumps({'error':'auth_required','login':'/login'}).encode()
            self.send_response(401)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data))
            self.end_headers(); self.wfile.write(data)
        else:
            self.send_response(302); self.send_header('Location','/login'); self.end_headers()

    def do_OPTIONS(self): self._send_cors(204); self.end_headers()
    def do_GET(self): self._route('GET')
    def do_POST(self): self._route('POST')
    def do_PUT(self): self._route('PUT')
    def do_PATCH(self): self._route('PATCH')
    def do_DELETE(self): self._route('DELETE')

    def _send_cors(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, PUT, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age','86400')

    def _route(self, method):
        path = self.path.split('?')[0]
        if path == '/login': self._serve_login(); return
        if path == '/api/auth' and method == 'POST': self._handle_auth(); return
        if path == '/logout': self._handle_logout(); return
        if path == '/favicon.ico': self.send_error(404); return
        if not self._check_auth(): self._send_401(); return
        self._handle(method)

    def _serve_login(self):
        if not AUTH_ENABLED:
            self.send_response(302); self.send_header('Location','/'); self.end_headers(); return
        ip = self.client_address[0]
        page = LOGIN_PAGE
        if is_locked(ip):
            remain = int(AUTH_LOCK_TIME - (time.time() - AUTH_FAIL_TIMES.get(ip, 0)))
            page = page.replace('<!--ERR-->', f'IP verrouillee — reessayez dans {max(1,remain//60)} min')
        data = page.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',len(data))
        self.send_header('Cache-Control','no-store')
        self.end_headers(); self.wfile.write(data)

    def _handle_auth(self):
        ip = self.client_address[0]
        if is_locked(ip):
            remain = int(AUTH_LOCK_TIME - (time.time() - AUTH_FAIL_TIMES.get(ip,0)))
            data = json.dumps({'ok':False,'error':f'IP verrouillee — reessayez dans {max(1,remain//60)} min'}).encode()
            self._send_cors(429)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data)); self.end_headers(); self.wfile.write(data); return
        cl = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(cl) if cl > 0 else b'{}'
        try: payload = json.loads(body)
        except Exception: payload = {}
        password = payload.get('password','')
        if hash_password(password) == AUTH_PASS_HASH:
            token = generate_token(); AUTH_TOKENS.add(token); reset_fails(ip)
            data = json.dumps({'ok':True,'redirect':'/'}).encode()
            self._send_cors(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data))
            self.send_header('Set-Cookie',f'bitosdash_token={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400')
            self.end_headers(); self.wfile.write(data)
            print(f"  Connexion reussie depuis {ip}")
        else:
            record_fail(ip)
            remaining = AUTH_FAIL_LOCK - AUTH_FAIL_COUNT.get(ip,0)
            if is_locked(ip):
                msg = f'IP verrouillee — {AUTH_FAIL_LOCK} echecs — reessayez dans 5 min'
            else:
                msg = f'Mot de passe incorrect ({remaining} tentative(s) restante(s))'
            data = json.dumps({'ok':False,'error':msg}).encode()
            self._send_cors(401)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',len(data)); self.end_headers(); self.wfile.write(data)

    def _handle_logout(self):
        ch = self.headers.get('Cookie','')
        if ch:
            c = SimpleCookie(ch)
            if 'bitosdash_token' in c: AUTH_TOKENS.discard(c['bitosdash_token'].value)
        self.send_response(302)
        self.send_header('Location','/login')
        self.send_header('Set-Cookie','bitosdash_token=; Path=/; Max-Age=0')
        self.end_headers()

    def _handle(self, method):
        path = self.path.split('?')[0]
        for prefix, target in PROXY_RULES.items():
            if path == prefix or path.startswith(prefix+'/') or path.startswith(prefix+'?'):
                self._proxy(method, prefix, target); return
        if path.startswith('/proxy/asic/'): self._proxy_asic(method, path); return
        if path in ('/status','/api/status'): self._serve_status(); return
        if path == '/api/proxy-test': self._serve_proxy_test(); return
        self._serve_static(path)

    def _proxy(self, method, prefix, target):
        suffix = self.path[len(prefix):]
        if suffix and not suffix.startswith('/') and not suffix.startswith('?'):
            suffix = '/' + suffix
        url = target + suffix
        body = None
        cl = int(self.headers.get('Content-Length',0))
        if cl > 0: body = self.rfile.read(cl)
        req_headers = {'Accept':'application/json','User-Agent':f'BitOS-Cloud-Dashboard/{VERSION}'}
        for k in ('Content-Type','Authorization'):
            v = self.headers.get(k)
            if v: req_headers[k] = v
        try:
            req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                ct = resp.headers.get('Content-Type','application/json')
                status = resp.status
        except urllib.error.HTTPError as e:
            data = e.read() or b'{}'; ct = 'application/json'; status = e.code
        except Exception as e:
            data = json.dumps({'error':str(e),'proxy':True,'url':url}).encode()
            ct = 'application/json'; status = 502
        self._send_cors(status)
        self.send_header('Content-Type',ct)
        self.send_header('Content-Length',len(data))
        self.send_header('X-Proxy-By','BitOS-Server')
        self.end_headers(); self.wfile.write(data)

    def _serve_static(self, path):
        if path in ('/',''): path = '/' + DASHBOARD_FILE
        name = path.lstrip('/')

        if name in EMBEDDED_ASSETS:
            mime, content = EMBEDDED_ASSETS[name]
            data = content.encode('utf-8')
            self._send_cors(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(data))
            self.send_header('Cache-Control','no-cache' if name.endswith('.html') else 'max-age=300')
            self.end_headers(); self.wfile.write(data)
            return

        file_path = (Path('.') / name).resolve()
        base_path = Path('.').resolve()
        if not str(file_path).startswith(str(base_path)):
            self.send_error(403,'Acces refuse'); return
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404,f'Non trouve: {path}'); return
        MIME = {'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8',
            '.css':'text/css; charset=utf-8','.json':'application/json','.png':'image/png',
            '.ico':'image/x-icon','.svg':'image/svg+xml','.woff2':'font/woff2','.woff':'font/woff',
            '.txt':'text/plain; charset=utf-8','.md':'text/markdown; charset=utf-8'}
        ext = file_path.suffix.lower()
        mime = MIME.get(ext,'application/octet-stream')
        data = file_path.read_bytes()
        self._send_cors(200)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',len(data))
        cache = 'no-cache' if ext == '.html' else 'max-age=300'
        self.send_header('Cache-Control',cache)
        self.end_headers(); self.wfile.write(data)

    def _serve_status(self):
        data = json.dumps({'status':'ok','version':VERSION,'file':DASHBOARD_FILE,
            'proxies':list(PROXY_RULES.keys()),'uptime':int(time.time()-START_TIME),
            'host':socket.gethostname(),'platform':platform.system(),'lan_ip':get_lan_ip(),
            'cors':'enabled','auth':AUTH_ENABLED,'sessions':len(AUTH_TOKENS)},indent=2).encode()
        self._send_cors(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',len(data))
        self.end_headers(); self.wfile.write(data)

    def _proxy_asic(self, method, path):
        parts = path[len('/proxy/asic/'):].split('/',1)
        asic_ip = parts[0]
        rest = '/' + parts[1] if len(parts) > 1 else '/'
        target_url = 'http://' + asic_ip + rest
        body = None
        cl = int(self.headers.get('Content-Length',0))
        if cl > 0: body = self.rfile.read(cl)
        req_headers = {'Accept':'application/json, text/html, */*',
            'User-Agent':f'BitOS-Cloud-Dashboard/{VERSION}',
            'Content-Type':self.headers.get('Content-Type','application/json')}
        auth = self.headers.get('Authorization')
        if auth: req_headers['Authorization'] = auth
        try:
            req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = resp.read(); ct = resp.headers.get('Content-Type','application/json'); status = resp.status
        except urllib.error.HTTPError as e:
            data = e.read() or b'{}'; ct = 'application/json'; status = e.code
        except Exception as e:
            data = json.dumps({'error':str(e),'asic_ip':asic_ip,'proxy':True}).encode()
            ct = 'application/json'; status = 502
        self._send_cors(status)
        self.send_header('Content-Type',ct)
        self.send_header('Content-Length',len(data))
        self.send_header('X-Proxy-ASIC',asic_ip)
        self.end_headers(); self.wfile.write(data)

    def _serve_proxy_test(self):
        results = {}
        for prefix, target in PROXY_RULES.items():
            try:
                req = urllib.request.Request(target+'/',
                    headers={'User-Agent':f'BitOS-Cloud-Dashboard/{VERSION}'}, method='GET')
                with urllib.request.urlopen(req, timeout=5) as resp:
                    results[prefix] = {'ok':True,'status':resp.status,'target':target}
            except urllib.error.HTTPError as e:
                results[prefix] = {'ok':True,'status':e.code,'target':target}
            except Exception as e:
                results[prefix] = {'ok':False,'error':str(e)[:80],'target':target}
        data = json.dumps({'proxy_tests':results,'timestamp':int(time.time()),
            'total':len(results),'ok':sum(1 for v in results.values() if v.get('ok'))},indent=2).encode()
        self._send_cors(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',len(data))
        self.end_headers(); self.wfile.write(data)

def print_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(border=1); qr.add_data(url); qr.make(fit=True)
        print(); qr.print_ascii(invert=True)
    except ImportError:
        print(f"\n  Acces mobile : {url}")

def watchdog(interval=2):
    last_mtime = 0
    while True:
        try:
            mtime = Path(DASHBOARD_FILE).stat().st_mtime
            if last_mtime and mtime != last_mtime:
                print(f"\n  {DASHBOARD_FILE} modifie — rafraichissez le navigateur")
            last_mtime = mtime
        except FileNotFoundError: pass
        time.sleep(interval)

def create_ssl_context():
    cert = Path('/tmp/bitosdash_cert.pem'); key = Path('/tmp/bitosdash_key.pem')
    if not cert.exists():
        try:
            subprocess.run(['openssl','req','-x509','-newkey','rsa:2048',
                '-keyout',str(key),'-out',str(cert),'-days','365','-nodes',
                '-subj','/CN=localhost/O=BitOS/C=FR'], check=True, capture_output=True)
            print("  Certificat auto-signe genere")
        except Exception as e:
            print(f"  HTTPS impossible: {e}"); return None
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(cert), str(key))
    return ctx

def get_lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80)); return s.getsockname()[0]
    except Exception: return '127.0.0.1'

def main():
    global AUTH_ENABLED, AUTH_PASS_HASH
    parser = argparse.ArgumentParser(description='BitOS Cloud Dashboard v3')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--lan', action='store_true')
    parser.add_argument('--qr', action='store_true')
    parser.add_argument('--https', action='store_true')
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--log', type=str, default='')
    parser.add_argument('--no-watch', action='store_true')
    parser.add_argument('--password', type=str, default='')
    parser.add_argument('--no-auth', action='store_true')
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)
    # index.html is embedded, no disk check required

    if args.lan and not args.no_auth:
        AUTH_ENABLED = True
        if args.password: pwd = args.password
        else:
            print("\n  Mode LAN — mot de passe requis\n")
            pwd = getpass.getpass("  Mot de passe BitOS : ")
            if not pwd: print("  Mot de passe vide — abandon."); sys.exit(1)
            pwd2 = getpass.getpass("  Confirmer :          ")
            if pwd != pwd2: print("  Les mots de passe ne correspondent pas."); sys.exit(1)
        AUTH_PASS_HASH = hash_password(pwd); pwd = '***'

    host = args.host or ('0.0.0.0' if args.lan else '127.0.0.1')
    port = args.port
    proto = 'https' if args.https else 'http'
    lan_ip = get_lan_ip()
    local_url = f"{proto}://localhost:{port}"
    lan_url = f"{proto}://{lan_ip}:{port}"

    if args.log: DashboardHandler.log_file = args.log

    print(BANNER)
    print(f"  Repertoire : {script_dir}")
    print(f"  Dashboard  : {DASHBOARD_FILE}")
    print(f"  Auth       : {'activee' if AUTH_ENABLED else 'desactivee'}")
    print(f"  Local      : {local_url}")
    if args.lan: print(f"  LAN        : {lan_url}")

    if args.qr: print_qr(lan_url if args.lan else local_url)

    if not args.no_watch:
        threading.Thread(target=watchdog, daemon=True).start()

    try:
        server = http.server.ThreadingHTTPServer((host, port), DashboardHandler)
        if args.https:
            ctx = create_ssl_context()
            if ctx:
                server.socket = ctx.wrap_socket(server.socket, server_side=True)
                print(f"\n  HTTPS active")
        print(f"\n  Serveur demarre — Ctrl+C pour arreter\n")
        if args.open:
            import webbrowser
            threading.Timer(0.8, lambda: webbrowser.open(local_url)).start()
        server.serve_forever()
    except PermissionError:
        print(f"\n  Port {port} refuse"); sys.exit(1)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n  Port {port} deja utilise")
        else: print(f"\n  Erreur reseau: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n  Serveur arrete\n")

if __name__ == '__main__':
    main()
