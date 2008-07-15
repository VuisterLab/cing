#!/bin/tcsh -f

set GWTDIR = "/Users/jd/progs/gwt-mac-1.4.62"

# No changes below this line
###################################################################

set APPDIR = `dirname $0`
echo 1
set CPICING = ${APPDIR}/src
set CPICING = ${CPICING}:${APPDIR}/bin
set CPICING = ${CPICING}:${GWTDIR}/gwt-user.jar
set CPICING = ${CPICING}:${GWTDIR}/gwt-dev-mac.jar
echo 2

java -XstartOnFirstThread -cp "${CPICING}" com.google.gwt.dev.GWTShell \
	 -out "${APPDIR}/www" cing.iCing/iCing.html
# make sure there's an eol left after the above java command, e.g. by this line.