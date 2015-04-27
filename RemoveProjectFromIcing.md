# Introduction #

Once the file is uploaded to iCing, the iCing and CCPN Analysis interfaces allow you to remove all data from the iCing server but what if you are already out of the interface?

# Resolution #

  1. Find your `UserId` which depends on the interface you used, see table below.
  1. Find you `AccessKey`. This is a 6 random character string, e.g. K5afmE. It can be found from the project url that you got that looked like: https://nmr.cmbi.ru.nl/tmp/cing/YOUR_USER_ID_HERE/YOUR_ACCESS_ID_HERE/... If you can't find it email me at jurgenfd@gmail.com with your project name and I'll have to do the removal by hand.
  1. Check if your data is still on the iCing server at:    https://nmr.cmbi.ru.nl/tmp/cing/YOUR_USER_ID_HERE/YOUR_ACCESS_ID_HERE/
  1. Install [curl](http://en.wikipedia.org/wiki/CURL)
  1. Execute
> > `curl -i -F Action=Purge -F UserId=YOUR_USER_ID_HERE -F AccessKey=YOUR_ACCESS_ID_HERE https://nmr.cmbi.ru.nl/icing/serv/iCingServlet`
  1. Repeat bullet 3 to see if your data really got removed. Make sure you clean your browser's cache.

**`UserId` lookup table**
| **Interace** | **`UserId`** |
|:-------------|:-------------|
| iCing | ano |
| CCPN Analysis | ccpnAp |