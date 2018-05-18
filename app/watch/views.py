#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 8:35:06 pm
# Author: Greg
# -----
# Last Modified: Thu May 17 2018
# Modified By: Greg
# -----
# Copyright (c) 2018 Greg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
### **************************************************************************** ###




# -*- coding: utf-8 -*-

from flask import stream_with_context, render_template, redirect, url_for, current_app, jsonify, request, Response
from . import watch
from app import mqtt,socketio
from flask_socketio import emit
import re
import time
from datetime import datetime
import json

devices = []
sessions = []

FORMAT_TIME_STRING = "%H:%M:%S.%f"

TIME_FIELD = "<span class='time'>[{}]  </span>"
SITE_ID = "<span class='siteId'>{}</span>"
ASR_TEXT = "<span class='asrtext'>{}</span>"
INTENT_STRING = "<span class='intentstring'>{}</span>"
TR = "<tr class='eTR'><td class='eTDL'><b>{}</b></td><td class='eTDM'>-></td><td class='eTDR'>{}</td></tr>"
SLOT = "<span class='slot'>{}</span>&nbsp;->&nbsp;{}<br>"
NLU_FILTER = "<span class='nlufilter'>{}</span>"
EVENT_HOTWORD = "<span class='hotword'>[Hotword]</span>"
EVENT_ASR = "<span class='asr'>[ASR]</span>"
EVENT_NLU = "<span class='nlu'>[NLU]</span>"
EVENT_TTS = "<span class='tts'>[TTS]</span>"
EVENT_AUDIOSERVER = "<span class='audioserver'>[Audio Server]</span>"
EVENT_INTENT = "<span class='intent'>[-]</span>"
EVENT_DIALOGUE = "<span class='dialogue'>[Dialogue]</span>"
EVENT_SOUND = "<span class='sound' style='font-weight: bold;'>[-]</span>"


terminationReasons = {
    'nominal': 'The session ended as expected',
    'abortedByUser': 'The session aborted by the user',
    'intentNotRecognized': 'The session ended because no intent was successfully detected',
    'timeout': 'The session timed out because no response from one of the components or no endSession message from the handler code was received in a timely manner',
    'error': 'The session failed with an error'
}


@socketio.on('disconnect', namespace='/watch')
def disconnect():
    global sessions
    global devices
    sessions = []
    #devices = []
    iamhere = ''

    #remove mqtt subscriptions
    #mqtt.unsubscribe_all()



def device_checbox_changed_handler(data):
    global devices
    device = data['device']
    checked = data['checked']

    if checked:
        #add topics to subscribe
        if device not in devices:
            devices.append(device)
    else:
        #remove topics
        if device in devices:
            devices.remove(device)



