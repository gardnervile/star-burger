#!/bin/bash
set -e

cd /opt/star-burger
source venv/bin/activate
export $(grep -v '^#' .env | xargs)   # <-- вот это важно

git pull
pip install -r requirements.txt
npm install
npm run build
python manage.py collectstatic --noinput
python manage.py migrate

sudo systemctl restart gunicorn
sudo systemctl reload nginx

# Отправляем инфу в Rollbar
curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_DEPLOY_TOKEN \
  -F environment=$ROLLBAR_ENVIRONMENT \
  -F revision=$(git rev-parse HEAD)
