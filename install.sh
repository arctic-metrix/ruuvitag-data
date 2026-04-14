sudo apt install git python3-venv python3-pip nginx gunicorn supervisor -y
cd /home/${USER}
git clone https://github.com/arctic-metrix/ruuvitag-data.git
cd ruuvitag-data
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt

read -p "Enter MAC-address: " MAC_ADDRESS

sudo systemctl enable supervisor
# Removed quotes from EOF so ${USER} and ${MAC_ADDRESS} expand correctly
# Changed filename to main.py.conf to avoid overwriting
# Fixed hardcoded 'arctic-metrix' path to use ${USER}
cat << EOF | sudo tee /etc/supervisor/conf.d/main.py.conf
[program:main]
directory=/home/${USER}/ruuvitag-data
command=/home/${USER}/ruuvitag-data/.env/bin/python3 /home/${USER}/ruuvitag-data/main.py -a ${MAC_ADDRESS}
autostart=true
autorestart=true
stderr_logfile=/var/log/main.err.log
stdout_logfile=/var/log/main.out.log
EOF

# Removed quotes from EOF so ${USER} expands correctly
# Left filename as app.conf
cat << EOF | sudo tee /etc/supervisor/conf.d/app.py.conf
[program:app]
directory=/home/${USER}/ruuvitag-data
command=/home/${USER}/ruuvitag-data/.env/bin/gunicorn --bind 0.0.0.0:8080 app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/app.err.log
stdout_logfile=/var/log/app.out.log
EOF

sudo supervisorctl reread
sudo supervisorctl update

# Quotes around 'EOF' are fine here since there are no variables to expand
# Added missing closing braces for location and server blocks
cat << 'EOF' | sudo tee /etc/nginx/sites-available/ruuvitag-data
server {
    listen 80;
    server_name ruuvitag.local;

    access_log /var/log/nginx/ruuvitag_access.log;
    error_log /var/log/nginx/ruuvitag_error.log;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8080;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/ruuvitag-data /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx