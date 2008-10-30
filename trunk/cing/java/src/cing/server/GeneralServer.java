package cing.server;


public class GeneralServer {
	public static void showDebug(String string) {
		System.out.println("DEBUG: " + string);
	}
	public static void showError(String string) {
		System.err.println("ERROR: " + string);
	}
}