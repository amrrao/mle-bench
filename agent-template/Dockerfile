FROM mlebench-env

ARG SUBMISSION_DIR
ENV SUBMISSION_DIR=${SUBMISSION_DIR}
ARG LOGS_DIR
ENV LOGS_DIR=${LOGS_DIR}
ARG CODE_DIR
ENV CODE_DIR=${CODE_DIR}
ARG AGENT_DIR
ENV AGENT_DIR=${AGENT_DIR}

RUN mkdir -p ${SUBMISSION_DIR} ${LOGS_DIR} ${CODE_DIR} ${AGENT_DIR}

ARG CONDA_ENV_NAME=agent
COPY requirements.txt /tmp/agent-requirements.txt
RUN conda run -n ${CONDA_ENV_NAME} pip install -r /tmp/agent-requirements.txt && \
    conda clean -afy

COPY . ${AGENT_DIR}/
RUN chmod +x ${AGENT_DIR}/start.sh

WORKDIR ${AGENT_DIR}

CMD ["/bin/bash"]
