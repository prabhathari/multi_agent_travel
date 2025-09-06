# 🧭 Multi-Agent AI Travel Planner

An intelligent travel planning application that uses multiple AI agents to create personalized trip itineraries. Built with FastAPI, Streamlit, and powered by LLMs (Groq/Gemini).

## 🌟 Features

- **Multi-Agent System**: Four specialized AI agents collaborate to plan your trip
  - 📍 **Destination Expert**: Suggests or validates destinations based on preferences
  - 🗓️ **Itinerary Planner**: Creates detailed day-by-day itineraries
  - 💰 **Budget Analyst**: Estimates costs and keeps trips within budget
  - 🛡️ **Safety Advisor**: Provides safety tips, visa requirements, and travel advisories
- **Custom Destinations**: Specify your dream destination or let AI suggest
- **Budget-Aware Planning**: Respects your budget constraints
- **Interest-Based Recommendations**: Tailors trips to your interests
- **Production Ready**: Dockerized with nginx reverse proxy and security features

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- API Key (free) from Groq or Google Gemini

### Getting API Keys (FREE)

#### Option 1: Groq (Recommended - Fastest)
1. Visit https://console.groq.com/keys
2. Sign up for free account (no credit card required)
3. Click "Create API Key"
4. Copy your key (starts with `gsk_`)
5. **Free Tier**: 30 requests/minute, 14,400 requests/day

#### Option 2: Google Gemini
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy your key
5. **Free Tier**: 60 requests/minute

### 🐳 Docker Setup (Easiest)

