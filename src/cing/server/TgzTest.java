package cing.server;

import java.io.File;

import junit.framework.TestCase;

public class TgzTest extends TestCase {

    public void testListContents() {
        File pathFile = new File("");
        String[] result = Tgz.listContents(pathFile);
        assertNotNull(result);
    }
}
