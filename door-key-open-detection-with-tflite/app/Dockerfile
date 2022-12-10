FROM public.ecr.aws/lambda/python:3.8

COPY app.py tflite_example.py requirements.txt ./
COPY saved_model.tflite signature.json /opt/ml/model/

RUN python3.8 -m pip install -r requirements.txt -t .

RUN yum -y update \
    && yum -y install gcc make gcc-c++ zlib-devel bison bison-devel gzip glibc-static mesa-libGL-devel \
    && yum -y install tar

RUN curl -O https://ftp.gnu.org/gnu/glibc/glibc-2.27.tar.gz \
    && tar zxvf glibc-2.27.tar.gz \
    && mv glibc-2.27/ /opt/glibc-2.27/ \
    && rm glibc-2.27.tar.gz

WORKDIR /opt/glibc-2.27/build
RUN /opt/glibc-2.27/configure --prefix=/var/task
RUN make
RUN make install
RUN cp -pa /var/task/lib/libm.so.6 /lib64/

CMD ["app.lambda_handler"]
