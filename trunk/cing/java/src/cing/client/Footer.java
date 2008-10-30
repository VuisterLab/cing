package cing.client;

import com.google.gwt.user.client.ui.HTML;

public class Footer extends iCingView {

	public Footer() {
		final HTML html = new HTML("<div id=\"footer\">"+General.eol+
				"<p align=\"center\">"+General.eol+
				"CING  version 0.8 (iCing v."+Keys.VERSION+")\t"+General.eol+
				"<a href=\"mailto:g.vuister@science.ru.nl\">Geerten W. Vuister</a>"+General.eol+", \t"+General.eol+
				"<a href=\"mailto:jurgend@cmbi.ru.nl\">Jurgen F. Doreleijers</a>"+General.eol+" and \t"+General.eol+
				"<a href=\"mailto:alanwilter@gmail.com\">Alan Wilter Sousa da Silva</a>"+
				"</p>"+General.eol+
				"</div>"+General.eol);
		initWidget(html);
	}
}
