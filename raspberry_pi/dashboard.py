"""
ResQMesh - Raspberry Pi operations dashboard

Starts the serial receiver and serves a live dashboard.

    cd ~/ResQMesh/raspberry_pi
    source ../venv/bin/activate
    python3 dashboard.py

Then open http://<PI_IP>:5000 from a laptop on the same network.
Find the Pi's address with:  hostname -I
"""

import time
from datetime import datetime

from flask import Flask, jsonify, render_template_string

import config
import db
from receiver import IncidentStore, SerialReceiver

app = Flask(__name__)
db.init_db()
store = IncidentStore()
store.preload(db.load_recent())
receiver = SerialReceiver(store, start_id=db.next_id_after_load())

PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ResQMesh Operations Dashboard</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0d1520;color:#e8eef5;
 font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif}
header{padding:16px 24px;border-bottom:1px solid #223247;display:flex;
 align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}
h1{margin:0;font-size:19px;letter-spacing:.3px}
.sub{font-size:12px;color:#7f95ab;margin-top:3px}
.pill{font-family:ui-monospace,Consolas,monospace;font-size:12px;padding:6px 12px;
 border-radius:20px;border:1px solid #2b3f57;background:#111d2b;margin-left:6px}
.ok{color:#3fb950;border-color:#1e4d2b}
.bad{color:#f85149;border-color:#5c2626}
.wrap{padding:20px 24px;display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:900px){.wrap{grid-template-columns:1fr}}
.panel{background:#111d2b;border:1px solid #223247;border-radius:12px;padding:18px}
.panel h2{margin:0 0 14px;font-size:11.5px;letter-spacing:1.4px;color:#7f95ab;font-weight:600}
.big{font-size:25px;font-weight:700;margin:0 0 2px}
.row{display:flex;justify-content:space-between;gap:14px;padding:7px 0;
 border-bottom:1px solid #1b2a3c;font-size:14px}
.row:last-child{border-bottom:0}
.k{color:#7f95ab}
.chip{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;
 border-radius:11px;letter-spacing:.5px}
.HIGH{background:#4a1113;color:#ff7b72}
.MEDIUM{background:#4a3411;color:#e3b341}
.LOW{background:#123222;color:#3fb950}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:#7f95ab;font-size:11px;letter-spacing:1px;padding:7px 6px;
 border-bottom:1px solid #223247}
td{padding:9px 6px;border-bottom:1px solid #1b2a3c;vertical-align:top}
.mono{font-family:ui-monospace,Consolas,monospace;color:#9db2c8}
.none{color:#5f748c;font-size:14px;padding:14px 0}
.stats{display:flex;gap:26px}
.stat b{display:block;font-size:22px}
.stat span{font-size:10.5px;color:#7f95ab;letter-spacing:.8px}
</style></head><body>

<header>
 <div>
  <h1>ResQMesh &mdash; Emergency Operations Dashboard</h1>
  <div class="sub">Raspberry Pi edge gateway &middot; no cellular network &middot; no internet</div>
 </div>
 <div>
  <span id="link" class="pill">LINK ...</span>
  <span id="last" class="pill">LAST ...</span>
 </div>
</header>

<div class="wrap">
 <div class="panel">
  <h2>ACTIVE INCIDENT</h2>
  <div id="latest"><div class="none">Waiting for the first SOS...</div></div>
 </div>

 <div class="panel">
  <h2>SESSION SUMMARY</h2>
  <div class="stats">
   <div class="stat"><b id="tot">0</b><span>RECEIVED</span></div>
   <div class="stat"><b id="hi" style="color:#ff7b72">0</b><span>HIGH PRIORITY</span></div>
   <div class="stat"><b id="port" class="mono" style="font-size:13px">-</b><span>SERIAL PORT</span></div>
  </div>
  <div class="sub" style="margin-top:16px;line-height:1.6">
   Priority is assigned by deterministic rules on the gateway:
   Medical, Fire, Accident and Crime are classified HIGH; Other is MEDIUM.
  </div>
 </div>

 <div class="panel" style="grid-column:1/-1">
  <h2>INCIDENT HISTORY</h2>
  <table>
   <thead><tr><th>#</th><th>TIME</th><th>PRIORITY</th><th>TYPE</th>
   <th>NAME</th><th>PHONE</th><th>DETAILS</th></tr></thead>
   <tbody id="hist"><tr><td colspan="7" class="none">No incidents yet.</td></tr></tbody>
  </table>
 </div>
</div>

<script>
function esc(s){return (s||"").replace(/[&<>]/g,function(c){
 return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}

async function tick(){
 try{
  const d = await (await fetch('/api/state')).json();

  const link = document.getElementById('link');
  link.textContent = d.link_ok ? 'LINK ONLINE' : 'LINK OFFLINE';
  link.className = 'pill ' + (d.link_ok ? 'ok' : 'bad');

  document.getElementById('last').textContent = 'LAST ' + (d.last_packet || '--:--:--');
  document.getElementById('tot').textContent = d.total;
  document.getElementById('hi').textContent = d.high;
  document.getElementById('port').textContent = d.serial_port || 'none';

  const L = d.latest;
  document.getElementById('latest').innerHTML = L ? (
   '<p class="big">' + esc(L.type) + ' <span class="chip ' + L.priority + '">' + L.priority + '</span></p>' +
   '<div class="sub" style="margin-bottom:12px">Received ' + L.time + ' on ' + L.date + '</div>' +
   '<div class="row"><span class="k">Name</span><span>' + esc(L.name) + '</span></div>' +
   '<div class="row"><span class="k">Phone</span><span class="mono">' + esc(L.phone) + '</span></div>' +
   '<div class="row"><span class="k">Details</span><span>' + esc(L.message) + '</span></div>' +
   '<div class="row"><span class="k">Status</span><span>' + esc(L.status) + '</span></div>'
  ) : '<div class="none">Waiting for the first SOS...</div>';

  document.getElementById('hist').innerHTML = d.incidents.length ? d.incidents.map(function(i){
   return '<tr><td class="mono">' + i.id + '</td><td class="mono">' + i.time + '</td>' +
    '<td><span class="chip ' + i.priority + '">' + i.priority + '</span></td>' +
    '<td>' + esc(i.type) + '</td><td>' + esc(i.name) + '</td>' +
    '<td class="mono">' + esc(i.phone) + '</td><td>' + esc(i.message) + '</td></tr>';
  }).join('') : '<tr><td colspan="7" class="none">No incidents yet.</td></tr>';
 }catch(e){ /* keep polling */ }
}
tick(); setInterval(tick, REFRESH_MS_PLACEHOLDER);
</script>
</body></html>
"""


@app.route("/")
def home():
    return render_template_string(
        PAGE.replace("REFRESH_MS_PLACEHOLDER", str(config.REFRESH_MS)))


@app.route("/api/state")
def api_state():
    items, total, last = store.snapshot()
    return jsonify({
        "link_ok": bool(receiver.connected and receiver.port),
        "serial_port": receiver.port,
        "last_packet": (datetime.fromtimestamp(last).strftime("%H:%M:%S")
                        if last else None),
        "total": total,
        "high": sum(1 for i in items if i["priority"] == "HIGH"),
        "latest": items[0] if items else None,
        "incidents": items,
    })


if __name__ == "__main__":
    receiver.start()
    print("ResQMesh dashboard on http://{}:{}".format(
        config.DASHBOARD_HOST, config.DASHBOARD_PORT))
    print("Open it from your laptop at http://<PI_IP>:{}".format(
        config.DASHBOARD_PORT))
    time.sleep(0.5)
    app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT,
            debug=False, use_reloader=False)
