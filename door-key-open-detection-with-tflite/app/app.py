import base64
import io
import json

from PIL import Image

from tflite_example import TFLiteModel

MODEL_DIR_PATH = '/opt/ml/model/'


def lambda_handler(event, context):

    image_bytes = event['body'].encode('utf-8')
    image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))

    print("Initialize the model")
    model = TFLiteModel(dir_path=MODEL_DIR_PATH)
    print("Load the model")
    model.load()
    print("Predict start!")
    outputs = model.predict(image)
    print(f"Predicted: {outputs}")

    return {
        'statusCode': 200,
        'body': json.dumps(outputs)
    }
