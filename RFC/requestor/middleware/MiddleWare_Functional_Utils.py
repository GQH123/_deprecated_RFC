from .MiddleWare_Exceptions import MiddleWare_UnknownFramework


def parse_content_type(resp, framework):
    if framework == 'requests':
        return resp.headers['content-type']
    elif framework == 'aiohttp':
        return resp.headers['CONTENT-TYPE']
    elif framework == 'asks':
        return resp.headers['Content-Type']
    else:
        raise MiddleWare_UnknownFramework(framework)

async def parse_content(resp, framework):
    if framework == 'requests':
        return resp.content
    elif framework == 'aiohttp':
        return await resp.read()
    elif framework == 'asks':
        return resp.content
    else:
        raise MiddleWare_UnknownFramework(framework)


async def return_json(resp, framework):
    if framework == 'requests':
        return resp.json()
    elif framework == 'aiohttp':
        return await resp.json() 
    elif framework == 'asks':
        return resp.json()
    else:
        raise MiddleWare_UnknownFramework(framework)


def get_status_code(resp, framework):
    if framework == 'requests':
        return resp.status_code
    elif framework == 'aiohttp':
        return resp.status
    elif framework == 'asks':
        return resp.status_code
    else:
        raise MiddleWare_UnknownFramework(framework)