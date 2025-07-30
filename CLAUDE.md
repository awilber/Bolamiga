# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Response Header Requirement

All responses from Claude Code must begin with a header in the following format (with labels in white/light gray):

```
<span style="color: #f0f0f0">Project:</span>
Bolamiga
<span style="color: #f0f0f0">Path:</span>
/Users/arlonwilber/Library/CloudStorage/GoogleDrive-awilber@wiredtriangle.com/Shared drives/AW/Personal/Projects/Bolamiga
<span style="color: #f0f0f0">Date/Time:</span>
[Current date and time]
<span style="color: #f0f0f0">Launch:</span>
python launch.py
---
```

## Project Overview

Bolamiga is a Blood Money-inspired retro space shooter built with Flask and HTML5 Canvas. It features authentic CRT-style visuals with scanlines, side-scrolling arcade action, particle effects, and synthesized audio.

## Common Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start server (recommended method with QA compliance)
python launch.py

# Alternative direct launch
python app.py

# Run QA tests
python qa_test.py

# Simple functional test
python simple_test.py
```

### Testing and Verification
```bash
# Health check endpoint
curl http://localhost:5030/api/health

# Verify game accessibility
curl http://localhost:5030/

# Check high scores API
curl http://localhost:5030/api/highscores
```

### Deployment
```bash
# Deploy to AWS EC2 (requires AWS CLI configuration)
./deploy.sh
```

## Application Architecture

### Backend Structure
- **Flask Application**: Simple web server serving game templates and API endpoints
- **Port Management**: Configurable via PORT environment variable (default: 5030)
- **Host Binding**: Uses '0.0.0.0' for accessibility from external sources
- **API Endpoints**:
  - `/` - Main game interface
  - `/game` - Game canvas page
  - `/api/highscores` - Mock high scores data
  - `/api/health` - Health check endpoint

### Frontend Structure
- **HTML5 Canvas Game Engine**: Real-time 60 FPS rendering with delta timing
- **Retro Styling**: CRT effects, scanlines, phosphor glow using CSS
- **Game State Management**: JavaScript objects for player, bullets, enemies, particles
- **Control System**: Arrow keys/WASD for movement, spacebar for firing

### Game Components
- **Player System**: Ship movement, health, weapon management
- **Enemy System**: Dynamic enemy spawning and AI behavior
- **Physics Engine**: 2D collision detection and particle effects
- **Audio System**: Synthesized retro sound effects
- **Score System**: High score tracking and level progression

## File Structure
- `app.py` - Main Flask application
- `launch.py` - QA-compliant server launcher with dependency management
- `templates/` - Jinja2 templates for web interface
  - `base.html` - Base template with retro CRT styling
  - `game.html` - Main game canvas and JavaScript engine
  - `index.html` - Landing page
- `qa_test.py` - Comprehensive QA testing suite
- `deploy.sh` - AWS EC2 deployment script
- `requirements.txt` - Python dependencies (Flask==3.1.0)

## Development Notes

### Process Management
The `launch.py` script handles proper process cleanup and port management. It kills existing Bolamiga processes before starting new ones to prevent port conflicts.

### QA Integration
The project includes comprehensive QA testing infrastructure:
- Health checks for server responsiveness
- Dependency verification
- Port availability testing
- Browser accessibility verification

### AWS Deployment
The deployment script creates EC2 instances with:
- Ubuntu 22.04 LTS
- Nginx reverse proxy (port 80 → 5030)
- Systemd service for automatic startup
- Security groups for HTTP and SSH access

### Game Engine Design
The JavaScript game engine uses object-oriented design with:
- Modular component system (player, enemies, bullets, particles)
- Delta-time based animation for consistent frame rates
- State management for game progression and UI updates
- Canvas-based rendering with retro visual effects