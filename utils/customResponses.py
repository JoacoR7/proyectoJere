from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

class JsonEmitter:

    def response(status, detail = None, content = None, exception = None):
        if detail == None:
            data = jsonable_encoder(content)
        elif exception != None:
            data = {"detail": detail,
                    "exception": str(exception)}
        else:
            data = {"detail": detail}
        return JSONResponse(content=data, status_code=status)

class sqlAlchemySplitter:

    def split(exception):
        exception = (str(exception).split(" "))[1].replace("(", "").replace(",", "")
        return exception
    