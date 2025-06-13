FROM python:3.10

# install pre-requisites
RUN apt-get update && apt-get -y install git fish vim watchman opam

# install the client
RUN pip install fb-sapp django-stubs 

COPY pyre-check /app/pyre-check
WORKDIR /app/pyre-check

RUN pip install -r requirements.txt
RUN ./scripts/setup.sh --local --no-tests --release


RUN echo "alias pyre='PYTHONPATH=\"/app/pyre-check/..:\$PYTHONPATH\" python -m pyre-check.client.pyre'" >> ~/.bashrc
RUN echo "export PYRE_BINARY=/app/pyre-check/source/_build/default/main.exe" >> ~/.bashrc

RUN groupadd -r pysa && useradd -r -m -g pysa pysa
# USER pysa


CMD ["sleep", "36000"]
