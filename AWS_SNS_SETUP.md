# AWS SNS SMS Setup Guide

## Quick Start (Easiest Method)

### Option 1: Use .env file (Recommended)
1. Copy `.env.example` to `.env`
2. Fill in your AWS credentials in `.env`:
   ```
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=your_secret_key
   ```
3. Restart your app

### Option 2: Use AWS CLI (Secure)
1. Run: `aws configure`
2. Enter your AWS Access Key ID and Secret Access Key
3. The app will automatically use these credentials

### Option 3: Environment Variables
Set these in your system environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (optional, defaults to us-east-1)

## Step-by-Step AWS Setup

## Step 1: Create AWS Account
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Complete the registration process

## Step 2: Create IAM User
1. Go to AWS IAM Console: https://console.aws.amazon.com/iam/
2. Click "Users" → "Add users"
3. Enter username (e.g., "health-monitor-sms")
4. Select "Access key - Programmatic access"
5. Click "Next: Permissions"

## Step 3: Set Permissions
1. Click "Attach existing policies directly"
2. Search for and select: `AmazonSNSFullAccess`
3. Click "Next: Tags" → "Next: Review" → "Create user"

## Step 4: Get Access Keys
1. After user creation, download the CSV file with Access Key ID and Secret Access Key
2. **Important:** Save these keys securely - you can't download them again!

## Step 5: Configure Credentials

### Method A: .env file (Easiest)
```bash
cp .env.example .env
# Edit .env with your keys
```

### Method B: AWS CLI
```bash
aws configure
# Enter your keys when prompted
```

### Method C: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Step 6: Test SMS
1. Run your app
2. Add abnormal health readings
3. When prompted for doctor's number, enter a valid mobile number
4. SMS should be sent via AWS SNS

## Free Tier Limits
- **100 SMS/month** free
- Additional SMS: ~$0.0065 per SMS
- Works in 200+ countries

## Important Notes
- **No Incoming SMS**: AWS SNS cannot receive SMS replies like Twilio
- **Doctor Replies**: Doctors cannot reply directly to SMS. They would need to contact via phone/email
- **Two-way SMS**: If you need doctor replies, consider using Twilio or other services

## Troubleshooting
- **Region Issues**: Try different AWS regions (us-east-1, us-west-2, eu-west-1)
- **Permissions**: Ensure SNS permissions are granted
- **Phone Format**: Must be in international format (+91XXXXXXXXXX)
- **Credentials**: Make sure credentials are correct and not expired