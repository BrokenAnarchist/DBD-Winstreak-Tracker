import sys, os, json, shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog,
    QInputDialog, QComboBox, QCheckBox, QFrame, QFileDialog, QMessageBox, QStyledItemDelegate, QStyleOptionViewItem
)
from PyQt5.QtGui import QPixmap, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, QEvent, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PIL import Image, ImageDraw, ImageFont

import ctypes.wintypes
import urllib.request
import zipfile


GITHUB_REPO = "BrokenAnarchist/DBD-Winstreak-Tracker"
CURRENT_VERSION = "1.0.0"

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
    "The Ghoul"
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
        
class UpdateDownloader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, url, output_file):
        super().__init__()
        self.url = url
        self.output_file = output_file

    def run(self):
        try:
            with urllib.request.urlopen(self.url) as response:
                total_size = int(response.getheader('Content-Length').strip())
                downloaded = 0
                block_size = 8192
                with open(self.output_file, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        f.write(buffer)
                        downloaded += len(buffer)
                        percent = int((downloaded / total_size) * 100)
                        self.progress.emit(percent)
            self.finished.emit()
        except Exception as e:
            print("Update failed:", e)
            
def fetch_latest_release_info():
    """Fetch the latest release metadata from GitHub."""
    try:
        url = "https://api.github.com/repos/BrokenAnarchist/DBD-Winstreak-Tracker/releases/latest"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            latest_version = data.get("tag_name", "")
            changelog = data.get("body", "No changelog provided.")
            zip_url = next((asset["browser_download_url"] for asset in data["assets"] if asset["name"].endswith(".zip")), None)
            return latest_version, changelog, zip_url
    except Exception as e:
        print(f"Failed to fetch release info: {e}")
        return None, None, None


def extract_and_replace(zip_path):
    """Extract downloaded update zip and overwrite necessary files."""
    extract_dir = os.path.join(os.getcwd(), "update_temp")
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        QMessageBox.critical(None, "Extraction Failed", f"Could not extract update:\n{e}")
        return

    # Move images into existing images folder (overwrite)
    extracted_images = os.path.join(extract_dir, "images")
    target_images = os.path.join(os.getcwd(), "images")
    os.makedirs(target_images, exist_ok=True)

    if os.path.exists(extracted_images):
        for file in os.listdir(extracted_images):
            src = os.path.join(extracted_images, file)
            dst = os.path.join(target_images, file)
            shutil.move(src, dst)  # Overwrites if file already exists

    # Replace the EXE (optional — depends on packaging structure)
    new_exe = os.path.join(extract_dir, "DBDWinstreakTracker.exe")
    current_exe = os.path.abspath(__file__).replace(".py", ".exe")
    try:
        if os.path.exists(new_exe):
            os.replace(new_exe, current_exe)
        QMessageBox.information(None, "Update Complete", "The app has been updated.\nPlease restart it.")
    except Exception as e:
        QMessageBox.critical(None, "Update Error", f"Could not replace the executable:\n{e}")


def show_update_dialog(self, new_version, changelog_text, zip_url):
    """Display update prompt with changelog and download controls."""
    dialog = QDialog(self)
    dialog.setWindowTitle(f"Update Available – {new_version}")
    layout = QVBoxLayout(dialog)

    layout.addWidget(QLabel(f"A new version ({new_version}) is available.\n\nRelease Notes:\n"))

    changelog_box = QTextEdit()
    changelog_box.setPlainText(changelog_text)
    changelog_box.setReadOnly(True)
    layout.addWidget(changelog_box)

    progress_bar = QProgressBar()
    progress_bar.setVisible(False)
    layout.addWidget(progress_bar)

    suppress_checkbox = QCheckBox("Don't show this automatically again")
    layout.addWidget(suppress_checkbox)

    def start_download():
        progress_bar.setVisible(True)
        download_path = "update.zip"
        downloader = UpdateDownloader(zip_url, download_path)
        downloader.progress.connect(progress_bar.setValue)
        downloader.finished.connect(lambda: extract_and_replace(download_path))
        downloader.start()

    # Button layout
    button_layout = QHBoxLayout()

    update_btn = QPushButton("Update Now")
    update_btn.clicked.connect(start_download)
    button_layout.addWidget(update_btn)

    skip_btn = QPushButton("Skip")
    def handle_skip():
        if suppress_checkbox.isChecked():
            self.settings["suppress_updates"] = True
            save_settings(self.settings)
        QMessageBox.information(self, "Reminder", "You are using an older version.\nSome features or characters may be unavailable.")
        dialog.reject()

    skip_btn.clicked.connect(handle_skip)
    button_layout.addWidget(skip_btn)

    layout.addLayout(button_layout)
    dialog.exec_()

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
        self.settings = load_settings()
        self.init_ui()
        self.installEventFilter(self)
        QTimer.singleShot(1500, lambda: self.manual_update_check(silent=True))
        
    def auto_check_updates(self):
        if not self.settings.get("suppress_updates", False):
            self.manual_update_check(silent=True)
        
    def manual_update_check(self, silent=False):
        latest_version, changelog, zip_url = fetch_latest_release_info()
        if latest_version and latest_version != CURRENT_VERSION:
            show_update_dialog(self, latest_version, changelog, zip_url)
        elif not silent:
            QMessageBox.information(self, "No Updates", "You are using the latest version.")
            
    def toggle_auto_update(self, state):
        self.settings["suppress_updates"] = (state == Qt.Unchecked)
        save_settings(self.settings)

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
            QComboBox {
                background-color: rgba(30, 30, 40, 0.9);
                border: 1px solid #5a5a7a;
                border-radius: 8px;
                padding: 6px 30px 6px 10px;
                color: #E0FFFF;
                font-weight: 500;
                font-size: 13px;
            }
            QComboBox:hover {
                background-color: rgba(50, 50, 70, 1.0);
                border: 1px solid #7c7c9c;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #5a5a7a;
                background-color: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                width: 14px;
                height: 14px;
                margin-right: 6px;
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
        self.image_label.setFixedSize(200, 200)
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
        self.update_button.clicked.connect(self.manual_update_check)
        
        self.auto_update_checkbox = QCheckBox("Check for updates on startup")
        self.auto_update_checkbox.setChecked(not self.settings.get("suppress_updates", False))
        self.auto_update_checkbox.stateChanged.connect(self.toggle_auto_update)
                
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
        frame_layout.addWidget(self.update_button)
        layout.addWidget(self.auto_update_checkbox)
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
            self.image_label.setPixmap(QPixmap(self.current_img).scaled(200, 200, Qt.KeepAspectRatio))
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
