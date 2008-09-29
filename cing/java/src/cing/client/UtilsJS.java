package cing.client;

/** Utilities that rely on cross platform,independent JS and thus worthy of GWT presence.
 * There is a little line of JS in the StyleSheetLoader code too.
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

}
