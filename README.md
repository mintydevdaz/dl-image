# DL-Image
#### Video Demo: https://www.youtube.com/watch?v=oruF190gEWE
#### Description: downloads images from a given URL

### Project Summary
DL-Image is a command-line-based Python application that downloads images from a user-entered URL / website and saves them to a user-defined folder located on the Desktop. It utilises the requests and BeautifulSoup (bs4) libraries to parse HTML, extracts the image tags and attempts to access the images within those tags. There are multiple exit strategies built-in to prevent the app from 'hanging'.

### Why make this app?
My non-programming friend was searching for a way to mass download images from a website so this project was born from that idea. There are a plethora of online coding tutorials that use the requests and bs4 libraries for webscraping but most that appear on the front page of Google's search are basic and lack the broader functionality to cover the main obstacles encountered when extracting a website's images.

### Ease of Use
As I was making this specifically for a friend, the app must be as easy as possible to execute. This meant that:
- all known errors must be caught and printed to the terminal.
- all errors must be informative to a layperson.
- images must be downloaded to an obvious directory location.
- unknown user input must be accounted for within the program.
At the time of submission, most errors should be caught.

### App Workflow
1. Request URL input from user. Validate URL and exit if invalid.
2. Parse HTML text from URL. Exit if error reaching website or request timeout. Return a Beautiful Soup object containing all html img tags. Exit if none found.
3. Extract all source references from image tags. Exit if unable to extract any.
4. Provide user with choice to continue operation or exit if 50+ images found.
5. Create new folder on user Desktop. Reject folder name if already in directory.
6. Download images from their source locations. Pass over any exception cases.
7. If no images could be downloaded, then remove empty folder from Desktop. Otherwise, provide final count of result.