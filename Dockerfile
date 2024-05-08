FROM python:3.10 as base
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update -y && apt-get install gcc -y && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv $VIRTUAL_ENV
RUN pip install -U poetry pip setuptools

WORKDIR /workdir
COPY pyproject.toml /workdir
COPY poetry.lock /workdir 
RUN chown -R $(whoami):$(whoami) /workdir

RUN poetry install  --no-interaction
RUN poetry run apt-get update && apt-get install make git -y

# Customize base image with agent deps
FROM python:3.10-slim-bullseye
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=base $VIRTUAL_ENV $VIRTUAL_ENV
RUN apt-get update -y && apt-get install gcc make -y && rm -rf /var/lib/apt/lists/*
ENV VIRTUAL_ENV=/opt/venv
# now we copy deps to be removed in later stages removed later
WORKDIR /workdir
COPY . .
ENV PYTHONPATH=.
ENTRYPOINT ["/opt/venv/bin/poetry"]
CMD ["run", "pytest", "tests"]


