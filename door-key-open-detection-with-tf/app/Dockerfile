FROM public.ecr.aws/lambda/python:3.8

COPY app.py tf_example.py requirements.txt ./
COPY saved_model.pb signature.json variables /opt/ml/model/

RUN python3.8 -m pip install -r requirements.txt -t .

CMD ["app.lambda_handler"]
