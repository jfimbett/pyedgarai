# Legacy entrypoint kept for backwards compatibility
# The API server has moved to src/pyedgarai/api/server.py
# Run `python -m pyedgarai.api.server` or `uvicorn pyedgarai.api.server:app` for deployment

from pyedgarai.api.server import app  # re-export the OpenAPI app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
