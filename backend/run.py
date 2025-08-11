from app import create_app
import logging


app = create_app()

app.config['PROPAGATE_EXCEPTIONS'] = True
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)