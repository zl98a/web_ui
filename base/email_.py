import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

my_sender = '937986869@qq.com'  # 发件人邮箱账号
my_pass = 'fhpshlpdlekvbefb'  # 发件人邮箱密码
my_user = ['937986869@qq.com', '1104350553@qq.com']  # 收件人邮箱账号，我这边发送给自己。可以添加多个账号


# '7357146@qq.com'
# '1104350553@qq.com'

def mail(filepath='', log='', outputFolder='', phone='', app='', ver='', app_type_=''):
    ret = True
    try:
        message = MIMEMultipart()
        message['From'] = Header("自动化测试报告", 'utf-8')
        message['To'] = Header("937986869@qq.com", 'utf-8')

        message['Subject'] = Header("%s自动化测试报告" % (app), 'utf-8')
        if app_type_ == 'app':
            text_content = MIMEText("UI测试报告APP版本:%s,手机机型：%s" % (ver, phone))
        else:
            text_content = MIMEText('测试报告已完成，请下载附件查看。')
        message.attach(text_content)
        # 附件报告
        if filepath:
            annex = MIMEApplication(open(filepath, 'rb').read())
            filename = str(filepath).split('/')[-1].split('.')[0] + '.html'
            annex.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(annex)
        # 附件日志
        if log:
            logfile = MIMEApplication(open(log, 'rb').read())
            logfile.add_header('Content-Disposition', 'attachment', filename="测试日志.log")
            message.attach(logfile)

        # 附件为压缩文件
        # if outputFolder:
        #     for filename in os.listdir(outputFolder):
        #         part = MIMEBase('application', "octet-stream")
        #         with open(os.path.join(outputFolder, filename)) as f:
        #             part.set_payload(f.read())
        #             encoders.encode_base64(part)
        #             part.add_header('Content-Disposition', 'attachment',filename=os.path.basename(filename))
        #             message.attach(part)
        if outputFolder:
            output = MIMEApplication(open(outputFolder, 'rb').read())

            output.add_header('Content-Disposition', 'attachment', filename='Api测试报告附件.tar')
            message.attach(output)

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(my_sender, my_pass)
        server.sendmail(my_sender, my_user, message.as_string())
        server.quit()
    except Exception as e:
        print(e)
        ret = False
    else:
        print('发送邮件成功。')
        return ret

# ret=mail(filepath="D:\\auto-test.sh\\test_result\\test_report\\我的页面.html",phone='redmi',ver='1.14')
# if ret:
#     print('发送成功')
# else:
#     print('发送失败')




