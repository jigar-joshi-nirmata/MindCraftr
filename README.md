# MindCraftr Backend

A Flask-based REST API for the MindCraftr learning platform.

## Features

- SQLite database for data persistence
- RESTful API endpoints for dashboard, topics, flashcards, and user profile
- CORS enabled for frontend integration
- Easy database seeding with sample data

## Quick Start

### Option 1: Use the Startup Script (Recommended)

```bash
./start_server.sh
```

This script will automatically:
- Create a virtual environment if needed
- Install all dependencies
- Initialize the database if it doesn't exist
- Start the Flask server with detailed logging

### Option 2: Manual Setup

1. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize database**:
```bash
python seed.py
```

4. **Start server**:
```bash
python server.py
```

The server will start on `http://localhost:5001`

> **Note**: We use port 5001 instead of 5000 because macOS uses port 5000 for AirPlay Receiver.

### Testing the API

Test all endpoints with:
```bash
./test_api.sh
```

Or test individual endpoints:
```bash
curl http://localhost:5001/api/v1/dashboard/stats
curl http://localhost:5001/api/v1/flashcards
```

## API Endpoints

### Dashboard

- **GET** `/api/v1/dashboard/stats` - Get test statistics
- **GET** `/api/v1/dashboard/recommendations` - Get recommended topics

### Topics

- **GET** `/api/v1/topics/<topic_id>/details` - Get detailed information about a topic

### Flashcards

- **GET** `/api/v1/flashcards` - Get all flashcards

### Profile

- **GET** `/api/v1/profile/stats` - Get user profile statistics
- **GET** `/api/v1/profile/mastery` - Get topic mastery data

### Presets

- **GET** `/api/v1/presets` - Get available test presets

### Health Check

- **GET** `/` - API health check

## Project Structure

```
MindCraftr/
├── database.py      # Database connection and helper functions
├── seed.py          # Database initialization script
├── server.py        # Flask application with API endpoints
├── requirements.txt # Python dependencies
└── mindcraftr.db   # SQLite database (created after running seed.py)
```

## Database Schema

### Users
- `id`, `name`, `email`

### Test Results
- `id`, `user_id`, `test_name`, `score`, `duration_seconds`, `questions_answered`, `total_questions`, `completed_at`

### Recommended Topics
- `id`, `user_id`, `title`, `summary`, `key_concepts`, `common_pitfalls`, `example_title`, `example_code`, `example_explanation`

### Flashcards
- `id`, `user_id`, `front_content`, `back_content`

### Topic Mastery
- `id`, `user_id`, `topic_name`, `mastery_score`

## Development

To reset the database with fresh data, simply run:

```bash
python seed.py
```

The server runs in debug mode by default for development convenience.

