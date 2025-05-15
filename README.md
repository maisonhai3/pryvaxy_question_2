# Time Series API

This project provides a FastAPI application that interfaces with InfluxDB for storing time series data.

## Project Structure

- `main.py`: FastAPI application with API endpoints
- `database.py`: InfluxDB client setup and dependency injection
- `models.py`: Pydantic models for data validation
- `Dockerfile`: Docker configuration for the API service
- `docker-compose.yml`: Docker Compose configuration for running both the API and InfluxDB
- `requirements.txt`: Python dependencies

## Features

- FastAPI with Pydantic for data validation
- InfluxDB for time series data storage
- Dependency injection for database access
- Docker Compose for easy deployment
- Persistent storage for InfluxDB data

## Prerequisites

- Docker and Docker Compose installed on your machine

## Getting Started

### Running the Application

1. Clone this repository:
   ```
   git clone <repository-url>
   cd time-series-api
   ```

2. Start the services with Docker Compose:
   ```
   docker-compose up -d
   ```

3. The API will be available at http://localhost:8000
   - API documentation is available at http://localhost:8000/docs
   - InfluxDB UI is available at http://localhost:8086

### Stopping the Application
