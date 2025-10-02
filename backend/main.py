# This file now redirects to the new app structure
# For legacy code, see main_legacy.py
# New implementation is in app/main.py

from app.main import app

# Export the app for uvicorn
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)