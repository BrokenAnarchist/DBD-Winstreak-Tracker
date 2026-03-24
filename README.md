# 🪓 DBD Winstreak Tracker

> A powerful and modern win streak tracker for **Dead by Daylight** players – designed with streamers, competitors, and stat lovers in mind.  
> Includes real-time OBS output, automatic updates.

---

## 🎮 Features

- 🎯 Track **win streaks** for each **Killer** and **Survivor**
- 🏆 Save **Personal Bests** and **Live Session Stats**
- 🖼 Live leaderboard option for selectable streaks
- 🖼 Popout Window with live preview (additional to the file outputs) which can be used as a Window Capture option through OBS
- 🖼️ **OBS overlay integration** (live text & images)
- 🧩 Built-in **update system** via GitHub releases
- 🖼 Different custom streak options; Goal (for things such as the All Perk Streak), Counter (for things such as the CopyCat streak), Request (for things such as build/character requests for Streams) or Multi-Goal (for things such as All Region Streaks)

---

## 🚀 Installation

### 🆕 New Users:
1. Download and run `WinstreakInstaller.exe` from the latest version in the [Releases Page](https://github.com/BrokenAnarchist/DBD-Winstreak-Tracker/releases)
2. Run the executable:  
   `Winstreak Tracker.exe`
   

> ⚠️ Do **not** move the `images/` folder or the app may not load character visuals.

## 💡 How to Use
 
1. Select a **Killer** or **Survivor** from the dropdown
3. Tick `Lock Active` to prevent accidental switching mid-streak
4. Press `+ Add Win` to increase your current streak
5. When you have finished the streak (either died or did not meet your win condition) click "Finish Streak" and your stats will be saved as your Personal Best
6. Select "Reset Streak" to make another attempt (This will **NOT** overwrite your current Personal Best unless you get a higher score
7. Setting the Leaderboard can be found in the "Settings" menu where you can select from all the available streak options to include

Note: If you wish to use the Text File version rather than Window Capture, Enable "Write OBS Text/Images" located on the right hand side of the Main Tools Window.


## 💡 How to Setup OBS Overlay **(Window Capture Method)**

1. Inside Winstreak App, enable "Write OBS Text/Images"
2. Find the folder where the text and image files are being outputted to, there is a label located just below the Toggle for the "Write OBS Text/Images" that says "OBS output: ON/OFF..."
3. In OBS add a new source type "Text (GDI+)" or "Image"
4. Enable "Read from File"
5. Go to the folder that the files are exporting to and select which ones you wish to use (Only the main files, not from the "Images" folder)
6. Select whichever of the files you want to have as an overlay for your OBS (You will need to make multiple different sources for each file you add)

   ### 💡 OBS File Output Formatting**
   Located inside the "Settings" window in the main app **(NOT THE LAUNCHER, AFTER YOU CLICK "Winstreak Tracker")** and then the "Text Formatting Window"

   1. The "Current Streak" and "Personal Best" sections don't really need any adjustments as they are moreso static data
   2. The "Single-Line Output" is the section you would change if you wish to add custom text. **MAKE SURE TO HAVE THE VALUES OF {name}, {number} and {best}** If you don't, the data will not be written to the Output file correctly
   3. Click "Save" and it will appear in the "Formatted.txt" file that was located in the Output folder


## 💡 How to Setup OBS Overlay **(Text Files/Image Method)**


---

## 🚀 Modes
- The "Regular Mode" is used specifically for if you are doing streaks for individual characters, such as a Blight Streak or Survivor Escape Streaks. Whereas the Custom Modes are more overall trackers, such as CopyCat Streaks.
- The "Custom Streaks" have the ability to set goals, for example if you are doing an All Killer Streak, you have the ability to specify the maximum that the counter can go up to.
- The "Custom Streaks" also generate an image that updates in real-time with the application that you can customise which can be used as an overlay on OBS if you do not have a custom made one.

- Under the Streak Selection, there is a "Custom Label" section, you can change the label so that it can say different things, for example you could do your team name escape streak, eg. "Eternal Escape Streak" or even change the killer streak from "The Blight" to "Blight" 

---

## 🧩 Advanced Features

- 📦 Auto-update from GitHub (with changelog popups)
- ⚙️ Silent update checks + "Don't show again" options

---

## 🧠 Smart/Analytical Tools

- Automatically records **longest streaks**
- Real-time **OBS overlays** with customized PNG + text output + Window Capture

---

## 📥 Updating

The app automatically checks for updates.  
You can also manually check by clicking **"Check for Updates"** inside the app.

If a new version is found:
- A changelog popup will appear
- The update will download and extract automatically
- New images (e.g. new killers) will be added into the `images/` folder

---

## 🔮 Roadmap

- Adding characters as they are added into the game

---

## 🙌 Credits

Developed by **BrokenAnarchist**  
Licensed under the [MIT License](LICENSE)

> Not affiliated with Behaviour Interactive.

---

## 🔗 Useful Links

- 📦 [Download Latest Release](https://github.com/BrokenAnarchist/DBD-Winstreak-Tracker/releases/latest)
- 🐞 Report Bugs via [GitHub Issues](https://github.com/BrokenAnarchist/DBD-Winstreak-Tracker/issues)

---
