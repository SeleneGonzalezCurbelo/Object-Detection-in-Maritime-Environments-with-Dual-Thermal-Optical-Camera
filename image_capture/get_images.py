import datetime
from enum import Enum
import logging
from datetime import datetime
import time
from onvif import ONVIFCamera
import json
import requests
from PIL import Image
import requests
from io import BytesIO
import os
import xml.etree.ElementTree as ET

logging.basicConfig(filename='prueba_thermal.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define camera ID constants
camera_id = 2

# ONVIF device's IP address and port
ip = 'xxx.xxx.xx.xx'
port = 80

# Authentication credentials
username = 'username'
password = 'password'

username_onvif = 'username_onvif'
password_onvif = 'password_onvif'

profile_token = 'profile_token'

class Request(Enum):
    """
    Enum class representing request status.

    Attributes:
        true (int): Value representing true.
        false (int): Value representing false.
    """
    ptz = "PTZCtrl"
    thermal = "Thermal"
    streaming = "Streaming"

class Enabled(Enum):
    """
    Enum class representing enabled status.

    Attributes:
        true (int): Value representing true.
        false (int): Value representing false.
    """
    true = 1
    false = 0

def create_camera():
    """
    Create an ONVIF camera object.

    Returns:
        ONVIFCamera: The ONVIF camera object.
    """
    return ONVIFCamera(ip, port, username_onvif, password_onvif, '/home/selene/etc/wsdl')


def get_ptz_service(camera):
    """
    Get the PTZ service of the ONVIF camera.

    Args:
        camera (ONVIFCamera): The ONVIF camera object.

    Returns:
        ONVIFPTZService: The PTZ service of the camera.
    """
    return camera.create_ptz_service()


def get_status(ptz_service, profile_token):
    """
    Operation to request PTZ status for the Node in the selected profile.

    Args:
        profile_token (str): The profile token.

    Returns:
        The PTZStatus for the requested MediaProfile.
    """
    return ptz_service.GetStatus({'ProfileToken': profile_token})

def build_url(endpoint, request, idPreset=None, aux=None):
    """
    Builds the URL for a given endpoint.

    Args:
        endpoint (str): The endpoint to be appended to the base URL.
        idPreset (int): The ID of the preset (optional).

    Returns:
        str: The complete URL.
    """
    base_url = f'http://{ip}/ISAPI'
    
    if request in (Request.ptz.value, Request.thermal.value, Request.streaming.value):
        base_url += f'/{request.capitalize()}/channels/{camera_id}/{endpoint}'
        if idPreset is not None:
            base_url += f'/{idPreset}'
        if aux is not None:
            base_url += f'/{aux}'
    else:
        base_url += f'/System/Video/inputs/channels/{camera_id}/focus'
    return base_url

def send_request(endpoint, request_type, idPreset, data, method, aux=None):
    """
    Sends an HTTP request to a specified endpoint with optional data and method.

    Args:
        endpoint (str): The endpoint URL.
        request_type (str): Type of request (e.g., 'presets', 'picture').
        idPreset (int or None): ID of the preset (or None if not applicable).
        data (dict or None): Data payload for POST or PUT requests.
        method (str): HTTP method ('GET', 'PUT', 'POST', 'DELETE').
        aux (str or None): Optional auxiliary parameter.

    Returns:
        requests.Response: Response object containing the server's response to the request.
    """
    url = build_url(endpoint, request_type, idPreset, aux=aux)
    auth = requests.auth.HTTPBasicAuth(username, password)
    if method == 'GET':
        response = requests.get(url, auth=auth)
    elif method == 'PUT':
        response = requests.put(url, data=data, auth=auth)
    elif method == 'POST':
        response = requests.post(url, data=data, auth=auth)
    elif method == 'DELETE':
        response = requests.delete(url, data=data, auth=auth)
    return response

def handle_ptz_response(response, operation):
    """
    Handles the response from a PTZ operation.

    Args:
        response (requests.Response): The response object from the request.
        operation (str): The name of the PTZ operation (e.g., 'Stop', 'Continuous Move', 'Absolute Move').

    Returns:
        bool: True if the response status code is 200, False otherwise.
    """
    if response.status_code == 200:
        logging.info(f'{operation} successful')
        return True
    else:
        logging.error(f'Error {operation}. Status code: {response.status_code}')
        if response.text:
            logging.error(f'Response content: {response.text}')
        return False

def goto(idPreset):
    """
    Sends a PTZ request to move to a specific preset.

    Args:
        idPreset (int): The ID of the preset to move to.
    """
    response = send_request('presets', Request.ptz.value, idPreset=idPreset, data=None, method='PUT', aux='goto')
    success = handle_ptz_response(response, f'Goto {idPreset}')
    if not success:
        logging.error('An error occurred. Please check the configuration and try again.')

def save_image_from_object(image, full_path):
    """
    Saves an image object to a specified full path.

    Args:
        image (PIL.Image.Image): Image object to be saved.
        full_path (str): Full path including filename where the image will be saved.
    """
    try:
        # Check if the directory exists, if not, create it
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = f'url/{current_time}.jpg'
        
        # Make a request to the specified URL
        response = requests.get(url)

        if response.status_code == 200:
            # Save the image to a local file
            with open('image.jpg', 'wb') as file:
                file.write(response.content)
            print('Image downloaded successfully.')
        else:
            print(f'Request error. Status code: {response.status_code}')
        
        # Save the image locally using the provided path
        image.save(full_path)
        print(f"Image saved at '{full_path}'")
    
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")

def save_image(directory):
    """
    Sends a request to obtain an image, opens it, and saves it locally.

    Args:
        directory (str): Directory path where the image will be saved.
    """    
    response = send_request('picture', Request.streaming.value, idPreset=None, data=None, method='GET')
    success = handle_ptz_response(response, f'Get Image')
    print(response)
    
    if not success:
        logging.error('An error occurred. Please check the configuration and try again.')

    # Open the image from the response content
    image_object = Image.open(BytesIO(response.content))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define the destination path for saving the image
    destination_path = f'{directory}/{current_time}.png'

    # Call the save_image_from_object function to save the image locally
    save_image_from_object(image_object, destination_path)

def get_preset_name_from_xml(response):
    """
    Extracts the preset name from an XML response.

    Args:
        response (requests.Response): Response object containing XML data.

    Returns:
        str: Extracted preset name if found, otherwise an empty string.
    """
    try:
        root = ET.fromstring(response.text)
        preset_name_element = root.find('.//presetName')
        if preset_name_element is not None and preset_name_element.text is not None:
            return preset_name_element.text.strip()
        else:
            logging.error('Unable to extract preset name from XML response.')
            return ''
    except ET.ParseError:
        logging.error('Error parsing XML response.')
        return ''

def get_preset_name_with_id(idPreset):
    """
    Gets a specific preset by its ID from the camera.

    Args:
        idPreset (int): The ID of the preset to retrieve.
    """
    response = send_request('presets', Request.ptz.value, idPreset=idPreset, data=None, method='GET')
    success = handle_ptz_response(response, f'Get Presets With Id {idPreset}')

    if not success:
        logging.error('An error occurred. Please check the configuration and try again.')

    return get_preset_name_from_xml(response)

def updata_preset(enabled, id, presetName):
    """
    Updatas a preset with the specified enabled status, ID, and name.

    Args:
        enabled (str): The enabled status (either 'true' or 'false').
        id (int): The ID of the preset to updata.
        presetName (str): The new name for the preset.
    """
    
    if enabled == Enabled.true.value:
        enabled = Enabled.true
    else:
        enabled = Enabled.false
    data = '<PTZPreset version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema"><enabled>{}</enabled><id>{}</id><presetName>{}</presetName></PTZPreset>'.format(enabled.name, id, presetName)
    response = send_request('presets', Request.ptz.value, idPreset=id, data=data, method='PUT')
    success = handle_ptz_response(response, f'Updata Preset {presetName}')

    if not success:
        logging.error('An error occurred. Please check the configuration and try again.')

def updata_preset_file(idPreset, status_dict):
    """
    Update the PanTilt values of a preset file with the given status dictionary.

    Args:
        idPreset (int or str): Identifier of the preset whose file needs to be updated.
        status_dict (dict): Dictionary containing 'x' and 'y' keys with new PanTilt values.
    """
    old_preset_name = get_preset_name_with_id(idPreset)

    directory = "/home/selene/scripts/presets_data/"
    filename = f'{directory}{old_preset_name}_preset.json'

    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            existing_data = json.load(json_file)

        # Update the PanTilt values in the existing data
        existing_data['Position']['PanTilt']['x'] = status_dict['x']
        existing_data['Position']['PanTilt']['y'] = status_dict['y']

        # Convert the dictionary to a JSON string
        updated_json = json.dumps(existing_data, indent=4, default=str)

        # Save the updated JSON data to the file
        with open(filename, 'w') as json_file:
            json_file.write(updated_json)

        logging.info(f'The PanTilt positions in {filename} have been updated.')
    else:
        logging.error(f'The file {filename} does not exist.')

    logging.info(f'The file {filename} has been updatad.')

def get_image(idPreset, presetName):
    """
    Function to capture an image when a camera reaches a specified preset position.

    Args:
        idPreset (int or str): Identifier of the preset position to move the camera to.
        presetName (str): Name of the preset, used to locate the corresponding JSON file
                         containing stored pan-tilt coordinates.
    """
    mycam = create_camera()
    ptz_service = get_ptz_service(mycam)
    directory = "/presets_data/"
    filename = f'{directory}{presetName}_preset.json'
    with open(filename, 'r') as json_file:
        stored_data = json.load(json_file)

    stored_pan_tilt_x = stored_data['Position']['PanTilt']['x']
    stored_pan_tilt_y = stored_data['Position']['PanTilt']['y']

    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        time.sleep(5)  
        goto(idPreset)
        status = get_status(ptz_service, profile_token)
        pan_tilt_x = status.Position.PanTilt.x
        pan_tilt_y = status.Position.PanTilt.y

        if (
            pan_tilt_x == stored_pan_tilt_x and
            pan_tilt_y == stored_pan_tilt_y
        ):
            save_image('images_position')

            status_dict = {
                'x': pan_tilt_x,
                'y': pan_tilt_y,
            }

            # Convert the dictionary to a JSON string
            preset_json = json.dumps(status_dict, indent=4, default=str)  # Use default=str to handle non-serializable types

            current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            directory = "directory/images/"
            filename = f'{directory}{current_date}.json'

            # Save the JSON data to a file
            with open(filename, 'w') as json_file:
                json_file.write(preset_json)

            logging.info(f"Current positions match those stored in preset {idPreset}.")
            logging.info(f"pan_tilt_x: {pan_tilt_x}, stored_pan_tilt_x:  {stored_pan_tilt_x}, pan_tilt_y: {pan_tilt_y}, stored_pan_tilt_y: {stored_pan_tilt_y}")
            break  
        else:
            logging.error(f"Current positions do not match those stored in preset {idPreset}.")
            logging.error(f"pan_tilt_x: {pan_tilt_x}, stored_pan_tilt_x:  {stored_pan_tilt_x}, pan_tilt_y: {pan_tilt_y}, stored_pan_tilt_y: {stored_pan_tilt_y}")

        attempt += 1
        logging.error(f"Attempt {attempt} failed. Retrying...")

    if attempt == max_attempts:

        status = get_status(ptz_service, profile_token)
        pan_tilt_x = status.Position.PanTilt.x
        pan_tilt_y = status.Position.PanTilt.y

        status_dict = {
            'x': pan_tilt_x,
            'y': pan_tilt_y,
        }

        # Convert the dictionary to a JSON string
        preset_json = json.dumps(status_dict, indent=4, default=str)  # Use default=str to handle non-serializable types

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        directory = "directory/images/"
        filename = f'{directory}{current_date}.json'

        # Save the JSON data to a file
        with open(filename, 'w') as json_file:
            json_file.write(preset_json)

        updata_preset_file(idPreset, status_dict)
        updata_preset(1, idPreset, "Newpreset2")

        logging.error("Maximum attempts reached. Operation could not be completed successfully.")

def main():

    presets = [
        {'presetId': 1, 'presetName': 'Preset 1'},
        {'presetId': 2, 'presetName': 'Preset 2'},
        {'presetId': 3, 'presetName': 'Preset 3'}
    ]

    for preset in presets:
        presetId = preset['presetId']
        presetName = preset['presetName']

        get_image(presetId, presetName)

if __name__ == "__main__":
    main()