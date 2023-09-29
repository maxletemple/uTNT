FROM ubuntu:16.04

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y gcc wget build-essential autoconf zip traceroute

RUN wget https://github.com/YvesVanaubel/TNT/archive/refs/heads/master.zip && unzip master.zip
WORKDIR TNT-master/TNT/scamper-tnt-cvs-20180523a/
RUN wget https://people.montefiore.uliege.be/gain/public/sc_tnt.c
RUN cp sc_tnt.c utils/sc_tnt/sc_tnt.c
RUN ./configure CFLAGS="-lpthread" && make && make install
RUN chmod +x /usr/local/bin/scamper && chmod +x utils/sc_tnt/sc_tnt
RUN echo "#!/bin/bash" > run_script.sh
RUN echo "/usr/local/bin/scamper -D -P 12345 && sleep 0.1" >> run_script.sh
RUN echo "cd utils/sc_tnt/ && ./sc_tnt -i 1.1.1.1 -p 12345 -o /tmp/out.warts" >> run_script.sh
#RUN echo "cp /usr/local/bin/scamper /tmp/" >> run_script.sh
#RUN echo "cp sc_tnt /tmp/" >> run_script.sh
RUN chmod +x run_script.sh
CMD ./run_script.sh
