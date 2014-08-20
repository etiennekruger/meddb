from frontend import app

if __name__ == "__main__":

    # run Flask dev-server
    app.config['SERVER_NAME'] = 'medicines.localhost:5000'
    app.run(port=5000)