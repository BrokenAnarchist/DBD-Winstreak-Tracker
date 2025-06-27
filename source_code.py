import sys, os, json, shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QInputDialog, QComboBox, QCheckBox, QFrame, QFileDialog, QMessageBox, QStyledItemDelegate, QStyleOptionViewItem
)
from PyQt5.QtGui import QPixmap, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QKeyEvent
from PIL import Image, ImageDraw, ImageFont

import ctypes.wintypes
import urllib.request
import webbrowser


APP_VERSION = "1.0.1"
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/BrokenAnarchist/DBD-Winstreak-Tracker/main/version.txt"
DOWNLOAD_URL = "https://github.com/BrokenAnarchist/DBD-Winstreak-Tracker/releases"


# OBS save folder (remains unchanged)
def get_documents_folder():
    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return Path(buf.value)

SAVE_DIR = get_documents_folder() / "Winstreaks"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Config/profile save folder (now in LocalAppData)
CONFIG_DIR = Path(os.getenv("LOCALAPPDATA")) / "DBD Winstreaks"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_FILE = CONFIG_DIR / "profiles.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DATA_FILE = "characters.json"
IMAGE_DIR = SAVE_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

KILLERS_IN_ORDER = [
    "The Trapper", "The Wraith", "The Hillbilly", "The Nurse", "The Shape",
    "The Hag", "The Doctor", "The Huntress", "The Cannibal", "The Nightmare",
    "The Pig", "The Clown", "The Spirit", "The Legion", "The Plague",
    "The Ghost Face", "The Demogorgon", "The Oni", "The Deathslinger",
    "The Executioner", "The Blight", "The Twins", "The Trickster", "The Nemesis",
    "The Cenobite", "The Artist", "The Onryō", "The Dredge", "The Mastermind",
    "The Knight", "The Skull Merchant", "The Singularity", "The Xenomorph",
    "The Good Guy", "The Unknown", "The Lich", "The Dark Lord", "The Houndmaster",
    "The Ghoul", "The Animatronic"
]

def generate_placeholders(relative_path):
    # Generate placeholder images for killers and survivor modes
    for killer in KILLERS_IN_ORDER:
        filename = f"{killer}.png"
        path = IMAGE_DIR / filename
        if not path.exists():
            img = Image.new("RGB", (300, 300), color=(30, 30, 30))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            d.text((10, 140), killer, fill=(200, 200, 200), font=font)
            img.save(path)

    # Also generate placeholder images for each survivor mode
    SURVIVOR_MODES = ["Solo", "2 Survivors", "3 Survivors", "4 Survivors"]
    
    roles = {
        "Killer Icon.png": "Killer",
        "Survivor Icon.png": "Survivor"
    }
    for filename, label in roles.items():
        role_path = IMAGE_DIR / filename
        if not role_path.exists():
            img = Image.new("RGB", (300, 300), color=(25, 25, 25))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except:
                font = ImageFont.load_default()
            bbox = d.textbbox((0, 0), label, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            d.text(((300 - w) / 2, (300 - h) / 2), label, fill=(255, 255, 255), font=font)
            img.save(role_path)

    for mode in SURVIVOR_MODES:
        filename = f"Survivor {mode}.png"
        path = IMAGE_DIR / filename
        if not path.exists():
            img = Image.new("RGB", (300, 300), color=(30, 30, 30))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            d.multiline_text((10, 120), f"Survivor\n{mode}", fill=(200, 200, 200), font=font, align="center")
            img.save(path)
            
def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
            
def check_for_updates():
    try:
        with urllib.request.urlopen(UPDATE_CHECK_URL) as response:
            latest_version = response.read().decode().strip()
        if latest_version > APP_VERSION:
            return latest_version
        else:
            return None
    except Exception as e:
        print("Could not check for updates:", e)
        return None

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)

def write_current_files(name, streak, best, img_path):
    (SAVE_DIR / "Current Streak.txt").write_text(str(streak))
    (SAVE_DIR / "Current Best.txt").write_text(str(best) if best > 0 else "LIVE")
    (SAVE_DIR / "Current Stats.json").write_text(json.dumps({
        "current_streak": streak,
        "personal_best": best if best > 0 else "LIVE"
    }, indent=2))

    # Use plain name for character output
    formatted_name = "Survivor" if name.lower().startswith("survivor") else name
    (SAVE_DIR / "Current Character.txt").write_text(formatted_name)

    if img_path and os.path.exists(img_path):
        shutil.copyfile(img_path, SAVE_DIR / "Current Character.png")


