# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import random
import re
import sys
import time
import urllib.request
from datetime import datetime
from typing import List
from urllib import parse
from urllib.error import URLError

from loguru import logger

_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome" \
              "/105.0.0.0 Safari/537.36 Edg/105.0.1343.42"


def start_greet(expectId: str, securityId: str, lid: str, encryptGeekId: str, geekName: str):
    start_url = "https://www.zhipin.com/wapi/zpjob/chat/start"
    start_headers = dict()
    start_headers["Content-Type"] = "application/x-www-form-urlencoded"
    start_headers["Cookie"] = _cookie
    start_headers["User-Agent"] = _user_agent  # 非必须
    # headers["zp_token"] = "V1RN4vF-L52VhiVtRvyRkcLSK17zvQxyQ~"
    # headers["traceId"] = "AB0CE048-62F5-4883-9A0D-FD7C45BFD340"
    # headers["X-Anti-Request-Token"] = "d41d8cd98f00b204e9800998ecf8427e"
    start_content = dict()
    start_content["expectId"] = expectId  # 必须，否则会报{"code":17,"message":"缺少必要参数","zpData":{}}
    start_content["jid"] = _encryptJobId  # 必须，否则会报{"code":17,"message":"缺少必要参数","zpData":{}}
    # content["gid"] = encryptGeekId  # 非必须
    # content["lid"] = lid  # 非必须
    start_content["securityId"] = securityId  # 必须，否则会报{"code":1092,"message":"操作失败","zpData":{}}
    start_data = parse.urlencode(start_content)
    start_request = urllib.request.Request(start_url, start_data.encode(), headers=start_headers)
    start_response = urllib.request.urlopen(start_request)
    start_result_str = start_response.read().decode()
    start_result_json: dict = json.loads(start_result_str)
    start_result_code = start_result_json.get("code")
    if start_result_code == 0:
        zpData: dict = start_result_json.get("zpData")
        if zpData:
            if zpData.get('limitTitle') or zpData.get('stateDesc'):
                logger.error(f"向候选人：【{geekName}】打招呼失败")
                logger.error(f"【limitTitle】{zpData.get('limitTitle')}")
                logger.error(f"【stateDesc】{zpData.get('stateDesc')}")
                exit(zpData.get('limitTitle'))
                return False
        logger.success(f"向候选人：【{geekName}】打招呼成功")
        return True
    else:
        logger.error("向候选人打招呼失败：错误信息如下")
        logger.error(start_result_str)
        return False


def check_edu_list(geekEdus: list, ) -> bool:
    if not _school_list:
        return True
    if geekEdus:
        for edu in geekEdus:
            school = edu.get("school")
            major = edu.get("major")
            degreeName = edu.get("degreeName")
            eduType = edu.get("eduType")  # 教育类型：1 全日制，2 非全日制，列表页没有给到具体的类型
            startDate = edu.get("startDate")
            endDate = edu.get("endDate")
            if not check_edu_end_date(endDate):
                return False
            if _school_list and _school_list.count(school):
                return True
    return False


def check_edu_end_date(end_date: str) -> bool:
    if len(end_date) > 4:
        return datetime.today().year >= int(end_date[:4])
    return True


