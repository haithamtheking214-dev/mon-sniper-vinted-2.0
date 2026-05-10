from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
# COLLE TON LIEN DISCORD ICI
WEBHOOK_URL = "https://discord.com/api/webhooks/1502382480018116741/TCeDP3g929NahLjDf-PaE9-v_K7NekZ8_Ef-_z1wXJcjoOADkFc34BIme69nPwFDv52l" 

class VSniperExtreme:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        self.last_items = []

    def send_discord(self, item):
        if not WEBHOOK_URL or "discord.com" not in WEBHOOK_URL: return
        data = {
            "username": "V-SNIPER ELITE",
            "embeds": [{
                "title": f"✨ {item['brand']} - {item['title']}",
                "url": item['url'],
                "color": 5763719,
                "fields": [
                    {"name": "💰 Prix", "value": f"`{item['price']}€`", "inline": True},
                    {"name": "📏 Taille", "value": f"`{item['size']}`", "inline": True}
                ],
                "image": {"url": item['img']}
            }]
        }
        requests.post(WEBHOOK_URL, json=data)

    def scan(self, q, pmin, pmax, status, size, discord_on):
        try:
            session = requests.Session()
            session.get("https://www.vinted.fr", headers=self.headers, timeout=10)
            p = [f"search_text={q}", "order=newest_first"]
            if pmin: p.append(f"price_from={pmin}")
            if pmax: p.append(f"price_to={pmax}")
            if status: p.append(f"status_ids={status}")
            if size: p.append(f"size_ids={size}")
            
            url = f"https://www.vinted.fr/api/v2/catalog/items?{'&'.join(p)}"
            r = session.get(url, headers=self.headers, timeout=10)
            items = r.json().get('items', [])
            res = []
            for i in items[:20]:
                d = {"id": i.get('id'), "title": i.get('title'), "price": i.get('price', {}).get('amount'), "brand": i.get('brand_title', 'N/A'), "size": i.get('size_title', 'N/A'), "img": i.get('photo', {}).get('url') if i.get('photo') else "", "url": f"https://www.vinted.fr{i.get('url')}"}
                res.append(d)
                if discord_on == 'true' and d['id'] not in self.last_items:
                    self.send_discord(d)
            self.last_items = [x['id'] for x in res]
            return res
        except Exception as e: return {"error": str(e)}

sniper = VSniperExtreme()

# --- L'INTERFACE (DESIGN NOIR & BLEU) ---
UI = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #010103; color: #fff; font-family: sans-serif; }
        .panel { background: #08080c; border: 1px solid #1a1a25; }
        input, select { background: #000 !important; border: 1px solid #1a1a25 !important; color: #fff !important; }
    </style>
</head>
<body class="flex h-screen">
    <aside class="w-80 panel p-6 flex flex-col gap-6">
        <h1 class="text-3xl font-black italic text-cyan-400 uppercase tracking-tighter">V-SNIPER</h1>
        <div class="space-y-4">
            <input id="q" placeholder="Marque..." class="w-full p-3 rounded-lg">
            <div class="flex gap-2">
                <input id="pmin" placeholder="Min" class="w-1/2 p-3 rounded-lg">
                <input id="pmax" placeholder="Max" class="w-1/2 p-3 rounded-lg">
            </div>
            <select id="size" class="w-full p-3 rounded-lg">
                <option value="">Taille</option>
                <option value="764">S</option><option value="765">M</option><option value="766">L</option>
            </select>
            <div class="flex items-center gap-2">
                <input type="checkbox" id="discord"> <label class="text-xs font-bold text-zinc-400">DISCORD ON</label>
            </div>
            <button onclick="run()" class="w-full bg-cyan-400 text-black font-black py-4 rounded-xl uppercase">Lancer Scan</button>
        </div>
    </aside>
    <main class="flex-1 p-10 overflow-y-auto">
        <div id="grid" class="grid grid-cols-2 lg:grid-cols-4 gap-6"></div>
    </main>
    <script>
        async function run() {
            const g = document.getElementById('grid');
            g.innerHTML = '<p class="col-span-full text-center animate-pulse text-cyan-400">SCANNING...</p>';
            const url = `/api/scan?q=${document.getElementById('q').value}&pmin=${document.getElementById('pmin').value}&pmax=${document.getElementById('pmax').value}&size=${document.getElementById('size').value}&discord=${document.getElementById('discord').checked}`;
            const r = await fetch(url);
            const d = await r.json();
            g.innerHTML = d.map(i => `
                <div class="panel p-3 rounded-xl">
                    <img src="${i.img}" class="w-full h-40 object-cover rounded-lg mb-2">
                    <div class="flex justify-between text-[10px] font-bold text-cyan-400"><span>${i.brand}</span><span>${i.price}€</span></div>
                    <div class="text-xs truncate">${i.title}</div>
                    <a href="${i.url}" target="_blank" class="block bg-white text-black text-center py-2 rounded mt-3 font-bold text-[10px]">VOIR</a>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(UI)

@app.route('/api/scan')
def api_scan():
    q = request.args.get('q', 'Nike')
    pmin, pmax = request.args.get('pmin', ''), request.args.get('pmax', '')
    size = request.args.get('size', '')
    discord = request.args.get('discord', 'false')
    return jsonify(sniper.scan(q, pmin, pmax, "", size, discord))

app = app