@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):

    return_string = ''

    if re.match(r"hermes/audioServer/.+/audioFrame",  message.topic, flags=0):
        global devices
       
        d = message.topic.split("/")[2]
        if d not in devices:
            devices.append(d)

    elif message.topic == 'hermes/tts/sayFinished':
        return_string = format_tts_sayfinished(message.payload)
    elif message.topic == 'hermes/tts/say':
        return_string = format_tts_say(message.payload)
    elif message.topic == 'hermes/dialogueManager/startSession':
        return_string = format_dialogueManager_startSession(message.payload)
    elif message.topic == 'hermes/dialogueManager/sessionQueued':
        return_string = format_dialogueManager_sessionQueued(message.payload)
    elif message.topic == 'hermes/dialogueManager/continueSession':
        return_string = format_dialogueManager_continueSession(message.payload)
    elif message.topic == 'hermes/dialogueManager/endSession':
        return_string = format_dialogueManager_endSession(message.payload)
    elif message.topic == 'hermes/feedback/sound/toggleOff':
        return_string = format_toggelSound(message.payload, 'Off')
    elif message.topic == 'hermes/feedback/sound/toggleOn':
        return_string = format_toggelSound(message.payload, 'On')
    elif message.topic == 'hermes/dialogueManager/sessionEnded':
        return_string = format_dialogue_sessionEnded(message.payload)
    elif message.topic == 'hermes/dialogueManager/sessionStarted':
        return_string = format_dialogue_sessionstarted(message.payload)
    elif message.topic == 'hermes/nlu/intentNotRecognized':
        return_string = format_nlu_intentNotRecognised(message.payload)
    elif message.topic == 'hermes/nlu/slotParsed':
        return_string = format_nlu_slotParsed(message.payload)
    elif message.topic.startswith('hermes/intent/'):
        return_string = format_intent_posted(message.topic, message.payload)
    elif message.topic == "hermes/nlu/intentParsed":
        return_string = format_nlu_intentParsed(message.payload)
    elif message.topic == "hermes/nlu/query":
        return_string = format_nlu(message.payload)
    elif message.topic == "hermes/asr/startListening":
        return_string = format_asr_toggle(message.payload, 'on')
    elif message.topic == "hermes/asr/stopListening":
        return_string = format_asr_toggle(message.payload, 'off')
    elif message.topic == "hermes/asr/textCaptured":
        return_string = format_asr_text(message.payload)
    elif message.topic == "hermes/asr/partialTextCaptured":
        return_string = format_asr_text(message.payload, True)
    elif message.topic == "hermes/hotword/toggleOn":
        return_string = format_hotword_toggle(message.payload, 'on')
    elif message.topic == "hermes/hotword/toggleOff":
        return_string = format_hotword_toggle(message.payload, 'off')
    elif message.topic == 'hermes/error/nlu':
        return_string = format_nlu_error(message.payload)
    elif re.match(r"hermes/hotword/.+/detected",  message.topic, flags=0):
        hotword_id = message.topic.split("/")[2]
        return_string = format_hotword_detected(hotword_id, message.payload)
    elif re.match(r"hermes/audioServer/.+/playFinished",  message.topic, flags=0):
        site_id = message.topic.split("/")[2]
        return_string = format_audioserver_playFinished(site_id)
    elif re.match(r"hermes/audioServer/.+/playBytes",  message.topic, flags=0):
        site_id = message.topic.split("/")[2]
        return_string = format_audioserver_playBytes(site_id)

    if return_string != '':
        socketio.emit('mqtt', return_string, namespace='/watch')

    
def getTimeString():
    return datetime.now().strftime(FORMAT_TIME_STRING)  

def format_hotword_detected(hw,payload):
    #might need to change for {"siteId":"zero","modelId":"default"} model = hotword custom etc??
    global devices
    payload = json.loads(payload.decode('utf-8'))
    s = payload['siteId']
    if s in devices:
        t =  getTimeString()
        #[Hotword] detected on site zero, for model default
        strg = TIME_FIELD + EVENT_HOTWORD + " detected on site " + SITE_ID + ", for model <b>{}</b><br>"
        return strg.format(t, s, hw)
    return ''

def format_hotword_toggle(payload, onoff):
    global sessions
    global devices
    #might need to change for {"siteId":"zero","modelId":"default"} model = hotword custom etc??
    payload = json.loads(payload.decode('utf-8'))
    s = payload['siteId']

    if s in devices:
        t = getTimeString()  
        #[Hotword] was asked to toggle itself 'off' on site zero
        #[Hotword] was asked to toggle itself 'on' on site zero
        strg = TIME_FIELD + EVENT_HOTWORD + " was asked to toggle itself '<b>{}</b>' on site " + SITE_ID + "<br>"
        return strg.format(t, onoff, s)
    else:
        sessionId = payload['sessionId']
        if sessionId not in sessions:
            sessions.append(sessionId)

    return ''

def format_toggelSound(payload, onoff):
    global devices
    #[00:52:33] [Dialogue] session with id 'd30078a8-c181-46b9-a6ce-9fd4ee3f7e27' was ended on site zero.
    # #The session was ended because one of the component didn't respond in a timely manner
    payload = json.loads(payload.decode('utf-8'))

    s = payload['siteId']
    if s in devices:

        t = getTimeString()
        siteId = payload['siteId']
        
        strg = TIME_FIELD + EVENT_SOUND + " " + SITE_ID + \
            " feedback sounds toggle {}<br>"
        strg = strg.format(t, siteId, onoff)

        return strg
    return ''

