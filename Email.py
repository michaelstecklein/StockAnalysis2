import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import Database


def send_update_email(message):
	fromaddr = "bgrogh@gmail.com"
	toaddr = "michaelstecklein@yahoo.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Stock Analysis 2 Update, {}".format(Database.get_last_market_date())
	body = "{}".format(message)
	msg.attach(MIMEText(body, 'plain'))
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "robert123abc")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()