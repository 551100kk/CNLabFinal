import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_verification_code(code, target_addr):
    username = 'cnlab2018test'
    password = 'cnlabtest'
    content = "Your verification code is " + str(code)
    mail_subject = '[CNLab] Verification Code'
    mail_from = 'CNLab Server'
    mail_to = 'CNLab Client'


    sender = username + '@gmail.com'
    receivers = [target_addr]

    try:
        smtp = smtplib.SMTP("smtp.gmail.com:587") 
        smtp.ehlo()
        smtp.starttls()
        smtp.login(username, password)
        msg = MIMEText(content)
        msg['Subject'] = Header(mail_subject, 'utf-8')
        msg['From'] = Header(mail_from, 'utf-8')
        msg['To'] = Header(mail_to, 'utf-8')
        result = smtp.sendmail(sender, receivers, msg.as_string())
        print ("Successed")
        smtp.quit()
        return 0
    except smtplib.SMTPException:
        print ("Error: can not send the email")
        return -1
