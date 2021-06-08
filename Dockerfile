FROM python:3.8.6-buster as builder

RUN apt-get update && \
    apt-get install -y \
               libblas-dev \
               liblapack-dev \
               gfortran && \
    python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install wheel && \
    pip install python-spams==2.6.1.11 dmri-amico==1.2.10

from python:3.8.6-slim

COPY --from=builder /opt/venv /opt/venv

RUN apt-get update && \
    apt-get install -y \
               libblas-dev \
               liblapack-dev \
               gfortran && \
    mkdir -p /opt/scripts

COPY amico_init.py run.pl run_noddi.py /opt/scripts/
RUN chmod -R +rx /opt/scripts

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV DIPY_HOME="/home/amicouser/.dipy"

RUN useradd --create-home amicouser
WORKDIR /home/amicouser

RUN /opt/scripts/amico_init.py && \
    chown -R amicouser $DIPY_HOME && \
    chmod -R +rX $DIPY_HOME

USER amicouser

LABEL maintainer="Philip A Cook (https://github.com/cookpa)" \
      description="Container for computing NODDI with AMICO. Please see the original \
AMICO site for more information and citations: https://github.com/daducci/AMICO"

ENTRYPOINT ["/opt/scripts/run.pl"]

