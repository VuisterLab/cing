Setup on ododo.nl and reciprocal on nmr.

For local settings use example template:

# Local settings
set webchat_exe = /opt/local/bin/webchatpp
set webchat_dir = $C/scripts/webchatpp


SETUPS
==== OSX =====

from root session with cpan do:

    install CPAN
    reload cpan

Then outside:
cpan WWW::Chat::Processor
cpan HTML::Form
# for https)
cpan LWP::Protocol::https 

==== UBUNTU ====

