package cing.server;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

public class General {

	public static void showDebug(String string) {
		System.out.println("DEBUG: " + string);

	}

	public static void showError(String string) {
		System.err.println("ERROR: " + string);
	}

	/**
	 *  
	 * @return true for error
	 */
	public static boolean chmod(File f, String mod) {
		String cmd = "chmod " + mod + " " + f.toString();
		showDebug("Executing command: [" + cmd + "]");
		try {
			Process p = Runtime.getRuntime().exec(cmd);
			BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line = null;
			while ((line = in.readLine()) != null) {
				General.showDebug(line);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return true;
	}
}