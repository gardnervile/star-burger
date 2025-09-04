echo "Отправляем информацию о деплое в Rollbar..."
curl -s https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_DEPLOY_TOKEN \
  -F environment=production \
  -F revision=$(git rev-parse HEAD) > /dev/null
echo " Деплой завершён и зафиксирован в Rollbar."
