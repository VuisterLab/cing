package cing;

/** Settings for Scripts code */
public interface Constants {
	/** Where are we installed? */
	public static final String cingRoot = System.getenv("CINGROOT");
	public static final String cingDirTests = cingRoot + "/Tests";
	public static final String cingDirTestsData = cingDirTests + "/data";
//	public static final String cingDirScripts = System.getProperty("CINGROOT");
//	public static final String cingDirData = System.getProperty("CINGROOT");
//	public static final String cingDirTmp = System.getProperty("CINGROOT");
//	cingDirScripts         = os.path.join(cingPythonCingDir,"Scripts")
//	cingDirData            = os.path.join(cingRoot,         "data")
//	cingDirTmp             = os.path.join("/tmp" , "cing")
}
