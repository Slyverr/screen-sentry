# Screen Sentry

Screen Sentry is a background application that watches your screen for visual
threats — fake login pages, phishing pop-ups, exposed sensitive data — and
alerts you in real-time, controllable from the tray or CLI.

**Status:** Experimental · Linux only

## Core Features

### Capture Mode (Manual)

Trigger a screenshot selection tool (Flameshot) directly from the system tray or
CLI. Capture any region — suspicious login pages, strange pop-ups, or sensitive
data exposure — and receive an instant analysis from your configured AI
provider.

- **Trigger:** Click tray icon · `screen-sentry capture`
- **Result:** Always shows detailed notification with analysis

### Watch Mode (Automatic)

Enable continuous monitoring with a single command. Screen Sentry captures your
entire screen every second and sends each frame for analysis.

- **Trigger:** `screen-sentry watch on/off/toggle`
- **Notifications:** Only for threats or uncertain detections (reduces alert
  fatigue)

### CLI Control via IPC

Full control through command line with Typer-powered interface. IPC allows
commands to control the running daemon without restarting.

```bash
screen-sentry capture              # Manual screenshot + analysis
screen-sentry watch on             # Enable watch mode
screen-sentry watch off            # Disable watch mode
screen-sentry watch toggle         # Toggle watch mode
screen-sentry quit                 # Stop the daemon
```

### System Tray Integration

Runs as a background daemon with tray icon for quick access:

- **Double-click:** Trigger manual capture
- **Right-click:** Access actions (capture, quit)
- **Minimal footprint:** No window clutter

### Smart Notifications

- **Manual Capture:** Always shows full analysis result
- **Watch Mode:** Only alerts on threats or uncertain results

## Getting Started

Screen Sentry requires a **Linux** environment with **Flameshot** installed for
screenshot capture.

```bash
# Clone and install
git clone https://github.com/slyverr/screen-sentry.git
cd screen-sentry

uv tool install -e .

# Start the daemon
screen-sentry

# Control the daemon
screen-sentry --help
```

## Configuration

Screen Sentry uses pluggable AI providers for image analysis. See
[CONFIGURATION.md](CONFIGURATION.md) for setup details.
