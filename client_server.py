# temporaty fix for
# https://stackoverflow.com/questions/60156202/flask-app-wont-launch-importerror-cannot-import-name-cached-property-from-w
# pip3 install --upgrade Werkzeug==0.16.1
from DeepPoolAI import ClientServer
srv = ClientServer()
srv.start_server('localhost', 9292, False)
