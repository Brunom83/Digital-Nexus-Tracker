# src/digimon_viewmodel.py
import sqlite3
import os
import pandas as pd # Precisamos disto para ler os CSVs
from database_manager import get_db_connection, create_tables

class DigimonViewModel:
    def __init__(self, profile_name="default"):
        self.profile = profile_name
        create_tables(self.profile)
        self._seed_database() # <--- A MAGIA ACONTECE AQUI

    def _get_conn(self):
        return get_db_connection(self.profile)

    def _seed_database(self):
        """
        Verifica se a BD está vazia. Se estiver, carrega os dados dos CSVs (Pasta data/).
        Isto garante que novos jogadores têm a lista pronta.
        """
        conn = self._get_conn()
        if conn is None: return

        # Verifica se já temos digimons
        count = conn.execute("SELECT COUNT(*) as c FROM digimon_collection").fetchone()['c']
        
        if count == 0:
            print(f"🌱 A semear BD para {self.profile}...")
            self._import_csv_digimons(conn)
            self._import_csv_seals(conn)
            self._import_default_shops(conn) # Opcional: Lojas padrão
            print("✅ Semeadura completa!")

    def _import_csv_digimons(self, conn):
        # Caminho para o CSV (assume que está na pasta data/ ao lado do executável/src)
        # Ajuste para funcionar tanto em Python como em .EXE
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Se estivermos num .exe (_internal), precisamos de subir ou ajustar
        if '_internal' in base_path:
            csv_path = os.path.join(base_path, '..', 'data', 'DigiHatch Tracker.csv')
        else:
            csv_path = os.path.join(base_path, '..', 'data', 'DigiHatch Tracker.csv')

        if not os.path.exists(csv_path):
            # Tenta procurar na pasta atual (caso do exe mal configurado)
            csv_path = os.path.join('data', 'DigiHatch Tracker.csv')

        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, sep=';').fillna('')
                with conn:
                    for _, row in df.iterrows():
                        nome = row.get('Digital Monsters List', 'Unknown')
                        fonte = row.get('WHERE TO GET THEM', 'Unknown')
                        # Insere com status 0 (Não tem)
                        conn.execute("INSERT OR IGNORE INTO digimon_collection (nome, hatch_status, cloned_status, fonte) VALUES (?, 0, 0, ?)", (nome, fonte))
            except Exception as e:
                print(f"Erro a importar Digimons: {e}")

    def _import_csv_seals(self, conn):
        # Mesma lógica de caminho
        base_path = os.path.dirname(os.path.abspath(__file__))
        if '_internal' in base_path:
            csv_path = os.path.join(base_path, '..', 'data', 'Seals Tracker.csv')
        else:
            csv_path = os.path.join(base_path, '..', 'data', 'Seals Tracker.csv')
            
        if not os.path.exists(csv_path):
             csv_path = os.path.join('data', 'Seals Tracker.csv')

        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, sep=';')
                stats_map = ['AT', 'HP', 'DE', 'CT', 'HT', 'BL', 'EV', 'DS']
                with conn:
                    for i, stat in enumerate(stats_map):
                        # Lógica de colunas pares (Nome, Quantidade)
                        # No CSV original tinhas pares. Vamos simplificar e assumir que o CSV tem estrutura
                        # Se o teu CSV mudou, esta lógica pode precisar de ajuste.
                        # Vou usar a lógica robusta que fizemos antes:
                        col_name_idx = i * 2
                        if col_name_idx < len(df.columns):
                            subset = df.iloc[:, [col_name_idx]].dropna()
                            for _, row in subset.iterrows():
                                name = row.iloc[0]
                                if name and str(name).strip() != '':
                                    conn.execute("INSERT OR IGNORE INTO seal_tracker (digimon_nome, stat_type, count) VALUES (?, ?, 0)", (str(name), stat))
            except Exception as e:
                print(f"Erro a importar Seals: {e}")

    def _import_default_shops(self, conn):
        # Podes hardcodar aqui as lojas iniciais para todos terem
        try:
            with conn:
                # Exemplo: Backup Disk na loja Normal
                conn.execute("INSERT OR IGNORE INTO shop_items (npc_type, item_name, cost, image_path) VALUES (?, ?, ?, ?)", 
                             ('Normal', 'Backup Disk', 500, ''))
        except: pass

    # --- RESTO DAS FUNÇÕES (Mantém tudo igual ao anterior) ---
    # (Coleção, Seals, Finanças, Dungeons, etc.)
    
    # COPIA AQUI TODAS AS OUTRAS FUNÇÕES QUE JÁ TINHAS NO FICHEIRO ANTERIOR
    # (get_all_digimon, process_run, etc.)
    
    def get_all_digimon(self):
        with self._get_conn() as conn: return conn.execute("SELECT * FROM digimon_collection ORDER BY nome").fetchall()
    def update_digimon_status(self, digimon_id, field, value):
        with self._get_conn() as conn: conn.execute(f"UPDATE digimon_collection SET {field} = ? WHERE id = ?", (value, digimon_id)); conn.commit()
    def get_collection_stats(self):
        with self._get_conn() as conn:
            r = conn.execute("SELECT COUNT(id) as t, SUM(hatch_status) as h, SUM(cloned_status) as c FROM digimon_collection").fetchone()
            return {'total': r['t'] or 0, 'chocados': r['h'] or 0, 'clonados': r['c'] or 0}
    def get_all_seals(self):
        with self._get_conn() as conn: return conn.execute("SELECT * FROM seal_tracker ORDER BY stat_type, digimon_nome").fetchall()
    def update_seal_count(self, s_id, val):
        with self._get_conn() as conn: conn.execute("UPDATE seal_tracker SET count = ? WHERE id = ?", (val, s_id)); conn.commit()
    def add_manual_seal(self, name, stat):
        try:
            with self._get_conn() as conn:
                conn.execute("INSERT INTO seal_tracker (digimon_nome, stat_type, count) VALUES (?, ?, 0)", (name, stat))
                conn.commit(); return True
        except: return False
    def get_wallet(self):
        with self._get_conn() as conn: return conn.execute("SELECT * FROM player_wallet WHERE id = 1").fetchone()
    def get_dungeons(self):
        with self._get_conn() as conn: return conn.execute("SELECT * FROM dungeons ORDER BY name, difficulty").fetchall()
    def add_dungeon(self, name, difficulty, points):
        try:
            with self._get_conn() as conn:
                conn.execute("INSERT INTO dungeons (name, difficulty, base_points) VALUES (?, ?, ?)", (name, difficulty, points))
                conn.commit(); return True
        except: return False
    def delete_dungeon(self, d_id):
        with self._get_conn() as conn: conn.execute("DELETE FROM dungeons WHERE id = ?", (d_id,)); conn.commit(); return True
    def process_run(self, dungeon_id):
        conn = self._get_conn()
        with conn:
            d = conn.execute("SELECT * FROM dungeons WHERE id = ?", (dungeon_id,)).fetchone()
            w = conn.execute("SELECT * FROM player_wallet WHERE id = 1").fetchone()
            if not d: return
            multiplier = w['vip_level'] + 1
            total = d['base_points'] * multiplier
            field = "points_easy" if d['difficulty'] == 'Easy' else "points_normal" if d['difficulty'] == 'Normal' else "points_hard"
            conn.execute("UPDATE dungeons SET run_count = run_count + 1 WHERE id = ?", (dungeon_id,))
            conn.execute(f"UPDATE player_wallet SET {field} = {field} + ? WHERE id = 1", (total,))
            conn.execute("INSERT INTO run_history (description, points_change) VALUES (?, ?)", (f"Run: {d['name']} ({d['difficulty']})", f"+{total} {d['difficulty']}"))
            conn.commit()
    def try_upgrade_vip(self, method):
        costs = {'Easy': 30000, 'Normal': 20000, 'Hard': 10000}
        cost = costs.get(method)
        field = f"points_{method.lower()}"
        conn = self._get_conn()
        with conn:
            w = conn.execute("SELECT * FROM player_wallet WHERE id = 1").fetchone()
            if w['vip_level'] >= 5: return "Max Level"
            if w[field] >= cost:
                conn.execute(f"UPDATE player_wallet SET {field} = {field} - ?, vip_level = vip_level + 1 WHERE id = 1", (cost,))
                conn.execute("INSERT INTO run_history (description, points_change) VALUES (?, ?)", (f"UPGRADE VIP {w['vip_level']+1} via {method}", f"-{cost} {method}"))
                conn.commit(); return True
            return False
    def add_shop_item(self, npc, name, cost, img_path):
        try:
            with self._get_conn() as conn:
                conn.execute("INSERT INTO shop_items (npc_type, item_name, cost, image_path) VALUES (?, ?, ?, ?)", (npc, name, cost, img_path))
                conn.commit(); return True
        except: return False
    def get_shop_items(self, npc):
        with self._get_conn() as conn: return conn.execute("SELECT * FROM shop_items WHERE npc_type = ? ORDER BY item_name", (npc,)).fetchall()
    def buy_shop_item(self, item_id):
        conn = self._get_conn()
        with conn:
            item = conn.execute("SELECT * FROM shop_items WHERE id = ?", (item_id,)).fetchone()
            w = conn.execute("SELECT * FROM player_wallet WHERE id = 1").fetchone()
            if not item: return False
            npc = item['npc_type']
            field = f"points_{npc.lower()}"
            if w[field] >= item['cost']:
                conn.execute(f"UPDATE player_wallet SET {field} = {field} - ? WHERE id = 1", (item['cost'],))
                conn.execute("INSERT INTO run_history (description, points_change) VALUES (?, ?)", (f"Comprou: {item['item_name']}", f"-{item['cost']} {npc}"))
                conn.commit(); return True
            return False
    def delete_shop_item(self, item_id):
        with self._get_conn() as conn: conn.execute("DELETE FROM shop_items WHERE id = ?", (item_id,)); conn.commit()
    def get_history(self):
        with self._get_conn() as conn: return conn.execute("SELECT * FROM run_history ORDER BY timestamp DESC LIMIT 50").fetchall()
    def clear_history(self):
        with self._get_conn() as conn: conn.execute("DELETE FROM run_history"); conn.commit()