# src/digimon_viewmodel.py

import sqlite3
import os
import sys
import pandas as pd
from database_manager import get_db_connection, create_tables

# --- FUNÇÃO AUXILIAR PARA CAMINHOS (CRÍTICO PARA O .EXE) ---
def get_resource_path(relative_path):
    """
    Obtém o caminho absoluto para recursos (data/db).
    Funciona tanto no ambiente de desenvolvimento (Python)
    como no executável final (PyInstaller/MEIPASS).
    """
    try:
        # Se estiver a correr como .exe, o PyInstaller cria uma pasta temporária
        base_path = sys._MEIPASS
    except Exception:
        # Se estiver a correr como script normal
        base_path = os.path.abspath(".")

    # Tenta encontrar o caminho
    final_path = os.path.join(base_path, relative_path)
    
    # Fallback: Se não encontrar, tenta subir um nível (comum em dev)
    if not os.path.exists(final_path):
        return os.path.join(os.path.abspath("."), relative_path)
        
    return final_path

class DigimonViewModel:
    def __init__(self, profile_name="default"):
        self.profile = profile_name
        # 1. Garante que as tabelas existem para este perfil
        create_tables(self.profile)
        # 2. Se a BD estiver vazia, preenche com os dados dos CSVs
        self._seed_database()

    def _get_conn(self):
        """Helper para obter a conexão do perfil atual de forma rápida."""
        return get_db_connection(self.profile)

    # =========================================================================
    #  SISTEMA DE SEMEADURA (IMPORTAÇÃO AUTOMÁTICA)
    # =========================================================================
    def _seed_database(self):
        conn = self._get_conn()
        if conn is None: return

        # Verifica se já existem digimons na coleção
        try:
            res = conn.execute("SELECT COUNT(*) as c FROM digimon_collection").fetchone()
            count = res['c'] if res else 0
        except: count = 0
        
        # Se estiver vazio (0), vamos importar!
        if count == 0:
            print(f"🌱 [SEED] A importar dados iniciais para o perfil '{self.profile}'...")
            self._import_csv_digimons(conn)
            self._import_csv_seals(conn)
            print("✅ [SEED] Importação concluída!")

    def _import_csv_digimons(self, conn):
        # Procura o ficheiro na pasta data
        csv_path = get_resource_path(os.path.join('data', 'DigiHatch Tracker.csv'))
        
        if os.path.exists(csv_path):
            try:
                # Lê o CSV com separador ';'
                df = pd.read_csv(csv_path, sep=';').fillna('')
                with conn:
                    for _, row in df.iterrows():
                        nome = row.get('Digital Monsters List', 'Unknown')
                        fonte = row.get('WHERE TO GET THEM', 'Unknown')
                        # Insere na BD
                        conn.execute("INSERT OR IGNORE INTO digimon_collection (nome, hatch_status, cloned_status, fonte) VALUES (?, 0, 0, ?)", (nome, fonte))
            except Exception as e:
                print(f"❌ Erro ao importar Digimons: {e}")
        else:
            print(f"⚠️ Aviso: Ficheiro não encontrado para Seed: {csv_path}")

    def _import_csv_seals(self, conn):
        csv_path = get_resource_path(os.path.join('data', 'Seals Tracker.csv'))
        
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, sep=';').fillna('')
                stats_map = ['AT', 'HP', 'DE', 'CT', 'HT', 'BL', 'EV', 'DS']
                with conn:
                    for i, stat in enumerate(stats_map):
                        # O CSV tem pares de colunas (Nome, Quantidade)
                        col_idx = i * 2
                        if col_idx < len(df.columns):
                            # Pega na coluna do nome
                            subset = df.iloc[:, [col_idx]].dropna()
                            for _, row in subset.iterrows():
                                name = row.iloc[0]
                                if name and str(name).strip() != '':
                                    conn.execute("INSERT OR IGNORE INTO seal_tracker (digimon_nome, stat_type, count) VALUES (?, ?, 0)", (str(name), stat))
            except Exception as e:
                print(f"❌ Erro ao importar Seals: {e}")

    # =========================================================================
    #  FUNCIONALIDADES: COLEÇÃO & SEALS
    # =========================================================================
    def get_all_digimon(self):
        with self._get_conn() as conn: 
            return conn.execute("SELECT * FROM digimon_collection ORDER BY nome").fetchall()

    def update_digimon_status(self, digimon_id, field, value):
        with self._get_conn() as conn: 
            conn.execute(f"UPDATE digimon_collection SET {field} = ? WHERE id = ?", (value, digimon_id))
            conn.commit()

    def get_collection_stats(self):
        with self._get_conn() as conn:
            r = conn.execute("SELECT COUNT(id) as t, SUM(hatch_status) as h, SUM(cloned_status) as c FROM digimon_collection").fetchone()
            return {'total': r['t'] or 0, 'chocados': r['h'] or 0, 'clonados': r['c'] or 0}

    def get_all_seals(self):
        with self._get_conn() as conn: 
            return conn.execute("SELECT * FROM seal_tracker ORDER BY stat_type, digimon_nome").fetchall()

    def update_seal_count(self, s_id, val):
        with self._get_conn() as conn: 
            conn.execute("UPDATE seal_tracker SET count = ? WHERE id = ?", (val, s_id))
            conn.commit()

    def add_manual_seal(self, name, stat):
        try:
            with self._get_conn() as conn:
                conn.execute("INSERT INTO seal_tracker (digimon_nome, stat_type, count) VALUES (?, ?, 0)", (name, stat))
                conn.commit()
                return True
        except: return False

    # =========================================================================
    #  FUNCIONALIDADES: FINANÇAS, VIP & DUNGEONS
    # =========================================================================
    def get_wallet(self):
        with self._get_conn() as conn: 
            return conn.execute("SELECT * FROM player_wallet WHERE id = 1").fetchone()

    def get_dungeons(self):
        with self._get_conn() as conn: 
            return conn.execute("SELECT * FROM dungeons ORDER BY name, difficulty").fetchall()

    def add_dungeon(self, name, difficulty, points):
        try:
            with self._get_conn() as conn:
                conn.execute("INSERT INTO dungeons (name, difficulty, base_points) VALUES (?, ?, ?)", (name, difficulty, points))
                conn.commit()
                return True
        except: return False

    def delete_dungeon(self, d_id):
        with self._get_conn() as conn: 
            conn.execute("DELETE FROM dungeons WHERE id = ?", (d_id,))
            conn.commit()
            return True

    def process_run(self, dungeon_id):
        """
        Processa uma run: Adiciona pontos à carteira (com multiplicador VIP) e regista no histórico.
        """
        conn = self._get_conn()
        with conn:
            d = conn.execute("SELECT * FROM dungeons WHERE id = ?", (dungeon_id,)).fetchone()
            w = conn.execute("SELECT * FROM player_wallet WHERE id = 1").fetchone()
            
            if not d: return

            # Lógica VIP
            multiplier = w['vip_level'] + 1
            total_earned = d['base_points'] * multiplier
            
            # Escolhe a moeda certa
            field = "points_easy"
            if d['difficulty'] == 'Normal': field = "points_normal"
            elif d['difficulty'] == 'Hard': field = "points_hard"
            
            # Atualizações
            conn.execute("UPDATE dungeons SET run_count = run_count + 1 WHERE id = ?", (dungeon_id,))
            conn.execute(f"UPDATE player_wallet SET {field} = {field} + ? WHERE id = 1", (total_earned,))
            
            # Log
            log_desc = f"Run: {d['name']} ({d['difficulty']})"
            log_change = f"+{total_earned} {d['difficulty']} (VIP x{multiplier})"
            conn.execute("INSERT INTO run_history (description, points_change) VALUES (?, ?)", (log_desc, log_change))
            
            conn.commit()

    def try_upgrade_vip(self, method):
        """Tenta subir de nível VIP gastando pontos."""
        # Custos definidos
        costs = {'Easy': 30000, 'Normal': 20000, 'Hard': 10000}
        cost = costs.get(method)
        field = f"points_{method.lower()}"
        
        conn = self._get_conn()
        with conn:
            w = conn.execute("SELECT * FROM player_wallet WHERE id = 1").fetchone()
            
            if w['vip_level'] >= 5: return "Max Level"
            
            if w[field] >= cost:
                # Paga e sobe nível
                conn.execute(f"UPDATE player_wallet SET {field} = {field} - ?, vip_level = vip_level + 1 WHERE id = 1", (cost,))
                
                # Log
                conn.execute("INSERT INTO run_history (description, points_change) VALUES (?, ?)", 
                             (f"UPGRADE VIP {w['vip_level']+1}", f"-{cost} {method}"))
                conn.commit()
                return True
            return False

    # =========================================================================
    #  FUNCIONALIDADES: LOJAS (SHOPS)
    # =========================================================================
    def add_shop_item(self, npc, name, cost, img_path):
        try:
            with self._get_conn() as conn:
                conn.execute("INSERT INTO shop_items (npc_type, item_name, cost, image_path) VALUES (?, ?, ?, ?)", 
                             (npc, name, cost, img_path))
                conn.commit()
                return True
        except: return False

    def get_shop_items(self, npc):
        with self._get_conn() as conn: 
            return conn.execute("SELECT * FROM shop_items WHERE npc_type = ? ORDER BY item_name", (npc,)).fetchall()
            
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
                conn.execute("INSERT INTO run_history (description, points_change) VALUES (?, ?)", 
                             (f"Comprou: {item['item_name']}", f"-{item['cost']} {npc}"))
                conn.commit()
                return True
            return False

    def delete_shop_item(self, item_id):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM shop_items WHERE id = ?", (item_id,))
            conn.commit()

    # =========================================================================
    #  FUNCIONALIDADES: TAREFAS DIÁRIAS (DAILIES)
    # =========================================================================
    def get_tasks(self):
        with self._get_conn() as conn: 
            # Garante que a tabela existe, caso seja um update
            try:
                return conn.execute("SELECT * FROM daily_tasks ORDER BY reset_type, name").fetchall()
            except: return []
    
    def add_task(self, name, rtype):
        try:
            with self._get_conn() as conn: 
                conn.execute("INSERT INTO daily_tasks (name, reset_type) VALUES (?, ?)", (name, rtype))
                conn.commit()
                return True
        except: return False

    def toggle_task(self, tid, status):
        with self._get_conn() as conn: 
            conn.execute("UPDATE daily_tasks SET is_done = ? WHERE id = ?", (status, tid))
            conn.commit()

    def reset_tasks(self, rtype):
        with self._get_conn() as conn: 
            conn.execute("UPDATE daily_tasks SET is_done = 0 WHERE reset_type = ?", (rtype,))
            conn.commit()
    
    def delete_task(self, tid):
        with self._get_conn() as conn: 
            conn.execute("DELETE FROM daily_tasks WHERE id = ?", (tid,))
            conn.commit()

    # =========================================================================
    #  FUNCIONALIDADES: HISTÓRICO GERAL
    # =========================================================================
    def get_history(self):
        with self._get_conn() as conn: 
            return conn.execute("SELECT * FROM run_history ORDER BY timestamp DESC LIMIT 50").fetchall()
    
    def clear_history(self):
        with self._get_conn() as conn: 
            conn.execute("DELETE FROM run_history")
            conn.commit()