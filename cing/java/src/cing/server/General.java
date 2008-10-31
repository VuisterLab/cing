package cing.server;


public class General {
	public static void showDebug(String string) {
		System.out.println("DEBUG: " + string);
	}
	public static void showError(String string) {
		System.err.println("ERROR: " + string);
	}
	public static void showOutput(String string) {
		System.out.println(string);
	}
}