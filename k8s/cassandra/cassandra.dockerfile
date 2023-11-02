# docker build -t d1scak3/cassandra:4.0_config -f cassandra.dockerfile .
# docker push d1scak3/cassandra:4.0 # no configuration
# docker push d1scak3/cassandra:4.0_config # with configuration

FROM cassandra:4.0

COPY jmx_prometheus_javaagent-0.18.0.jar /opt/cassandra/lib/jmx_prometheus_javaagent-0.18.0.jar

COPY cassandra-config.yaml /etc/cassandra/cassandra.yaml

COPY jmx_exporter.yaml /opt/cassandra/conf/jmx_exporter.yaml

COPY cassandra-env.sh /opt/cassandra/conf/cassandra-env.sh

# RUN echo 'JVM_OPTS="$JVM_OPTS -javaagent:$CASSANDRA_HOME/lib/jmx_prometheus_javaagent-0.18.0.jar=7070:/opt/cassandra/conf/jmx_exporter.yml"' >> cassandra-env.shfbfa48a80395