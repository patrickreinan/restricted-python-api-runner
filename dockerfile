FROM pypy:3

WORKDIR /app

COPY . /app

RUN python3 -m pip install -r requirements.txt

RUN pip install --no-cache-dir -r requirements-sandbox.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

CMD ["flask", "run"]