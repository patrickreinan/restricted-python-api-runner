

# RestrictedPython REST API Example

This application exposes a REST API for safely executing untrusted Python code using the [RestrictedPython](https://github.com/zopefoundation/RestrictedPython) library. It replaces the use of nsjail with a pure-Python sandboxing approach and provides a `/run` endpoint for code execution.

## Features
- REST API for running untrusted code snippets in a restricted environment
- Prevents access to dangerous built-ins (e.g., `open`, `exec`, `import os`)
- Automated tests using `pytest` to verify both allowed and forbidden operations
- OpenAPI (Swagger) specification for the API

## Usage

### 1. Build and run with Docker Compose
```sh
docker compose up
```

The API will be available at [http://localhost:5050/run](http://localhost:5050/run).



### 2. Example API Requests

#### Example with curl (success)
```sh
curl -X POST http://localhost:5050/run \
	-H "Content-Type: application/json" \
	-d '{"code": "result = 2 * 3\noutput = f\"Result: {result}\""}'
```

#### Example with curl (blocked operation)
```sh
curl -X POST http://localhost:5050/run \
	-H "Content-Type: application/json" \
	-d '{"code": "output = open(\"test.txt\", \"w\")"}'
```


#### Example with curl: Matplotlib plot (SVG output)
This example generates a simple line plot using matplotlib and pandas, and returns the first 100 characters of the SVG output.
```sh
curl -X POST http://localhost:5050/run \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "code": "import matplotlib.pyplot as plt\nimport numpy as np\nimport sys\n# Generate sample data\ndays = [\"Mon\", \"Tue\", \"Wed\", \"Thu\", \"Fri\", \"Sat\", \"Sun\"]\ntemperatures = np.random.randint(15, 35, size=7)  # Random temps between 15 and 35\n# Plot\nplt.figure(figsize=(8, 4))\nplt.plot(days, temperatures, marker='o', color='b')\nplt.title(\"7-Day Weather Forecast\")\nplt.xlabel(\"Day\")\nplt.ylabel(\"Temperature (°C)\")\nplt.grid(True)\n# Output SVG to stdout\nplt.savefig(sys.stdout, format=\"svg\")\nplt.close()"
}
EOF
```


### 3. Run tests
```sh
docker compose run --rm restrictedpython-api pytest
```

## Files
- `app.py`: Flask REST API exposing the `/run` endpoint.
- `test_app.py`: Pytest test suite for the API and all scenarios.
- `openapi.yaml`: OpenAPI 3.0 spec for the REST API.
- `requirements.txt`: Lists dependencies (`RestrictedPython`, `pytest`, `flask`).
- `dockerfile` and `docker-compose.yml`: For containerized execution.

## Scenarios Tested
- Simple math (allowed)
- String manipulation (allowed)
- File access (blocked)
- Importing modules (blocked)
- Use of `exec` (blocked)
- Reading environment variables (blocked)

## Security Note
RestrictedPython provides a strong but not perfect sandbox. For highly sensitive use-cases, consider additional OS-level sandboxing.
