"""
Pytest configuration and fixtures for FastAPI tests.

Fixtures provide isolated test environments with fresh test data for each test.
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


@pytest.fixture
def clean_activities():
    """Provide fresh test data with activities and participants."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }


@pytest.fixture
def app(clean_activities, monkeypatch):
    """Create a fresh FastAPI app instance with clean test data.
    
    The monkeypatch fixture injects our clean test data into the app module,
    ensuring each test starts with a known state and modifications don't
    affect other tests.
    """
    from src import app as app_module
    
    # Replace the activities dictionary with clean test data
    monkeypatch.setattr(app_module, "activities", clean_activities)
    
    return app_module.app


@pytest.fixture
def client(app):
    """Provide a TestClient connected to the test app.
    
    TestClient makes requests without running a real server, making tests
    fast and isolated. It's perfect for unit testing FastAPI endpoints.
    """
    return TestClient(app)
