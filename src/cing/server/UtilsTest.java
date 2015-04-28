package cing.server;

import Wattos.Utils.General;
import junit.framework.TestCase;
import cing.client.Utils;

/** Test case of code that itself will be compiled to Javascript. The test code here will NOT!
 *  
 * @author jd
 *
 */
public class UtilsTest extends TestCase {

    static {
        General.setVerbosityToDebug();
    }
    
    public void testGetFileNameWithoutPath() {
        String[] testList = new String[] {
                "1brv.tgz",
                "C:\\Users\\jd\\1brv.tgz"
        };
        String[] testOutputList = new String[] {
                "1brv.tgz",
                "1brv.tgz"
        };
        for (int i=0;i<testList.length;i++) {
            String result = Utils.getFileNameWithoutPath(testList[i]);
            General.showDebug("in: [" + testList[i] + "] out: [" + result + "]");
            assertEquals(testOutputList[i], result);
        }
    }
}
