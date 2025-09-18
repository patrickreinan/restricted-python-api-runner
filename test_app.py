import pytest
from app import app

scenarios = [
    ("Simple math", "result = 2 * 3\noutput = f'Result: {result}'", "Result: 6", 0),
    ("String manipulation", "output = 'Hello ' + 'world!'", "Hello world!", 0),
    ("File access (should fail)", "output = open('test.txt', 'w')", "name 'open' is not defined", 1),
    ("Import os (should fail)", "import os\noutput = os.listdir('.')", "__import__ not found", 1),
    ("Use exec (should fail)", "exec('output = 123')", "Exec calls are not allowed.", 1),
    ("Read env vars (should fail)", "import os\noutput = os.environ", "__import__ not found", 1),
]

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5050'
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("name,code,expected_output,expected_exitcode", scenarios)
def test_run_endpoint(client, name, code, expected_output, expected_exitcode):
    response = client.post('/run', json={"code": code})
    assert response.status_code == 200
    data = response.get_json()
    assert data["exitCode"] == expected_exitcode
    assert expected_output in str(data["output"])
