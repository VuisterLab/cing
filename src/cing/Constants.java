package cing;

/** Settings for Scripts code */
public interface Constants {
    /** Where are we installed? */
    public static final String cingRoot = System.getenv("CINGROOT");
    public static final String cingDirTests = cingRoot + "/Tests";
    public static final String cingDirTestsData = cingRoot + "/data/Tests";
    public static final String dRoot = System.getenv("D");
}