class CenteredComboDelegate(QStyledItemDelegate):
    def initStyleOption(self, option: QStyleOptionViewItem, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignHCenter

class WinStreakApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winstreak Tracker")
        self.setWindowIcon(QIcon("Winstreak App Logo Transparent.ico"))
        self.setFixedSize(550, 820)
        self.profiles = load_profiles()
        self.current_profile = None
        self.lock_active = False
        self.obs_enabled = True
        self.current_img = None
        self.setup_palette()
        self.init_ui()
        self.installEventFilter(self)
        self.settings = load_settings()
        QTimer.singleShot(1500, self.auto_check_updates)
        
    def auto_check_updates(self):
        if not self.settings.get("suppress_updates", False):
            self.manual_update_check(silent=True)
        
    def manual_update_check(self, silent=False):
        latest = check_for_updates()
        if latest:
            msg = QMessageBox(self)
            msg.setWindowTitle("Update Available")
            msg.setText(f"A new version ({latest}) is available.\nWould you like to download it?")
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            # Add custom checkbox
            dont_show_checkbox = QCheckBox("Don't show this automatically again")
            msg.setCheckBox(dont_show_checkbox)

            if msg.exec_() == QMessageBox.Yes:
                import webbrowser
                webbrowser.open(DOWNLOAD_URL)
            else:
                if dont_show_checkbox.isChecked():
                    self.settings["suppress_updates"] = True
                    save_settings(self.settings)
                QMessageBox.information(self, "Reminder", "You are using an old version.\nSome newer features or characters may not be available.")
        elif not silent:
            QMessageBox.information(self, "No Updates", "You are using the latest version.")

    def setup_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(20, 20, 20))
        palette.setColor(QPalette.WindowText, QColor(200, 255, 255))
        self.setPalette(palette)
        self.setStyleSheet("""
            QWidget {
                background-color: #141414;
                color: #E0FFFF;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QPushButton {
                background-color: #1f1f2e;
                border: 1px solid #3b3b4f;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #29293d;
            }
            QComboBox, QCheckBox, QLabel {
                margin: 4px;
                border: none;
                outline: none;
            }
            QComboBox QAbstractItemView {
                text-align: center;
            }
            QFrame {
                border: 1px solid #444;
                border-radius: 12px;
                padding: 8px;
                margin: 6px;
                background-color: #1a1a1a;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()

        self.profile_dropdown = QComboBox()
        self.profile_dropdown.addItems(["Select Profile"] + list(self.profiles.keys()))
        self.profile_dropdown.setItemDelegate(CenteredComboDelegate(self.profile_dropdown))
        self.profile_dropdown.currentTextChanged.connect(self.select_profile)

        self.new_profile_button = QPushButton("+ New Profile")
        self.new_profile_button.clicked.connect(self.create_profile)
        
        self.delete_profile_button = QPushButton("🗑 Delete Profile")
        self.delete_profile_button.clicked.connect(self.delete_profile)

        self.dropdown = QComboBox()
        self.dropdown.addItems(["Survivor"] + KILLERS_IN_ORDER)
        self.dropdown.setItemDelegate(CenteredComboDelegate(self.dropdown))
        self.dropdown.currentTextChanged.connect(self.load_killer)

        self.survivor_mode = QComboBox()
        self.survivor_mode.addItems(["Solo", "2 Survivors", "3 Survivors", "4 Survivors"])
        self.survivor_mode.setItemDelegate(CenteredComboDelegate(self.survivor_mode))
        self.survivor_mode.currentTextChanged.connect(lambda: self.load_killer("Survivor"))

        name_layout = QHBoxLayout()
        self.name_label = QLabel("Character: -")
        self.lock_checkbox = QCheckBox("Lock Active")
        self.lock_checkbox.stateChanged.connect(self.toggle_lock)
        name_layout.addWidget(self.name_label)
        name_layout.addStretch()
        name_layout.addWidget(self.lock_checkbox)

        self.image_label = QLabel()
        self.image_label.setFixedSize(250, 250)
        self.image_label.setAlignment(Qt.AlignCenter)
        image_wrapper = QHBoxLayout()
        image_wrapper.addStretch()
        image_wrapper.addWidget(self.image_label)
        image_wrapper.addStretch()

        self.streak_label = QLabel("🔥 Current Streak: 0")
        self.best_label = QLabel("🥇 Personal Best: LIVE")

        self.win_button = QPushButton("+ Add Win")
        self.win_button.clicked.connect(self.add_win)

        self.finish_button = QPushButton("✔ Finish Streak")
        self.finish_button.clicked.connect(self.finish_streak)

        self.reset_button = QPushButton("✘ Reset Streak")
        self.reset_button.clicked.connect(self.reset_streak)

        self.obs_toggle = QCheckBox("Enable OBS Output")
        self.obs_toggle.setChecked(True)
        self.obs_toggle.stateChanged.connect(self.toggle_obs)

        self.obs_status = QLabel(f"OBS output: ON → {SAVE_DIR}")
        self.obs_status.setAlignment(Qt.AlignCenter)
        
        self.import_button = QPushButton("📥 Import Profiles")
        self.export_button = QPushButton("📥 Export Profiles")
        self.import_button.clicked.connect(self.import_profiles)
        self.export_button.clicked.connect(self.export_profiles)
        
        self.update_button = QPushButton("🔄 Check for Updates")
        self.update_button.clicked.connect(lambda: self.manual_update_check(silent=False))
        
        import_export_layout = QHBoxLayout()
        import_export_layout.addWidget(self.import_button)
        import_export_layout.addWidget(self.export_button)
        import_export_layout.addWidget(self.update_button)
        layout.addLayout(import_export_layout)

        frame = QFrame()
        frame_layout = QVBoxLayout()
        profile_row = QHBoxLayout()
        profile_row.addWidget(self.profile_dropdown)

        profile_buttons = QHBoxLayout()
        profile_buttons.addWidget(self.new_profile_button)
        profile_buttons.addWidget(self.delete_profile_button)
        profile_buttons.setSpacing(6)

        profile_row.addLayout(profile_buttons)
        frame_layout.addLayout(profile_row)
        frame_layout.addWidget(self.dropdown)
        frame_layout.addWidget(self.survivor_mode)
        frame_layout.addLayout(name_layout)
        frame_layout.addLayout(image_wrapper)
        frame_layout.addWidget(self.streak_label)
        frame_layout.addSpacing(-10)
        frame_layout.addWidget(self.best_label)
        frame_layout.addWidget(self.win_button)
        frame_layout.addWidget(self.finish_button)
        frame_layout.addWidget(self.reset_button)
        frame_layout.addWidget(self.obs_toggle)
        frame_layout.addWidget(self.obs_status)
        frame.setLayout(frame_layout)

        layout.addWidget(frame)
        self.setLayout(layout)
        
        self.toggle_lock(Qt.Unchecked)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key_F17:
                self.add_win()
                return True
        return super().eventFilter(obj, event)

    def select_profile(self, name):
        if name == "Select Profile":
            self.current_profile = None
            return
        if name not in self.profiles:
            self.profiles[name] = {}
        self.current_profile = name

        self.dropdown.setCurrentText("Survivor")
        self.survivor_mode.setCurrentText("Solo")

        QTimer.singleShot(0, lambda: self.load_killer("Survivor"))

    def create_profile(self):
        name, ok = QInputDialog.getText(self, "Create New Profile", "You are creating a new profile.\nPlease name it:")
        if ok and name.strip():
            profile_name = name.strip()
            if profile_name not in self.profiles:
                self.profiles[profile_name] = {}
                save_profiles(self.profiles)
                self.profile_dropdown.addItem(profile_name)
                self.profile_dropdown.setCurrentText(profile_name)
            else:
                QMessageBox.warning(self, "Profile Exists", "A profile with that name already exists.")
                
    def delete_profile(self):
        current = self.profile_dropdown.currentText()
        if current == "Select Profile":
            QMessageBox.warning(self, "No Profile Selected", "Please select a profile to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Delete Profile",
            f"Are you sure you want to delete the profile '{current}'?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.profiles.pop(current, None)
            save_profiles(self.profiles)
            index = self.profile_dropdown.findText(current)
            self.profile_dropdown.removeItem(index)
            self.profile_dropdown.setCurrentIndex(0)
            self.current_profile = None
            self.name_label.setText("Character: -")
            self.streak_label.setText("🔥 Current Streak: 0")
            self.best_label.setText("🥇 Personal Best: LIVE")
            self.image_label.clear()
            
    def import_profiles(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import JSON", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "r") as f:
                imported = json.load(f)
                self.profiles.update(imported)
                save_profiles(self.profiles)
                self.profile_dropdown.clear()
                self.profile_dropdown.addItems(["Select Profile"] + list(self.profile.keys()))
                
    def export_profiles(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export JSON", "", "JSON FILES (*.json)")
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.profiles, f, indent=4)

    def toggle_lock(self, state):
        self.lock_active = state == Qt.Checked
        self.dropdown.setDisabled(self.lock_active)
        self.survivor_mode.setDisabled(self.lock_active)

        if self.lock_active:
            self.win_button.setStyleSheet("""
                QPushButton {
                    background-color: #228B22;
                    color: white;
                    border: 1px solid #1e7c1e;
                    border-radius: 8px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #2e8b57;
                }
            """)
            if self.current_profile:
                self.update_obs_files()
        else:
            self.win_button.setStyleSheet("""
                QPushButton {
                    background-color: #8b0000;
                    color: white;
                    border: 1px solid #aa0000;
                    border-radius: 8px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #b22222;
                }
            """)

    def toggle_obs(self, state):
        self.obs_enabled = bool(state)
        self.obs_status.setText(f"OBS output: ON → {SAVE_DIR}" if self.obs_enabled else "OBS output: OFF")

    def full_name(self):
        if self.dropdown.currentText() == "Survivor":
            return f"Survivor - {self.survivor_mode.currentText()}"
        return self.dropdown.currentText()

    def load_killer(self, name):
        if not self.current_profile:
            return
        key = self.full_name()
        profile_data = self.profiles.get(self.current_profile, {})
        char = profile_data.get(key, {"wins": 0, "current_streak": 0, "personal_best": 0, "image_path": None, "live": True})
        profile_data[key] = char
        self.profiles[self.current_profile] = profile_data
        
        self.survivor_mode.setVisible(name == "Survivor")
        key = self.full_name()
        
        self.name_label.setText(f"Character: {key}")
        self.streak_label.setText(f"🔥 Current Streak: {char['current_streak']}")
        self.best_label.setText(f"🥇 Personal Best: {'LIVE' if char.get('live', True) else char.get('personal_best', 0)}")

        if self.dropdown.currentText() == "Survivor":
            image_name = f"Survivor {self.survivor_mode.currentText()}.png"
        else:
            image_name = f"{key}.png"

        default_img = IMAGE_DIR / image_name
        self.current_img = char.get("image_path") or (str(default_img) if default_img.exists() else None)
        if self.current_img:
            self.image_label.setPixmap(QPixmap(self.current_img).scaled(250, 250, Qt.KeepAspectRatio))
        else:
            self.image_label.clear()
        if self.obs_enabled and self.lock_active:
            self.update_obs_files()

        # ---- UPDATE CURRENT ROLE IMAGE ----
        current_role_path = SAVE_DIR / "Current Role.png"
        if self.dropdown.currentText() == "Survivor":
            survivor_icon = IMAGE_DIR / "Survivor Icon.png"
            if survivor_icon.exists():
                shutil.copyfile(survivor_icon, current_role_path)
        else:
            killer_icon = IMAGE_DIR / "Killer Icon.png"
            if killer_icon.exists():
                shutil.copyfile(killer_icon, current_role_path)
        
        # ---- UPDATE STREAK ICON IMAGE ----
        streak_icon_path = SAVE_DIR / "Streak Icon.png"
        if self.dropdown.currentText() == "Survivor":
            escape_icon = IMAGE_DIR / "Escape Icon.png"
            if escape_icon.exists():
                shutil.copyfile(escape_icon, streak_icon_path)
        else:
            transparent = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
            transparent.save(streak_icon_path)  
        save_profiles(self.profiles)

    def update_obs_files(self):
        char = self.profiles[self.current_profile][self.full_name()]
        best = char['personal_best'] if not char.get('live', True) else 0
        write_current_files(self.full_name(), char['current_streak'], best, self.current_img)

    def add_win(self):
        if not self.lock_active or not self.current_profile:
            return
        char = self.profiles[self.current_profile][self.full_name()]
        char['wins'] += 1
        char['current_streak'] += 1
        save_profiles(self.profiles)
        current = self.dropdown.currentText()
        self.load_killer(current)

    def finish_streak(self):
        char = self.profiles[self.current_profile][self.full_name()]
        if char['current_streak'] > 0:
            char['personal_best'] = max(char['personal_best'], char['current_streak'])
            char['live'] = False
        save_profiles(self.profiles)
        current = self.dropdown.currentText()
        self.load_killer(current)

    def reset_streak(self):
        char = self.profiles[self.current_profile][self.full_name()]
        char['wins'] = 0
        char['current_streak'] = 0
        save_profiles(self.profiles)
        current = self.dropdown.currentText()
        self.load_killer(current)

if __name__ == "__main__":
    generate_placeholders("")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Winstreak App Logo Transparent.ico"))
    win = WinStreakApp()
    win.show()
    sys.exit(app.exec_())
