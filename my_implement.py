import pjsua as pj
import sys

lib =pj.Lib()


class MyAccountCallback(pj.AccountCallback):
 def __init__(self, account=None):
  pj.AccountCallback.__init__(self,account)

 def on_incoming_call(self, call):
  call.hangup(486, "Busy here")

 def on_reg_state(self):
  print "Registration complete, status=", self.account_info().reg_status, "(" + self.account.info().reg_reason + ")"



try:
 my_ua_cfg = pj.UAConfig()
 my_ua_cfg.stun_host = "stun.pjsip.org"
 my_media_cfg = pj.MediaConfig()
 my_media_cfg.enable_ice = True

 lib.init(ua_cfg=my_ua_cfg,media_cfg=my_media_cfg)

except pj.Error, err:
 print 'Initialization error:', err

try:
 udp = lib.create_transport(pj.TransportType.UDP)
except pj.Error, e:
 print "Error creating transport:", e

try:
 lib.start()
except pj.Error, e:
 print "Error starting pjsua:", e

lck = lib.auto_lock()


try:
 acc_cfg = pj.AccountConfig()
 user_id = "1001"
 user_password = "12345"
 user_domain = "10.0.0.1"
 acc_cfg.id = "sip:" + user_id + "@" + user_domain
# acc_cfg.id = "sip:1001@10.0.0.1"
 acc_cfg.reg_uri = "sip:"+user_domain
 acc_cfg.proxy = [ "sip:"+user_domain+";lr" ]
# acc_cfg.info = 

 acc_cfg.auth_cred = [ pj.AuthCred("*", user_id, user_password) ]


 acc_cb = MyAccountCallback()
# acc = lib.create_account(acc_cfg, cb=acc_cb)
# acc = lib.create_account(acc_cfg)
 acc.set_callback(acc_cb)

except pj.Error, err:
 print 'Error creating account:', err

del lck

lib.destroy()
lib = None 


#class MyAccountCallback(pj.AccountCallback):
# def __init__(self, account=None):
#  pj.AccountCallback.__init__(self,account)

# def on_incoming_call(self, call):
#  call.hangup(486, "Busy here")

# def on_reg_state(self):
#  print "Registration complete, status=", self.account_info().reg_status, "(" + self.account.info().reg_reason + ")"


