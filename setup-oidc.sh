#!/bin/bash

# AWS OIDC Setup for Bolamiga GitHub Actions
# This script sets up secure OIDC authentication between GitHub Actions and AWS

set -e

AWS_ACCOUNT_ID="437878371059"
GITHUB_REPO="awilber/Bolamiga"
ROLE_NAME="GitHubActions-Bolamiga-Role"

echo "🔐 Setting up AWS OIDC for Bolamiga deployment..."

# Step 1: Create OIDC Identity Provider (if not exists)
echo "📋 Creating GitHub Actions OIDC Identity Provider..."
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --client-id-list sts.amazonaws.com 2>/dev/null || echo "✅ OIDC Provider already exists"

# Step 2: Create Trust Policy
echo "🔒 Creating trust policy for GitHub Actions..."
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_REPO}:*"
        }
      }
    }
  ]
}
EOF

# Step 3: Create IAM Role
echo "👤 Creating IAM role for GitHub Actions..."
aws iam create-role \
  --role-name ${ROLE_NAME} \
  --assume-role-policy-document file://trust-policy.json \
  --description "Role for GitHub Actions to deploy Bolamiga" 2>/dev/null || echo "✅ Role already exists"

# Step 4: Create Deployment Policy
echo "📜 Creating deployment permissions policy..."
cat > deployment-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "s3:*",
        "iam:PassRole",
        "iam:ListInstanceProfiles",
        "iam:CreateServiceLinkedRole"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow", 
      "Action": [
        "sts:TagSession"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Step 5: Attach Policy to Role
echo "🔗 Attaching deployment policy to role..."
aws iam put-role-policy \
  --role-name ${ROLE_NAME} \
  --policy-name BolamigaDeploymentPolicy \
  --policy-document file://deployment-policy.json

# Step 6: Get Role ARN
ROLE_ARN=$(aws iam get-role --role-name ${ROLE_NAME} --query 'Role.Arn' --output text)

echo ""
echo "✅ OIDC Setup Complete!"
echo "📋 Configuration Details:"
echo "   Role ARN: ${ROLE_ARN}"
echo "   GitHub Repo: ${GITHUB_REPO}"
echo "   AWS Account: ${AWS_ACCOUNT_ID}"
echo ""
echo "🔧 Next Steps:"
echo "1. Add this Role ARN as a GitHub secret:"
echo "   gh secret set AWS_ROLE_ARN --body '${ROLE_ARN}'"
echo ""
echo "2. Test the deployment pipeline"
echo ""

# Cleanup
rm -f trust-policy.json deployment-policy.json

echo "🎉 Ready for secure OIDC deployments!"