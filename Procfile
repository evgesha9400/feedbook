web: gunicorn feedbook.wsgi --log-file -
web: daphne feedbook.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2