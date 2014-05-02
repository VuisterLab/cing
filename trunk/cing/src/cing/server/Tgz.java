package cing.server;

import java.io.File;

/**
 * 
 * Was going to include the ice untarring but it fails for long filenames. Giving up issue 
jd:stella/jars/ java com.ice.tar.tar -tvf $CINGROOT/data/Tests/ccpn/basp2.tgz
com.ice.tar.InvalidHeaderException: bad header in block 0 record 0, header magic is not 'ustar' or unix-style zeros, it is '75-83-657642-1121', or (dec) 75, -83, -65, 76, 42, -1, 121
    at com.ice.tar.TarInputStream.getNextEntry(Unknown Source)
    at com.ice.tar.TarArchive.listContents(Unknown Source)
    at com.ice.tar.tar.instanceMain(Unknown Source)
    at com.ice.tar.tar.main(Unknown Source)
jd:stella * @author jd
 * 
 */
public class Tgz {
    public static String[] listContents(File pathFile) {
        
        
        String[] result = new String[] { "bla", "blabla" };
        return result;
    }
}