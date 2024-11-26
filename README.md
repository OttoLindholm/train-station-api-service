# Train Station API Service

This repository contains the implementation of a Train Management System designed to facilitate the management of
trains, journeys, crew, and stations. The system allows travelers to easily book tickets for upcoming trips, ensuring a
smooth and efficient travel experience.

## Features

- **JWT Authentication**: Secure access to the API endpoints.
- **Admin Panel**: Manage data directly from `/admin/`.
- **API Documentation**: Swagger documentation is available at `/api/doc/swagger/`.
- **Ticket Booking**: Allows travelers to book tickets for journeys.
- **Train Management**: Create and manage train details, including capacities and types.
- **Station Management**: Add and manage stations.
- **Journey Scheduling**: Schedule journeys with route and timing details.
- **Crew Assignment**: Assign crew members to trains and journeys.
- **Search and Filter**: Efficiently search and filter trains, journeys, and stations.

---

## Installation Using GitHub

To set up and run the Train Station API Service locally, follow the steps below:

### Prerequisites

- **Python 3.9+**
- **PostgreSQL** installed and running

### Steps to Install

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd train-station-api-service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables using the `.env.sample` file provided in the repository:
   ```bash
   cp .env.template .env
   ```

   Fill out the `.env` file with your database credentials and other required values.

5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
6. Load demo data:
   ```bash 
   python manage.py loaddata demo_data.json
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Run with Docker

To run the API using Docker, ensure that Docker and Docker Compose are installed on your system. Then:

1. Build and start the containers:
   ```bash
   docker-compose build
   docker-compose up
   ```

2. Access the application at `http://localhost:8000`.

> The Docker image for this API is also available on Docker Hub. You can pull it directly using:
> ```bash
> docker pull ottolindholm/train-station-api-service:v1
> ```

---

## Getting Access

1. **Register a new user**:
   ```
   POST /api/user/register/
   ```

2. **Get access token**:
   ```
   POST /api/user/token/
   ```

Use the access token in the Authorization header to access protected endpoints.

---

## Contribution

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a clear description of your changes.
