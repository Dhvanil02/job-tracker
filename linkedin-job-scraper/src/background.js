chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "getLinkedInCookies") {
    // Retrieve the 'li_at' cookie
    chrome.cookies.get({ url: "https://www.linkedin.com", name: "li_at" }, function (liAtCookie) {
      // Retrieve the 'JSESSIONID' cookie
      chrome.cookies.get({ url: "https://www.linkedin.com", name: "JSESSIONID" }, function (jsessionCookie) {

        // Build the response with both cookies
        let cookies = {
          li_at: liAtCookie ? liAtCookie.value : null,
          JSESSIONID: jsessionCookie ? jsessionCookie.value : null
        };

        // Log both cookies for debugging
        console.log("LinkedIn li_at cookie:", cookies.li_at);
        console.log("LinkedIn JSESSIONID cookie:", cookies.JSESSIONID);

        // Send the cookies back to the caller
        sendResponse({ cookies: cookies });
      });
    });

    return true;  // Required to keep the message channel open for async response
  }
  if (message.action === "callApi") {
    checkJobs(message.data).then((resps) => {
      sendResponse({ result: resps });
    });
    return true; 
  }
});

// Function to call the API
function checkJobs(jsonData) {
  return new Promise((resolve, reject) => {
    const url = "http://127.0.0.1:5000/scrape-jobs";
    const method = "POST";

    // Ensure we are sending the body correctly
    fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json' // Ensure content type is set
      },
      body: JSON.stringify(jsonData)
    })
    .then((res) => {
      if (res.ok) {
        return res.json(); // Parse JSON response
      }
      throw new Error('Network response was not ok.');
    })
    .then((data) => {
      resolve(data);
    })
    .catch((error) => {
      reject(error);
    });
  });
}