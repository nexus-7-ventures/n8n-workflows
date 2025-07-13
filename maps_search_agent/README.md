# Maps Search Evaluation Agent

A fully offline, screen-based AI agent for autonomous Maps Search Evaluation tasks on Windows 11.

## 🚀 Quick Start

### 1. Add Your Guidelines File
**CRITICAL:** Place your `guidelines.txt` file in this directory before running the agent.
```
maps_search_agent/
├── guidelines.txt  ← ADD YOUR FILE HERE
├── main.py
├── mouse_controller.py
└── ...
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Additional Requirements:**
- Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your system PATH

### 3. Run the Agent
```bash
python main.py
```

## 🎯 Features

### ✅ Human-like Behavior Simulation
- Advanced mouse movements with Bezier curves and jitter
- Realistic typing with typos, corrections, and natural pauses
- Random screen exploration and UI interactions
- Anti-detection timing patterns

### ✅ Task Pacing Control
- **24±3 tasks per hour** with randomized intervals
- Automatic breaks every 10-12 tasks (5-10 minutes)
- Emergency throttling capabilities
- Rolling window task management

### ✅ Rating & Evaluation System
- Loads logic from your `guidelines.txt` file
- User intent analysis (navigational, local, transactional)
- Demotion factor detection (distance, data accuracy, closure)
- Confidence scoring and QA validation

### ✅ Comprehensive Logging
- All tasks logged to `ratings_log.csv`
- Optional screenshot capture before/after tasks
- Performance metrics and session statistics
- Replay system for debugging

## 📁 File Structure

```
maps_search_agent/
├── main.py                 # Main entry point
├── mouse_controller.py     # Human-like mouse behavior
├── keyboard_sim.py         # Typing simulation
├── ocr_reader.py          # Screen text extraction
├── rating_engine.py       # Evaluation logic
├── comment_generator.py   # Natural comment generation
├── throttler.py           # Task pacing control
├── logger.py              # CSV logging system
├── qa_agent.py            # Quality assurance
├── replay.py              # Debugging tools
├── screenshot_logger.py   # Screenshot capture
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## ⚙️ Configuration

### Task Pacing
Edit `throttler.py` to adjust:
- Target tasks per hour (default: 24±3)
- Break frequency and duration
- Emergency throttling settings

### Screenshot Capture
Screenshots are **optional**. To enable:
```python
# In main.py, set:
screenshot_logging_enabled = True
```

### Mouse & Keyboard Behavior
Customize behavior in:
- `mouse_controller.py` - Movement patterns, speed, jitter
- `keyboard_sim.py` - Typing speed, typo rate, pauses

## 🛡️ Anti-Detection Features

- **No browser automation** - Pure screen interaction only
- **Human timing variations** - Never repeat exact intervals
- **Natural behavior patterns** - Random movements, pauses, exploration
- **Realistic user simulation** - Typos, corrections, hesitation

## 📊 Output Files

- **`ratings_log.csv`** - All task results with timestamps
- **`agent.log`** - Detailed application logs
- **`screenshots/`** - Optional task screenshots
- **`memory.md`** - Generated evaluation memory (auto-created)
- **`comments_examples.txt`** - Comment examples (auto-created)
- **`query_samples.txt`** - Query samples (auto-created)

## 🔧 Troubleshooting

### OCR Issues
- Install Tesseract OCR properly
- Verify Tesseract is in system PATH
- Test with: `tesseract --version`

### Mouse/Keyboard Control
- Run as Administrator on Windows
- Disable Windows mouse acceleration
- Ensure no other automation tools are running

### Performance
- Close unnecessary applications
- Use dedicated monitor for agent
- Ensure stable internet connection

## 🚨 Important Notes

1. **Guidelines Required:** The agent MUST have `guidelines.txt` to function properly
2. **Windows 11 Only:** Designed specifically for Windows 11 environments
3. **Full Control:** Agent takes complete control of mouse and keyboard
4. **Real IP Required:** Uses your actual IP address and screen
5. **Manual Start:** You must manually navigate to the Maps interface before starting

## 📞 Support

Check the logs in `agent.log` for detailed error information and debugging.
