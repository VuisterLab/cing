package cing.client;

import com.google.gwt.user.client.ui.HTML;

public class Footer extends iCingView {

	final HTML html = new HTML("<div id=\"footer\">"+General.eol+
			"<p align=\"center\">"+General.eol+
			"CING  version 0.8 (iCing v."+Keys.VERSION+")\t"+General.eol+
			"<a href=\"mailto:g.vuister@science.ru.nl\">Geerten W. Vuister</a>, \t"+General.eol+
			"<a href=\"mailto:jurgend@cmbi.ru.nl\">Jurgen F. Doreleijers</a>"+General.eol+" and \t"+General.eol+
			"<a href=\"mailto:alanwilter@gmail.com\">Alan Wilter Sousa da Silva</a>"+
			"</p>"+General.eol+
			"</div>"+General.eol);

	public Footer() {
		super();
	}
	
	public void setIcing(iCing icing) {
		super.setIcing(icing);
//		final iCing icingShadow = icing;		
		verticalPanel.add(html);
	}
}