def format_asr_toggle(payload, onoff):
    global devices
    #might need to change for {"siteId":"zero","modelId":"default"} model = hotword custom etc??
    payload = json.loads(payload.decode('utf-8'))
    s = payload['siteId']
    if s in devices:
        t = getTimeString() 
        #[Asr] was asked to stop listening on site zero
        #[Asr] was asked to listen on site zero
        if onoff == 'off':
            strg = TIME_FIELD + EVENT_ASR + \
                " was asked to <b>stop</b> listening on site " + SITE_ID + "<br>"
        else:
            strg = TIME_FIELD + EVENT_ASR + \
                " was asked to listen on site " + SITE_ID + "<br>"
        return strg.format(t, s)
    return ''

def format_asr_text(payload, partial=False):
    global devices
    #[Asr] captured text "what 's the weather like" in 4.0s
    payload = json.loads(payload.decode('utf-8'))
    s = payload['siteId']
    if s in devices:
        t = getTimeString()
        sec = payload['seconds']
        text = payload['text'].encode('utf-8')
       
        #[Asr] captured text "what 's the weather like" in 4.0s
        if partial:
            strg = TIME_FIELD + EVENT_ASR + " captured text \"" + ASR_TEXT + "\" on " + SITE_ID + " in <b>{}s</b><br>"
        else:
            strg = TIME_FIELD + EVENT_ASR + " captured partial text \"" + ASR_TEXT + "\" on " + SITE_ID + " in <b>{}s</b><br>"
        return strg.format(t, text, s, sec)
    return ''

def format_nlu(payload):
    global sessions
    #[07:41:24] [Nlu] was asked to parse input weather
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''
   
    t = getTimeString()
    text = payload['input']
    intentFilter = payload['intentFilter']
    #[07:41:24] [Nlu] was asked to parse input weather
    strg=''
    if intentFilter:
        strg = TIME_FIELD + EVENT_NLU + " was asked to parse input <b>\"" + text + "\"</b> within " + NLU_FILTER + "<br>"
        strg = strg.format(t, intentFilter)
    else:    
        strg = TIME_FIELD + EVENT_NLU + " was asked to parse input <b>\"" + text + "\"</b><br>"
        strg = strg.format(t)
    return strg
    
def format_nlu_intentParsed(payload):
    global sessions
    #[07:41:24] [Nlu] was asked to parse input weather
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''
   
    t = getTimeString()
    text = payload['input']
    intent = payload['intent']['intentName']
    prob = payload['intent']['probability']
    slottext = complete_slot_information(payload['slots'])
    #[13:33:03] [Nlu] detected intent searchWeatherForecast with probability 0.995 for input "what 's the weather like tomorrow"
    #          Slots ->
    #             forecast_start_datetime -> 2018-05-07 00:00: 00 + 00: 00

    if len(slottext) > 0:
        #has slots
        strg = TIME_FIELD + EVENT_NLU + " detected intent " + INTENT_STRING + " with probability <b>{}</b> for input <b>\"" + text + "\"</b><br>" + slottext
    
    else:
        #no slots to list
        strg = TIME_FIELD + EVENT_NLU + " detected intent " + INTENT_STRING + \
            " with probability <b>{}</b> for input <b>\"" + text + "\"</b><br>"

    strg = strg.format(t, intent, "{0:.3f}".format(prob))

    return strg
    
def format_nlu_intentNotRecognised(payload):
    global sessions
    #[00:34:57] [Nlu] intent not recognized for "hawaii"
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''
   
    t = getTimeString()
    text = payload['input']

    strg = TIME_FIELD + EVENT_NLU + INTENT_STRING.format(' intent not recognized') + " for \"" + text + "\"<br>"
    strg = strg.format(t)

    return strg

def format_nlu_error(payload):
    global sessions
    #[00:34:57] [Nlu] intent not recognized for "hawaii"
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''
   
    t = getTimeString()
    error = payload['error']
    context = ''
    if 'context' in payload:
        context = payload['context']

    strg = TIME_FIELD + EVENT_NLU + " <b>Error:</b> \"" + error + "\" {}<br>"
    strg = strg.format(t, '. {}'.format(context))

    return strg

def format_nlu_slotParsed(payload):
    global sessions
    #
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''
   
    t = getTimeString()
    inputstring = payload['input']
    intentName = payload['intentName']
    slottext = complete_slot_information(payload['slots'])


    strg = TIME_FIELD + EVENT_NLU + " Partial query on \"" + intentName + "\" for  " + INTENT_STRING + "{}<br>{}"
    strg = strg.format(t, inputstring,slottext)

    return strg
  
