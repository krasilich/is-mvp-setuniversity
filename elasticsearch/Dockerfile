FROM elasticsearch:8.16.1

COPY --chown=elasticsearch:elasticsearch elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

USER root
COPY restore.sh /usr/local/bin/restore.sh
RUN chmod +x /usr/local/bin/restore.sh
USER elasticsearch
