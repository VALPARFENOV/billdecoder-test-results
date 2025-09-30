#!/bin/bash

# 🚀 Quick Firebase Deploy Script for BillDecoder Presentation

echo "🔥 Deploying BillDecoder presentation to Firebase..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Check if user is logged in
if ! firebase projects:list &> /dev/null; then
    echo "🔐 Please login to Firebase:"
    firebase login
fi

# Initialize Firebase project if not already done
if [ ! -f "firebase.json" ]; then
    echo "⚙️  Initializing Firebase project..."
    firebase init hosting --project default
fi

# Deploy to Firebase
echo "🚀 Deploying to Firebase..."
firebase deploy

echo "✅ Deployment complete!"
echo "🌐 Your presentation is now live!"
echo "📧 Share the URL with your colleagues!"
