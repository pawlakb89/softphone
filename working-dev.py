import sys
import pjsua as pj
import getpass

LOG_LEVEL=5
current_call = None

def log_cb(level, str, len):
    print str,


class MyAccountCallback(pj.AccountCallback):

    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    # Notyfikacje na polaczenie przychodzace
    def on_incoming_call(self, call):
        global current_call 
        if current_call:
            call.answer(486, "Busy")
            return

        print "Polaczenie przychodzace od: ", call.info().remote_uri
        print "Nacisnij 'a' aby odebrac."

        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180)


# Odbieranie eventow z polaczenia
class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Na zmiane stanu polaczenia
    def on_state(self):
        global current_call
        print "Polaczenie z ", self.call.info().remote_uri,
        print "jest ", self.call.info().state_text,
        print "ostatni kod last_code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
            print 'Biezace polaczenie ', current_call

    # Na zmiane stanu mediow
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Podlaczenie do urzadzenia audio
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print "Lataja media! :D"
        else:
            print "Nie lataja media! :( hold maybe"

# Metoda to wykonania polaczenia
def make_call(uri):
    try:
        print "Wykonuje polaczenie do ", uri
        return acc.make_call(uri, cb=MyCallCallback())
    except pj.Error, e:
        print "Exception: " + str(e)
        return None


# Tworzenie instancji biblioteki
lib = pj.Lib()

try:
    lib.init(log_cfg = pj.LogConfig(level=LOG_LEVEL, callback=log_cb))

    # Utworz transport UDP, ktory slucha na porcie 5060
    transport = lib.create_transport(pj.TransportType.UDP, 
                                     pj.TransportConfig(5060))
    print "\nLa la la slucham na: ", transport.info().host, 
    print ":", transport.info().port, "\n"

    lib.start()
    
    print "Lista urzadzen audio enum_snd_dev()" + str(lib.enum_snd_dev())
    print "Lista urzadzen audio z get_snd_dev() = ", str(lib.enum_snd_dev())

    lib.set_snd_dev(0,0) #lub -1,-2 do sprawdzenia
    # kiedy nie ma zadnego audio dev mozna ustawic null, wtedy kompletny brak dzwieku ale nic sie nie wywala
    #lib.set_null_snd_dev()

    #print "\nMenu: \n[r] - Rejestracja z parametrami uzytkownika, \n[d] - Rejestracja domyslna"
    #input = sys.stdin.readline().rstrip("\r\n")
    #if input==r:
    #    print "\nPodaj domene: "
    #    domain = sys.stdin.readline().rstrip("\r\n")
    #    print "\nPodaj id uzytkownika: "
    #    user_id = sys.stdin.redline().rstrip("\r\n")
        
        #print "\nPodaj haslo uzytkownika"
        #user_password = sys.stdin.redline().rstrip("\r\n")
    #    user_password = getpass.getpass("\nPodaj haslo uzytkownika: ")
        
    #    print  "Podaj port"
    #    user_port = sys.stdin.redline().rstrip("\r\n")
    #if input ==d:
        
    #    user_id = "1001"
    #    user_password = "1234"
    #    user_domain = "192.168.43.75"
    #    user_port = "5060"
    
    
    # Tworzenie konta
    #user_proxy = user_domain + ":" + user_port
    #acc = lib.create_account(pj.AccountConfig("10.2.0.4", "504", "gdasg649a"))
    #acc = lib.create_account(pj.AccountConfig(domain=user_domain, username=user_id, password=user_password)
    #str = "\""+user_domain+"\",\""+user_id+"\",\""+user_password+"\""
    #
#acc = lib.create_account(pj.AccountConfig(str)
    acc = lib.create_account(pj.AccountConfig("192.168.43.75", "1003", "1234"))
    
    cb = MyAccountCallback(acc)
    acc.set_callback(cb)
    print "\nUkonczono rejestracje, status = ", acc.info().reg_status, \
          "(" + acc.info().reg_reason + ")"    

    if len(sys.argv) > 1:
        lck = lib.auto_lock()
        current_call = make_call(sys.argv[1])
        print 'Current call is', current_call
        del lck

    my_sip_uri = "sip:1003@" + transport.info().host + ":" + str(transport.info().port)

    # Menu glowne (petelka):
    while True:
        print "Moje SIP URI to: ", my_sip_uri
        print "\nMenu glowne: \n [m] - Wykonaj polaczenie\n [d] - Wyslij DTMF(RFC)\n [h] - Rozlacz\n [a] - Odbierz polaczenie\n [q] - Wyjdz"

        input = sys.stdin.readline().rstrip("\r\n")
        if input == "m":
            if current_call:
                print "Masz juz jedno polaczenie!"
                continue
            print "\n Podaj numer docelowy: ", 
# Aby nie trzeba bylo podawac dest URI w formacie sip:user_id@user_domain:port
#    old -> input = sys.stdin.readline().rstrip("\r\n")
            input = sys.stdin.readline().rstrip("\r\n")
            created_uri = "sip:"+input+"@"+user_domain+":"+user_port
            if input == "":
                continue
            lck = lib.auto_lock()
            current_call = make_call(created_uri)
            del lck
## DTMF
        elif input == "d":
            if not current_call:
                print "Nie masz aktywnego polaczenia aby wyslac DTMF!"
                continue
            print "Podaj sekwencje DTMF do wyslania: \n"
            dtmf = sys.stdin.readline().rstrip("\r\n")
            current_call.dial_dtmf(dtmf)
## Hangup
        elif input == "h":
            if not current_call:
                print "Nie masz aktywnego polaczenia, ktore mozna rozlaczyc!"
                continue
            current_call.hangup()

        elif input == "a":
            if not current_call:
                print "Nie ma polaczenia, ktore mozesz odebrac!"
                continue
            current_call.answer(200)

        elif input == "q":
            break

    # Rozpierdol Liba()
    transport = None
    acc.delete()
    acc = None
    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
