import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


def send_email(subject, message):
	fromaddr = "bgrogh@gmail.com"
	toaddr = "michaelstecklein@yahoo.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = subject
	body = "{}".format(message)
	msg.attach(MIMEText(body, 'plain'))
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "robert123abc")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	
def send_errors_email(error_str):
	send_email("Stock Analysis 2, ERROR", error_str)

def send_update_email(date, message):
	send_email("Stock Analysis 2 Update, {}".format(date),message)