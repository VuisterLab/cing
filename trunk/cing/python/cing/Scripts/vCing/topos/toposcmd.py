#!/usr/bin/env python

"""
Run e.g.:
$CINGROOT/python/cing/Scripts/vCing/topos/toposcmd.py --realm https://topos.grid.sara.nl/4.1 --pool vCing --timeout 30 get-token-url
$CINGROOT/python/cing/Scripts/vCing/topos/toposcmd.py --realm https://topos.grid.sara.nl/4.1 --pool vCing --timeout 30 get-num-tokens
"""
from cing.Libs.NTutils import * #@UnusedWildImport
import StringIO
import getopt
import pycurl

def usage():
  nTerror( """usage:
  toposcmd --url <url> create-realm
  toposcmd --realm <realm> --pool <pool> create-tokens <token1> <token2> ...
  toposcmd --realm <realm> --pool <pool> get-token-url
  toposcmd --realm <realm> --pool <pool> get-token
  toposcmd --realm <realm> --pool <pool> --token <token> get-token-content
  toposcmd --realm <realm> --pool <pool> --token <token> remove-token
  toposcmd --realm <realm> --pool <pool> remove-pool
  toposcmd --realm <realm>  remove-realm
  toposcmd --realm <realm> --pool <pool> get-num-tokens

  In stead of
         --realm <realm> --pool <pool> --token <token>
  one can also specify the whole url (without 'nextToken'):
         --url <url>
  """)


class toposcmd:
    def __init__(self, realm='https://topos.grid.sara.nl/4.1/', pool='vCing', timeout = 300):
        self.realm    = realm
        self.pool     = pool
        self.timeout  = timeout
        self.token    = None
        self.cmd      = None
        self.args     = []
        self.url      = None
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYPEER,0)
        self.curl.setopt(pycurl.NOPROGRESS,1)
        self.curl.setopt(pycurl.FAILONERROR,1)
        self.curl.setopt(pycurl.HTTPHEADER,["Content-type: text/plain", "Accept: text/plain"])
        self.curl.result = StringIO.StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.curl.result.write)

    def show(self):
        nTmessage("""
realm:     %s
pool:      %s
timeout:   %s
token:     %s
url:       %s
args:      %s""" % (self.realm, self.pool,self.timeout,self.token,self.url,self.args))

    def check(self,x,s):
        'Return True on error'
        if x:
            return False
        nTerror(" not defined:"+s)
        return True

#    def getrealm(self):
#        import subprocess
#        return subprocess.Popen(["toposrealm"],
#                stdout=subprocess.PIPE).communicate()[0].\
#                strip().replace('\n',"")

    def makeurl(self,realm=None,pool=None,token=None):
        if self.url :
            return
        if realm :
            if not self.realm:
                print "ERROR: Failed to find realm and previous method disappeared."
                return
