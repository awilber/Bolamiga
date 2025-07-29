#!/bin/bash

# AWS Deployment Script for Bolamiga
# This script sets up an EC2 instance and deploys the retro space shooter game

set -e

# Configuration
APP_NAME="bolamiga"
INSTANCE_TYPE="t3.micro"
KEY_NAME="bolamiga-key"
SECURITY_GROUP="bolamiga-sg"
AMI_ID="ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS
REGION="us-east-1"

echo "🎮 Starting AWS deployment for Bolamiga..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Create key pair if it doesn't exist
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION > /dev/null 2>&1; then
    echo "📄 Creating EC2 key pair..."
    aws ec2 create-key-pair --key-name $KEY_NAME --region $REGION --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Key pair created: ${KEY_NAME}.pem"
fi

# Create security group if it doesn't exist
if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP --region $REGION > /dev/null 2>&1; then
    echo "🔒 Creating security group..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP \
        --description "Security group for Bolamiga game server" \
        --region $REGION \
        --query 'GroupId' --output text)
    
    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 22 --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 80 --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 5030 --cidr 0.0.0.0/0 \
        --region $REGION
    
    echo "✅ Security group created: $SECURITY_GROUP_ID"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' --output text)
fi

# Create user data script
cat > user-data.sh << 'EOF'
#!/bin/bash
apt-get update
apt-get install -y python3 python3-pip git curl nginx

# Start and enable nginx
systemctl start nginx
systemctl enable nginx

# Clone repository
cd /home/ubuntu
git clone https://github.com/awilber/Bolamiga.git
cd Bolamiga

# Install Python dependencies
pip3 install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/bolamiga.service << 'SVCEOF'
[Unit]
Description=Bolamiga Retro Space Shooter
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Bolamiga
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF

# Create nginx configuration
cat > /etc/nginx/sites-available/bolamiga << 'NGINXEOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5030;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/bolamiga /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl reload nginx

# Start Bolamiga service
systemctl daemon-reload
systemctl enable bolamiga
systemctl start bolamiga

# Set ownership
chown -R ubuntu:ubuntu /home/ubuntu/Bolamiga
EOF

# Launch EC2 instance
echo "🚀 Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --user-data file://user-data.sh \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$APP_NAME},{Key=Project,Value=Bolamiga}]" \
    --query 'Instances[0].InstanceId' --output text)

echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo ""
echo "🎉 Deployment completed!"
echo "📋 Instance Details:"
echo "   Instance ID: $INSTANCE_ID"
echo "   Public IP: $PUBLIC_IP"
echo "   SSH Access: ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo ""
echo "🎮 Bolamiga Game URLs:"
echo "   Production: http://$PUBLIC_IP"
echo "   Direct:     http://$PUBLIC_IP:5030"
echo ""
echo "⏰ Note: It may take 5-10 minutes for the application to be fully ready."
echo "💡 Monitor deployment: ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo journalctl -u bolamiga -f'"

# Clean up
rm user-data.sh

echo ""
echo "🔧 Next steps:"
echo "1. Test the game at http://$PUBLIC_IP"
echo "2. Configure your domain name to point to $PUBLIC_IP"
echo "3. Set up SSL certificates if needed"
echo "4. Monitor with systemctl status bolamiga"