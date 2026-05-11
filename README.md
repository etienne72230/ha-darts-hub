# Darts Hub for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Unofficial Home Assistant integration to retrieve real-time data from an Autodarts board locally and control it. This integration uses a **Local Push** system for instant responsiveness.

## ⚠️ Mandatory Prerequisites

You **must** have the following tools running on your local network:
1. **Darts-hub** (or Darts-caller): Acts as a Socket.IO server for match management.
👉 **[Download and install Darts-hub (lbormann/darts-hub)](https://github.com/lbormann/darts-hub)**
2. **Autodarts Desktop/Board**: The core target software.
## ⚙️ How Data Retrieval Works (Dual-Source Logic)

This integration is designed to be reactive even when you are not playing an official match. It monitors two distinct local sources simultaneously:

### 1. Darts-hub (Port 8079 - Socket.IO)
- **Role:** Primary source for competitive matches.
- **Data Provided:** Real-time player names, current scores (X01/Cricket), match events, and caller information.

### 2. Autodarts API (Port 3180 - REST/WebSocket)
- **Role:** Fallback source for "Free Practice", and Active controller for the board.
- **Data Provided:** If no match is active in Darts-hub, it fetches raw dart hits (Value, Multiplier, X/Y coords) directly from the board.
- **Control:** Allows sending direct commands to the board (like Reset or Calibration).

## ✨ Features

### 🕹️ Interactive Controls (Buttons)
You can now control your board directly from your Home Assistant dashboard!
- **Reset Board:** Instantly resets the current throw/board state.
- **Calibrate Board:** Triggers the automatic camera calibration algorithm.

### 🔌 Smart Connection Management
- **Auto-Unavailable State:** If Darts-hub is disconnected, entities turn `Unavailable`. It retries every 10 seconds.
- **Smart Dart Reset:** Statistics for Dart 1, 2, and 3 reset to `-` or `0` when darts are pulled (`darts-pulled`).
- **Uppercase formatting:** Fields are automatically formatted to uppercase (e.g., `T20`, `BULL`).

### 📊 Entity List
- **Match Info:** Board Status, Current Event, Match ID, Game Mode.
- **Players:** Current Player, Player Names (1-6).
- **Scores:** Points Left, Round Score, Player Scores (1-6).
- **Dart Analysis:** Detailed stats (Value, Multiplier, Field, Type, X/Y) for **Dart 1**, **Dart 2**, **Dart 3**, and **Last Dart**.
- **Controls (Buttons):** Reset Board, Calibrate Board.

## 📥 Installation

### Method 1: Via HACS (Recommended)

The easiest way is to use the quick-add button below, which will directly open your Home Assistant and prompt you to add the repository:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=etienne72230&repository=ha-darts-hub&category=integration)

**If the button doesn't work, you can do it manually:**

1. Open HACS in your Home Assistant interface.
2. Go to the **Integrations** section.
3. Click on the 3 dots in the top right corner, then select **Custom repositories**.
4. Add the URL `https://github.com/etienne72230/ha-darts-hub` and choose the **Integration** category.
5. Search for **Darts Hub** in the HACS search bar and click **Download**.
6. **Restart** Home Assistant.

### Method 2: Manual Installation

1. Download the latest release from this GitHub repository.
2. Extract the archive and copy the `darts_hub` folder (located inside `custom_components/`) into the `custom_components/` directory of your Home Assistant installation.
3. **Restart** Home Assistant.

---

## ⚙️ Configuration

The integration is fully configured via the Home Assistant user interface, no YAML coding is required!

1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Click the **Add Integration** button in the bottom right corner.
3. Search for **Darts Hub**.
4. A prompt will appear. Enter:
   - **Host:** The IP address of the machine running *Darts-hub* (e.g., `192.168.1.50` or `localhost` if it runs on the same machine).
   - **Port:** The port configured in Darts-hub (default is `8079`).
   - **Darts-hub Port**: The port configured in Darts-hub (default is `8079`).
   - **Autodarts Port**:  The port configured in autodarts (default is `3180').
5. Click Submit. Your entities are ready and will react to the next dart thrown!