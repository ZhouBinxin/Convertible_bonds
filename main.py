import csv
import json
import os
import smtplib
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from chinese_calendar import is_workday
from dotenv import load_dotenv

today = datetime.now()
yesterday = today - timedelta(days=1)


def get_data(access_token):
    requestURL = "https://quantapi.51ifind.com/api/v1/data_pool"
    requestHeaders = {"Content-Type": "application/json",
                      "access_token": access_token}

    global yesterday

    formData = {"reportname": "p00868", "functionpara": {"edate": yesterday, "zqlx": "全部"},
                "outputpara": "jydm,jydm_mc,p00868_f002,p00868_f016,p00868_f007,p00868_f006,p00868_f001,p00868_f028,p00868_f011,p00868_f005,p00868_f014,p00868_f008,p00868_f003,p00868_f026,p00868_f023,p00868_f004,p00868_f012,p00868_f017,p00868_f024,p00868_f019,p00868_f027,p00868_f018,p00868_f022,p00868_f021,p00868_f015,p00868_f010,p00868_f025,p00868_f009,p00868_f029,p00868_f013,p00868_f020,p00868_f030"}

    response = requests.post(requestURL, headers=requestHeaders, data=json.dumps(formData))

    if response.status_code == 200:
        data = response.json()
        return data

    else:
        print("An error occurred: {}".format(response.status_code))


def save_to_csv(data):
    desired_data = []
    row = data["tables"][0]["table"]
    jydm = row["jydm"]

    for i in range(len(jydm)):
        row_data = [row["jydm"][i], row["jydm_mc"][i], row["p00868_f002"][i], row["p00868_f016"][i],
                    row["p00868_f007"][i],
                    row["p00868_f006"][i], row["p00868_f001"][i], row["p00868_f028"][i], row["p00868_f011"][i],
                    row["p00868_f005"][i], row["p00868_f014"][i], row["p00868_f008"][i], row["p00868_f003"][i],
                    row["p00868_f026"][i], row["p00868_f023"][i], row["p00868_f004"][i], row["p00868_f012"][i],
                    row["p00868_f017"][i], row["p00868_f024"][i], row["p00868_f019"][i], row["p00868_f027"][i],
                    row["p00868_f018"][i], row["p00868_f022"][i], row["p00868_f021"][i], row["p00868_f015"][i],
                    row["p00868_f010"][i], row["p00868_f025"][i], row["p00868_f009"][i], row["p00868_f029"][i],
                    row["p00868_f013"][i], row["p00868_f020"][i], row["p00868_f030"][i]]

        # 使用null代替--
        row_data = ["null" if val == "--" else val for val in row_data]

        desired_data.append(row_data)

    new_headers = ["代码", "名称", "交易日期", "前收盘价", "开盘价", "最高价", "最低价", "收盘价", "涨跌",
                   "涨跌幅(%)",
                   "已计息天数", "应计利息", "剩余期限(年)", "当期收益率(%)", "纯债到期收益率(%)", "纯债价值",
                   "纯债溢价", "纯债溢价率(%)", "转股价格", "转股比例", "转换价值", "转股溢价", "转股溢价率(%)",
                   "转股市盈率", "转股市净率", "套利空间", "平价/底价", "期限(年)", "发行日期",
                   "票面利率/发行参考利率(%)", "交易市场", "债券类型"]

    global yesterday

    with open(f'{yesterday}.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(new_headers)
        csvwriter.writerows(desired_data)


def get_access_token(refreshToken):
    getAccessTokenUrl = 'https://ft.10jqka.com.cn/api/v1/get_access_token'
    getAccessTokenHeader = {"ContentType": "application/json", "refresh_token": refreshToken}
    getAccessTokenResponse = requests.post(url=getAccessTokenUrl, headers=getAccessTokenHeader)
    response = json.loads(getAccessTokenResponse.content)
    if response['errorcode'] != 0:
        print(response['errmsg'])
        accessToken = None
    else:
        accessToken = json.loads(getAccessTokenResponse.content)['data']['access_token']
    return accessToken


def send_email():
    # 电子邮件配置
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['SENDER_PASSWORD']
    receiver_emails = ['chushankeji@163.com', 'pinhsin@189.cn']

    global yesterday
    github = "https://github.com/ZhouBinxin/Convertible_bonds"
    gitee = "https://gitee.com/pinhsin/Convertible_bonds"
    article_content = f"{yesterday} \n Github:{github} \n Gitee:{gitee}"
    # feedback = f"发送日期：{yesterday} \n 接收邮箱：{receiver_email}"

    # 创建MIMEText对象
    msg = MIMEMultipart()
    msg.attach(MIMEText(article_content, 'plain'))
    # 设置发件人和收件人
    msg['From'] = sender_email
    msg['Subject'] = f'可转债数据 By binxin'

    # # 创建第二封邮件
    # msg2 = MIMEMultipart()
    # msg2.attach(MIMEText(feedback, 'plain'))
    # msg2['From'] = sender_email
    # msg2['To'] = "ths_action@bxin.top"
    # msg2['Subject'] = 'THS'

    # 添加附件
    filename = f"{yesterday}.csv"
    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
    msg.attach(part)

    # 连接到SMTP服务器并发送邮件
    with smtplib.SMTP_SSL('smtp.163.com', 465) as server:
        server.login(sender_email, sender_password)
        for receiver_email in receiver_emails:
            msg['To'] = receiver_email
            server.sendmail(sender_email, receiver_email, msg.as_string())
        # server.sendmail(sender_email, "ths_action@bxin.top", msg2.as_string())


def is_trade_day(date):
    """
    判断是否是交易日

    :param date:
    :return:
    """
    if is_workday(date):
        if date.isoweekday() < 6:
            return True
    return False


def main():
    global yesterday
    if is_trade_day(yesterday):
        yesterday = yesterday.strftime("%Y%m%d")
        # 导入.env
        load_dotenv()
        refreshToken = os.environ['REFRESH_TOKEN']
        access_token = get_access_token(refreshToken)
        if access_token:
            data = get_data(access_token)
            save_to_csv(data)
            # send_email()


if __name__ == '__main__':
    main()
