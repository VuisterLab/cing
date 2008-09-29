package cing.client;

import java.util.ArrayList;

public class Classification {
	/** Of course using hashes would have been faster on the lookup but 
	 * don't know if GWT supports them on the client side.
	 */
	static final String[][] classi = new String[][] { 
		{ "CCPN", "project", null, null },
		{ "CCPN", "bogus", "blabla", null },
		{ "CING", "project", null, null },
		{ "DYANA/DIANA", "distance", "hydrogen bond", "upper" },
		{ "DYANA/DIANA", "distance", "hydrogen bond", "lower" },
		{ "DYANA/DIANA", "dihedral angle", null, null },
		{ "DYANA/DIANA", "distance", "NOE", null },
		{ "XPLOR/CNS", "distance", "hydrogen bond", null },
		{ "XPLOR/CNS", "distance", "NOE", null },
		{ "PDB", "coordinate", null, null },
		{ "CING", "project", null, null }
	};

	public static ArrayList<String> getProgramList() {
		ArrayList<String> r = new ArrayList<String>();
		for (String[] o : classi ) {
			if ( ! r.contains( o[0] )) {
				r.add(o[0]);
			}
		}
		return r;
	}
	
	/**
	 * @return null if no types are present or the list of allowed types.
	 */
	public static ArrayList<String> getTypeList(String program) {
		if ( program == null ) {
			return null;
		}
		ArrayList<String> r = new ArrayList<String>();
		for (String[] o : classi ) {
			if ( o[0].equals(program ) ) {
				if ( ! r.contains( o[1] )) {
					r.add(o[1]);
				}
			}
		}
		return r;
	}
	/**
	 * @return null if no types are present or the list of allowed types.
	 */
	public static ArrayList<String> getSubTypeList(String program, String type) {
		if ( program == null || type == null ) {
			return null;
		}
		ArrayList<String> r = new ArrayList<String>();
		for (String[] o : classi ) {
			if ( o[0] == null || o[1] == null ) { // impossible but just noting.
				continue;
			}
			if ( o[0].equals(program) && o[1].equals(type) ) {
				if ( ! r.contains( o[2] )) {
					r.add(o[2]);
				}
			}
		}
		return r;
	}
	/**
	 * @return null if no types are present or the list of allowed types.
	 */
	public static ArrayList<String> getOtherList(String program, String type, String subType) {
		if ( program == null || type == null || subType == null ) {
			return null;
		}
		ArrayList<String> r = new ArrayList<String>();
		for (String[] o : classi ) {
			General.showDebug("Looking at string[0]: ["+o[0]+"]");
			if ( o[0] == null || o[1] == null || o[2] == null ) {
				continue;
			}
			if ( o[0].equals(program) && o[1].equals(type) && o[2].equals(subType) ) {
				if ( ! r.contains( o[3] )) {
					r.add(o[3]);
				}
			}
		}
		return r;
	}
	
};