# src/app.py
import sys
import math
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QTableWidget, QTableWidgetItem, QCheckBox, 
    QHBoxLayout, QLabel, QHeaderView, QTabWidget, QSpinBox, 
    QPushButton, QLineEdit, QComboBox, QFormLayout, QGroupBox, QMessageBox,
    QListWidget, QListWidgetItem, QProgressBar, QFileDialog, QDialog, QScrollArea,
    QMenuBar, QMenu
)
from PySide6.QtGui import QAction, QDesktopServices 
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QFont, QPixmap, QIcon
import qtawesome as qta 
from digimon_viewmodel import DigimonViewModel

# ==========================================
# 🎨 TEMAS (CORES)
# ==========================================

# TEMA 1: BLUE (Default / Teku)
THEME_BLUE = """
QMainWindow, QWidget, QDialog { background-color: #1e1e24; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
QMenuBar { background-color: #2d2d36; color: #fff; border-bottom: 2px solid #00d4ff; }
QMenuBar::item:selected { background-color: #00d4ff; color: #000; }
QMenu { background-color: #2d2d36; border: 1px solid #444; }
QMenu::item:selected { background-color: #3d4450; color: #00d4ff; }
QTableWidget, QListWidget { background-color: #25252b; border: 1px solid #3a3a45; border-radius: 8px; outline: 0; gridline-color: #3a3a45; }
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
QCheckBox::indicator { width: 22px; height: 22px; border: 2px solid #555; background-color: #2d2d36; border-radius: 4px;}
QCheckBox::indicator:checked { background-color: #00d4ff; border-color: #00d4ff; }
QProgressBar { border: none; border-radius: 4px; text-align: center; background: #15151a; color: white; font-weight: bold; height: 25px;}
QProgressBar::chunk { background-color: #00d4ff; }
"""

# TEMA 2: GREEN (Server Official / Racing Drones)
THEME_GREEN = """
QMainWindow, QWidget, QDialog { background-color: #050505; color: #ccffcc; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
QMenuBar { background-color: #111; color: #fff; border-bottom: 2px solid #39ff14; }
QMenuBar::item:selected { background-color: #39ff14; color: #000; }
QMenu { background-color: #111; border: 1px solid #39ff14; }
QMenu::item:selected { background-color: #39ff14; color: #000; }
QTableWidget, QListWidget { background-color: #0a0a0a; border: 1px solid #333; border-radius: 0px; gridline-color: #222; }
QHeaderView::section { background-color: #111; color: #39ff14; padding: 10px; font-weight: bold; border: 1px solid #39ff14; }
QTableWidget::item:selected { background-color: #1a1a1a; color: #39ff14; border: 1px solid #39ff14; }
QTabWidget::pane { border: 1px solid #333; background: #000; }
QTabBar::tab { background: #111; color: #555; padding: 12px 25px; margin-right: 2px; border: 1px solid #333; font-weight: bold; }
QTabBar::tab:selected { background: #000; color: #39ff14; border: 1px solid #39ff14; border-bottom: 0; }
QSpinBox, QLineEdit, QComboBox { background-color: #0a0a0a; color: #39ff14; border: 1px solid #333; padding: 8px; font-weight: bold; border-radius: 0; }
QGroupBox { border: 1px solid #333; border-radius: 0; margin-top: 30px; font-weight: bold; color: #39ff14; background-color: #000; padding-top: 20px; }
QGroupBox::title { subcontrol-origin: margin; top: 0px; left: 15px; padding: 0 5px; background-color: #000; color: #39ff14; }
QPushButton { background-color: #111; border: 1px solid #333; color: #39ff14; padding: 10px 20px; border-radius: 0; font-weight: bold; }
QPushButton:hover { background-color: #39ff14; color: #000; }
QCheckBox::indicator { width: 22px; height: 22px; border: 1px solid #333; background-color: #000; border-radius: 0; }
QCheckBox::indicator:checked { background-color: #39ff14; border-color: #39ff14; }
QProgressBar { border: 1px solid #333; border-radius: 0; text-align: center; background: #000; color: #39ff14; font-weight: bold; height: 25px; }
QProgressBar::chunk { background-color: #39ff14; }
"""

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNO Tracker Login")
        self.setFixedSize(400, 250)
        self.selected_profile = None
        layout = QVBoxLayout(self); layout.setSpacing(20); layout.setContentsMargins(40, 40, 40, 40)
        lbl = QLabel("WHO IS PLAYING?"); lbl.setAlignment(Qt.AlignCenter); lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d4ff;")
        layout.addWidget(lbl)
        self.combo_profiles = QComboBox(); self.combo_profiles.setEditable(True); self.combo_profiles.setPlaceholderText("Enter your name...")
        profiles_dir = os.path.join(os.path.dirname(__file__), '..', 'profiles')
        if os.path.exists(profiles_dir): self.combo_profiles.addItems([f.replace('.db', '') for f in os.listdir(profiles_dir) if f.endswith('.db')])
        layout.addWidget(self.combo_profiles)
        btn_login = QPushButton("LOGIN / CREATE"); btn_login.setStyleSheet("background-color: #00d4ff; color: #000; padding: 15px;")
        btn_login.clicked.connect(self.handle_login); layout.addWidget(btn_login)
    def handle_login(self):
        name = self.combo_profiles.currentText().strip()
        if name: self.selected_profile = name; self.accept()
        else: QMessageBox.warning(self, "Error", "Please enter a name!")

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_title = QLabel("DMO Tracker")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d4ff;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_ver = QLabel("Version 1.1 (Tasks Update)")
        lbl_ver.setStyleSheet("color: #888;")
        lbl_ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_ver)
        
        lbl_desc = QLabel("\nA tool to manage your progress,\neconomy, collection and tasks in DMO.\n\nDeveloped with 💙 by Vicius")
        lbl_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_desc)
        
        lbl_links = QLabel('<a href="https://github.com/Brunom83" style="color: #00d4ff;">GitHub</a> | <a href="https://linkedin.com" style="color: #00d4ff;">LinkedIn</a>')
        lbl_links.setOpenExternalLinks(True)
        lbl_links.setAlignment(Qt.AlignCenter)
        lbl_links.setStyleSheet("font-size: 16px; margin-top: 20px;")
        layout.addWidget(lbl_links)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("margin-top: 20px;")
        layout.addWidget(btn_close)

