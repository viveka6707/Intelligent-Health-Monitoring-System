# Email-to-SMS Setup Guide (Free Alternative to AWS/Twilio)

## Why Email-to-SMS?
- **100% FREE** - No costs for SMS sending
- **No special accounts needed** - Just use your Gmail
- **Works worldwide** - Converts email to SMS automatically
- **No API keys required** - Uses standard email

## Step 1: Set up Gmail App Password

### For Gmail Security
1. Go to your Google Account: https://myaccount.google.com/
2. Click "Security" in left sidebar
3. Under "Signing in to Google", click "App passwords"
4. You might need to sign in again
5. Select "Mail" and "Windows Computer" (or any device)
6. Click "Generate"
7. **Copy the 16-character password** - this is your app password

## Step 2: Configure .env file

Edit the `.env` file in your project folder:

```
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=abcd-efgh-ijkl-mnop  # Your 16-char app password
```

## Step 3: Test the Setup

1. Run your health monitor app
2. Add abnormal health readings
3. When asked for doctor's number, enter: `+91XXXXXXXXXX`
4. The app will send an email that gets converted to SMS

## How It Works

```
Your App → Email (Gmail) → SMS Gateway → Doctor's Phone
```

The email is sent to a special email address that SMS carriers provide, which automatically converts it to SMS.

## SMS Gateway Addresses

Different carriers use different email domains. The app tries common ones:

- **AT&T**: `number@txt.att.net`
- **Verizon**: `number@vtext.com`
- **T-Mobile**: `number@tmomail.net`
- **Sprint**: `number@messaging.sprintpcs.com`

## For Indian Numbers

Indian carriers may use different gateways. If the default doesn't work, you can:

1. **Check with doctor's carrier** which email gateway they use
2. **Use a paid SMS service** like Twilio for reliable delivery
3. **Use WhatsApp API** (requires WhatsApp Business account)

## Troubleshooting

### "Authentication failed"
- Make sure you're using the **app password**, not your regular Gmail password
- Enable "Less secure app access" in Gmail settings (if app password doesn't work)

### SMS not received
- Try different carrier gateways
- Check if the phone number format is correct (+91XXXXXXXXXX)
- Some carriers block email-to-SMS

### Gmail blocks the email
- Add the recipient email to your contacts
- Check spam folder
- Make sure app password is correct

## Alternative: Use Different Email Provider

If Gmail doesn't work, you can use:
- **Outlook**: smtp-mail.outlook.com (port 587)
- **Yahoo**: smtp.mail.yahoo.com (port 587)

Just update the SMTP settings in the code.

## Cost: 100% FREE
- No SMS costs
- No API fees
- No monthly charges
- Only your internet connection

This is the most cost-effective way to send SMS alerts without any paid services!