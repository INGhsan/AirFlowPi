FROM apache/airflow:2.9.1

USER root

# Install OpenJDK 17 and socat — required for Talend jobs and internal port proxying
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  default-jre-headless \
  socat \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Ensure JAVA_HOME is set so the .sh scripts can find java
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow
