# snipsWebAdmin
Web based administrative system for Snips devices

Install this to the main RPi snips instance (not satellite devices)

    # install pip
    sudo apt-get install python-pip
    
    #clone this git
    git clone https://github.com/oziee/snipsWebAdmin.git
    
    #install deps
    cd snipsWebAdmin
    pip install -r requirements.txt
    
# Starting web console


    # alter the settings.yml file in the base directory
    change the MQTT settings to match as needed
    
    # start
    ./boot.sh
    
    (if it doesnt start you need to change the boot.sh to bootable.. only have to do this one)
    chmod +x boot.sh
    
    then run ./boot.sh again
    
You can create a service to start the console when the pi starts

    
