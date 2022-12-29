import base64
import json
import os
import subprocess
import time

import requests
import boto3

SORACOM_AUTH_KEY_ID = os.environ.get("SORACOM_AUTH_KEY_ID")
SORACOM_AUTH_KEY = os.environ.get("SORACOM_AUTH_KEY")
DEVICE_ID = os.environ.get("DEVICE_ID")
COMMON_ARG = ' --auth-key-id ' + SORACOM_AUTH_KEY_ID + ' --auth-key ' + SORACOM_AUTH_KEY

INFERENCE_LAMBDA_ARN = os.environ.get("INFERENCE_LAMBDA_ARN")
LINE_NOTIFY_TOKEN = os.environ.get("LINE_NOTIFY_TOKEN")


def lambda_handler(event, context):
    print("Export image from Soracom Cloud Camera Service")
    exported_image_bytes = export_image()
    print("Invoke inference lambda to inference the exported image")
    lambda_response = invoke_inference_lambda(exported_image_bytes)
    label_name = get_prediction_label_from_inference_lambda_result(lambda_response)
    print("Notify the result")
    notify_to_line(label_name, exported_image_bytes)

    return


def run_cmd(cmd):
    cmd = cmd + COMMON_ARG
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return res


def export_image():
    """Exports image from Soracom Cloud Camera Service using Soracom API"""
    photo_shoot_time = int(time.time()) * 1000
    export_sora_cam_image_cmd = "soracom sora-cam devices images export --image-filters 'wide_angle_correction' --device-id " + DEVICE_ID + " --time " + str(photo_shoot_time)
    exported_image_info = json.loads(run_cmd(export_sora_cam_image_cmd).stdout.decode())
    export_id = exported_image_info.get("exportId")

    # As the export takes time, need to sleep here
    time.sleep(2)
    get_exported_sora_cam_image_cmd = "soracom sora-cam devices images get-exported --device-id " + DEVICE_ID + " --export-id " + export_id
    updated_exported_image_info = json.loads(run_cmd(get_exported_sora_cam_image_cmd).stdout.decode())

    image_url = updated_exported_image_info.get("url")
    image_data_bytes = requests.get(image_url).content
    return image_data_bytes


def invoke_inference_lambda(image_data):
    """Invoke inference lambda to inference the exported image"""
    client = boto3.client('lambda')

    img_b64 = base64.b64encode(image_data).decode("utf8")

    data = {
        "body": img_b64
    }
    payload = json.dumps(data)

    response = client.invoke(
        FunctionName=INFERENCE_LAMBDA_ARN,
        InvocationType='RequestResponse',
        Payload=payload
    )

    return response


def get_prediction_label_from_inference_lambda_result(lambda_response):
    """Pick up the label from the result, 'open' or 'closed'"""
    payload = lambda_response['Payload'].read()
    res_body = json.loads(payload).get('body')
    predictions_list = json.loads(res_body).get('predictions')
    highest_confidence_prediction = list(sorted(predictions_list, key=lambda item: item['confidence'], reverse=True))[0]
    highest_prediction_label = highest_confidence_prediction.get('label')

    return highest_prediction_label


def notify_to_line(label_name, image_bytes):
    """Notify the result to LINE"""
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}

    if label_name == "closed":
        message = 'The door is ' + label_name
    elif label_name == "open":
        message = 'The door is ' + label_name
    else:
        message = 'Cannot detect the image'

    data = {'message': 'message: ' + message}
    files = {'imageFile': image_bytes}
    response = requests.post(line_notify_api, headers=headers, data=data, files=files)
    print(response)
