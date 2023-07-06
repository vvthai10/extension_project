// Auto connect web socket when extension run
var socket = new WebSocket("ws://localhost:8082");
socket.onopen = function () {
  console.log("Connected to WebSocket server");
};

// Loop 5 times to can send message to server
for (let i = 0; i < 10; i++) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send("Hello from extension");
    break;
  }
}

// Function get message from server
socket.onmessage = function (event) {
  var message = event.data;
  console.log("Received message: " + message);
  // Xử lý các thông điệp từ WebSocket server
};

// Function handle when disconnect server
socket.onclose = function () {
  console.log("Disconnected from WebSocket server");
  // Thực hiện các hoạt động khi kết nối bị đóng
};

// Function send message to server
function sendMessage(message) {
  socket.send(message);
}

/*
  Đoạn mã dưới đây được sao chép từ nguồn: 
*/

var takeScreenshot = {
  /**
   * @description ID of current tab
   * @type {Number}
   */
  tabId: null,

  /**
   * @description Canvas element
   * @type {Object}
   */
  screenshotCanvas: null,

  /**
   * @description 2D context of screenshotCanvas element
   * @type {Object}
   */
  screenshotContext: null,

  /**
   * @description Number of pixels by which to move the screen
   * @type {Number}
   */
  scrollBy: 0,

  /**
   * @description Sizes of page
   * @type {Object}
   */
  size: {
    width: 0,
    height: 0,
  },

  /**
   * @description Keep original params of page
   * @type {Object}
   */
  originalParams: {
    overflow: "",
    scrollTop: 0,
  },

  /**
   * @description Initialize plugin
   */
  initialize: function () {
    this.screenshotCanvas = document.createElement("canvas");
    this.screenshotContext = this.screenshotCanvas.getContext("2d");
    this.uri = null;

    this.bindEvents();
  },

  /**
   * @description Bind plugin events
   */
  bindEvents: function () {
    // handle onClick plugin icon event
    chrome.browserAction.onClicked.addListener(
      function (tab) {
        this.tabId = tab.id;

        chrome.tabs.executeScript(
          tab.id,
          { code: "document.documentElement.innerHTML" },
          function (result) {
            var html = result[0];

            // Trả về thông tin HTML cho extension
            // sendResponse({ html: html });
            console.log(html);
            socket.send(html);
          }
        );

        chrome.tabs.executeScript(tab.id, {
          code: 'document.getElementById("abcdefghijklmn").innerText = "Cập nhật giá trị mới";',
        });

        chrome.tabs.sendMessage(tab.id, {
          msg: "getPageDetails",
        });
      }.bind(this)
    );

    // handle chrome requests
    chrome.runtime.onMessage.addListener(
      function (request, sender, callback) {
        if (request.msg === "setPageDetails") {
          this.size = request.size;
          this.scrollBy = request.scrollBy;
          this.originalParams = request.originalParams;

          // set width & height of canvas element
          this.screenshotCanvas.width = this.size.width;
          this.screenshotCanvas.height = this.size.height;

          this.scrollTo(0);
        } else if (request.msg === "capturePage") {
          this.capturePage(request.position, request.lastCapture);
        }
      }.bind(this)
    );
  },

  /**
   * @description Send request to scroll page on given position
   * @param {Number} position
   */
  scrollTo: function (position) {
    chrome.tabs.sendMessage(this.tabId, {
      msg: "scrollPage",
      size: this.size,
      scrollBy: this.scrollBy,
      scrollTo: position,
    });
  },

  /**
   * @description Takes screenshot of visible area and merges it
   * @param {Number} position
   * @param {Boolean} lastCapture
   */
  capturePage: function (position, lastCapture) {
    var self = this;
    socket.send("Hello from extension");
    // sendMessage("Gửi tin nè");

    // Lấy thông tin HTML của trang web hiện tại
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      var tab = tabs[0];
      chrome.tabs.sendMessage(
        tab.id,
        { action: "getHTML" },
        function (response) {
          var html = response.html;

          // Gửi thông tin HTML tới WebSocket server
          console.log(html);
        }
      );
    });

    setTimeout(function () {
      chrome.tabs.captureVisibleTab(
        null,
        {
          format: "png",
        },
        function (dataURI) {
          var newWindow,
            image = new Image();
          chrome.runtime.sendMessage({ screenshot: dataURI });
          if (typeof dataURI !== "undefined") {
            image.onload = function () {
              self.screenshotContext.drawImage(image, 0, position);

              if (lastCapture) {
                self.resetPage();
                newWindow = window.open();
                newWindow.document.write(
                  "<style type='text/css'>body {margin: 0;}</style>"
                );
                newWindow.document.write(
                  "<img src='" +
                    self.screenshotCanvas.toDataURL("image/png") +
                    "'/>"
                );
              } else {
                self.scrollTo(position + self.scrollBy);
              }
            };

            image.src = dataURI;
            chrome.tabs.sendMessage(self.tabId, {
              msg: "screenshot",
              originalParams: dataURI,
            });
          } else {
            chrome.tabs.sendMessage(self.tabId, {
              msg: "showError",
              originalParams: self.originalParams,
            });
          }
        }
      );
    }, 100);
  },

  /**
   * @description Send request to set original params of page
   */
  resetPage: function () {
    console.log("Reset page");
    chrome.tabs.sendMessage(this.tabId, {
      msg: "resetPage",
      originalParams: this.originalParams,
    });
  },
};

takeScreenshot.initialize();
