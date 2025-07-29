#!/bin/bash

# Bolamiga AWS Deployment Script
echo "🚀 Deploying Bolamiga to AWS..."

# Configuration
APP_NAME="bolamiga"
INSTANCE_NAME="bolamiga-game-server"
KEY_NAME="bolamiga-key"
SECURITY_GROUP="bolamiga-sg"
REGION="us-east-1"

# Create security group if it doesn't exist
echo "Creating security group..."
aws ec2 create-security-group \
    --group-name $SECURITY_GROUP \
    --description "Security group for Bolamiga game server" \
    --region $REGION 2>/dev/null || echo "Security group already exists"

# Add rules to security group
aws ec2 authorize-security-group-ingress \
    --group-name $SECURITY_GROUP \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "SSH rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-name $SECURITY_GROUP \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "Port 5000 rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-name $SECURITY_GROUP \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || echo "HTTP rule already exists"

# Create key pair if it doesn't exist
if [ ! -f "${KEY_NAME}.pem" ]; then
    echo "Creating key pair..."
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
fi

# Launch EC2 instance
echo "Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type t2.micro \
    --key-name $KEY_NAME \
    --security-groups $SECURITY_GROUP \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "Public IP: $PUBLIC_IP"

# Wait a bit more for SSH to be ready
echo "Waiting for SSH to be ready..."
sleep 30

# Create deployment script
cat > deploy_to_instance.sh << 'EOF'
#!/bin/bash
cd /home/ec2-user
sudo yum update -y
sudo yum install -y python3 python3-pip git

# Clone or update application
if [ -d "bolamiga" ]; then
    cd bolamiga
    git pull
else
    git clone https://github.com/awilber/bolamiga.git
    cd bolamiga
fi

# Install dependencies
pip3 install --user -r requirements.txt

# Kill any existing process
pkill -f "python.*app.py" || true

# Start the application
nohup ~/.local/bin/python3 app.py > bolamiga.log 2>&1 &

echo "Bolamiga deployed successfully!"
echo "Access at: http://$PUBLIC_IP:5000"
EOF

# Copy files and deploy
echo "Deploying application..."
scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no deploy_to_instance.sh ec2-user@$PUBLIC_IP:/tmp/
scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no -r . ec2-user@$PUBLIC_IP:/home/ec2-user/bolamiga/

ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP "chmod +x /tmp/deploy_to_instance.sh && /tmp/deploy_to_instance.sh"

echo ""
echo "🎮 Bolamiga Deployment Complete!"
echo "🌐 Game URL: http://$PUBLIC_IP:5000"
echo "🔧 SSH Access: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"

# Clean up
rm deploy_to_instance.sh