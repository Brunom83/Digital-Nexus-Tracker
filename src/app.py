# src/app.py
import sys
import math
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QTableWidget, QTableWidgetItem, QCheckBox, 
    QHBoxLayout, QLabel, QHeaderView, QTabWidget, QSpinBox, 
    QPushButton, QLineEdit, QComboBox, QFormLayout, QGroupBox, QMessageBox,
    QListWidget, QListWidgetItem, QProgressBar, QFileDialog, QDialog, QScrollArea
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon
import qtawesome as qta 
from digimon_viewmodel import DigimonViewModel

# --- CSS ---
DARK_THEME = """
QMainWindow, QWidget, QDialog { background-color: #1e1e24; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
QTableWidget, QListWidget { background-color: #25252b; border: 1px solid #3a3a45; border-radius: 8px; outline: 0; }
QHeaderView::section { background-color: #2d2d36; color: #00d4ff; padding: 10px; font-weight: bold; border: none; border-bottom: 2px solid #00d4ff; }
QTableWidget::item:selected { background-color: #3d4450; border-left: 3px solid #00d4ff; }
QTabWidget::pane { border: 0; background: #1e1e24; }
QTabBar::tab { background: #25252b; color: #888; padding: 12px 25px; margin-right: 5px; border-radius: 5px; font-weight: bold;}
QTabBar::tab:selected { background: #00d4ff; color: #1e1e24; }
QSpinBox, QLineEdit, QComboBox { background-color: #2d2d36; color: #fff; border: 1px solid #4a4a55; border-radius: 4px; padding: 8px; font-weight: bold; min-height: 20px;}
QGroupBox { border: 1px solid #4a4a55; border-radius: 8px; margin-top: 30px; font-weight: bold; color: #00d4ff; background-color: #25252b; padding-top: 20px;}
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; top: 0px; left: 15px; padding: 0 5px; background-color: #25252b; }
QPushButton { background-color: #3a3a45; border: none; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;}
QPushButton:hover { background-color: #4a4a55; border: 1px solid #00d4ff; }
QCheckBox { spacing: 10px; }
QCheckBox::indicator { width: 22px; height: 22px; border: 2px solid #555; background-color: #2d2d36; border-radius: 4px;}
QCheckBox::indicator:checked { background-color: #00d4ff; border-color: #00d4ff; }
QProgressBar { border: none; border-radius: 4px; text-align: center; background: #15151a; color: white; font-weight: bold; height: 25px;}
QScrollArea { border: none; background-color: transparent; }
"""

# --- JANELA DE LOGIN (NOVO) ---
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login DMO Tracker")
        self.setFixedSize(400, 250)
        self.selected_profile = None
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo/Title
        lbl = QLabel("QUEM ESTÁ A JOGAR?")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d4ff;")
        layout.addWidget(lbl)
        
        # Input Perfil
        self.combo_profiles = QComboBox()
        self.combo_profiles.setEditable(True)
        self.combo_profiles.setPlaceholderText("Escreve o teu nome...")
        
        # Carregar perfis existentes
        profiles_dir = os.path.join(os.path.dirname(__file__), '..', 'profiles')
        if os.path.exists(profiles_dir):
            files = [f.replace('.db', '') for f in os.listdir(profiles_dir) if f.endswith('.db')]
            self.combo_profiles.addItems(files)
        
        layout.addWidget(self.combo_profiles)
        
        # Botão Entrar
        btn_login = QPushButton("ENTRAR / CRIAR")
        btn_login.setStyleSheet("background-color: #00d4ff; color: #000; padding: 15px;")
        btn_login.clicked.connect(self.handle_login)
        layout.addWidget(btn_login)

    def handle_login(self):
        name = self.combo_profiles.currentText().strip()
        if name:
            self.selected_profile = name
            self.accept() # Fecha e diz "OK"
        else:
            QMessageBox.warning(self, "Erro", "Escreve um nome!")

