SDK使用说明
最近更新时间：2025.07.10 14:22:35
首次发布时间：2024.09.13 12:04:46
我的收藏
有用
无用
前置说明（必读）​
注：接口类型分为三类：同步接口，异步接口，同步转异步接口​
以下内容为调用SDK的通用说明，以 智能绘图-通用2.0L-文生图 为例：​
Step1: 查看接口文档请求参数-Query参数中的Action及对应Version，根据Action全局检索SDK，找到对应的example或参考本文档中的调用示例​​​
Step2: 查看接口文档请求参数-Body参数、请求示例，将请求示例内容复制到调用示例的body入参部分​Image​​
Step3: 更新其他关键信息，比如AK/SK，然后运行程序进行调试即可​
​Image​​
Step4: 调通SDK示例后，再正式集成到工程中

# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your ak')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        "task_id": "xxx",
        "req_json": "{\"logo_info\":{\"add_logo\":true，\"position\":1, \"language\":1,\"opacity\"：0.5}}"
    }
    resp = visual_service.cv_sync2async_get_result(form)
    print(resp)