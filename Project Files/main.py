# Main file run 
from website import create_app

app = create_app()

#Runs file name __main__
if __name__ == '__main__':
    app.run(debug=True)

