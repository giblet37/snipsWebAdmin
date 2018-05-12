# snipsWebAdmin
Web based administrative system for Snips devices

Install this to the main RPi snips instance (not satellite devices)

    #install pip
    sudo apt-get install python-pip python-git
    
    #clone this git
    git clone https://github.com/oziee/snipsWebAdmin.git
    
    #install deps
    cd snipsWebAdmin
    pip install -r requirements.txt
    
# Starting web console


    #alter the settings.yml file in the base directory
    change the MQTT settings to match as needed
    
    #start
    ./boot.sh (good for using a service, also cleans up compiled pyc files for a fresh start)

    else you can just use 'python snipsFlask.py' 
    
    (if it doesnt start you need to change the boot.sh to bootable.. only have to do this once)
    chmod +x boot.sh
    
    then run ./boot.sh again
    
Or you can create a service to start the console when the pi starts

    #copy service file
    sudo cp snipsWebAdmin.service /lib/systemd/system/snipsWebAdmin.service
    sudo systemctl enable snipsWebAdmin.service
    sudo systemctl start snipsWebAdmin.service

# console errors
gunicorn 19.6 which is installed but apt-get has BUGS which cause errors in the console to display. These really do not mean anything and should just be ignored.
You can install gunicorn from BackPorts following the gunicorn docs here http://docs.gunicorn.org/en/stable/install.html#stable-stretch
this version 19.7 (still no the newest version 19.8.1 :( ) does not display these errors
    
```
[2018-05-12 01:31:51 +0000] [13011] [ERROR] Error handling request /socket.io/?EIO=3&transport=websocket&sid=085c90445e6543e2847ab06462d7fced
Traceback (most recent call last):
  File "/usr/lib/python2.7/dist-packages/gunicorn/workers/async.py", line 52, in handle
    self.handle_request(listener_name, req, client, addr)
  File "/usr/lib/python2.7/dist-packages/gunicorn/workers/async.py", line 112, in handle_request
    resp.close()
  File "/usr/lib/python2.7/dist-packages/gunicorn/http/wsgi.py", line 418, in close
    self.send_headers()
  File "/usr/lib/python2.7/dist-packages/gunicorn/http/wsgi.py", line 334, in send_headers
    tosend = self.default_headers()
  File "/usr/lib/python2.7/dist-packages/gunicorn/http/wsgi.py", line 315, in default_headers
    elif self.should_close():
  File "/usr/lib/python2.7/dist-packages/gunicorn/http/wsgi.py", line 238, in should_close
    if self.status_code < 200 or self.status_code in (204, 304):
AttributeError: 'Response' object has no attribute 'status_code'
```