# --- APP PRINCIPAL ---
class DigimonTrackerApp(QMainWindow):
    def __init__(self, profile_name):
        super().__init__()
        self.vm = DigimonViewModel(profile_name) # Passa o perfil para a BD
        self.setWindowTitle(f"DMO Tracker: Digital Nexus Edition | Perfil: {profile_name}")
        self.resize(1500, 950)
        self.setStyleSheet(DARK_THEME)
        self.setWindowIcon(qta.icon('fa5s.egg', color='#00d4ff'))

        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(24, 24)) 
        self.setCentralWidget(self.tabs)

        self.tab_collection = QWidget(); self.setup_collection_tab()
        self.tabs.addTab(self.tab_collection, qta.icon('fa5s.dragon', color='#fff'), " COLEÇÃO")

        self.tab_seals = QWidget(); self.setup_seals_tab()
        self.tabs.addTab(self.tab_seals, qta.icon('fa5s.stamp', color='#fff'), " SEALS")
        
        self.tab_finance = QWidget(); self.setup_finance_tab()
        self.tabs.addTab(self.tab_finance, qta.icon('fa5s.coins', color='#fff'), " DASHBOARD")

        self.load_collection_data()
        self.load_seals_data('AT') 
        self.update_header_stats()
        self.refresh_finance_ui()

    # ... (COLEÇÃO E SEALS IGUAIS AO ANTERIOR - MANTÉM O CÓDIGO) ...
    def setup_collection_tab(self):
        layout = QVBoxLayout(self.tab_collection); layout.setSpacing(15); layout.setContentsMargins(20, 20, 20, 20)
        self.stats_label = QLabel("Carregando..."); self.stats_label.setStyleSheet("background: #25252b; border-left: 5px solid #00d4ff; padding: 20px; font-size: 18px; border-radius: 5px;")
        layout.addWidget(self.stats_label)
        self.col_table = QTableWidget(); self.col_table.setColumnCount(5); self.col_table.setHorizontalHeaderLabels(["Nome", "Hatched?", "Full Cloned?", "Fonte", "ID"])
        self.col_table.verticalHeader().setVisible(False); self.col_table.verticalHeader().setDefaultSectionSize(50)
        self.col_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch); self.col_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.col_table.setColumnWidth(1, 120); self.col_table.setColumnWidth(2, 120); self.col_table.setColumnHidden(4, True)
        layout.addWidget(self.col_table)
    def load_collection_data(self):
        data = self.vm.get_all_digimon(); self.col_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.col_table.setItem(row, 0, QTableWidgetItem(item['nome'])); self.col_table.setItem(row, 3, QTableWidgetItem(item['fonte']))
            self.add_checkbox(self.col_table, row, 1, item['id'], 'hatch_status', item['hatch_status']); self.add_checkbox(self.col_table, row, 2, item['id'], 'cloned_status', item['cloned_status'])
    def add_checkbox(self, table, row, col, db_id, field, val):
        c = QWidget(); c.setStyleSheet("background: transparent;"); l = QHBoxLayout(c); l.setAlignment(Qt.AlignCenter); l.setContentsMargins(0,0,0,0)
        cb = QCheckBox(); cb.setCursor(Qt.PointingHandCursor); cb.setChecked(val == 1); cb.stateChanged.connect(lambda s, i=db_id, f=field: self.on_col_change(i, f, s))
        l.addWidget(cb); c.setLayout(l); table.setCellWidget(row, col, c)
    def on_col_change(self, db_id, field, state): self.vm.update_digimon_status(db_id, field, 1 if state == 2 else 0); self.update_header_stats()
    def update_header_stats(self):
        s = self.vm.get_collection_stats(); p_h = (s['chocados']/s['total'])*100 if s['total'] else 0; p_c = (s['clonados']/s['total'])*100 if s['total'] else 0
        self.stats_label.setText(f"📊 TOTAL: <b>{s['total']}</b> &nbsp;|&nbsp; 🐣 CHOCADOS: <span style='color:#00ff00'>{s['chocados']}</span> ({p_h:.1f}%) &nbsp;|&nbsp; 💪 CLONADOS: <span style='color:#d4af37'>{s['clonados']}</span> ({p_c:.1f}%)")

    def setup_seals_tab(self):
        layout = QHBoxLayout(self.tab_seals); layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(20)
        left_widget = QWidget(); left_layout = QVBoxLayout(left_widget); fl = QHBoxLayout(); self.seal_btns = {}
        for stat in ['AT', 'HP', 'DE', 'CT', 'HT', 'BL', 'EV', 'DS']:
            b = QPushButton(stat); b.setCheckable(True); b.setFixedWidth(60); b.clicked.connect(lambda c, s=stat: self.change_seal_filter(s))
            fl.addWidget(b); self.seal_btns[stat] = b
        fl.addStretch(); left_layout.addLayout(fl)
        self.seal_table = QTableWidget(); self.seal_table.setColumnCount(5); self.seal_table.setHorizontalHeaderLabels(["Stat", "Digimon", "Qtd", "Openers", "ID"])
        self.seal_table.verticalHeader().setVisible(False); self.seal_table.verticalHeader().setDefaultSectionSize(60)
        self.seal_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch); self.seal_table.setColumnHidden(4, True)
        left_layout.addWidget(self.seal_table)
        right_widget = QWidget(); right_widget.setFixedWidth(340); right_layout = QVBoxLayout(right_widget)
        gb_add = QGroupBox("➕ NOVO SELO"); fl_add = QFormLayout(); fl_add.setSpacing(15)
        self.inp_seal_stat = QComboBox(); self.inp_seal_stat.addItems(['AT', 'HP', 'DE', 'CT', 'HT', 'BL', 'EV', 'DS'])
        self.inp_seal_name = QLineEdit(); self.inp_seal_name.setPlaceholderText("Ex: Agumon")
        btn_save_seal = QPushButton(" Criar Selo"); btn_save_seal.setIcon(qta.icon('fa5s.save')); btn_save_seal.clicked.connect(self.add_new_seal); btn_save_seal.setStyleSheet("background-color: #00d4ff; color: black;")
        fl_add.addRow("Stat:", self.inp_seal_stat); fl_add.addRow("Nome:", self.inp_seal_name); fl_add.addRow(btn_save_seal)
        gb_add.setLayout(fl_add); right_layout.addWidget(gb_add); right_layout.addStretch()
        layout.addWidget(left_widget, 1); layout.addWidget(right_widget, 0)
        self.seal_btns['AT'].setChecked(True)
    def change_seal_filter(self, stat):
        for k, b in self.seal_btns.items(): b.setChecked(k == stat)
        self.load_seals_data(stat)
    def load_seals_data(self, filter_stat):
        data = [s for s in self.vm.get_all_seals() if s['stat_type'] == filter_stat]; self.seal_table.setRowCount(len(data)); bold = QFont(); bold.setBold(True); bold.setPointSize(12)
        for r, item in enumerate(data):
            self.seal_table.setItem(r, 0, QTableWidgetItem(item['stat_type'])); self.seal_table.setItem(r, 1, QTableWidgetItem(item['digimon_nome']))
            s = QSpinBox(); s.setRange(0, 3000); s.setValue(item['count']); s.setAlignment(Qt.AlignCenter); s.valueChanged.connect(lambda v, row=r, id=item['id']: self.on_seal_change(row, id, v))
            cw = QWidget(); cw.setStyleSheet("background: transparent;"); cl = QHBoxLayout(cw); cl.setContentsMargins(0,0,0,0); cl.setAlignment(Qt.AlignCenter); cl.addWidget(s); self.seal_table.setCellWidget(r, 2, cw)
            ops = math.ceil(item['count']/50); o_item = QTableWidgetItem(str(ops)); o_item.setTextAlignment(Qt.AlignCenter); o_item.setFont(bold)
            if ops > 0: o_item.setForeground(Qt.yellow)
            self.seal_table.setItem(r, 3, o_item)
    def on_seal_change(self, row, db_id, val): self.vm.update_seal_count(db_id, val); ops = math.ceil(val/50); it = QTableWidgetItem(str(ops)); it.setTextAlignment(Qt.AlignCenter); f = QFont(); f.setBold(True); f.setPointSize(12); it.setFont(f); it.setForeground(Qt.yellow if ops > 0 else Qt.white); self.seal_table.setItem(row, 3, it)
    def add_new_seal(self):
        name = self.inp_seal_name.text(); stat = self.inp_seal_stat.currentText()
        if name and self.vm.add_manual_seal(name, stat): self.inp_seal_name.clear(); 
        if self.seal_btns[stat].isChecked(): self.load_seals_data(stat)
        else: QMessageBox.warning(self, "Erro", "Selo já existe.")

    # ==========================================
    # ABA 3: FINANCE (COM SCROLL AREA FIX)
    # ==========================================
    def setup_finance_tab(self):
        # Layout principal da ABA (Sem scroll)
        tab_layout = QVBoxLayout(self.tab_finance)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area Mágica
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Só scroll vertical se precisar
        
        # Widget que vai DENTRO do scroll (O conteúdo real)
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(25)
        
        # Coluna 1 (Carteira)
        col1 = QWidget(); c1l = QVBoxLayout(col1); c1l.setSpacing(20)
        col1.setMinimumWidth(350) # Garante largura mínima
        
        wg = QGroupBox("💳 CARTEIRA"); wl = QVBoxLayout()
        self.l_easy = QLabel("EASY: 0"); self.l_easy.setStyleSheet("color:#00ff00; font-weight:bold; font-size:18px")
        self.l_norm = QLabel("NORMAL: 0"); self.l_norm.setStyleSheet("color:#00d4ff; font-weight:bold; font-size:18px")
        self.l_hard = QLabel("HARD: 0"); self.l_hard.setStyleSheet("color:#ff4444; font-weight:bold; font-size:18px")
        wl.addWidget(self.l_easy); wl.addWidget(self.l_norm); wl.addWidget(self.l_hard); wg.setLayout(wl); c1l.addWidget(wg)

        vg = QGroupBox("👑 VIP"); vl = QVBoxLayout(); vl.setSpacing(10)
        self.l_vip = QLabel("VIP 0"); self.l_vip.setStyleSheet("color:#d4af37; font-size:22px; font-weight:bold")
        vl.addWidget(self.l_vip)
        self.pb_easy = QProgressBar(); self.pb_easy.setRange(0, 30000); self.pb_easy.setStyleSheet("QProgressBar::chunk{background:#00ff00}")
        self.b_up_easy = QPushButton(" UPGRADE (Easy)"); self.b_up_easy.setIcon(qta.icon('fa5s.arrow-circle-up', color='white')); self.b_up_easy.clicked.connect(lambda: self.do_up('Easy'))
        vl.addWidget(QLabel("Easy (30k):")); vl.addWidget(self.pb_easy); vl.addWidget(self.b_up_easy)
        self.pb_norm = QProgressBar(); self.pb_norm.setRange(0, 20000); self.pb_norm.setStyleSheet("QProgressBar::chunk{background:#00d4ff}")
        self.b_up_norm = QPushButton(" UPGRADE (Normal)"); self.b_up_norm.setIcon(qta.icon('fa5s.arrow-circle-up', color='white')); self.b_up_norm.clicked.connect(lambda: self.do_up('Normal'))
        vl.addWidget(QLabel("Normal (20k):")); vl.addWidget(self.pb_norm); vl.addWidget(self.b_up_norm)
        self.pb_hard = QProgressBar(); self.pb_hard.setRange(0, 10000); self.pb_hard.setStyleSheet("QProgressBar::chunk{background:#ff4444}")
        self.b_up_hard = QPushButton(" UPGRADE (Hard)"); self.b_up_hard.setIcon(qta.icon('fa5s.arrow-circle-up', color='white')); self.b_up_hard.clicked.connect(lambda: self.do_up('Hard'))
        vl.addWidget(QLabel("Hard (10k):")); vl.addWidget(self.pb_hard); vl.addWidget(self.b_up_hard); vg.setLayout(vl); c1l.addWidget(vg)
        
        cg = QGroupBox("🧮 CALCULADORA"); cl = QVBoxLayout()
        self.calc_dungeon_cb = QComboBox(); self.calc_dungeon_cb.setPlaceholderText("Onde vais farmar?")
        cl.addWidget(QLabel("Dungeon:")); cl.addWidget(self.calc_dungeon_cb)
        self.calc_tabs = QTabWidget()
        tab_vip = QWidget(); l_vip = QVBoxLayout(tab_vip)
        btn_calc_vip = QPushButton(" META VIP"); btn_calc_vip.setIcon(qta.icon('fa5s.calculator')); btn_calc_vip.setStyleSheet("background-color: #d4af37; color: black;")
        btn_calc_vip.clicked.connect(self.calculate_vip_runs)
        self.res_vip = QLabel("..."); self.res_vip.setWordWrap(True); self.res_vip.setStyleSheet("color: #ccc; font-style: italic;")
        l_vip.addWidget(btn_calc_vip); l_vip.addWidget(self.res_vip); l_vip.addStretch(); self.calc_tabs.addTab(tab_vip, "📈 VIP")
        tab_item = QWidget(); l_item = QFormLayout(tab_item); l_item.setSpacing(10)
        self.in_item_cost = QSpinBox(); self.in_item_cost.setRange(0, 100000); self.in_item_cost.setSuffix(" pts")
        self.in_item_qty = QSpinBox(); self.in_item_qty.setRange(1, 1000); self.in_item_qty.setValue(1)
        btn_calc_item = QPushButton(" FARM"); btn_calc_item.setIcon(qta.icon('fa5s.shopping-cart')); btn_calc_item.clicked.connect(self.calculate_item_runs)
        self.res_item = QLabel("..."); self.res_item.setWordWrap(True); self.res_item.setStyleSheet("color: #ccc; font-style: italic;")
        l_item.addRow("Custo:", self.in_item_cost); l_item.addRow("Qtd:", self.in_item_qty); l_item.addRow(btn_calc_item); l_item.addRow(self.res_item); self.calc_tabs.addTab(tab_item, "🛒 Item")
        cl.addWidget(self.calc_tabs); cg.setLayout(cl); c1l.addWidget(cg); c1l.addStretch()

        # Coluna 2 (Dungeons & Shops)
        col2 = QWidget(); c2l = QVBoxLayout(col2)
        col2.setMinimumWidth(450)
        dg = QGroupBox("⚔️ DUNGEONS"); dl = QVBoxLayout()
        self.t_dg = QTableWidget(); self.t_dg.setColumnCount(5); self.t_dg.setHorizontalHeaderLabels(["Nome", "Diff", "Pts", "RUN", "ID"])
        self.t_dg.verticalHeader().setVisible(False); self.t_dg.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch); self.t_dg.setColumnHidden(4, True); self.t_dg.verticalHeader().setDefaultSectionSize(50)
        btn_del_dg = QPushButton(" APAGAR SELECIONADA"); btn_del_dg.setIcon(qta.icon('fa5s.trash-alt', color='white')); btn_del_dg.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold;")
        btn_del_dg.clicked.connect(self.delete_selected_dungeon)
        dl.addWidget(self.t_dg); dl.addWidget(btn_del_dg); dg.setLayout(dl); c2l.addWidget(dg)
        sg = QGroupBox("🛒 LOJAS"); sl = QVBoxLayout()
        self.s_tabs = QTabWidget(); self.ts_easy = self.mk_shop_t(); self.s_tabs.addTab(self.ts_easy, "Easy"); self.ts_norm = self.mk_shop_t(); self.s_tabs.addTab(self.ts_norm, "Normal"); self.ts_hard = self.mk_shop_t(); self.s_tabs.addTab(self.ts_hard, "Hard")
        sl.addWidget(self.s_tabs); sg.setLayout(sl); c2l.addWidget(sg)

        # Coluna 3 (Admin)
        col3 = QWidget(); col3.setFixedWidth(350); c3l = QVBoxLayout(col3)
        adg = QGroupBox("🛠️ CRIAR DUNGEON"); afl = QFormLayout(); afl.setSpacing(15)
        self.i_dn = QLineEdit(); self.i_dd = QComboBox(); self.i_dd.addItems(["Easy", "Normal", "Hard"]); self.i_dp = QSpinBox(); self.i_dp.setRange(0,5000)
        b_ad = QPushButton(" Adicionar"); b_ad.setIcon(qta.icon('fa5s.plus')); b_ad.clicked.connect(self.add_dg)
        afl.addRow("Nome:", self.i_dn); afl.addRow("Dif:", self.i_dd); afl.addRow("Pts:", self.i_dp); afl.addRow(b_ad); adg.setLayout(afl); c3l.addWidget(adg)
        asi = QGroupBox("🛠️ CRIAR ITEM LOJA"); asl = QFormLayout(); asl.setSpacing(15)
        self.i_sn = QComboBox(); self.i_sn.addItems(["Easy", "Normal", "Hard"]); self.i_si = QLineEdit(); self.i_sc = QSpinBox(); self.i_sc.setRange(0, 99999)
        self.i_img_path = QLineEdit(); self.i_img_path.setPlaceholderText("Imagem...")
        b_pick = QPushButton(" Procurar..."); b_pick.setIcon(qta.icon('fa5s.folder-open')); b_pick.clicked.connect(self.pick_image)
        b_ai = QPushButton(" Criar Item"); b_ai.setIcon(qta.icon('fa5s.save')); b_ai.clicked.connect(self.add_item)
        asl.addRow("NPC:", self.i_sn); asl.addRow("Item:", self.i_si); asl.addRow("Custo:", self.i_sc); asl.addRow(b_pick); asl.addRow(self.i_img_path); asl.addRow(b_ai); asi.setLayout(asl); c3l.addWidget(asi)
        hl = QHBoxLayout(); hl.addWidget(QLabel("📜 Histórico:")); b_clr = QPushButton(" Limpar"); b_clr.setIcon(qta.icon('fa5s.eraser')); b_clr.setFixedSize(90, 30); b_clr.setStyleSheet("background:red; border:none"); b_clr.clicked.connect(self.clear_log); hl.addWidget(b_clr)
        c3l.addLayout(hl); self.lst_hist = QListWidget(); c3l.addWidget(self.lst_hist); c3l.addStretch()

        main_layout.addWidget(col1, 1); main_layout.addWidget(col2, 2); main_layout.addWidget(col3, 0)
        
        # Configurar scroll
        scroll.setWidget(content_widget)
        tab_layout.addWidget(scroll)

    def mk_shop_t(self):
        t = QTableWidget(); t.setColumnCount(5); t.setHorizontalHeaderLabels(["Img", "Item", "Custo", "Buy", "X"])
        t.verticalHeader().setVisible(False); t.verticalHeader().setDefaultSectionSize(60)
        t.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        t.setColumnWidth(0, 60); t.setColumnWidth(4, 40)
        return t
    def pick_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Escolher Imagem", "", "Images (*.png *.jpg *.webp)")
        if fname: self.i_img_path.setText(fname)
    def refresh_finance_ui(self):
        w = self.vm.get_wallet()
        self.l_easy.setText(f"EASY: {w['points_easy']}"); self.pb_easy.setValue(min(w['points_easy'], 30000)); self.b_up_easy.setEnabled(w['points_easy']>=30000)
        self.l_norm.setText(f"NORMAL: {w['points_normal']}"); self.pb_norm.setValue(min(w['points_normal'], 20000)); self.b_up_norm.setEnabled(w['points_normal']>=20000)
        self.l_hard.setText(f"HARD: {w['points_hard']}"); self.pb_hard.setValue(min(w['points_hard'], 10000)); self.b_up_hard.setEnabled(w['points_hard']>=10000)
        self.l_vip.setText(f"VIP LEVEL {w['vip_level']} (x{w['vip_level']+1})")
        dgs = self.vm.get_dungeons(); self.t_dg.setRowCount(len(dgs)); curr_idx = self.calc_dungeon_cb.currentIndex(); self.calc_dungeon_cb.clear()
        for r, d in enumerate(dgs):
            self.t_dg.setItem(r, 0, QTableWidgetItem(d['name'])); self.t_dg.setItem(r, 1, QTableWidgetItem(d['difficulty'])); self.t_dg.setItem(r, 2, QTableWidgetItem(str(d['base_points'])))
            b = QPushButton(f"+{d['base_points']}"); b.setIcon(qta.icon('fa5s.play', color='black')); b.setStyleSheet("background:#00d4ff; color:black; font-weight:bold"); b.clicked.connect(lambda _, id=d['id']: self.do_run(id))
            self.t_dg.setCellWidget(r, 3, b); self.t_dg.setItem(r, 4, QTableWidgetItem(str(d['id']))); self.calc_dungeon_cb.addItem(f"{d['name']} ({d['difficulty']})", d)
        if curr_idx >= 0 and curr_idx < self.calc_dungeon_cb.count(): self.calc_dungeon_cb.setCurrentIndex(curr_idx)
        self.load_shop(self.ts_easy, 'Easy'); self.load_shop(self.ts_norm, 'Normal'); self.load_shop(self.ts_hard, 'Hard')
        self.lst_hist.clear(); [self.lst_hist.addItem(QListWidgetItem(f"{h['description']} ({h['points_change']})")) for h in self.vm.get_history()]
    def load_shop(self, t, npc):
        items = self.vm.get_shop_items(npc); t.setRowCount(len(items))
        for r, i in enumerate(items):
            lbl_img = QLabel(); 
            if i['image_path'] and os.path.exists(i['image_path']): pixmap = QPixmap(i['image_path']).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation); lbl_img.setPixmap(pixmap)
            else: lbl_img.setText("No Img")
            lbl_img.setAlignment(Qt.AlignCenter); t.setCellWidget(r, 0, lbl_img); t.setItem(r, 1, QTableWidgetItem(i['item_name'])); t.setItem(r, 2, QTableWidgetItem(str(i['cost'])))
            b = QPushButton("BUY"); b.setIcon(qta.icon('fa5s.shopping-cart', color='black')); b.setStyleSheet("background:#00ff00; color:black"); b.clicked.connect(lambda _, id=i['id']: self.do_buy(id)); t.setCellWidget(r, 3, b)
            b_del = QPushButton(""); b_del.setIcon(qta.icon('fa5s.times', color='white')); b_del.setStyleSheet("background:red; color:white; font-weight:bold"); b_del.clicked.connect(lambda _, id=i['id']: self.do_del_shop(id)); t.setCellWidget(r, 4, b_del)
    def add_dg(self): 
        if self.vm.add_dungeon(self.i_dn.text(), self.i_dd.currentText(), self.i_dp.value()): self.refresh_finance_ui()
    def add_item(self):
        if self.vm.add_shop_item(self.i_sn.currentText(), self.i_si.text(), self.i_sc.value(), self.i_img_path.text()): self.refresh_finance_ui()
    def do_run(self, did): self.vm.process_run(did); self.refresh_finance_ui()
    def do_up(self, m): 
        if self.vm.try_upgrade_vip(m): QMessageBox.information(self,"GG","VIP UPGRADE!"); self.refresh_finance_ui()
        else: QMessageBox.warning(self,"Erro","Sem pontos!")
    def do_buy(self, iid):
        if self.vm.buy_shop_item(iid): self.refresh_finance_ui()
        else: QMessageBox.warning(self,"Erro","Sem dinheiro!")
    def do_del_shop(self, iid):
        if QMessageBox.question(self, "Apagar", "Apagar este item?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes: self.vm.delete_shop_item(iid); self.refresh_finance_ui()
    def clear_log(self): self.vm.clear_history(); self.refresh_finance_ui()
    def delete_selected_dungeon(self):
        row = self.t_dg.currentRow()
        if row < 0: QMessageBox.warning(self, "Aviso", "Seleciona uma Dungeon!"); return
        d_id = int(self.t_dg.item(row, 4).text())
        if QMessageBox.question(self, "Apagar", "Apagar esta Dungeon?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes: self.vm.delete_dungeon(d_id); self.refresh_finance_ui()
    def calculate_vip_runs(self):
        idx = self.calc_dungeon_cb.currentIndex(); 
        if idx < 0: self.res_vip.setText("Cria uma dungeon primeiro!"); return
        dungeon = self.calc_dungeon_cb.currentData(); w = self.vm.get_wallet(); vip_lvl = w['vip_level']
        req_points = 30000 if dungeon['difficulty'] == 'Easy' else 20000 if dungeon['difficulty'] == 'Normal' else 10000
        field = f"points_{dungeon['difficulty'].lower()}"; current_pts = w[field]
        if current_pts >= req_points: self.res_vip.setText("Já tens pontos para subir de nível!"); return
        missing = req_points - current_pts; pts_per_run = dungeon['base_points'] * (vip_lvl + 1)
        if pts_per_run == 0: self.res_vip.setText("Essa dungeon dá 0 pontos!"); return
        runs = math.ceil(missing / pts_per_run); self.res_vip.setText(f"Faltam {missing} pts ({dungeon['difficulty']}).\nCom {pts_per_run} pts/run:\n👉 {runs} RUNS")
    def calculate_item_runs(self):
        idx = self.calc_dungeon_cb.currentIndex()
        if idx < 0: self.res_item.setText("Cria uma dungeon primeiro!"); return
        dungeon = self.calc_dungeon_cb.currentData(); cost = self.in_item_cost.value(); qty = self.in_item_qty.value(); total_cost = cost * qty
        w = self.vm.get_wallet(); pts_per_run = dungeon['base_points'] * (w['vip_level'] + 1)
        if pts_per_run == 0: self.res_item.setText("0 pts/run!"); return
        runs = math.ceil(total_cost / pts_per_run); self.res_item.setText(f"Total: {total_cost} pts.\nCom {pts_per_run} pts/run:\n👉 {runs} RUNS")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- 1. LOGIN ---
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        # --- 2. APP PRINCIPAL (Só abre se o login for aceite) ---
        window = DigimonTrackerApp(login.selected_profile)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()