class DigimonTrackerApp(QMainWindow):
    def __init__(self, profile_name):
        super().__init__()
        self.vm = DigimonViewModel(profile_name)
        self.setWindowTitle(f"DMO Tracker: Digital Nexus Edition | Profile: {profile_name}")
        self.resize(1500, 950)
        
        # --- DEFINIR TEMA INICIAL (BLUE) ---
        self.setStyleSheet(THEME_BLUE)
        self.setWindowIcon(qta.icon('fa5s.egg', color='#00d4ff'))
        
        self.setup_menu()
        
        self.tabs = QTabWidget(); 
        self.tabs.setIconSize(QSize(24, 24)); 
        self.setCentralWidget(self.tabs)
        self.tab_collection = QWidget(); 
        self.setup_collection_tab(); 
        self.tabs.addTab(self.tab_collection, qta.icon('fa5s.dragon', color='#fff'), " COLLECTION")
        self.tab_seals = QWidget(); 
        self.setup_seals_tab(); 
        self.tabs.addTab(self.tab_seals, qta.icon('fa5s.stamp', color='#fff'), " SEALS")
        self.tab_finance = QWidget(); 
        self.setup_finance_tab(); 
        self.tabs.addTab(self.tab_finance, qta.icon('fa5s.coins', color='#fff'), " DASHBOARD")
        self.tab_tasks = QWidget(); 
        self.setup_tasks_tab(); 
        self.tabs.addTab(self.tab_tasks, qta.icon('fa5s.calendar-check', color='#fff'), " TASKS")

        self.load_collection_data(); 
        self.load_seals_data('AT'); 
        self.update_header_stats(); 
        self.refresh_finance_ui(); 
        self.load_tasks()

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        
        # JSON ACTIONS
        action_backup = QAction(qta.icon('fa5s.save', color='#fff'), "Backup Data (JSON)", self); 
        action_backup.triggered.connect(self.do_backup); 
        file_menu.addAction(action_backup)
        action_restore = QAction(qta.icon('fa5s.upload', color='#fff'), "Restore Data (JSON)", self); 
        action_restore.triggered.connect(self.do_restore); 
        file_menu.addAction(action_restore)
        file_menu.addSeparator()
        
        action_logout = QAction(qta.icon('fa5s.sign-out-alt', color='#fff'), "Logout", self); 
        action_logout.triggered.connect(self.close); 
        file_menu.addAction(action_logout)
        action_exit = QAction(qta.icon('fa5s.times', color='#f44'), "Exit", self); 
        action_exit.triggered.connect(QApplication.instance().quit); 
        file_menu.addAction(action_exit)
        
        # THEMES MENU
        view_menu = menu_bar.addMenu("View")
        action_teku = QAction("Theme: Blue (Default)", self); 
        action_teku.triggered.connect(lambda: self.setStyleSheet(THEME_BLUE)); 
        view_menu.addAction(action_teku)
        action_drones = QAction("Theme: Nexus (Server Official)", self); 
        action_drones.triggered.connect(lambda: self.setStyleSheet(THEME_GREEN)); 
        view_menu.addAction(action_drones)

        help_menu = menu_bar.addMenu("Help")
        action_wiki = QAction(qta.icon('fa5s.book', color='#fff'), "Open Wiki (DNO)", self); 
        action_wiki.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://digital-nexus-online.fandom.com/wiki/Digital_Nexus_Online_Wiki"))); 
        help_menu.addAction(action_wiki)
        action_about = QAction(qta.icon('fa5s.info-circle', color='#00d4ff'), "About...", self); 
        action_about.triggered.connect(self.show_about); 
        help_menu.addAction(action_about)

    def show_about(self): dlg = AboutDialog(); dlg.exec()

    # --- JSON LOGIC ---
    def do_backup(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Backup", f"DMO_Backup_{self.vm.profile}.json", "JSON Files (*.json)")
        if fname:
            if self.vm.export_data_to_json(fname): QMessageBox.information(self, "Success", "Backup saved!")
            else: QMessageBox.warning(self, "Error", "Failed to save backup.")
    def do_restore(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open Backup", "", "JSON Files (*.json)")
        if fname:
            if QMessageBox.question(self, "Confirm Restore", "This will OVERWRITE your current data.\nAre you sure?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                if self.vm.import_data_from_json(fname):
                    QMessageBox.information(self, "Success", "Data restored!"); self.load_collection_data(); self.load_seals_data('AT'); self.refresh_finance_ui(); self.load_tasks(); self.update_header_stats()
                else: QMessageBox.warning(self, "Error", "Failed to restore.")

    # --- ABA 1: COLEÇÃO ---
    def setup_collection_tab(self):
        layout = QVBoxLayout(self.tab_collection)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet("background: #25252b; border-left: 5px solid #00d4ff; padding: 20px; font-size: 18px; border-radius: 5px;")
        layout.addWidget(self.stats_label)
        self.col_table = QTableWidget()
        self.col_table.setColumnCount(5)
        self.col_table.setHorizontalHeaderLabels(["Name", "Hatched?", "Full Cloned?", "Source", "ID"])
        self.col_table.verticalHeader().setVisible(False)
        self.col_table.verticalHeader().setDefaultSectionSize(50)
        self.col_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.col_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.col_table.setColumnWidth(1, 120)
        self.col_table.setColumnWidth(2, 120)
        self.col_table.setColumnHidden(4, True)
        layout.addWidget(self.col_table)

    def load_collection_data(self):
        data = self.vm.get_all_digimon()
        self.col_table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.col_table.setItem(row, 0, QTableWidgetItem(item['nome']))
            self.col_table.setItem(row, 3, QTableWidgetItem(item['fonte']))
            self.add_checkbox(self.col_table, row, 1, item['id'], 'hatch_status', item['hatch_status'])
            self.add_checkbox(self.col_table, row, 2, item['id'], 'cloned_status', item['cloned_status'])

    def add_checkbox(self, table, row, col, db_id, field, val):
        c = QWidget()
        c.setStyleSheet("background: transparent;")
        l = QHBoxLayout(c)
        l.setAlignment(Qt.AlignCenter)
        l.setContentsMargins(0,0,0,0)
        cb = QCheckBox()
        cb.setCursor(Qt.PointingHandCursor)
        cb.setChecked(val == 1)
        cb.stateChanged.connect(lambda s, i=db_id, f=field: self.on_col_change(i, f, s))
        l.addWidget(cb)
        c.setLayout(l)
        table.setCellWidget(row, col, c)

    def on_col_change(self, db_id, field, state):
        self.vm.update_digimon_status(db_id, field, 1 if state == 2 else 0)
        self.update_header_stats()

    def update_header_stats(self):
        s = self.vm.get_collection_stats()
        p_h = (s['chocados']/s['total'])*100 if s['total'] else 0
        p_c = (s['clonados']/s['total'])*100 if s['total'] else 0
        self.stats_label.setText(f"📊 TOTAL: <b>{s['total']}</b> &nbsp;|&nbsp; 🐣 HATCHED: <span style='color:#00ff00'>{s['chocados']}</span> ({p_h:.1f}%) &nbsp;|&nbsp; 💪 CLONED: <span style='color:#d4af37'>{s['clonados']}</span> ({p_c:.1f}%)")

    # --- ABA 2: SEALS ---
    def setup_seals_tab(self):
        layout = QHBoxLayout(self.tab_seals)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        fl = QHBoxLayout()
        self.seal_btns = {}
        for stat in ['AT', 'HP', 'DE', 'CT', 'HT', 'BL', 'EV', 'DS']:
            b = QPushButton(stat)
            b.setCheckable(True)
            b.setFixedWidth(60)
            b.clicked.connect(lambda c, s=stat: self.change_seal_filter(s))
            fl.addWidget(b)
            self.seal_btns[stat] = b
        fl.addStretch()
        left_layout.addLayout(fl)
        
        self.seal_table = QTableWidget()
        self.seal_table.setColumnCount(5)
        self.seal_table.setHorizontalHeaderLabels(["Stat", "Digimon", "Qty", "Openers", "ID"])
        self.seal_table.verticalHeader().setVisible(False)
        self.seal_table.verticalHeader().setDefaultSectionSize(60)
        self.seal_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.seal_table.setColumnHidden(4, True)
        left_layout.addWidget(self.seal_table)
        
        right_widget = QWidget()
        right_widget.setFixedWidth(340)
        right_layout = QVBoxLayout(right_widget)
        
        gb_add = QGroupBox("➕ NEW SEAL")
        fl_add = QFormLayout()
        fl_add.setSpacing(15)
        self.inp_seal_stat = QComboBox()
        self.inp_seal_stat.addItems(['AT', 'HP', 'DE', 'CT', 'HT', 'BL', 'EV', 'DS'])
        self.inp_seal_name = QLineEdit()
        self.inp_seal_name.setPlaceholderText("Ex: Agumon")
        btn_save_seal = QPushButton(" Create Seal")
        btn_save_seal.setIcon(qta.icon('fa5s.save'))
        btn_save_seal.clicked.connect(self.add_new_seal)
        btn_save_seal.setStyleSheet("background-color: #00d4ff; color: black;")
        
        fl_add.addRow("Stat:", self.inp_seal_stat)
        fl_add.addRow("Name:", self.inp_seal_name)
        fl_add.addRow(btn_save_seal)
        gb_add.setLayout(fl_add)
        right_layout.addWidget(gb_add)
        right_layout.addStretch()

        layout.addWidget(left_widget, 1)
        layout.addWidget(right_widget, 0)
        self.seal_btns['AT'].setChecked(True)

    def change_seal_filter(self, stat):
        for k, b in self.seal_btns.items(): b.setChecked(k == stat)
        self.load_seals_data(stat)

    def load_seals_data(self, filter_stat):
        data = [s for s in self.vm.get_all_seals() if s['stat_type'] == filter_stat]
        self.seal_table.setRowCount(len(data))
        bold = QFont()
        bold.setBold(True)
        bold.setPointSize(12)
        for r, item in enumerate(data):
            self.seal_table.setItem(r, 0, QTableWidgetItem(item['stat_type']))
            self.seal_table.setItem(r, 1, QTableWidgetItem(item['digimon_nome']))
            
            s = QSpinBox()
            s.setRange(0, 3000)
            s.setValue(item['count'])
            s.setAlignment(Qt.AlignCenter)
            s.valueChanged.connect(lambda v, row=r, id=item['id']: self.on_seal_change(row, id, v))
            
            cw = QWidget()
            cw.setStyleSheet("background: transparent;")
            cl = QHBoxLayout(cw)
            cl.setContentsMargins(0,0,0,0)
            cl.setAlignment(Qt.AlignCenter)
            cl.addWidget(s)
            self.seal_table.setCellWidget(r, 2, cw)
            
            ops = math.ceil(item['count']/50)
            o_item = QTableWidgetItem(str(ops))
            o_item.setTextAlignment(Qt.AlignCenter)
            o_item.setFont(bold)
            if ops > 0: o_item.setForeground(Qt.yellow)
            self.seal_table.setItem(r, 3, o_item)

    def on_seal_change(self, row, db_id, val):
        self.vm.update_seal_count(db_id, val)
        ops = math.ceil(val/50)
        it = QTableWidgetItem(str(ops))
        it.setTextAlignment(Qt.AlignCenter)
        f = QFont()
        f.setBold(True)
        f.setPointSize(12)
        it.setFont(f)
        if ops > 0: it.setForeground(Qt.yellow)
        else: it.setForeground(Qt.white)
        self.seal_table.setItem(row, 3, it)
        
    def add_new_seal(self):
        name = self.inp_seal_name.text()
        stat = self.inp_seal_stat.currentText()
        if name and self.vm.add_manual_seal(name, stat):
            self.inp_seal_name.clear()
            if self.seal_btns[stat].isChecked():
                self.load_seals_data(stat)
        else:
            QMessageBox.warning(self, "Error", "Seal already exists.")

    # --- ABA 3: DASHBOARD ---
    def setup_finance_tab(self):
        tab_layout = QVBoxLayout(self.tab_finance)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        # COL 1
        col1 = QWidget()
        c1l = QVBoxLayout(col1)
        c1l.setSpacing(20)
        col1.setMinimumWidth(350)
        
        wg = QGroupBox("💳 WALLET")
        wl = QVBoxLayout()
        self.l_easy = QLabel("EASY: 0")
        self.l_easy.setStyleSheet("color:#00ff00; font-weight:bold; font-size:18px")
        self.l_norm = QLabel("NORMAL: 0")
        self.l_norm.setStyleSheet("color:#00d4ff; font-weight:bold; font-size:18px")
        self.l_hard = QLabel("HARD: 0")
        self.l_hard.setStyleSheet("color:#ff4444; font-weight:bold; font-size:18px")
        wl.addWidget(self.l_easy)
        wl.addWidget(self.l_norm)
        wl.addWidget(self.l_hard)
        wg.setLayout(wl)
        c1l.addWidget(wg)

        vg = QGroupBox("👑 VIP PROGRESS")
        vl = QVBoxLayout()
        vl.setSpacing(10)
        self.l_vip = QLabel("VIP 0")
        self.l_vip.setStyleSheet("color:#d4af37; font-size:22px; font-weight:bold")
        vl.addWidget(self.l_vip)
        
        self.pb_easy = QProgressBar()
        self.pb_easy.setRange(0, 30000)
        self.pb_easy.setStyleSheet("QProgressBar::chunk{background:#00ff00}")
        self.b_up_easy = QPushButton(" UPGRADE (Easy)")
        self.b_up_easy.setIcon(qta.icon('fa5s.arrow-circle-up', color='white'))
        self.b_up_easy.clicked.connect(lambda: self.do_up('Easy'))
        vl.addWidget(QLabel("Easy (30k):"))
        vl.addWidget(self.pb_easy)
        vl.addWidget(self.b_up_easy)

        self.pb_norm = QProgressBar()
        self.pb_norm.setRange(0, 20000)
        self.pb_norm.setStyleSheet("QProgressBar::chunk{background:#00d4ff}")
        self.b_up_norm = QPushButton(" UPGRADE (Normal)")
        self.b_up_norm.setIcon(qta.icon('fa5s.arrow-circle-up', color='white'))
        self.b_up_norm.clicked.connect(lambda: self.do_up('Normal'))
        vl.addWidget(QLabel("Normal (20k):"))
        vl.addWidget(self.pb_norm)
        vl.addWidget(self.b_up_norm)

        self.pb_hard = QProgressBar()
        self.pb_hard.setRange(0, 10000)
        self.pb_hard.setStyleSheet("QProgressBar::chunk{background:#ff4444}")
        self.b_up_hard = QPushButton(" UPGRADE (Hard)")
        self.b_up_hard.setIcon(qta.icon('fa5s.arrow-circle-up', color='white'))
        self.b_up_hard.clicked.connect(lambda: self.do_up('Hard'))
        vl.addWidget(QLabel("Hard (10k):"))
        vl.addWidget(self.pb_hard)
        vl.addWidget(self.b_up_hard)
        vg.setLayout(vl)
        c1l.addWidget(vg)
        
        cg = QGroupBox("🧮 CALCULATOR")
        cl = QVBoxLayout()
        self.calc_dungeon_cb = QComboBox()
        self.calc_dungeon_cb.setPlaceholderText("Where to farm?")
        cl.addWidget(QLabel("Dungeon:"))
        cl.addWidget(self.calc_dungeon_cb)
        
        self.calc_tabs = QTabWidget()
        
        tab_vip = QWidget()
        l_vip = QVBoxLayout(tab_vip)
        btn_calc_vip = QPushButton(" VIP GOAL")
        btn_calc_vip.setIcon(qta.icon('fa5s.calculator'))
        btn_calc_vip.setStyleSheet("background-color: #d4af37; color: black;")
        btn_calc_vip.clicked.connect(self.calculate_vip_runs)
        self.res_vip = QLabel("Select a dungeon...")
        self.res_vip.setWordWrap(True)
        self.res_vip.setStyleSheet("color: #ccc; font-style: italic;")
        l_vip.addWidget(btn_calc_vip)
        l_vip.addWidget(self.res_vip)
        l_vip.addStretch()
        self.calc_tabs.addTab(tab_vip, "📈 VIP")

        tab_item = QWidget()
        l_item = QFormLayout(tab_item)
        l_item.setSpacing(10)
        self.in_item_cost = QSpinBox()
        self.in_item_cost.setRange(0, 100000)
        self.in_item_cost.setSuffix(" pts")
        self.in_item_qty = QSpinBox()
        self.in_item_qty.setRange(1, 1000)
        self.in_item_qty.setValue(1)
        btn_calc_item = QPushButton(" ITEM GOAL")
        btn_calc_item.setIcon(qta.icon('fa5s.shopping-cart'))
        btn_calc_item.clicked.connect(self.calculate_item_runs)
        self.res_item = QLabel("...")
        self.res_item.setWordWrap(True)
        self.res_item.setStyleSheet("color: #ccc; font-style: italic;")
        l_item.addRow("Cost:", self.in_item_cost)
        l_item.addRow("Qty:", self.in_item_qty)
        l_item.addRow(btn_calc_item)
        l_item.addRow(self.res_item)
        self.calc_tabs.addTab(tab_item, "🛒 Item")
        
        cl.addWidget(self.calc_tabs)
        cg.setLayout(cl)
        c1l.addWidget(cg)
        c1l.addStretch()

        # COL 2
        col2 = QWidget()
        c2l = QVBoxLayout(col2)
        col2.setMinimumWidth(450)
        
        dg = QGroupBox("⚔️ DUNGEONS")
        dl = QVBoxLayout()
        self.t_dg = QTableWidget()
        self.t_dg.setColumnCount(5)
        self.t_dg.setHorizontalHeaderLabels(["Name", "Diff", "Pts", "RUN", "ID"])
        self.t_dg.verticalHeader().setVisible(False)
        self.t_dg.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.t_dg.setColumnHidden(4, True)
        self.t_dg.verticalHeader().setDefaultSectionSize(50)
        
        btn_del_dg = QPushButton(" DELETE SELECTED")
        btn_del_dg.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        btn_del_dg.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold;")
        btn_del_dg.clicked.connect(self.delete_selected_dungeon)
        
        dl.addWidget(self.t_dg)
        dl.addWidget(btn_del_dg)
        dg.setLayout(dl)
        c2l.addWidget(dg)

        sg = QGroupBox("🛒 SHOPS")
        sl = QVBoxLayout()
        self.s_tabs = QTabWidget()
        self.ts_easy = self.mk_shop_t()
        self.s_tabs.addTab(self.ts_easy, "Easy")
        self.ts_norm = self.mk_shop_t()
        self.s_tabs.addTab(self.ts_norm, "Normal")
        self.ts_hard = self.mk_shop_t()
        self.s_tabs.addTab(self.ts_hard, "Hard")
        sl.addWidget(self.s_tabs)
        sg.setLayout(sl)
        c2l.addWidget(sg)

        # COL 3
        col3 = QWidget()
        col3.setFixedWidth(350)
        c3l = QVBoxLayout(col3)
        
        adg = QGroupBox("🛠️ CREATE DUNGEON")
        afl = QFormLayout()
        afl.setSpacing(15)
        self.i_dn = QLineEdit()
        self.i_dd = QComboBox()
        self.i_dd.addItems(["Easy", "Normal", "Hard"])
        self.i_dp = QSpinBox()
        self.i_dp.setRange(0,5000)
        b_ad = QPushButton(" Add")
        b_ad.setIcon(qta.icon('fa5s.plus'))
        b_ad.clicked.connect(self.add_dg)
        afl.addRow("Name:", self.i_dn)
        afl.addRow("Diff:", self.i_dd)
        afl.addRow("Pts:", self.i_dp)
        afl.addRow(b_ad)
        adg.setLayout(afl)
        c3l.addWidget(adg)

        asi = QGroupBox("🛠️ CREATE SHOP ITEM")
        asl = QFormLayout()
        asl.setSpacing(15)
        self.i_sn = QComboBox()
        self.i_sn.addItems(["Easy", "Normal", "Hard"])
        self.i_si = QLineEdit()
        self.i_sc = QSpinBox()
        self.i_sc.setRange(0, 99999)
        self.i_img_path = QLineEdit()
        self.i_img_path.setPlaceholderText("Image Path...")
        b_pick = QPushButton(" Browse...")
        b_pick.setIcon(qta.icon('fa5s.folder-open'))
        b_pick.clicked.connect(self.pick_image)
        b_ai = QPushButton(" Create Item")
        b_ai.setIcon(qta.icon('fa5s.save'))
        b_ai.clicked.connect(self.add_item)
        
        asl.addRow("NPC:", self.i_sn)
        asl.addRow("Item:", self.i_si)
        asl.addRow("Cost:", self.i_sc)
        asl.addRow(b_pick)
        asl.addRow(self.i_img_path)
        asl.addRow(b_ai)
        asi.setLayout(asl)
        c3l.addWidget(asi)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("📜 History:"))
        b_clr = QPushButton(" Clear")
        b_clr.setIcon(qta.icon('fa5s.eraser'))
        b_clr.setFixedSize(90, 30)
        b_clr.setStyleSheet("background:red; border:none")
        b_clr.clicked.connect(self.clear_log)
        hl.addWidget(b_clr)
        c3l.addLayout(hl)
        
        self.lst_hist = QListWidget()
        c3l.addWidget(self.lst_hist)
        c3l.addStretch()

        main_layout.addWidget(col1, 1)
        main_layout.addWidget(col2, 2)
        main_layout.addWidget(col3, 0)
        
        scroll.setWidget(content_widget)
        tab_layout.addWidget(scroll)

    def mk_shop_t(self):
        t = QTableWidget()
        t.setColumnCount(5)
        t.setHorizontalHeaderLabels(["Img", "Item", "Cost", "Buy", "X"])
        t.verticalHeader().setVisible(False)
        t.verticalHeader().setDefaultSectionSize(60)
        t.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        t.setColumnWidth(0, 60)
        t.setColumnWidth(4, 40)
        return t
    
    def pick_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Images (*.png *.jpg *.webp)")
        if fname:
            self.i_img_path.setText(fname)

    def refresh_finance_ui(self):
        w = self.vm.get_wallet()
        self.l_easy.setText(f"EASY: {w['points_easy']}")
        self.pb_easy.setValue(min(w['points_easy'], 30000))
        self.b_up_easy.setEnabled(w['points_easy']>=30000)
        self.l_norm.setText(f"NORMAL: {w['points_normal']}")
        self.pb_norm.setValue(min(w['points_normal'], 20000))
        self.b_up_norm.setEnabled(w['points_normal']>=20000)
        self.l_hard.setText(f"HARD: {w['points_hard']}")
        self.pb_hard.setValue(min(w['points_hard'], 10000))
        self.b_up_hard.setEnabled(w['points_hard']>=10000)
        self.l_vip.setText(f"VIP LEVEL {w['vip_level']} (x{w['vip_level']+1})")

        dgs = self.vm.get_dungeons()
        self.t_dg.setRowCount(len(dgs))
        curr_idx = self.calc_dungeon_cb.currentIndex()
        self.calc_dungeon_cb.clear()
        
        for r, d in enumerate(dgs):
            self.t_dg.setItem(r, 0, QTableWidgetItem(d['name']))
            self.t_dg.setItem(r, 1, QTableWidgetItem(d['difficulty']))
            self.t_dg.setItem(r, 2, QTableWidgetItem(str(d['base_points'])))
            b = QPushButton(f"+{d['base_points']}")
            b.setIcon(qta.icon('fa5s.play', color='black'))
            b.setStyleSheet("background:#00d4ff; color:black; font-weight:bold")
            b.clicked.connect(lambda _, id=d['id']: self.do_run(id))
            self.t_dg.setCellWidget(r, 3, b)
            self.t_dg.setItem(r, 4, QTableWidgetItem(str(d['id'])))
            self.calc_dungeon_cb.addItem(f"{d['name']} ({d['difficulty']})", d)

        if curr_idx >= 0 and curr_idx < self.calc_dungeon_cb.count():
            self.calc_dungeon_cb.setCurrentIndex(curr_idx)

        self.load_shop(self.ts_easy, 'Easy')
        self.load_shop(self.ts_norm, 'Normal')
        self.load_shop(self.ts_hard, 'Hard')
        
        self.lst_hist.clear()
        for h in self.vm.get_history():
            self.lst_hist.addItem(QListWidgetItem(f"{h['description']} ({h['points_change']})"))

    def load_shop(self, t, npc):
        items = self.vm.get_shop_items(npc)
        t.setRowCount(len(items))
        for r, i in enumerate(items):
            lbl_img = QLabel()
            if i['image_path'] and os.path.exists(i['image_path']):
                pixmap = QPixmap(i['image_path']).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_img.setPixmap(pixmap)
            else:
                lbl_img.setText("No Img")
            lbl_img.setAlignment(Qt.AlignCenter)
            t.setCellWidget(r, 0, lbl_img)
            
            t.setItem(r, 1, QTableWidgetItem(i['item_name']))
            t.setItem(r, 2, QTableWidgetItem(str(i['cost'])))
            
            b = QPushButton("BUY")
            b.setIcon(qta.icon('fa5s.shopping-cart', color='black'))
            b.setStyleSheet("background:#00ff00; color:black")
            b.clicked.connect(lambda _, id=i['id']: self.do_buy(id))
            t.setCellWidget(r, 3, b)
            
            b_del = QPushButton("")
            b_del.setIcon(qta.icon('fa5s.times', color='white'))
            b_del.setStyleSheet("background:red; color:white; font-weight:bold")
            b_del.clicked.connect(lambda _, id=i['id']: self.do_del_shop(id))
            t.setCellWidget(r, 4, b_del)

    # --- ACTION HANDLERS ---
    def add_dg(self): 
        if self.vm.add_dungeon(self.i_dn.text(), self.i_dd.currentText(), self.i_dp.value()): self.refresh_finance_ui()
    def add_item(self):
        if self.vm.add_shop_item(self.i_sn.currentText(), self.i_si.text(), self.i_sc.value(), self.i_img_path.text()): self.refresh_finance_ui()
    def do_run(self, did): self.vm.process_run(did); self.refresh_finance_ui()
    def do_up(self, m): 
        if self.vm.try_upgrade_vip(m): QMessageBox.information(self,"GG","VIP UPGRADE!"); self.refresh_finance_ui()
        else: QMessageBox.warning(self,"Error","Not enough points!")
    def do_buy(self, iid):
        if self.vm.buy_shop_item(iid): self.refresh_finance_ui()
        else: QMessageBox.warning(self,"Error","Not enough funds!")
    def do_del_shop(self, iid):
        if QMessageBox.question(self, "Delete", "Delete this item?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes: self.vm.delete_shop_item(iid); self.refresh_finance_ui()
    def clear_log(self): self.vm.clear_history(); self.refresh_finance_ui()
    def delete_selected_dungeon(self):
        row = self.t_dg.currentRow()
        if row < 0: QMessageBox.warning(self, "Warning", "Select a Dungeon first!"); return
        d_id = int(self.t_dg.item(row, 4).text())
        if QMessageBox.question(self, "Delete", "Delete this Dungeon?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes: self.vm.delete_dungeon(d_id); self.refresh_finance_ui()
    
    def calculate_vip_runs(self):
        idx = self.calc_dungeon_cb.currentIndex()
        if idx < 0: self.res_vip.setText("Create a dungeon first!"); return
        dungeon = self.calc_dungeon_cb.currentData()
        w = self.vm.get_wallet()
        vip_lvl = w['vip_level']
        
        req_points = 0
        if dungeon['difficulty'] == 'Easy': req_points = 30000
        elif dungeon['difficulty'] == 'Normal': req_points = 20000
        elif dungeon['difficulty'] == 'Hard': req_points = 10000
        
        field = f"points_{dungeon['difficulty'].lower()}"
        current_pts = w[field]
        
        if current_pts >= req_points:
            self.res_vip.setText("You have enough points to level up!")
            return
            
        missing = req_points - current_pts
        pts_per_run = dungeon['base_points'] * (vip_lvl + 1)
        
        if pts_per_run == 0: self.res_vip.setText("This dungeon gives 0 points!"); return
        
        runs = math.ceil(missing / pts_per_run)
        self.res_vip.setText(f"Missing {missing} pts ({dungeon['difficulty']}).\nAt {pts_per_run} pts/run:\n👉 {runs} RUNS")

    def calculate_item_runs(self):
        idx = self.calc_dungeon_cb.currentIndex()
        if idx < 0: self.res_item.setText("Create a dungeon first!"); return
        dungeon = self.calc_dungeon_cb.currentData()
        
        cost = self.in_item_cost.value()
        qty = self.in_item_qty.value()
        total_cost = cost * qty
        
        w = self.vm.get_wallet()
        pts_per_run = dungeon['base_points'] * (w['vip_level'] + 1)
        
        if pts_per_run == 0: self.res_item.setText("0 pts/run!"); return
        
        runs = math.ceil(total_cost / pts_per_run)
        self.res_item.setText(f"Total: {total_cost} pts.\nAt {pts_per_run} pts/run:\n👉 {runs} RUNS")

    # --- ABA 4: TASKS ---
    def setup_tasks_tab(self):
        layout = QHBoxLayout(self.tab_tasks)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)
        
        # Left
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setSpacing(20)
        
        gd = QGroupBox("📅 DAILY TASKS")
        ld = QVBoxLayout()
        self.list_daily = QListWidget()
        btn_reset_d = QPushButton(" RESET DAILY")
        btn_reset_d.setIcon(qta.icon('fa5s.redo', color='black'))
        btn_reset_d.setStyleSheet("background: orange; color: black; font-weight: bold")
        btn_reset_d.clicked.connect(lambda: self.reset_tasks('Daily'))
        ld.addWidget(self.list_daily)
        ld.addWidget(btn_reset_d)
        gd.setLayout(ld)
        
        gw = QGroupBox("📅 WEEKLY TASKS")
        lw = QVBoxLayout()
        self.list_weekly = QListWidget()
        btn_reset_w = QPushButton(" RESET WEEKLY")
        btn_reset_w.setIcon(qta.icon('fa5s.redo', color='black'))
        btn_reset_w.setStyleSheet("background: orange; color: black; font-weight: bold")
        btn_reset_w.clicked.connect(lambda: self.reset_tasks('Weekly'))
        lw.addWidget(self.list_weekly)
        lw.addWidget(btn_reset_w)
        gw.setLayout(lw)
        
        ll.addWidget(gd)
        ll.addWidget(gw)
        
        # Right
        right = QWidget()
        right.setFixedWidth(350)
        rl = QVBoxLayout(right)
        
        gb = QGroupBox("🛠️ ADD TASK")
        gl = QFormLayout()
        gl.setSpacing(15)
        self.inp_task_name = QLineEdit()
        self.inp_task_name.setPlaceholderText("Task Name...")
        self.inp_task_type = QComboBox()
        self.inp_task_type.addItems(["Daily", "Weekly"])
        b_add = QPushButton(" Add Task")
        b_add.setIcon(qta.icon('fa5s.plus'))
        b_add.clicked.connect(self.add_task)
        
        btn_del_task = QPushButton(" DELETE SELECTED")
        btn_del_task.setIcon(qta.icon('fa5s.trash', color='white'))
        btn_del_task.setStyleSheet("background: red; color: white; margin-top: 20px")
        btn_del_task.clicked.connect(self.delete_selected_task)

        gl.addRow("Name:", self.inp_task_name)
        gl.addRow("Type:", self.inp_task_type)
        gl.addRow(b_add)
        gb.setLayout(gl)
        
        rl.addWidget(gb)
        rl.addWidget(btn_del_task)
        rl.addStretch()
        
        layout.addWidget(left)
        layout.addWidget(right)

    def load_tasks(self):
        self.list_daily.clear()
        self.list_weekly.clear()
        tasks = self.vm.get_tasks()
        
        # Disconnect to avoid loops
        try: self.list_daily.itemChanged.disconnect()
        except: pass
        try: self.list_weekly.itemChanged.disconnect()
        except: pass

        for t in tasks:
            item = QListWidgetItem(t['name'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if t['is_done'] else Qt.Unchecked)
            item.setData(Qt.UserRole, t['id'])
            
            f = item.font()
            f.setStrikeOut(t['is_done'] == 1)
            item.setFont(f)
            
            if t['is_done']: item.setForeground(Qt.gray)
            else: item.setForeground(Qt.white)

            if t['reset_type'] == 'Daily':
                self.list_daily.addItem(item)
            else:
                self.list_weekly.addItem(item)
        
        self.list_daily.itemChanged.connect(self.on_task_change)
        self.list_weekly.itemChanged.connect(self.on_task_change)

    def on_task_change(self, item):
        tid = item.data(Qt.UserRole)
        state = 1 if item.checkState() == Qt.Checked else 0
        self.vm.toggle_task(tid, state)
        f = item.font()
        f.setStrikeOut(state == 1)
        item.setFont(f)
        item.setForeground(Qt.gray if state else Qt.white)

    def add_task(self):
        if self.vm.add_task(self.inp_task_name.text(), self.inp_task_type.currentText()):
            self.inp_task_name.clear()
            self.load_tasks()
            
    def reset_tasks(self, rtype):
        if QMessageBox.question(self, "Reset", f"Reset all {rtype} tasks?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            self.vm.reset_tasks(rtype)
            self.load_tasks()

    def delete_selected_task(self):
        item = self.list_daily.currentItem()
        if not item: item = self.list_weekly.currentItem()
        
        if not item:
            QMessageBox.warning(self, "Warning", "Select a task first!")
            return
        
        tid = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Delete", f"Delete task '{item.text()}'?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            self.vm.delete_task(tid)
            self.load_tasks()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        window = DigimonTrackerApp(login.selected_profile)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()