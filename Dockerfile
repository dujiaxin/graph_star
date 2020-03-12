FROM nvidia/cuda:10.1-cudnn7-runtime-ubuntu16.04
ARG PYTHON_VERSION=3.6
RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         git \
         curl \
         ca-certificates && \
     rm -rf /var/lib/apt/lists/*
RUN curl -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh && \
     /opt/conda/bin/conda install -y python=$PYTHON_VERSION \
      pytorch torchvision cudatoolkit=10.1 -c pytorch&& \
     #/opt/conda/bin/conda install -y -c pytorch magma-cuda100 && \
     /opt/conda/bin/conda clean -ya
ENV PATH /opt/conda/bin:$PATH
RUN pip install torch_geometric texttable tensorboardX
RUN pip install torch-scatter==latest+cu101 torch-sparse==latest+cu101 -f https://pytorch-geometric.com/whl/torch-1.4.0.html
#docker tag nlp:casewestern fashui01/nlp:casewestern
#docker push fashui01/nlp:casewestern


#/redis-5.0.0/src/redis-server
#CMD [ "cd", "./redis-5.0.0/src/" ]
#CMD ["redis-server"]
