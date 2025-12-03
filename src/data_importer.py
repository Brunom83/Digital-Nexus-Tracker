# src/data_importer.py
import pandas as pd
from database_manager import get_db_connection, create_tables
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def import_digimon_data():
    path = os.path.join(DATA_DIR, 'DigiHatch Tracker.csv')
    if not os.path.exists(path): return
    
    try:
        df = pd.read_csv(path, sep=';').fillna('')
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            count = 0
            for _, row in df.iterrows():
                nome = row['Digital Monsters List']
                fonte = row['WHERE TO GET THEM']
                hatch = 0 if str(row['Hatched?']).upper() == 'FALSO' else 1
                cloned = 0 if str(row['Fully Cloned?']).upper() == 'FALSO' else 1
                
                cursor.execute("""
                    INSERT OR REPLACE INTO digimon_collection (nome, hatch_status, cloned_status, fonte)
                    VALUES (?, ?, ?, ?)
                """, (nome, hatch, cloned, fonte))
                count += 1
            print(f"✅ Importados {count} Digimons.")
    except Exception as e:
        print(f"Erro Digimon Import: {e}")

def import_seals_data():
    path = os.path.join(DATA_DIR, 'Seals Tracker.csv')
    if not os.path.exists(path): 
        print("AVISO: Seals Tracker.csv não encontrado.")
        return

    try:
        # Lê o CSV
        df = pd.read_csv(path, sep=';')
        
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            count_imported = 0
            
            # Lista das colunas de STATS no teu CSV (pela ordem)
            # 0:AT, 2:HP, 4:DE, 6:CT, 8:HT
            stats_map = ['AT', 'HP', 'DE', 'CT', 'HT']
            
            for i, stat in enumerate(stats_map):
                col_name_idx = i * 2       # Ex: 0, 2, 4...
                col_count_idx = (i * 2) + 1 # Ex: 1, 3, 5...
                
                # Pega apenas nestas duas colunas e remove vazios
                subset = df.iloc[:, [col_name_idx, col_count_idx]].dropna()
                
                for _, row in subset.iterrows():
                    digi_name = row.iloc[0]
                    val_count = row.iloc[1]
                    
                    if pd.notna(digi_name) and str(digi_name).strip() != '':
                        # Insere na BD
                        cursor.execute("""
                            INSERT OR IGNORE INTO seal_tracker (digimon_nome, stat_type, count)
                            VALUES (?, ?, ?)
                        """, (str(digi_name), stat, int(val_count) if pd.notna(val_count) else 0))
                        count_imported += 1
            
            print(f"✅ Importados {count_imported} Seals.")

    except Exception as e:
        print(f"Erro Seals Import: {e}")

if __name__ == '__main__':
    create_tables()
    import_digimon_data()
    import_seals_data()