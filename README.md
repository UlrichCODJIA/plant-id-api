# Plant Identification API

This project provides a Machine Learning Inference API for identifying plant species based on uploaded images. It utilizes the Plantnet API for plant identification and incorporates various features such as request validation, error handling, caching, rate limiting, authentication, logging, and monitoring.

## Prerequisites

- Python 3.7 or higher
- Flask 2.1.0 or higher
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   `git clone https://github.com/your-username/plant-id-api.git`

2. Navigate to the project directory:
   `cd plant-id-api`

3. Create a virtual environment (optional but recommended):

   ```shell
   python -m venv venv
   source venv/bin/activate
   ```

4. Install the required dependencies:
   `pip install -r requirements.txt`

5. Create a `.env` file in the project root and provide the necessary configuration values:

   ```shell
   PLANTNET_API_KEY=your-api-key
   JWT_SECRET=your-jwt-secret
   ```

## Usage

1. Start the API server:
   `python app.py`

2. Send a POST request to the `/identify` endpoint with the following parameters:

   - `image` (required): One or more image files of the plant to be identified (up to 5 images).
   - `organ_<index>` (optional): The organ of the plant in the corresponding image (e.g., `organ_1`, `organ_2`, etc.). Default is "auto" if not specified.

   Include the authentication token in the `Authorization` header of the request.

3. The API will respond with the identification results in JSON format.

## API Documentation

The API documentation is generated using Swagger and can be accessed via the `/apidocs` endpoint when running the Flask application. The documentation provides details about the available endpoints, request/response formats, authentication requirements, and error codes.

## Authentication

The API endpoints are protected by JWT-based authentication. To access the endpoints, include a valid JWT token in the `Authorization` header of the request. The token should be prefixed with `Bearer`.

## Logging and Monitoring

The API includes logging statements to capture important events and errors. The logs are output to the console.

Prometheus metrics are exposed by the API for monitoring purposes. The metrics can be accessed at the `/metrics` endpoint.

## Error Handling

The API handles common errors and returns appropriate error responses with meaningful error messages. The following error scenarios are covered:

- Missing or invalid authentication token
- Missing or invalid image files
- Unsupported file extensions or content types
- Rate limit exceeded
- Internal server errors

## Caching

The API implements caching to store and reuse the results of frequently identified plant species. The identification results are cached for a configurable duration (default: 1 hour) to reduce the number of requests made to the Plantnet API and improve response times.

## Rate Limiting

The API enforces rate limiting to prevent abuse and ensure fair usage. The `/identify` endpoint is limited to a configurable number of requests per minute (default: 10) per client IP address.
