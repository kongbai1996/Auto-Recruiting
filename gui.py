import json
from json import JSONDecodeError

import PySimpleGUI as sg

from run import run

# print(sg.theme_list())  # 获取主题名称列表，并打印出来
# sg.theme('')  # 随机主题

cache_json = dict()


def default_setting():
    cache_json["position_name"] = "C/C++开发工程师"
    cache_json["position_key"] = "C++"
    cache_json["page"] = 30
    cache_json["log_level"] = "INFO"


try:
    cache_json_str = open("wt2_cache").read()
    cache_json = json.loads(cache_json_str)
except (FileNotFoundError, JSONDecodeError):
    default_setting()

layout = [
    [sg.Text("请输入wt2"), sg.In(cache_json.get("wt2"), key="wt2")],
    [sg.Text("请输入匹配的职位"), sg.InputText(cache_json.get("position_name"), key="position_name")],
    [sg.Text("请输入匹配的关键字"), sg.InputText(cache_json.get("position_key"), key="position_key")],
    [sg.Text("请输入查询页数"), sg.InputText(cache_json.get("page"), key="page")],
    [sg.Text("请输入日志级别"), sg.InputText(cache_json.get("log_level"), key="log_level")],
    [sg.Text("结果", key="my_result")],
    [sg.Button("开始搜索")],
]

window = sg.Window("Auto-Recruiting", layout)

_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome" \
              "/105.0.0.0 Safari/537.36 Edg/105.0.1343.42"
_wt2 = "DMNUqkUp0RqCcgpmtzRV7MipLqEpyO9ZY9Iq94mTSKlODg1zn9JqUqdm0BBOMsIH7fYxO7eCvbdjnzyQ1b4KH8A~~"
_cookie = f"wt2={_wt2}"
_encryptJobId = ""
_school_list = list()

while True:
    event, values = window.read()  # 窗口的读取，有两个返回值(1.事件 2.值)
    if event is None:  # 窗口关闭事件
        break
    if event == "开始搜索":
        new_wt2: str = values.get("wt2")
        window["my_result"].update("reasdfsafad")
        if values != cache_json:
            with open("wt2_cache", "w") as wt2_file:
                wt2_file.write(json.dumps(values))
        if new_wt2:
            window.close()
            position_name = values.get("position_name")
            position_key = values.get("position_key")
            page = values.get("page")
            log_level = values.get("log_level")
            result = run(new_wt2, position_name, position_key, int(page), log_level)
            layout = [
                [sg.Text("自动打招呼结果")],
                [sg.In(result, key="result")]
            ]
            window = sg.Window("Auto-Recruiting-Result", layout)
            while True:
                event, values = window.read()  # 窗口的读取，有两个返回值(1.事件 2.值)
                if event is None:  # 窗口关闭事件
                    break

        else:
            sg.popup("wt2为必填项，请先输入！")

window.close()
