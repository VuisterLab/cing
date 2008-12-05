package cing.server;

import java.util.HashMap;

import Wattos.Utils.General;

import junit.framework.TestCase;

public class UtTest extends TestCase {

    public void testMapToPythonRFC822ConfigurationSettings() {
        General.setVerbosityToDebug();
        HashMap<String, String> parameterMap = new HashMap<String, String>();
        parameterMap.put("keytje", "valuetje");
        General.showDebug(parameterMap.toString());
        String result = Ut.mapToPythonRFC822ConfigurationSettings(parameterMap);
        General.showDebug("result: [" + result +"]");
        // Just learning java:
        General.showDebug("should be xxx: [" + (true? "xxx":"yyy") +"]");
    }
}