def find_relevant_talent(geek: dict):
    regex_list: List[str] = list()
    geekCard: dict = geek.get("geekCard")
    geekName = geekCard.get("geekName")
    geekGender = geekCard.get("geekGender")  # 性别 1是男0是女
    ageDesc = geekCard.get("ageDesc")  # 年龄 29岁
    if len(ageDesc) >= 2 and int(ageDesc[:2]) > 30:
        logger.info(f"年龄不匹配：候选人姓名：{geekName}，性别：{'男' if geekGender == 1 else '女'}，"
                    f"年龄：{ageDesc}")
        return False
    geekWorkYear = geekCard.get("geekWorkYear")
    geekDegree = geekCard.get("geekDegree")
    geekDesc: dict = geekCard.get("geekDesc")
    geekDesc_content = geekDesc.get("content")  # 个人优势
    regex_list.append(geekDesc_content)
    expectPositionName = geekCard.get("expectPositionName")  # 期望岗位
    regex_list.append(expectPositionName)
    expectLocationName = geekCard.get("expectLocationName")  # 期望城市
    activeTimeDesc = geekCard.get("activeTimeDesc")  # 活跃状态
    # if not activeTimeDesc:
    #     activeTime = geekCard.get("activeTime")  # 活跃时间
    #     if time.time() - activeTime > 60 * 60 * 24 * 30 * 3:
    #         logger.info(f"不活跃：候选人姓名：{geekName}，性别：{'男' if geekGender == 1 else '女'}，"
    #                     f"上次活跃时间：{time.strftime('%Y年%m月%d日 %H:%M:%S', time.localtime(activeTime))}，"
    #                     f"年龄：{ageDesc}")
    #         return False
    geekEdu: dict = geekCard.get("geekEdu")  # 教育信息（最高）
    height_school = geekEdu.get("school")
    height_major = geekEdu.get("major")
    graduationDate = geekEdu.get("endDate")
    geekEdus: List[dict] = geekCard.get("geekEdus")  # 所有教育信息
    geekWorks: dict = geekCard.get("geekWorks")  # 工作经历
    if geekWorks:
        for work in geekWorks:
            company = work.get("company")
            positionCategory = work.get("positionCategory")
            positionName = work.get("positionName")
            regex_list.append(positionName)
            responsibility = work.get("responsibility")  # 工作内容
            workPerformance = work.get("workPerformance")  # 业绩
            workEmphasisList = work.get("workEmphasisList")  # 工作重点标签
            startDate = work.get("startDate")
            endDate = work.get("endDate")
    regex_math_list = list()
    for regex in regex_list:
        new_position_match = _position_match
        # 对正则的特殊字符进行转义，由于转义的时候会用到\所以提前对\转义，否则会对转义后的转义字符重复转义。目前转义的字符是【\,+,?,*,.】
        for char in "\\+?*.":
            new_position_match = new_position_match.replace(char, f"\\{char}")
        regex_result = re.search(f"\\.*{new_position_match}\\.*", regex)
        if regex_result:
            regex_math_list.append(regex)
    if regex_math_list:
        logger.info(f"匹配到岗位关键字：{regex_math_list}")
        if check_edu_list(geekEdus):
            logger.success(
                f"匹配到简历：候选人姓名：{geekName}，性别：{'男' if geekGender == 1 else '女'}，年龄：{ageDesc}，"
                f"工作年限：{geekWorkYear}，期望岗位：{expectPositionName}，学历：{geekDegree}，学校：{height_school}，"
                f"毕业时间：{graduationDate}，专业：{height_major}")
        else:
            logger.info(f"未匹配到教育经历：候选人姓名：{geekName}，性别：{'男' if geekGender == 1 else '女'}，年龄：{ageDesc}，"
                        f"工作年限：{geekWorkYear}，期望岗位：{expectPositionName}，学历：{geekDegree}，"
                        f"学校：{height_school}，毕业时间：{graduationDate}，专业：{height_major}")
            return False
        expectId = geekCard.get("expectId")
        lid = geekCard.get("lid")
        securityId = geekCard.get("securityId")
        encryptGeekId = geekCard.get("encryptGeekId")
        time.sleep(random.randint(3, 10))  # 随机延时3-10秒，防止出现人机验证
        if start_greet(expectId, securityId, lid, encryptGeekId, geekName):
            return True
    return False


def query_position(position_name: str) -> str:
    headers = dict()
    headers["Cookie"] = _cookie  # 必须，否则会报'{"code":7,"message":"当前登录状态已失效","zpData":{}}'
    headers["User-Agent"] = _user_agent  # 非必须
    query_position_url = "https://www.zhipin.com/wapi/zpjob/job/data/list?position=0&type=0"
    request = urllib.request.Request(f"{query_position_url}", headers=headers)
    try:
        response = urllib.request.urlopen(request)
        result_str: str = response.read().decode()
        if not result_str:
            logger.warning(f"查询职位列表请求结果为空")
        response_content_type = None
        for header_tuple in response.headers._headers:
            if header_tuple[0] == 'Content-Type':
                response_content_type = header_tuple[1]
        if response_content_type == "application/json" or response_content_type == "application/json;charset=UTF-8":
            result_json: dict = json.loads(result_str)
            if result_json.get("code") == 0:
                zp: dict = result_json.get("zpData")
                if zp and zp.get("data"):
                    position_size = len(zp.get("data"))
                    logger.info(f"共获取到【{position_size}】个职位。")
                    for position_detail in zp.get("data"):
                        if position_detail.get("jobName") == position_name:
                            logger.success(f"找到【{position_name}】职位，职位id为【{position_detail.get('encryptJobId')}】")
                            return position_detail.get("encryptJobId")
                    logger.warning(f"职位列表中没有找到【{position_name}】职位")
                else:
                    logger.warning(f"查询职位列表为空。")
            else:
                logger.error(f"查询职位列表失败，错误码：{result_json.get('code')}，错误信息：{result_json.get('message')}")
                logger.debug(f"查询职位列表失败，查询返回的json：{result_json}")
        else:
            logger.warning(f"查询职位列表的结果为【{response_content_type}】类型。")
            logger.error(f"查询职位列表失败，可能出现人机验证，请到网页进行验证。")
            logger.debug(f"查询职位列表，查询返回结果如下：\n{result_str}")
    except URLError as e:
        logger.error(f"查询职位列表，发生URLError异常，一般重试即可。")
        logger.error(e)
    except OSError as e:
        logger.error(f"查询职位列表，发生OSError异常")
        logger.error(e)
    except Exception as e:
        logger.error(f"查询职位列表，发生未知异常")
        logger.error(e)


