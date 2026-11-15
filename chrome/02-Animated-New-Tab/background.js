chrome.action.onClicked.addListener(() => {
  chrome.tabs.create({url: chrome.runtime.getURL('newtab.html')});
});

chrome.runtime.onInstalled.addListener(details => {
  if (details.reason === 'install') {
    chrome.tabs.create({url: chrome.runtime.getURL('newtab.html')});
  }
});
