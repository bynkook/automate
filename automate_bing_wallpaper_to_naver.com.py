import requests
import json
import datetime
import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def download_bing_wallpaper():
	"""Download today's Bing wallpaper"""
	# Bing's wallpaper API endpoint
	api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
	try:
		# Get wallpaper metadata
		response = requests.get(api_url)
		image_data = json.loads(response.text)
		# Extract image URL
		image_url = image_data["images"][0]["url"]
		image_url = image_url.split("&")[0]	 # Remove extra parameters
		full_image_url = "https://www.bing.com" + image_url
		# Generate filename with today's date
		today = datetime.date.today().strftime("%Y%m%d")
		image_extension = image_url.split(".")[-1]
		filename = f"bing_wallpaper_{today}.{image_extension}"
		# Download the image
		img_response = requests.get(full_image_url)
		with open(filename, 'wb') as handler:
			handler.write(img_response.content)
		print(f"Wallpaper downloaded: {filename}")
		return filename, image_data["images"][0]["copyright"]
	except Exception as e:
		print(f"Error downloading wallpaper: {e}")
		return None, None
def send_email_with_attachment(filename, image_description, sender_email, sender_password, recipient_email):
	"""Send email with wallpaper attachment via Naver SMTP with SSL"""
	# Updated Naver SMTP configuration with SSL
	smtp_server = "smtp.naver.com"
	smtp_port = 465	 # SSL port for Naver
	try:
		# Create message
		msg = MIMEMultipart()
		msg['From'] = sender_email
		msg['To'] = recipient_email
		msg['Subject'] = f"Bing Daily Wallpaper - {datetime.date.today().strftime('%Y-%m-%d')}"
		# Email body
		body = f"""
		Today's Bing Wallpaper
		Description: {image_description}
		Date: {datetime.date.today().strftime('%Y-%m-%d')}
		Enjoy your daily wallpaper!
		"""
		msg.attach(MIMEText(body, 'plain'))
		# Attach the image file
		with open(filename, "rb") as attachment:
			part = MIMEBase('application', 'octet-stream')
			part.set_payload(attachment.read())
		encoders.encode_base64(part)
		part.add_header(
			'Content-Disposition',
			f'attachment; filename= {filename}'
		)
		msg.attach(part)
		# Create SSL context for secure connection
		context = ssl.create_default_context()
		# Send email using SSL (not STARTTLS)
		server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
		server.login(sender_email, sender_password)
		server.sendmail(sender_email, recipient_email, msg.as_string())
		server.quit()
		print("Email sent successfully!")
	except Exception as e:
		print(f"Error sending email: {e}")

def main():
	"""Main function to download wallpaper and send email"""
	# Configuration - Replace with your actual email credentials
	SENDER_EMAIL = "your_email@naver.com"
	SENDER_PASSWORD = "your_email_password"	 # Use app password if 2FA is enabled
	RECIPIENT_EMAIL = "your_email@server.com"
	# Download wallpaper
	filename, description = download_bing_wallpaper()
	if filename:
		# Send email with attachment
		send_email_with_attachment(
			filename,
			description,
			SENDER_EMAIL,
			SENDER_PASSWORD,
			RECIPIENT_EMAIL
		)
		# Clean up - delete local file after sending
		try:
			os.remove(filename)
			print(f"Local file {filename} deleted")
		except Exception:
			print(f"Could not delete {filename}")
	else:
		print("Failed to download wallpaper")

if __name__ == "__main__":
	main()