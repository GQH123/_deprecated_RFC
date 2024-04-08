import os
import cgi
import mimetypes
from tqdm import tqdm

from ..utils.log import get_logger

__all__ = [
    'get_status_code',
    'get_filename',
    'get_fileext',
    'get_content_type',
    'get_content_sync',
    'get_content_async',
    'get_json_sync',
    'get_json_async',
    'get_text_sync',
    'get_text_async',
    'get_content_length',
    'get_stream_sync',
]

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


def get_status_code(resp, request_lib):
    if request_lib == 'requests':
        return resp.status_code
    elif request_lib == 'aiohttp':
        return resp.status
    elif request_lib == 'asks':
        return resp.status_code
    else:
        raise ValueError(f"unsupported request_lib {repr(request_lib)}")


def get_filename(resp, request_lib, default_filename=None):
    contentdisposition = resp.headers.get('content-disposition')
    if contentdisposition is None:
        return default_filename
    _, params = cgi.parse_header(contentdisposition)
    try:
        filename = params["filename"]
    except Exception:
        filename = None
    if filename is None:
        return default_filename
    return filename


def get_fileext(resp, request_lib):
    content_type = get_content_type(resp, request_lib)
    if content_type is None:
        return ''
    if ';' in content_type:
        content_type = content_type.split(';')[0]
    ext = mimetypes.guess_extension(content_type)
    if ext is None:
        if '/' in content_type:
            return '.' + content_type.split('/')[-1]
        else:
            return '.' + content_type
    if not ext.startswith('.'):
        ext = '.' + ext
    return ext


def get_content_type(resp, request_lib):
    if request_lib == 'requests':
        return resp.headers.get('content-type', None)  # 'text/html; charset=UTF-8'
    elif request_lib == 'aiohttp':
        return resp.headers.get('CONTENT-TYPE', None)
    elif request_lib == 'asks':
        return resp.headers['Content-Type']
    else:
        raise ValueError(f"unsupported request_lib {repr(request_lib)}")


def get_content_sync(resp, request_lib):
    if request_lib == 'requests':
        return resp.content
    elif request_lib == 'asks':
        return resp.content
    else:
        raise ValueError(f"unsupported sync request_lib {repr(request_lib)}")


async def get_content_async(resp, request_lib):
    if request_lib == 'aiohttp':
        return await resp.read()
    else:
        raise ValueError(f"unsupported async request_lib {repr(request_lib)}")


def get_json_sync(resp, request_lib):
    if request_lib == 'requests':
        return resp.json()
    elif request_lib == 'asks':
        return resp.json()
    else:
        raise ValueError(f"unsupported sync request_lib {repr(request_lib)}")


async def get_json_async(resp, request_lib):
    if request_lib == 'aiohttp':
        return await resp.json() 
    else:
        raise ValueError(f"unsupported async request_lib {repr(request_lib)}")


def get_text_sync(resp, request_lib):
    if request_lib == 'requests':
        return resp.text
    else:
        raise ValueError(f"unsupported sync request_lib {repr(request_lib)}")


async def get_text_async(resp, request_lib):
    if request_lib == 'aiohttp':
        return await resp.text() 
    else:
        raise ValueError(f"unsupported async request_lib {repr(request_lib)}")


def get_content_length(resp, request_lib):
    return resp.headers.get('content-length', 0)


def get_stream_sync(resp, request_lib, path, chunk_size, logger=None):
    total_size = int(get_content_length(resp, request_lib))
    if request_lib == 'requests':
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        progress_bar.update(len(chunk))
                        f.write(chunk)
        if total_size != 0 and progress_bar.n != total_size:
            os.remove(path)
            if logger is not None:
                logger.warning(f"failed to download stream to {repr(path)}")
            return
        if logger is not None:
            logger.info(f"downloaded stream to {repr(path)}")
    else:
        raise ValueError(f"unsupported request_lib {repr(request_lib)}")


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")