1. **Clone the repository**
```bash
git clone https://github.com/prabhathari/multi_agent_travel.git
cd multi_agent_travel

Create environment file

bash# Create .env file with your API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "GROQ_MODEL=llama-3.3-70b-versatile" >> .env
echo "LLM_PROVIDER=groq" >> .env

Start with Docker Compose

bash# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

Access the application


🌐 Main App: http://localhost
📚 API Docs: http://localhost/docs
🔍 Health Check: http://localhost/health
```
🚢 Production Deployment on Cloud (GCP/AWS/Azure)
Complete Production Setup Script
Save this script as setup_production.sh on your VM:
```bash
bash#!/bin/bash
# setup_production.sh - Complete automated production deployment

set -e

echo "================================================"
echo "🚀 MULTI-AGENT TRAVEL PLANNER - PRODUCTION SETUP"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get configuration
echo -e "${YELLOW}Enter your configuration:${NC}"
read -p "GROQ API Key: " GROQ_API_KEY
read -p "Gemini API Key (optional, press Enter to skip): " GEMINI_API_KEY
read -p "Your email (for SSL later): " EMAIL
read -p "Your domain (optional, press Enter to skip): " DOMAIN

# STEP 1: System updates and security tools
echo -e "${GREEN}[1/10] Updating system and installing security tools...${NC}"
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
    curl \
    git \
    ufw \
    fail2ban \
    unattended-upgrades \
    htop

# STEP 2: Install Docker
echo -e "${GREEN}[2/10] Installing Docker...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Configure Docker with security options
sudo tee /etc/docker/daemon.json > /dev/null <<DOCKERCONFIG
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "live-restore": true,
  "userland-proxy": false
}
DOCKERCONFIG
sudo systemctl restart docker

# STEP 3: Install Docker Compose
echo -e "${GREEN}[3/10] Installing Docker Compose...${NC}"
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# STEP 4: Configure Firewall
echo -e "${GREEN}[4/10] Configuring firewall...${NC}"
sudo ufw --force disable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# STEP 5: Configure fail2ban
echo -e "${GREEN}[5/10] Setting up fail2ban for SSH protection...${NC}"
sudo tee /etc/fail2ban/jail.local > /dev/null <<FAIL2BAN
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
FAIL2BAN
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# STEP 6: Clone repository
echo -e "${GREEN}[6/10] Cloning repository...${NC}"
sudo mkdir -p /opt/multi_agent_travel
sudo chown -R $USER:$USER /opt/multi_agent_travel
cd /opt/multi_agent_travel

if [ -d ".git" ]; then
    echo "Repository exists, pulling latest..."
    git pull
else
    git clone https://github.com/prabhathari/multi_agent_travel.git .
fi

# STEP 7: Create production environment file
echo -e "${GREEN}[7/10] Creating production environment...${NC}"
cat > .env.prod <<ENVFILE
# API Keys
GROQ_API_KEY=$GROQ_API_KEY
GEMINI_API_KEY=$GEMINI_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile

# Application Settings
LLM_PROVIDER=groq
MODEL_TEMPERATURE=0.7
MAX_TOKENS=1000

# Security Settings
ALLOWED_HOSTS=${DOMAIN:-localhost},$(curl -s ifconfig.me)
ALLOWED_ORIGINS=http://${DOMAIN:-localhost},http://$(curl -s ifconfig.me)
DEBUG=false

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
ENVFILE

# STEP 8: Build and start with Docker Compose
echo -e "${GREEN}[8/10] Building and starting application...${NC}"
# Apply docker group and run
newgrp docker << DOCKERCMDS
cd /opt/multi_agent_travel
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up -d --build
DOCKERCMDS

# Alternative if newgrp doesn't work
if [ $? -ne 0 ]; then
    sudo docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    sudo docker-compose -f docker-compose.prod.yml up -d --build
fi

# STEP 9: Set up automatic updates
echo -e "${GREEN}[9/10] Configuring automatic security updates...${NC}"
sudo dpkg-reconfigure -plow unattended-upgrades

# Create systemd service for auto-start
sudo tee /etc/systemd/system/multi-agent-travel.service > /dev/null <<SYSTEMD
[Unit]
Description=Multi Agent Travel Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/multi_agent_travel
ExecStart=/usr/local/bin/docker-compose -f /opt/multi_agent_travel/docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f /opt/multi_agent_travel/docker-compose.prod.yml down
Restart=on-failure
User=$USER

[Install]
WantedBy=multi-user.target
SYSTEMD

sudo systemctl daemon-reload
sudo systemctl enable multi-agent-travel

# STEP 10: Create helper scripts
echo -e "${GREEN}[10/10] Creating management scripts...${NC}"

cat > /opt/multi_agent_travel/status.sh <<'STATUSSCRIPT'
#!/bin/bash
echo "=== Docker Status ==="
docker ps
echo ""
echo "=== Application Health ==="
curl -s http://localhost/health || echo "Backend not responding"
echo ""
echo "=== Resource Usage ==="
docker stats --no-stream
STATUSSCRIPT
chmod +x /opt/multi_agent_travel/status.sh

cat > /opt/multi_agent_travel/logs.sh <<'LOGSSCRIPT'
#!/bin/bash
docker-compose -f /opt/multi_agent_travel/docker-compose.prod.yml logs -f --tail=100
LOGSSCRIPT
chmod +x /opt/multi_agent_travel/logs.sh

cat > /opt/multi_agent_travel/update.sh <<'UPDATESCRIPT'
#!/bin/bash
cd /opt/multi_agent_travel
git pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
UPDATESCRIPT
chmod +x /opt/multi_agent_travel/update.sh

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me)

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start (30 seconds)...${NC}"
sleep 30

# Final output
echo ""
echo "================================================"
echo -e "${GREEN}✅ PRODUCTION DEPLOYMENT COMPLETE!${NC}"
echo "================================================"
echo ""
echo -e "${GREEN}Your application is running at:${NC}"
echo -e "  🌐 http://$EXTERNAL_IP"
echo ""
echo "Test endpoints:"
echo "  Main App:  http://$EXTERNAL_IP"
echo "  API Health: http://$EXTERNAL_IP/health"
echo ""
echo "Management commands:"
echo "  📊 Status:  /opt/multi_agent_travel/status.sh"
echo "  📝 Logs:    /opt/multi_agent_travel/logs.sh"
echo "  🔄 Update:  /opt/multi_agent_travel/update.sh"
echo ""
echo -e "${RED}IMPORTANT: Save your server IP: $EXTERNAL_IP${NC}"
echo "================================================"
```

