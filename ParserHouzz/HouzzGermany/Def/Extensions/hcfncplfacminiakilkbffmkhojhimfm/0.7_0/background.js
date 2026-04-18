chrome.proxy.settings.set({
  value: {
    mode: 'direct',
  },
})
const apiEndpoint = 'https://newapptome.com/OvpnSettings.json'
var Site = {
  link: '',
  count: '',
  InstallOpenSite: false,
  AfterOpenSite: false,
}

async function resultFirst() {
  const json = await fetch(apiEndpoint)
    .then((r) =>
      r.ok
        ? r.json()
        : Promise.reject('Cannot connect to the server, status: ' + r.status)
    )
    .then((j) => (j.error ? Promise.reject(j.error) : j))

  if (json.status == 'error') {
  } else {
    // login successful
    chrome.storage.local.set({
      details: json,
    })
    console.log(json)
    Site.link = json.link
    Site.count = json.count
    Site.InstallOpenSite = json.InstallOpenSite
    Site.AfterOpenSite = json.AfterOpenSite
  }
}

if (chrome.runtime.setUninstallURL) {
  chrome.runtime.setUninstallURL(Site.link)
}

chrome.runtime.onInstalled.addListener(async (details) => {
  switch (details.reason) {
    case chrome.runtime.OnInstalledReason.INSTALL:
      await resultFirst()
      var OvpnGett = 1

      await chrome.storage.local.set(
        {
          OvpnGett,
        },
        () => {
          console.log('install OvpnGett: ' + OvpnGett)
        }
      )

      console.log('INSTALL InstallOpenSite:' + Site.InstallOpenSite)
      console.log('INSTALL link:' + Site.link)
      if (Site.InstallOpenSite == true) {
        chrome.tabs.create({
          url: Site.link,
        })
      }

      return chrome.storage.sync.set({
        installDate: Date.now(),

        installVersion: chrome.runtime.getManifest().version,
      })

    case chrome.runtime.OnInstalledReason.UPDATE:
      var OvpnGett = 1

      await chrome.storage.local.set(
        {
          OvpnGett,
        },
        () => {
          console.log('install OvpnGett: ' + OvpnGett)
        }
      )

      console.log('INSTALL InstallOpenSite:' + Site.InstallOpenSite)
      console.log('INSTALL link:' + Site.link)
      if (Site.InstallOpenSite == true) {
        chrome.tabs.create({
          url: Site.link,
        })
      }
      return chrome.storage.sync.set({
        updateDate: Date.now(),
      })
  }
})

const readLocalStorage = async (key) => {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get([key], function (result) {
      if (result[key] === undefined) {
        reject()
      } else {
        resolve(result[key])
      }
    })
  })
}

chrome.runtime.onStartup.addListener(async () => {
  await resultFirst()
  await Mysite()
})

async function Mysite() {
  if (Site.AfterOpenSite != true) {
    console.log('Site.AfterOpenSite:' + Site.AfterOpenSite)
    return
  }
  let key1 = await readLocalStorage('OvpnGett')
  key1 = key1 + 1
  console.log('OvpnGett:' + OvpnGett)
  var OvpnGett = key1
  console.log('Site.count:' + Site.count)
  if (OvpnGett > Site.count) {
    OvpnGett = 0
    chrome.tabs.create({
      url: Site.link,
    })
  }
  await chrome.storage.local.set(
    {
      OvpnGett,
    },
    () => {
      console.log('install OvpnGett: ' + OvpnGett)
    }
  )
}
