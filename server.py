# temporaty fix for
# https://stackoverflow.com/questions/60156202/flask-app-wont-launch-importerror-cannot-import-name-cached-property-from-w
# pip3 install --upgrade Werkzeug==0.16.1
from DeepPoolAI import AdminServer
# machine_id = <place random number there>
srv = AdminServer('./key.txt', machine_id)
srv.start_server('localhost', 9797, False)
