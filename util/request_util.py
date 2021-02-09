import requests

"""
工具类封装
"""


class RequestUtil(object):

    def __init__(self):
        pass

    def request(self, url, method, headers=None, param=None, content_type=None):
        """
        通用请求工具类
        @param url:
        @param method:
        @param headers:
        @param param:
        @param content_type:
        @return:
        """
        try:
            if method == "get":
                response = requests.get(url=url, headers=headers, params=param).json()
                return response
            elif method == "post":
                if content_type == "application/json":
                    response = requests.post(url=url, headers=headers, json=param).json()
                    return response
                else:
                    response = requests.post(url=url, headers=headers, data=param).json()
                    return response
            else:
                print("http method not allowed")

        except Exception as e:
            print("http请求数据:{0}".format(e))


if __name__ == '__main__':
    # # get请求
    # url = "https://api.xdclass.net/pub/api/v1/web/video_detail"
    # data = {"video_id": 53}
    # r = RequestUtil()
    # result = r.request(url,"get",param=data)
    # print(result)

    # post请求
    url = "https://api.xdclass.net/pub/api/v1/web/is_favorite"
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "token": "xdclasseyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4ZGNsYXNzIiwicm9sZXMiOiIxIiwiaW1nIjoiaHR0cHM6Ly90aGlyZHd4LnFsb2dvLmNuL21tb3Blbi92aV8zMi9RMGo0VHdHVGZUSWZ1d3EwenRkMnRXWkZaek9sZ1JISklIVFJDN1hManNPM1lBRUtmTUliZzhtampHNnRjdW9CWGhNeUZzNmtpYTlqeGljTDRVbWx5Q0tRLzEzMiIsImlkIjo2Nzg0NDUyLCJuYW1lIjoi5a2j6aOOIiwiaWF0IjoxNjEyMzQ2MzE2LCJleHAiOjE2MTI5NTExMTZ9.gHkzQzxNdoIAaVpLGIqo8Z_IkkTilsW4dQE82DBkSyI"
               }
    data = {"video_id": 3}
    r = RequestUtil()
    result = r.request(url, "post", headers=headers, param=data, content_type="application/x-www-form-urlencoded")
    print(result)
