from flask import Response, jsonify


def build_response(data: dict, status_code: int = 200) -> Response:
    '''
    Description
    -----------
    combine data and status code into a single Response object.

    Parameters
    ---------
    data: dict
    data to be serialized into json

    status_code: int. Default 200
    HTTP status code for the response.

    Returns
    --------
    Response: flask.Response
    '''
    response = jsonify(data)
    response.status_code = status_code
    return response
