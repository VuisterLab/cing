package cing.client;

import com.google.gwt.user.client.ui.HTML;

public class Footer extends iCingView {

	public Footer() {

		final HTML html = new HTML("<div id=\"footer\">\n"+
				"<p align=\"center\">\n"+
				"CING  version 0.8 (iCing v."+iCing.VERSION+")\t\n"+
				"<a href=\"mailto:g.vuister@science.ru.nl\">Geerten W. Vuister</a>\n, \t\n"+
				"<a href=\"mailto:jurgend@cmbi.ru.nl\">Jurgen F. Doreleijers</a>\n and \t\n"+
				"<a href=\"mailto:alanwilter@gmail.com\">Alan Wilter Sousa da Silva</a>"+
				"</p>\n"+
				"</div>\n");
		initWidget(html);
	}
}
