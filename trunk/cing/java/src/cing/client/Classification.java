package cing.client;

import java.util.ArrayList;

public class Classification {
	/** Of course using hashes would have been faster on the lookup but 
	 * don't know if GWT supports them on the client side.
	 */
	static final String[][] classi = new String[][] { 
		{ "CCPN", "project", iCing.STRING_NA, iCing.STRING_NA },
//		{ "CING", "project", iCing.STRING_NA, iCing.STRING_NA },
//		{ "CCPN", "bogus", "blabla", iCing.STRING_NA },
//		{ "DYANA/DIANA", "distance", "hydrogen bond", "upper" },
//		{ "DYANA/DIANA", "distance", "hydrogen bond", "lower" },
//		{ "DYANA/DIANA", "distance", "NOE", "upper" },
//		{ "DYANA/DIANA", "distance", "NOE", "lower" },
//		{ "DYANA/DIANA", "dihedral angle", iCing.STRING_NA, iCing.STRING_NA },
//		{ "XPLOR/CNS", "distance", "hydrogen bond", iCing.STRING_NA },
//		{ "XPLOR/CNS", "distance", "NOE", iCing.STRING_NA },
//		{ "PDB", "coordinate", iCing.STRING_NA, iCing.STRING_NA },
	};

	public static ArrayList<String> getProgramList() {
		ArrayList<String> r = new ArrayList<String>();
		for (String[] o : classi ) {
			if ( ! r.contains( o[0] )) {
				r.add(o[0]);
			}
		}
//		General.showDebug("getProgramList: " + Utils.toString(r,false,true,","));
		return r;
	}
	
	/**
	 * @return empty if no types are present or the list of allowed types.
	 */
	public static ArrayList<String> getTypeList(String program) {
		ArrayList<String> r = new ArrayList<String>();
		if ( program != null ) {
			for (String[] o : classi ) {
				if ( o[0].equals(program ) ) {
					if ( ! r.contains( o[1] )) {
						r.add(o[1]);
					}
				}
			}
		}
//		General.showDebug("getTypeList: " + Utils.toString(r,false,true,","));
		return r;
	}
	/**
	 * @return empty if no types are present or the list of allowed types.
	 */
	public static ArrayList<String> getSubTypeList(String program, String type) {
		ArrayList<String> r = new ArrayList<String>();
		for (String[] o : classi ) {
			if ( o[0].equals(program) && o[1].equals(type) ) {
				if ( ! r.contains( o[2] )) {
					r.add(o[2]);
				}
			}
		}
//		General.showDebug("getSubTypeList: " + Utils.toString(r,false,true,","));		
		return r;
	}
	/**
	 * @return empty if no types are present or the list of allowed types.
	 */
	public static ArrayList<String> getOtherList(String program, String type, String subType) {
		ArrayList<String> r = new ArrayList<String>();
		for (String[] o : classi ) {
//			General.showDebug("Looking at string[0]: ["+o[0]+"]");
			if ( o[0].equals(program) && o[1].equals(type) && o[2].equals(subType) ) {
				if ( ! r.contains( o[3] )) {
					r.add(o[3]);
				}
			}
		}
//		General.showDebug("getOtherList: " + Utils.toString(r,false,true,","));		
		return r;
	}
	
};