#                self.realm = self.getrealm()
            self.check(self.realm,"realm")
            self.url = self.realm
        if pool :
            self.check(self.pool,"pool")
            self.url = self.url + "/pools/" + self.pool
        if token :
            self.check(self.token,"token")
            self.url = self.url + "/tokens/" + token
        if self.cmd:
            self.url = self.url + "/" + self.cmd
        nTerror("wwvv url: %s" % self.url)


    def proceed(self):

        if len(self.args) == 0:
            usage()
            sys.exit(1)
        if self.args[0]   == "create-realm" :
            self.create_realm()
        elif self.args[0] == "create-tokens" :
            self.create_tokens()
        elif self.args[0] == "get-token-url" :
            self.get_token_url()
        elif self.args[0] == "get-token" :
            self.get_token()
        elif self.args[0] == "get-token-content" :
            self.get_token_content()
        elif self.args[0] == "remove-token" :
            self.remove_token()
        elif self.args[0] == "remove-pool" :
            self.remove_pool()
        elif self.args[0] == "remove-realm" :
            self.remove_realm()
        elif self.args[0] == "get-num-tokens" :
            self.get_num_tokens()
        else:
            nTerror("Invalid command: '"+self.args[0]+"'")
            sys.exit(2)

    def handle_default(self):
        self.curl.setopt(pycurl.URL,self.url)
        nTdebug( "Curling %s with request: %s" % (self.url, pycurl.CUSTOMREQUEST))
        try:
            self.curl.perform()
        except:
            return
        nTmessage( self.curl.result.getvalue() )
        self.curl.result.seek(0)

    def create_realm(self):   # niet gecontroleerd
        self.cmd = ""
        self.makeurl(realm=1)
        self.handle_default()

    def remove_realm(self):
        self.cmd = ""
        self.makeurl(realm=1)
        self.curl.setopt(pycurl.CUSTOMREQUEST,"DELETE")
        self.handle_default()

    def create_tokens(self):
        self.cmd = "nextToken"
        self.makeurl(realm=1,pool=1)
        if not self.url:
            self.check(self.realm,"realm")
            self.check(self.pool,"pool")
            self.url  = self.realm+"/pools/"+self.pool+"/nextToken"
        for d in self.args[1:] :
            data = StringIO.StringIO(d)
            data.seek(0)
            self.curl.setopt(pycurl.READFUNCTION,data.read)
            self.curl.setopt(pycurl.UPLOAD,1)
            self.curl.setopt(pycurl.URL,self.url)
            self.curl.perform()
            nTmessage( self.curl.result.getvalue() )
            self.curl.result.seek(0)

    def get_token_url(self):
        if not self.url:
            self.check(self.realm,"realm")
            self.check(self.pool,"pool")
            self.url  = self.realm+"/pools/"+self.pool+"/nextToken"
        self.handle_default()

    def get_token(self):
        if not self.url:
            self.check(self.realm,"realm")
            self.check(self.pool,"pool")
            self.url  = self.realm+"/pools/"+self.pool+"/nextToken"
        nTmessage("url: %s" % self.url)
        self.curl.setopt(pycurl.URL,self.url)
        try:
            self.curl.perform()
        except:
            NTtracebackError()
            nTmessage( "exception was caught in toposcmd.get_token()" )
            return
        nTmessage( self.curl.result.getvalue().split("/")[-1] )
        self.curl.result.seek(0)

    def get_token_content(self):
        if not self.url:
            self.check(self.realm,"realm")
            self.check(self.pool,"pool")
            self.check(self.token,"token")
            self.url  = self.realm+"/pools/"+self.pool+"/tokens/"+self.token
        self.curl.setopt(pycurl.FOLLOWLOCATION,1)
        self.handle_default()

    def get_num_tokens(self):
        "JFD can't get this one to work...."
        pass
#        if not self.url:
#            self.check(self.realm,"realm")
#            self.check(self.pool,"pool")
#            self.url = self.realm+"/pools"
#        nTmessage("url: %s" % self.url)
#        self.curl.setopt(pycurl.FOLLOWLOCATION,1)
#        self.curl.setopt(pycurl.URL,self.url)
#        try:
#            self.curl.perform()
#        except:
#            NTtracebackError()
#            nTmessage( "exception was caught in toposcmd.get_num_tokens()" )
#            return
#        self.curl.result.seek(0)
#        for line in self.curl.result:
#            l = line.split()
#            p = self.pool
#            if p[-1] != "/":
#                p = p + "/"
#            if l[0] == p:
#                print l[1]
#                break

    def remove_token(self):
        if not self.url:
            self.check(self.realm,"realm")
            self.check(self.pool,"pool")
            self.check(self.token,"token")
            self.url = self.realm+"/pools/"+self.pool+"/tokens/"+self.token
        self.curl.setopt(pycurl.CUSTOMREQUEST,"DELETE")
        self.handle_default()

    def remove_pool(self):
        if not self.url:
            self.check(self.realm,"realm")
            self.check(self.pool,"pool")
            self.url  = self.realm+"/pools/"+self.pool
        self.curl.setopt(pycurl.CUSTOMREQUEST,"DELETE")
        self.handle_default()

def main():

    cmd = toposcmd()

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "",
            ["realm=","pool=","token=","timeout=","url="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    print "DEBUG: opts %s" % opts
    for o, a in opts:
        if o == "--realm":
            cmd.realm = a
        elif o == "--pool" :
            cmd.pool = a
        elif o == "--token" :
            cmd.token = a
        elif o == "--timeout":
            cmd.timeout = a
        elif o == "--url":
            cmd.url = a
        else:
            assert False, "invalid option"
    # ...
    cmd.args = args
    # cmd.show()
    cmd.proceed()


if __name__ == "__main__":
    main()