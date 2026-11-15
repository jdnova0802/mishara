# Executor only. Does not bake Stripe keys. Run against a local Gate mouth.
FROM python:3.12-slim
WORKDIR /drill
COPY sandbox.py report.py executor.py fixture.json ./
USER nobody
ENV GATE_DRILL_MOUTH=http://host.docker.internal:5001/demo/issuing/mouth
CMD ["python3", "executor.py"]