def format_intent_posted(topic, payload):
    global devices
    #[07:41:24] [Nlu] was asked to parse input weather
    payload = json.loads(payload.decode('utf-8'))

    s = payload['siteId']
    if s in devices:
        t = getTimeString()

        strg = TIME_FIELD + EVENT_INTENT + " Snips published " + INTENT_STRING + \
            " for skill to use for site " + SITE_ID + "<br>"
        strg = strg.format(t, topic, s)

        return strg
    return ''

def format_dialogue_sessionstarted(payload):
    global sessions
    #[00:34:54] [Dialogue] session with id 'd38a01d9-f28d-4372-b18b-2f38b266d891' was started on site zero
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''
   
    t = getTimeString()
    siteId = payload['siteId']

    strg = TIME_FIELD + EVENT_DIALOGUE + " session with id \'" + \
        s + "\' was started on site " + SITE_ID + "<br>"
    strg = strg.format(t, siteId)

    return strg

def format_dialogue_sessionEnded(payload):
    global sessions
    #[00:52:33] [Dialogue] session with id 'd30078a8-c181-46b9-a6ce-9fd4ee3f7e27' was ended on site zero. 
    # #The session was ended because one of the component didn't respond in a timely manner
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        sessions.remove(s)
        return ''

    t = getTimeString()
    siteId = payload['siteId']
    termination = payload['termination']['reason']


    strg = TIME_FIELD + EVENT_DIALOGUE + " session with id \'" + \
        s + "\' was ended on site " + SITE_ID + ". {}<br>"
    strg = strg.format(t, siteId, terminationReasons[termination])

    return strg

def format_dialogueManager_endSession(payload):
    global sessions
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''

    t = getTimeString()

    text = ''
    if 'text' in payload:
        text = payload['text']

    if text == '':
        strg = TIME_FIELD + EVENT_DIALOGUE + " session with id \'" + s + "\' is being asked to end without saying anything.<br>"
    else:
        strg = TIME_FIELD + EVENT_DIALOGUE + " session with id \'" + s + "\' is being asked to end and say \"" + text + "\".<br>"
    
    strg = strg.format(t)

    return strg

def format_dialogueManager_continueSession(payload):
    global sessions
    payload = json.loads(payload.decode('utf-8'))

    s = payload['sessionId']
    if s in sessions:
        return ''

    t = getTimeString()
    text = payload['text']
    intentFilter = ''
    if 'intentFilter' in payload:
        intentFilter = payload['intentFilter']

    if intentFilter == '':
        strg = TIME_FIELD + EVENT_DIALOGUE + " continue session with id \'" + s + "\' and say \"" + text + "\".<br>"
        strg = strg.format(t)
    else:
        strg = TIME_FIELD + EVENT_DIALOGUE + " continue session with id \'" + s + "\' and say \"" + text + "\". The session will now filter results from the intents [\"{}\"].<br>"
        strg = strg.format(t,intentFilter)
    
    return strg

def format_dialogueManager_sessionQueued(payload):
    global sessions
    payload = json.loads(payload.decode('utf-8'))

    strg = ''

    s = payload['siteId']
    if s in devices:
        sessionId = payload['sessionId']
        t = getTimeString()
        customData = ''
        if 'customData' in payload:
            customData = payload['customData']

        strg = TIME_FIELD + EVENT_DIALOGUE + " session queued with id \'{}\' on site " + SITE_ID + ".<br>"
        strg = strg.format(t,sessionId,s)

    return strg

def format_dialogueManager_startSession(payload):
    global sessions
    payload = json.loads(payload.decode('utf-8'))

    strg = ''

    s = payload['siteId']
    if s in devices:
        ini = payload['init']
        inittype = ini['type']
        t = getTimeString()
        text = ''
        if 'text' in ini:
            text = ini['text']

        canBeEnqueued = False
        if 'canBeEnqueued' in ini:
            canBeEnqueued = ini['canBeEnqueued']

        strg = TIME_FIELD + EVENT_DIALOGUE + " was asked to start a session type <b>{}</b> on site " + SITE_ID
        strg = strg.format(t,s,inittype)

        if inittype == 'action':
            strg += ", canBeEnqueued is <b>\'{}\'</b>".format(str(canBeEnqueued))
        
        if len(text) > 0:
            strg += " with text <b>\'{}\'</b>".format(text)

        strg += "<br>"

    return strg

