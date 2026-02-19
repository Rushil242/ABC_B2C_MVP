# Stage 1: Build Frontend
FROM node:18-slim as frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend & Runtime
# Use the official Playwright Python image (includes browsers)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN playwright install chromium

# Copy Backend Code
COPY backend/ ./backend/
COPY api/ ./api/
COPY automation/ ./automation/

# Copy Frontend Build from Stage 1
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Command to run the application
# We need to serve the frontend too. We will use the Vercel-like routing but inside FastAPI or just serve static.
# For simplicity with the current setup, we might need a small adjustment to main.py to serve 'frontend/dist' as static
# OR we can use 'uvicorn' and assume the backend handles API, but handling frontend routing (SPA) in FastAPI might need a wildcard route.
# Let's add the SPA catch-all to main.py in the next step. For now, just the command.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
