FROM ubuntu:22.04

WORKDIR /app/

# Locale
RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

# For Python3
RUN apt-get update && \
    apt-get install -y software-properties-common
RUN add-apt-repository universe
RUN apt-get update && \
    apt-get install -y wget && \
    apt-get install -y python3
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py

# Lux Tools
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install jupyter
RUN jupyter nbextension install --py luxwidget
RUN jupyter nbextension enable --py luxwidget

# Lux
COPY ./lux/ /app/lux/
COPY ./setup.py /app/setup.py
COPY ./setup.cfg /app/setup.cfg
COPY ./README.md /app/README.md
RUN pip install -e /app/

EXPOSE 8888
WORKDIR /
CMD [ "jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root" ]
