import pytest
from app import app

scenarios = [
    # Pandas scenarios
    (
        "Pandas DataFrame mean (import as pd)",
        "import pandas as pd\ndf = pd.DataFrame({'a':[1,2,3]})\noutput = float(df['a'].mean())",
        "2.0",
        0
    ),
    (
        "Pandas DataFrame mean (import pandas)",
        "import pandas\ndf = pandas.DataFrame({'a':[1,2,3]})\noutput = float(df['a'].mean())",
        "2.0",
        0
    ),
    (
        "Pandas DataFrame mean (pd only)",
        "df = pd.DataFrame({'a':[1,2,3]})\noutput = float(df['a'].mean())",
        "2.0",
        0
    ),
    # Numpy scenarios
    (
        "Numpy array mean (import as np)",
        "import numpy as np\na = np.array([1,2,3])\noutput = float(np.mean(a))",
        "2.0",
        0
    ),
    (
        "Numpy array mean (import numpy)",
        "import numpy\na = numpy.array([1,2,3])\noutput = float(numpy.mean(a))",
        "2.0",
        0
    ),
    (
        "Numpy array mean (np only)",
        "a = np.array([1,2,3])\noutput = float(np.mean(a))",
        "2.0",
        0
    ),
    (
        "Numpy array sum (import as np)",
        "import numpy as np\na = np.array([1,2,3])\noutput = int(np.sum(a))",
        "6",
        0
    ),
    (
        "Numpy array sum (import numpy)",
        "import numpy\na = numpy.array([1,2,3])\noutput = int(numpy.sum(a))",
        "6",
        0
    ),
    (
        "Numpy array sum (np only)",
        "a = np.array([1,2,3])\noutput = int(np.sum(a))",
        "6",
        0
    ),
    # Matplotlib scenarios
    (
        "Matplotlib plot (pyplot)",
        "from matplotlib import pyplot\npyplot.plot([1,2,3],[4,5,6])\noutput = pyplot.gca().has_data()",
        "True",
        0
    ),
    (
        "Matplotlib plot (import matplotlib)",
        "import matplotlib\nmatplotlib.pyplot.plot([1,2,3],[4,5,6])\noutput = matplotlib.pyplot.gca().has_data()",
        "True",
        0
    ),
    (
        "Matplotlib plot (plt only)",
        "plt.plot([1,2,3],[4,5,6])\noutput = plt.gca().has_data()",
        "True",
        0
    ),
    (
        "Matplotlib figure creation (pyplot)",
        "from matplotlib import pyplot\npyplot.close('all')\nfig = pyplot.figure()\noutput = fig.number",
        "1",
        0
    ),
    # Weather simulation scenario
    (
        "Weather 7-day simulation (pandas+matplotlib SVG)",
        "from matplotlib import pyplot\nimport pandas as pd\nimport numpy as np\npyplot.close('all')\ndays = pd.date_range('2025-09-17', periods=7)\ntemps = np.random.randint(15, 30, size=7)\ndf = pd.DataFrame({'day': days, 'temp': temps})\nfig, ax = pyplot.subplots()\ndf.plot(x='day', y='temp', kind='line', marker='o', ax=ax)\nfrom io import StringIO\nbuf = StringIO()\nfig.savefig(buf, format='svg')\nbuf.seek(0)\noutput = buf.read()[:100]",
        "<?xml",
        0
    ),
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
    if data["exitCode"] != expected_exitcode or expected_output not in str(data["output"]):
        print(f"\n--- DEBUG OUTPUT for {name} ---\n{data['output']}\n-----------------------------\n")
    assert data["exitCode"] == expected_exitcode
    assert expected_output in str(data["output"])
