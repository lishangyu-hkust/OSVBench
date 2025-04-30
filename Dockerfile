FROM lsysimpure/osvbench:001

VOLUME /root/hyperkernel/outputs
WORKDIR /root/hyperkernel

ARG SPEC_TO_RUN=NOT_SPECIFIED

RUN mkdir -p /root/hyperkernel/outputs
COPY spec_util.py /root/hyperkernel/spec_util.py
RUN chmod +x /root/hyperkernel/spec_util.py

COPY results/Spec/$SPEC_TO_RUN.json /root/hyperkernel/$SPEC_TO_RUN.json

ENV PYTHONPATH="/root/Projects/z3-z3-4.5.0/build/python"

COPY verify.sh /root/hyperkernel/verify.sh

ENTRYPOINT ["/root/hyperkernel/verify.sh"]
