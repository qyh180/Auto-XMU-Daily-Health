from email.utils import formataddr
from selenium import webdriver
import time
import smtplib
import sys
from email.mime.text import MIMEText

result = []
with open('acount.txt', 'r', encoding='utf-8') as f:
    for line in f:
        result.extend(list(line.strip('\n').split(',')))

acount = result[0][7:]
pwd = result[1][4:]
receivers = result[2][6:].split(',')


def sendemail(receivers, subject, content):
    # 163邮箱服务器地址
    mail_host = 'smtp.163.com'
    # 163用户名
    mail_user = 'xxxxxx'
    # 密码(部分邮箱为授权码)
    mail_pass = 'XXX'  # 此时隐去密码，可以替换成自己的授权密码
    # 邮件发送方邮箱地址
    sender = 'xxxx@163.COM'
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发

    print(content)
    # 邮件内容设置
    message = MIMEText(content, 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = subject
    # 发送方信息
    message['From'] = formataddr(['小助手', sender])
    # 接受方信息
    message['To'] = receivers[0]
    # 登录并发送邮件
    smtpObj = smtplib.SMTP()
    # 连接到服务器
    smtpObj.connect(mail_host, 25)
    # 登录到服务器
    smtpObj.login(mail_user, mail_pass)
    # 发送
    smtpObj.sendmail(
        sender, receivers, message.as_string())
    # 退出
    smtpObj.quit()


def Sigin_Daily_Health_Report(acount, pwd):
    print('正在启动中啦，请稍等会自动关闭')
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=option, executable_path='chromedriver.exe')
    driver.maximize_window()
    try:
        driver.get('https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu')
        driver.implicitly_wait(5)

        driver.find_element_by_id('username').clear()
        driver.find_element_by_id('username').send_keys(acount)

        driver.find_element_by_id('password').clear()
        driver.find_element_by_id('password').send_keys(pwd)
        # 登录这个按钮很奇怪，它的xpath里的数字会在4和5来回变化，所以用try结构
        try:
            driver.find_element_by_xpath('//*[@id="casLoginForm"]/p[5]/button').click()
        except:
            driver.find_element_by_xpath('//*[@id="casLoginForm"]/p[4]/button').click()
        # 点击Daily Health Report
        driver.find_element_by_xpath(
            '//*[@id="mainPage-page"]/div[1]/div[3]/div[2]/div[2]/div[3]/div/div[1]/div[2]/div[1]').click()
        time.sleep(1)

        # 会新弹出打卡页面，但是程序不知道，所以要切换页面标签，使程序切换到新弹出的打卡页面操作
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        # 然后在打卡页面点击我的表单
        driver.find_element_by_xpath('//*[@id="mainM"]/div/div/div/div[1]/div[2]/div/div[3]/div[2]').click()
        time.sleep(2)
        # 查询打卡状态，如果是“请选择”则还未打卡 如果是 “是yes”则已经打卡
        state = driver.find_element_by_xpath('//*[@id="select_1582538939790"]/div/div/span[1]').text
        if state == '请选择':
            # 点击下拉框
            driver.find_element_by_xpath('//*[@id="select_1582538939790"]/div/div').click()
            # 点击 是（yes）
            driver.find_element_by_xpath('/html/body/div[8]/ul/div/div[3]/li/label').click()
            time.sleep(0.5)
            # 点击保存
            driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[2]/div[1]/div/div/span/span').click()
            time.sleep(0.5)
            # 网页会弹出一个警告框alert 要使程序点确定，用switch_to.alert定位警告框，accept点确定
            driver.switch_to.alert.accept()

            time.sleep(0.5)
            print('打卡已成功')
        else:
            print('打卡已成功')

        driver.get('https://xmuxg.xmu.edu.cn/schoolcustom/demo')
        How_Many_day = driver.find_element_by_xpath('//*[@id="clockDay"]').text
        driver.quit()
        content = '打卡成功！我{}啦'.format(How_Many_day)
        sendemail(receivers=receivers, subject='打卡成功', content=content)
        print(content)
    except Exception as e:
        content = '失败原因：{}'.format(str(e))
        # sendemail(receivers=receivers, subject='打卡失败', content=content)
        print('打卡失败')
        print(content)
        driver.quit()


if __name__ == '__main__':
    Sigin_Daily_Health_Report(acount, pwd)
