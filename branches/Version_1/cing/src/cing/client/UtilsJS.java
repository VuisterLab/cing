package cing.client;

/**
 * Utilities that rely on cross platform,independent JS and thus worthy of GWT presence. There is a little line of JS in
 * the StyleSheetLoader code too.
 * 
 * @author jd
 * 
 */
public class UtilsJS {
    /**
     * Get the URL of the page, without an hash of query string.
     * 
     * @return the location of the page
     */
    public static native String getHostPageLocation()
    /*-{
      var s = $doc.location.href;
    
      // Pull off any hash.
      var i = s.indexOf('#');
      if (i != -1)
        s = s.substring(0, i);
    
      // Pull off any query string.
      i = s.indexOf('?');
      if (i != -1)
        s = s.substring(0, i);
    
      // Ensure a final slash if non-empty.
      return s;
    }-*/;

/**    
  * 
  * @return One of:
SAFARI
mozilla/5.0 (macintosh; u; intel mac os x 10_5_6; en-us) applewebkit/525.27.1 (khtml, like gecko) version/3.2.1 safari/525.27.1
CHROME
mozilla/5.0 (windows; u; windows nt 6.0; en-us) applewebkit/525.19 (khtml, like gecko) chrome/1.0.154.43 safari/525.19
IE
mozilla/4.0 (compatible; msie 7.0; windows nt 6.0; slcc1; .net clr 2.0.50727; .net clr 3.0.04506)
etc.
  */    
    public static native String getUserAgent() /*-{
           return navigator.userAgent.toLowerCase();
       }-*/;

}
