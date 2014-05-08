import sys
import pjsua as pj

LOG_LEVEL=5
current_call = None
#PJMEDIA_AUDIO_DEV_HAS_PORTAUDIO = 0
#PJMEDIA_AUDIO_DEV_HAS_ALSA = 1

def log_cb(level, str, len):
    print str,


class MyAccountCallback(pj.AccountCallback):

    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    # Notification on incoming call
    def on_incoming_call(self, call):
        global current_call 
        if current_call:
            call.answer(486, "Busy")
            return

        print "Incoming call from ", call.info().remote_uri
        print "Press 'a' to answer"

        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180)


# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global current_call
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
            print 'Current call is', current_call

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print "Media is now active"
        else:
            print "Media is inactive"

# Function to make call
def make_call(uri):
    try:
        print "Making call to", uri
        return acc.make_call(uri, cb=MyCallCallback())
    except pj.Error, e:
        print "Exception: " + str(e)
        return None


# Create library instance
lib = pj.Lib()

try:
    # Init library with default config and some customized
    # logging config.
    lib.init(log_cfg = pj.LogConfig(level=LOG_LEVEL, callback=log_cb))

    # Create UDP transport which listens to any available port
    transport = lib.create_transport(pj.TransportType.UDP, 
                                     pj.TransportConfig(5060))
    print "\nListening on", transport.info().host, 
    print "port", transport.info().port, "\n"

    # Start the library
    lib.start()
    
    print "List sound dev" + str(lib.enum_snd_dev())
    #lib.set_snd_dev(1,1)
    snd_dev = lib.get_snd_dev()
    print str(snd_dev)
    lib.set_snd_dev(0,0)
    # when no sound card found
    #lib.set_null_snd_dev()  # here is the problem i cant capture mic, speaker from local system

    # Create local account
    #acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())
    ###### TUTAJ TRZEBA DOROBIC POBIERANIE TEGO OD USERA I ZAPISYWANIE W PONIZSZYCH ZMIENNYCH, LUB ZAPISYWANIE DO PLIKU I JEZELI NIE ISTNIEJE TO COS #########
    user_id = "504"
    user_password = "gdasg649a"
    user_domain = "10.2.0.4"
    user_port = "5060"
    user_proxy = user_domain + ":" + user_port
    #acc = lib.create_account(pj.AccountConfig("10.2.0.4", "504", "gdasg649a"))
    #acc = lib.create_account(pj.AccountConfig(user_domain, user_id, user_password)
    
    acc = lib.create_account(pj.AccountConfig("192.168.43.75", "1003", "1234"))
    cb = MyAccountCallback(acc)
    acc.set_callback(cb)
    #cb.wait()
    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
          "(" + acc.info().reg_reason + ")"    

    # If argument is specified then make call to the URI
    if len(sys.argv) > 1:
        lck = lib.auto_lock()
        current_call = make_call(sys.argv[1])
        print 'Current call is', current_call
        del lck

    my_sip_uri = "sip:" + transport.info().host + \
                 ":" + str(transport.info().port)

    # Menu loop
    while True:
        print "My SIP URI is", my_sip_uri
        print "Menu:  m=make call, d=send dtmf, h=hangup call, a=answer call, q=quit"

        input = sys.stdin.readline().rstrip("\r\n")
        if input == "m":
            if current_call:
                print "Already have another call"
                continue
            print "Enter destination URI to call: ", 
# Aby nie trzeba bylo podawac dest URI w formacie sip:user_id@user_domain:port
#    old -> input = sys.stdin.readline().rstrip("\r\n")
            input = sys.stdin.readline().rstrip("\r\n")
            created_uri = "sip:"+input+"@"+user_domain+":"+user_port
            if input == "":
                continue
            lck = lib.auto_lock()
            #current_call = make_call(input)
            current_call = make_call(created_uri)
            del lck
## Dodane dtmf
        elif input == "d":
            if not current_call:
                print "There is no call that dtmf can be sent"
                continue
            print "Please provide dtmf to send: \n"
            dtmf = sys.stdin.readline().rstrip("\r\n")
            current_call.dial_dtmf(dtmf)
### ^ DTMF
        elif input == "h":
            if not current_call:
                print "There is no call"
                continue
            current_call.hangup()

        elif input == "a":
            if not current_call:
                print "There is no call"
                continue
            current_call.answer(200)

        elif input == "q":
            break

    # Shutdown the library
    transport = None
    acc.delete()
    acc = None
    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
