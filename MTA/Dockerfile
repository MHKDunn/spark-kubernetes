# builder step used to download and configure spark environment
FROM openjdk:11.0.11-jre-slim-buster as builder

# Add Dependencies
RUN apt-get update && apt-get install -y curl \
	nano wget software-properties-common ssh net-tools \
	ca-certificates python3 python3-pip python3-numpy \
	python3-matplotlib python3-scipy python3-pandas \
	python3-simpy unzip libpq-dev python-dev

RUN update-alternatives --install "/usr/bin/python" "python" "$(which python3)" 1

RUN pip3 install --upgrade pip \
	sqlalchemy \
	requests \
	psycopg2

# Fix the value of PYTHONHASHSEED
# Note: this is needed when you use Python 3.3 or greater
ENV SPARK_VERSION=3.0.2 \
	HADOOP_VERSION=3.2 \
	SPARK_HOME=/opt/spark \
	PYTHONHASHSEED=1

# Download and uncompress spark from the apache archive
RUN wget --no-verbose -O apache-spark.tgz "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
	&& mkdir -p /opt/spark \
	&& tar -xf apache-spark.tgz -C /opt/spark --strip-components=1 \
	&& rm apache-spark.tgz

RUN wget --no-verbose -O requests-2.7.0.tar.gz "https://files.pythonhosted.org/packages/0a/00/8cc925deac3a87046a4148d7846b571cf433515872b5430de4cd9dea83cb/requests-2.7.0.tar.gz" \
	&& tar -zxvf requests-2.7.0.tar.gz -C /opt/spark --strip-components=1 \
	&& rm requests-2.7.0.tar.gz


# Apache spark environment
FROM builder as apache-spark

WORKDIR /opt/spark

ENV SPARK_MASTER_PORT=7077 \
	SPARK_MASTER_WEBUI_PORT=8080 \
	SPARK_LOG_DIR=/opt/spark/logs \
	SPARK_MASTER_LOG=/opt/spark/logs/spark-master.out \
	SPARK_WORKER_LOG=/opt/spark/logs/spark-worker.out \
	SPARK_WORKER_WEBUI_PORT=8080 \
	SPARK_WORKER_PORT=7000 \
	SPARK_MASTER="spark://spark-master:7077" \
	SPARK_WORKLOAD="master"

EXPOSE 8080 7077 6066

RUN mkdir -p $SPARK_LOG_DIR && \
	touch $SPARK_MASTER_LOG && \
	touch $SPARK_WORKER_LOG && \
	ln -sf /dev/stdout $SPARK_MASTER_LOG && \
	ln -sf /dev/stdout $SPARK_WORKER_LOG


#-------------------------------------------------


#Download and uncompress kubectl, and install unzip, ping and nslookup
# RUN apt-get install -y curl && curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
# RUN chmod +x ./kubectl && mv ./kubectl /usr/local/bin && apt-get install -y unzip && apt-get install -y iputils-ping && apt-get install -y dnsutils


COPY ./app /opt/spark-apps
COPY ./data /opt/spark-data
COPY start-spark.sh /


CMD ["/bin/bash", "/start-spark.sh"]
