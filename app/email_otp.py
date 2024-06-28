from email.message import EmailMessage
import ssl
import smtplib

def send_otp(to, otp):
    try:
        # Initialising Email Object
        emailObj = EmailMessage()
        emailObj["From"] = "aadityajain010203@gmail.com"
        emailObj["To"] = to
        emailObj["Subject"] = "OTP Verification for Registration at Blogify"
        emailObj.add_alternative(f"<h3>Here is your OTP for Blogify</h3><h2 style='margin-left : 50px;'>{otp}</h2>", subtype="html")

        # SSL Certificate
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as smtp:
            smtp.login("aadityajain010203@gmail.com", "your password here")
            smtp.send_message(emailObj)

        return True

    except:
        return False
    

if __name__ == "__main__":
    print(send_otp("aadityajain0128@gmail.com", 3412))