def format_audioserver_playBytes(siteId):
    #might need to change for {"siteId":"zero","modelId":"default"} model = hotword custom etc??
    global devices
   
    if siteId in devices:
        t = getTimeString()  # strftime("%H:%M:%S.%f", gmtime())    
        #[Hotword] detected on site zero, for model default
        strg = TIME_FIELD + EVENT_AUDIOSERVER + " was asked to play a file on site " + SITE_ID + "<br>"
        return strg.format(t, siteId)
    return ''

def format_audioserver_playFinished(siteId):
    global devices
   
    if siteId in devices:
        t = getTimeString()  # strftime("%H:%M:%S.%f", gmtime())    
        #[Hotword] detected on site zero, for model default
        strg = TIME_FIELD + EVENT_AUDIOSERVER + " site " + SITE_ID + " finished paying the sound file<br>"
        return strg.format(t, siteId)
    return ''

def format_tts_say(payload):
    return ''

def format_tts_sayfinished(payload):
    return ''

def complete_slot_information(slots):
    slottext = ''

    if len(slots) > 0:
        for slotItem in slots:
            kind = slotItem['value']['kind']
            slot1=''
            if kind == 'Custom' or kind == 'InstantTime':
                slot1 = slotItem['value']['value']
            elif kind == 'TimeInterval':
                slot1 = 'From {} to {}'.format( slotItem['value']['from'], slotItem['value']['to'] ) 
            
            slot2 = slotItem['slotName']
            joined = TR.format(slot2, slot1)
            slottext = '{}{}'.format(slottext, joined)
        row1 = "<tr class='eTR'><td class='eTDL' style='color:black;text-align: center;'><b>Slots</b> -></b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td class='eTDM'></td><td class='eTDR'></td></tr>"
        slottext = "<table>" + row1 + slottext + "</table><br>"

    return slottext

def background():
    global devices
    global sessions

    devices = []
    sessions = []
    count = 0

    #lets get a list of client that are out there working
    mqtt.unsubscribe_all()
    mqtt.subscribe("hermes/audioServer/+/audioFrame")
    
    while len(mqtt.topics) > 0:
        #print("bg")
        
        count += 1
        if count == 2:
            mqtt.unsubscribe_all()
            #print(devices)
        time.sleep(.5)

    #subscript to topics to watch
    
    mqtt.subscribe('hermes/tts/say')
    mqtt.subscribe('hermes/feedback/sound/toggleOff')
    mqtt.subscribe('hermes/feedback/sound/toggleOn')
    mqtt.subscribe('hermes/audioServer/+/playFinished')
    mqtt.subscribe('hermes/audioServer/+/playBytes/#')
    mqtt.subscribe('hermes/dialogueManager/startSession')
    mqtt.subscribe('hermes/dialogueManager/sessionQueued')
    mqtt.subscribe('hermes/dialogueManager/continueSession')
    mqtt.subscribe('hermes/dialogueManager/endSession')
    mqtt.subscribe('hermes/dialogueManager/sessionEnded')
    mqtt.subscribe('hermes/dialogueManager/sessionStarted')
    mqtt.subscribe('hermes/nlu/intentNotRecognized')
    mqtt.subscribe('hermes/intent/#')
    mqtt.subscribe('hermes/nlu/intentParsed')
    mqtt.subscribe('hermes/nlu/query')
    mqtt.subscribe('hermes/nlu/slotParsed')
    mqtt.subscribe('hermes/error/nlu')
    mqtt.subscribe("hermes/asr/textCaptured")
    mqtt.subscribe("hermes/asr/partialTextCaptured")
    mqtt.subscribe("hermes/asr/startListening")
    mqtt.subscribe("hermes/asr/stopListening")
    mqtt.subscribe("hermes/hotword/+/detected")
    mqtt.subscribe("hermes/hotword/toggleOn")
    mqtt.subscribe("hermes/hotword/toggleOff")

        
    #d = devices
    #devices = []


    return render_template('watch.html', devices=devices,deviceCount=len(devices))


@watch.route('/watch')
def watch():
    
    socketio.on_event('checkbox', device_checbox_changed_handler, namespace='/watch')

    return Response(stream_with_context(background()))
