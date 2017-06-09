FROM registry.opensource.zalan.do/stups/ubuntu:16.04-49

#making this a cachable point as compile takes forever without -j

RUN apt-get update && \
    apt-get -y install iputils-ping \
                       libboost-all-dev \
                       libev4 \
                       libev-dev \
                       libldap2-dev \
                       libpq-dev \
                       libsasl2-dev \
                       libsnappy-dev \
                       libssl-dev \
                       python-dev \
                       python-pip \
                       python-psycopg2 \
                       unixodbc-dev && \
    pip2 install -U pip Cython \
                        setuptools \
                        urllib3



# make requests library use the Debian CA bundle (includes Zalando CA)
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

ADD requirements.txt /app/requirements.txt

# TODO: Remove once cassandra-driver issue is fixed (ref: https://datastax-oss.atlassian.net/browse/PYTHON-656)
RUN pip2 install -U Cython==0.24.1

RUN pip2 install --upgrade -r /app/requirements.txt

ADD ./ /app/

RUN cd /app && python2 setup.py install

COPY zmon_worker_extras/ /app/zmon_worker_extras

ENV ZMON_PLUGINS "$ZMON_PLUGINS:/app/zmon_worker_extras/check_plugins"

CMD ["zmon-worker", "-c", "/app/config.yaml"]

COPY scm-source.json /
