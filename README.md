# snipsWebAdmin
Web based administrative system for Snips devices

Install this to the main RPi snips instance (not satellite devices)

..

    # install pip
    sudo apt-get install python-pip
    
    #clone this git
    git clone https://github.com/oziee/snipsWebAdmin.git
    
    #install deps
    pip install -r requirements.txt
    
# Starting web console
..

    # start
    cd snipsWebAdmin
    ./boot.sh
    
    (if it doesnt start you need to change the boot.sh to bootable.. only have to do this one)
    chmod +x boot.sh
    
    then run ./boot.sh again
    
You can create a service to start the console when the pi starts

    
