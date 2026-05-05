# Darts Hub

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Unofficial [Home Assistant](https://www.home-assistant.io/) integration to retrieve real-time data from an Autodarts board locally (via WebSocket). 

Unlike cloud integrations that constantly poll servers, this integration uses a **Local Push** system, providing instant responsiveness for every dart thrown!

## ⚠️ Mandatory Prerequisites

For this integration to work, **it does not connect directly to Autodarts**. You **must** have the third-party tool **Darts-hub** (or Darts-caller) running on your local network.
This tool acts as a local WebSocket server that listens to the board and redistributes the data in real-time to Home Assistant.

👉 **[Download and install Darts-hub (lbormann/darts-hub)](https://github.com/lbormann/darts-hub)**

## ✨ Features

Once configured, the integration instantly creates over 20 sensors that update in real-time:
- **Match Status:** Board status, Match ID, Current event.
- **Player Information:** Current player, Current caller, Points left.
- **Last Dart Stats:** Value, Multiplier, Hit area (field name), Exact coordinates (X and Y).
- **Scores:** Current round score, and remaining scores tracking for players (up to 6 players).

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

## ⚙️ Configuration

The integration is fully configured via the Home Assistant user interface, no YAML coding is required!

1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Click the **Add Integration** button in the bottom right corner.
3. Search for **Darts Hub**.
4. A prompt will appear. Enter:
   - **Host**: The IP address of the machine running *Darts-hub* (e.g., `192.168.1.50` or `localhost` if it runs on the same machine).
   - **Port**: The port configured in Darts-hub (default is `8079`).
5. Click Submit. Your entities are ready and will react to the next dart thrown!