### Snapz Pro X Version 2.1.3 trial version ###

**UPDATE**
Note that nowadays in Lion the capture can be done from Quicktime as detailed here:
http://www.macstories.net/reviews/lions-quicktime-player-screen-recording-improvements-and-new-sharing-features/

# Setup #
  * Set to single display.
  * Set screen resolution to no more than 1280 x 800 for getting enough font size.
  * Set mouse locator to always on.
  * Set Safari browser default font size to somewhat larger
  * Hide Safari Bookmarks (Shift Cmd B; or find it directly under View).
  * Disable applications such as Skype and Google Notifier that may interrupt.

# Author #
  * Open Snapz with Shift Cmd 3.
  * Select movie mode (top right icon).
  * Set boundaries to full-screen.
  * Select to select a filename before starting recording.
  * Press enter to start action..
  * Press Shift Cmd 3 to cut action.
  * Check screen resolution and audio with a short test recording every time!
  * Repeat until happy.
  * While you wait for the movie to render in Snapz you can improve this Wiki; I did!

# Publish #
  * Edit with iMovie.
    * Import to the Event Library (bottom left panel). Takes time to generate thumbnails.
    * Create a new project in the Project Library (top left panel)
    * Select and trim sections from the event library clips and drag and drop them to the new project.
    * Add a music track from say iTunes and set the volume to like 1 %.
  * Export from iMovie using "Export using Quicktime" with settings recommended by YouTube.
    * Video H.264 compression, 1280 x 720 (HD)
  * If the video becomes over 10 minutes; YouTube currently removes it after upload. Split the movie using e.g. like:
`splitmovie -o "CING Screencast part.mov" -self-contained -no-fast-start -duration 9:00 "CING Screencast.mov"`
  * At YouTube
    * Enter your account info and set the category to "Science & Technology".
    * Title like: Analysis iCing interface Screencast
    * Enter description like: "Hi, my name is Jurgen and in this screencast I will show you how to use Analysis to validate your NMR project with in iCing."
    * Add Tags like: CING, Analysis, NMR, Structure Validation, Proteins, Nucleic Acids, CCPN, PDB
    * Size has to be at least 1280 x 720 (16:9 HD).
  * Link to it from as many web pages as you see fit.
  * Closed captions can easily be created by youtubecc.