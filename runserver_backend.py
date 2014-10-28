from backend import app

if __name__ == "__main__":

    # run Flask dev-server
    app.config['SERVER_NAME'] = 'medicines.localhost:5001'
    app.run(port=5001)