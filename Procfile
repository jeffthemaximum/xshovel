web: daphne project.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
scraper_worker: python manage.py runworker --exclude-channels=websocket.* --exclude-channels=http.* -v2
http_socket_worker: python manage.py runworker --only-channels=websocket.* --only-channels=http.*