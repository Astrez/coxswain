from enum import Enum
from typing import Union, Tuple, Any, Callable, TypeVar
from functools import wraps
from flask import jsonify

import logging
import traceback

# Logger for errors
errLogger = logging.getLogger("app.logger")

F = TypeVar('F', bound=Callable[..., Any])

class status(tuple, Enum):
    """
    values of format (status string, custom status code, http status code)
    """
    success = "SUCCESS", 200
    failure = "FAILURE", 200
    invalid = "INVALID", 500
    unauth = 'NOT AUTHORISED', 403
    error = "ERROR", 500
    bad_request = "BAD REQUEST", 401

class Response:
    @staticmethod
    def responseFormat(result : Union[list, str, dict], status) -> Tuple[Any, int]:
        '''Responses of the type 
        {
            'result' : "RESULT", 
            'status' : "STATUS" 
        }
        '''
        return jsonify({'result' : result, 'status' : status[0]}), status[1]

class Utils:
    '''
    Class for error handling for routes
    '''

    @staticmethod
    def getParams(request, params : tuple) -> Callable[[F], F]:
        def decorated(f : F) -> F:
            @wraps(f)
            def wrapper(*args, **kwargs) -> Tuple[Any, int]:
                try:
                    data = {i : request.args.get(i) for i in params}
                    if None in data.values():
                        return Response.responseFormat("Please include all valid parameters", status.invalid)
                    return f(data, *args, **kwargs)
                except Exception as e:
                    errLogger.error(traceback.format_exc())
                    return Response.responseFormat(str(e), status.error)
            return wrapper
        return decorated
    
    @staticmethod
    def getBody(request, elements : dict) -> Callable[[F], F]:      
        def decorated(f : F) -> F:
            @wraps(f)
            def wrapper(*args, **kwargs) -> Tuple[Any, int]:
                try:
                    received = request.get_json()
                    if received:
                        if sorted(received.keys()) == sorted(elements.keys()):
                            for i, j in received.items():
                                if type(j) not in elements[i]:
                                    return Response.responseFormat("Datatypes not valid", status.invalid)
                            return f(received, *args, **kwargs)
                        return Response.responseFormat("Please include all valid key value pairs", status.invalid)
                    return Response.responseFormat("Please include body", status.invalid)
                except Exception as e:
                    errLogger.error(traceback.format_exc())
                    return Response.responseFormat(str(e), status.error)
            return wrapper
        return decorated