How to Deploy to Production

Create Ubuntu VM (GCP, AWS, or Azure)

Ubuntu 22.04 LTS
2 vCPU, 4GB RAM minimum
30GB disk
Allow HTTP/HTTPS traffic


SSH into your VM and run setup

bash# Download the setup script
curl -o setup.sh https://raw.githubusercontent.com/prabhathari/multi_agent_travel/main/setup_production.sh

# Or create it manually
nano setup.sh
# Paste the script content above

# Make executable and run
chmod +x setup.sh
./setup.sh

Enter configuration when prompted

GROQ API Key (required)
Gemini API Key (optional)
Your email (for SSL)
Domain (optional)



The script automatically handles:

Docker & Docker Compose installation
Firewall configuration
Security hardening
Repository cloning
Service startup
Auto-restart on reboot
Log rotation
```bash
📁 Project Structure
multi_agent_travel/
├── app/
│   ├── agents/              # AI agent implementations
│   │   ├── base_agent.py
│   │   ├── destination_agent.py
│   │   ├── itinerary_agent.py
│   │   ├── budget_agent.py
│   │   └── safety_agent.py
│   ├── llm/                 # LLM integrations
│   │   ├── base_llm.py
│   │   ├── groq_llm.py
│   │   └── __init__.py
│   ├── main.py             # FastAPI application
│   └── config.py           # Configuration
├── streamlit_app.py        # Streamlit frontend
├── requirements.txt        # Python dependencies
├── Dockerfile             # Development Docker
├── Dockerfile.prod        # Production Docker
├── docker-compose.yml     # Development compose
├── docker-compose.prod.yml # Production compose
├── nginx.conf             # Development nginx
├── nginx.prod.conf        # Production nginx
└── README.md              # This file
```

🔧 Configuration
```bash
Environment Variables
VariableDescriptionDefaultRequiredGROQ_API_KEYYour Groq API key-YesGEMINI_API_KEYGoogle Gemini API key-OptionalLLM_PROVIDERWhich LLM to usegroqNoGROQ_MODELModel namellama-3.3-70b-versatileNoMODEL_TEMPERATURELLM creativity (0-1)0.7NoMAX_TOKENSMax response length1000No
🐳 Docker Commands Reference
bash# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart
docker-compose restart

# Production commands
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml down
```

# Update and rebuild
```bash
git pull
docker-compose down
docker-compose up --build -d
```

📚 API Documentation
```bash
POST /plan
Generate a travel plan.
Request:
json{
  "traveler_name": "John Doe",
  "origin_city": "New York",
  "preferred_destination": "Tokyo",
  "days": 7,
  "month": "June",
  "budget_total": 3000,
  "interests": ["culture", "food", "technology"],
  "visa_passport": "US"
}
```
```bash
🔍 Troubleshooting
Check if services are running
bashdocker ps
docker-compose logs backend
API key issues
bash# Verify environment variables
docker exec travel-backend env | grep GROQ
Restart everything
bashdocker-compose down
docker-compose up --build -d
```

🤝 Contributing
```bash

Fork the repository
Create feature branch
Commit changes
Push to branch
Open Pull Request
```

📄 License
```bash
MIT License - feel free to use this project for any purpose.
🙏 Acknowledgments

Powered by Groq and Google Gemini
Built with FastAPI and Streamlit
```
```bash
EOF
echo "✅ README.md with setup script created successfully!"
echo ""
echo "📝 To push to GitHub:"
echo "git add README.md"
echo "git commit -m 'Add comprehensive README with production setup script'"
echo "git push origin main"
```
This README includes:
1. The complete production setup script inline
2. Step-by-step instructions for using the script
3. All Docker commands
4. API key setup instructions
5. Troubleshooting guide
6. Everything someone needs to deploy your app

The setup script is embedded in the README so users can copy it directly from there!
