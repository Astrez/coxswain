from enum import Enum
from typing import Union, Tuple, Any, Callable, TypeVar
from functools import wraps
from flask import jsonify


F = TypeVar('F', bound=Callable[..., Any])

class status(tuple, Enum):
    """
    values of format (status string, custom status code, http status code)
    """
    success = "SUCCESS", 1000, 200
    failure = "FAILURE", 1005, 200
    invalid = "INVALID", 1100, 500
    unauth = 'NOT AUTHORISED', 1400, 403
    error = "ERROR", 1500, 500

class Response:
    @staticmethod
    def responseFormat1(result : Union[list, str, dict], status) -> Tuple[Any, int]:
        '''Responses of the type 
        {
            'result' : "RESULT", 
            'status' : "STATUS" 
            'status_code' : 1111
        }
        '''
        return jsonify({'result' : result, 'status' : status[0]}), status[2]

class Utils:

    @staticmethod
    def getParams(request, params : tuple) -> Callable[[F], F]:
        def decorated(f : F) -> F:
            @wraps(f)
            def wrapper(*args, **kwargs) -> Tuple[Any, int]:
                try:
                    data = {i : request.args.get(i) for i in params}
                    if None in data.values():
                        return Response.responseFormat1("Please include all valid parameters", status.invalid)
                    return f(data, *args, **kwargs)
                except Exception as e:
                    return Response.responseFormat1(str(e), status.error)
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
                                    return Response.responseFormat1("Datatypes not valid", status.invalid)
                            return f(received, *args, **kwargs)
                        return Response.responseFormat1("Please include all valid key value pairs", status.invalid)
                    return Response.responseFormat1("Please include body", status.invalid)
                except Exception as e:
                    return Response.responseFormat1(str(e), status.error)
            return wrapper
        return decorated