def query_resume():
    headers = dict()
    headers["Cookie"] = _cookie  # 必须，否则会报'{"code":7,"message":"当前登录状态已失效","zpData":{}}'
    headers["User-Agent"] = _user_agent  # 非必须
    # 搜索条件
    age = "16,30"  # 年龄：16-30岁
    gender = "0"  # 性别：0不限
    exchangeResume = "0"  # 是否与同事交换简历：0不限
    switchJob = "0"  # 跳槽频率：0不限
    activation = "2505"  # 活跃度：2505本月活跃
    recentNotView = "2301"  # 近期没有看过：2301近14天没有
    school = "0"  # 学校：
    major = "0"  # 专业：0不限
    experience = "104,105,106,103"  # 工作经验：0不限
    degree = "203,204,205"  # 学位：
    intention = "701,704,703"  # 求职意向
    salary = "0"  # 薪资待遇：0不限
    query_base_url = "https://www.zhipin.com/wapi/zpjob/rec/geek/list"
    query_url_all = f"{query_base_url}?age={age}&gender={gender}&exchangeResumeWithColleague={exchangeResume}" \
                    f"&switchJobFrequency={switchJob}&activation={activation}&recentNotView={recentNotView}" \
                    f"&school={school}&major={major}&experience={experience}&degree={degree}&salary={salary}" \
                    f"&intention={intention}&jobId={_encryptJobId}"
    sum_resume = 0
    start_greet_count = 0
    for i in range(1, 1 + _page):
        time.sleep(random.randint(3, 10))  # 随机延时3-10秒，防止出现人机验证
        request = urllib.request.Request(f"{query_url_all}&page={i}", headers=headers)
        try:
            response = urllib.request.urlopen(request)
            result_str: str = response.read().decode()
            if not result_str:
                logger.warning(f"查询第【{i}】页的结果为空")
                break
            response_content_type = None
            for header_tuple in response.headers._headers:
                if header_tuple[0] == 'Content-Type':
                    response_content_type = header_tuple[1]
            if response_content_type == "application/json" or response_content_type == "application/json;charset=UTF-8":
                result_json: dict = json.loads(result_str)
                if result_json.get("code") == 0:
                    zp: dict = result_json.get("zpData")
                    if zp and zp.get("geekList"):
                        current_page_size = len(zp.get("geekList"))
                        logger.info(f"当前第【{i}】页，本页共获取到【{current_page_size}】份简历。")
                        if current_page_size != 15:
                            logger.warning(f"当前第【{i}】页，本页共获取到简历数不足15份，请注意，本页获取到【{current_page_size}】份简历。")
                        sum_resume += current_page_size
                        for geek in zp.get("geekList"):
                            if find_relevant_talent(geek):
                                start_greet_count += 1
                        if i % 2 == 0:
                            logger.success(f"已处理【{sum_resume}】份简历，已向【{start_greet_count}】位应聘者打招呼。")
                    else:
                        logger.warning(f"当前第【{i}】页，本页没有获取到简历。")
                        break
                    if not zp.get("hasMore"):
                        logger.warning(f"当前第【{i}】页，没有更多的简历了。")
                        break
                else:
                    logger.error(f"当前第【{i}】页，错误码：{result_json.get('code')}，错误信息：{result_json.get('message')}")
                    logger.debug(f"当前第【{i}】页，查询返回的json：{result_json}")
                    break
            else:
                logger.warning(f"当前第【{i}】页，查询信息返回的结果为【{response_content_type}】类型。")
                logger.error(f"当前第【{i}】页，可能出现人机验证，请到网页进行验证。")
                logger.debug(f"当前第【{i}】页，查询返回结果如下：\n{result_str}")
                break
        except URLError as e:
            logger.error(f"当前第【{i}】页，发生URLError异常，一般重试即可。")
            logger.error(e)
            continue
        except OSError as e:
            logger.error(f"当前第【{i}】页，发生OSError异常")
            logger.error(e)
            break
        except Exception as e:
            logger.error(f"当前第【{i}】页，发生未知异常")
            logger.error(e)
            break
    logger.success(f"共处理【{sum_resume}】份简历，共向【{start_greet_count}】位应聘者打招呼。")


if __name__ == '__main__':
    _wt2 = "DM5llbLG63r3iE9pPJqtR7o1t8Tt_MJS4ZEVxMSLSiV6OQcpONWhNs-zl8_pe8HSM9n8zZzXNnrp2Onp1lTdvcw~~"
    _cookie = f"wt2={_wt2}"
    _encryptJobId = query_position("web前端开发工程师")  # 要匹配的职位，精确匹配
    _position_match = "前端"  # 要匹配的职位
    _page = 30  # 查询的页数，每页15条应聘者数据，网页上一次最多只给查30页的数据，不支持30页以上的参数
    _school_check = True  # 是否匹配教育经历，默认匹配
    _log_level = "INFO"  # 日志等级，默认INFO，可选DEBUG，SUCCESS，ERROR，WARNING等
    logger.remove()
    logger.add(sys.stderr, level=_log_level)
    try:
        if _school_check:
            _school_list = list(
                filter(
                    lambda line: not (line == ""),
                    map(lambda line: line.rstrip("\n"), open("schoolList.txt", encoding="utf-8").readlines()),
                )
            )
        else:
            _school_list = list()
        query_resume()
    except FileNotFoundError:
        logger.error(f"没有找到schoolList.txt文件，请新建该文件并写入院校名单信息")
