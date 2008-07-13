package cing.server;

import java.io.File;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileItemFactory;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;

public class FileUploadServlet extends HttpServlet {
  private static final long 
      serialVersionUID = 6098745782027999297L;
  
  private static final String 
      UPLOAD_DIRECTORY = "/Users/jd";
  
  private static final long MAX_SIZE = 50000;
  private static final String ACCEPTABLE_CONTENT_TYPE =
      "image/jpeg";
  private static final String CONTENT_TYPE_UNACCEPTABLE =
      "{error: 'File upload failed. "
      + " Only JPEG images can be uploaded'}";

  private static final String SIZE_UNACCEPTABLE =
      "{error: 'File upload failed. File size must be " 
      + MAX_SIZE + " bytes or less'}";
  
  private static final String SUCCESS_MESSAGE =
    "{message: 'File upload succeeded'}";

  public void doPost(HttpServletRequest request,
      HttpServletResponse response) throws ServletException,
      IOException {
    FileItemFactory factory = new DiskFileItemFactory();
    ServletFileUpload upload = new ServletFileUpload(factory);
    List items = null;
    String json = null;

    try {
      items = upload.parseRequest(request);
    }
    catch (FileUploadException e) {
      e.printStackTrace();
    }
    Iterator it = items.iterator();
    while (it.hasNext()) {
      FileItem item = (FileItem) it.next();
      json = processFile(item);
//      System.out.println("Msg to json later: " + json);
    }
    response.setContentType("text/plain");
    response.getWriter().write(json);
  }
  
  private String processFile(FileItem item) {
    if (!isContentTypeAcceptable(item))
      return CONTENT_TYPE_UNACCEPTABLE;

    if (!isSizeAcceptable(item))
      return SIZE_UNACCEPTABLE;

    File uploadedFile =
        new File(UPLOAD_DIRECTORY + "/" + item.getName());

    String message = null;
    try {
      item.write(uploadedFile);
      message = SUCCESS_MESSAGE;
    }
    catch (Exception e) {
      e.printStackTrace();
    }
    return message;
  }
  private boolean isSizeAcceptable(FileItem item) {
    return item.getSize() <= MAX_SIZE;
  }
  private boolean isContentTypeAcceptable(FileItem item) {
    return item.getContentType().equals(
        ACCEPTABLE_CONTENT_TYPE);
  }
}