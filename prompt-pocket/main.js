const { app, BrowserWindow, globalShortcut, ipcMain, Tray, Menu, nativeImage } = require('electron')
const path = require('path')
const fs = require('fs')

const BUNDLED_DATA_DIR = path.join(__dirname, 'data')
const START_HIDDEN_ARG = '--hidden'
const APP_ICON_ICO = path.join(__dirname, 'assets', 'icon.ico')
const APP_ICON_PNG = path.join(__dirname, 'assets', 'icon.png')

let win = null
let tray = null

const DEFAULT_CONFIG = {
  shortcut: 'CommandOrControl+Shift+P',
  autoLaunch: true
}

const gotTheLock = app.requestSingleInstanceLock()
if (!gotTheLock) {
  app.quit()
}

app.on('second-instance', () => {
  if (!win) return
  if (!win.isVisible()) win.show()
  if (win.isMinimized()) win.restore()
  win.focus()
})

function getDataDir() {
  return app.isPackaged
    ? path.join(app.getPath('userData'), 'data')
    : BUNDLED_DATA_DIR
}

function getDataFile(name) {
  return path.join(getDataDir(), name)
}

function ensureDataDir() {
  const dataDir = getDataDir()
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true })
  }
}

function ensureSeedFile(name, fallbackContent) {
  ensureDataDir()

  const target = getDataFile(name)
  if (fs.existsSync(target)) return target

  const bundled = path.join(BUNDLED_DATA_DIR, name)
  try {
    if (fs.existsSync(bundled)) {
      fs.copyFileSync(bundled, target)
    } else {
      fs.writeFileSync(target, fallbackContent, 'utf-8')
    }
  } catch (e) {
    if (!fs.existsSync(target)) {
      fs.writeFileSync(target, fallbackContent, 'utf-8')
    }
  }

  return target
}

function getConfig() {
  try {
    const configFile = ensureSeedFile('config.json', JSON.stringify(DEFAULT_CONFIG, null, 2))
    if (!fs.existsSync(configFile)) return { ...DEFAULT_CONFIG }
    return { ...DEFAULT_CONFIG, ...JSON.parse(fs.readFileSync(configFile, 'utf-8')) }
  } catch (e) {
    return { ...DEFAULT_CONFIG }
  }
}

function saveConfig(config) {
  try {
    const configFile = getDataFile('config.json')
    ensureDataDir()
    fs.writeFileSync(configFile, JSON.stringify(config, null, 2), 'utf-8')
    return true
  } catch (e) {
    return false
  }
}

function inferCreatedAt(item = {}) {
  if (item.createdAt) return item.createdAt
  if (item.id && /^\d+$/.test(String(item.id))) {
    const fromId = new Date(Number(item.id))
    if (!Number.isNaN(fromId.getTime())) {
      return fromId.toISOString()
    }
  }
  return new Date().toISOString()
}

function normalizeItem(item = {}) {
  return {
    id: item.id ? String(item.id) : Date.now().toString(),
    title: item.title || '',
    category: item.category || '',
    content: item.content || '',
    createdAt: inferCreatedAt(item),
    updatedAt: item.updatedAt || item.createdAt || null,
    deletedAt: item.deletedAt || null
  }
}

function readJSON(file) {
  try {
    ensureDataDir()
    if (!fs.existsSync(file)) return []
    const parsed = JSON.parse(fs.readFileSync(file, 'utf-8'))
    return Array.isArray(parsed) ? parsed.map(normalizeItem) : []
  } catch (e) {
    return []
  }
}

function writeJSON(file, data) {
  try {
    ensureDataDir()
    const normalized = Array.isArray(data) ? data.map(normalizeItem) : []
    fs.writeFileSync(file, JSON.stringify(normalized, null, 2), 'utf-8')
    return true
  } catch (e) {
    return false
  }
}

function isStartHidden() {
  return process.argv.includes(START_HIDDEN_ARG)
}

function createWindow() {
  win = new BrowserWindow({
    width: 900,
    height: 680,
    show: false,
    frame: false,
    alwaysOnTop: true,
    resizable: true,
    icon: fs.existsSync(APP_ICON_ICO) ? APP_ICON_ICO : APP_ICON_PNG,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  win.loadFile(path.join(__dirname, 'index.html'))

  win.on('ready-to-show', () => {
    if (!isStartHidden()) {
      win.show()
      win.focus()
    }
  })

  win.on('close', (e) => {
    if (!app.isQuitting) {
      e.preventDefault()
      win.hide()
    }
  })

  win.on('minimize', (e) => {
    e.preventDefault()
    win.hide()
  })
}

function createTray() {
  const iconPath = fs.existsSync(APP_ICON_PNG) ? APP_ICON_PNG : (fs.existsSync(APP_ICON_ICO) ? APP_ICON_ICO : path.join(__dirname, 'icon.svg'))
  const trayIcon = nativeImage.createFromPath(iconPath)

  tray = new Tray(trayIcon)

  const contextMenu = Menu.buildFromTemplate([
    { label: '显示窗口', click: () => toggleWindow(true) },
    { type: 'separator' },
    {
      label: '开机自启',
      type: 'checkbox',
      checked: getConfig().autoLaunch,
      click: (menuItem) => {
        const config = getConfig()
        config.autoLaunch = menuItem.checked
        saveConfig(config)
        setAutoLaunch(menuItem.checked)
      }
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        app.isQuitting = true
        app.quit()
      }
    }
  ])

  tray.setToolTip('Prompt Pocket')
  tray.setContextMenu(contextMenu)
  tray.on('click', () => toggleWindow())
}

function toggleWindow(forceShow = false) {
  if (!win) return

  if (forceShow) {
    win.show()
    if (win.isMinimized()) win.restore()
    win.focus()
    return
  }

  if (win.isVisible() && win.isFocused()) {
    win.hide()
  } else {
    win.show()
    if (win.isMinimized()) win.restore()
    win.focus()
  }
}

function getAutoLaunchSettings(enable) {
  const settings = {
    openAtLogin: enable,
    name: 'Prompt Pocket'
  }

  if (process.platform === 'win32') {
    settings.path = process.execPath
    settings.args = process.defaultApp
      ? [app.getAppPath(), START_HIDDEN_ARG]
      : [START_HIDDEN_ARG]
  } else {
    settings.openAsHidden = true
    settings.args = [START_HIDDEN_ARG]
  }

  return settings
}

function setAutoLaunch(enable) {
  app.setLoginItemSettings(getAutoLaunchSettings(enable))
}

function registerShortcut() {
  const config = getConfig()
  globalShortcut.unregisterAll()

  const success = globalShortcut.register(config.shortcut, () => toggleWindow())
  if (!success) {
    console.error('Failed to register shortcut:', config.shortcut)
  }
}

function saveItem(file, payload) {
  const items = readJSON(file)
  const now = new Date().toISOString()

  if (payload.id) {
    const idx = items.findIndex(item => item.id === String(payload.id))
    if (idx >= 0) {
      items[idx] = normalizeItem({
        ...items[idx],
        ...payload,
        id: items[idx].id,
        updatedAt: now
      })
    } else {
      items.unshift(normalizeItem({ ...payload, createdAt: now, updatedAt: now }))
    }
  } else {
    items.unshift(normalizeItem({
      ...payload,
      id: Date.now().toString(),
      createdAt: now,
      updatedAt: now,
      deletedAt: null
    }))
  }

  return writeJSON(file, items) ? readJSON(file) : []
}

function softDeleteItem(file, id) {
  const items = readJSON(file)
  const idx = items.findIndex(item => item.id === String(id))
  if (idx >= 0) {
    items[idx] = normalizeItem({
      ...items[idx],
      deletedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    })
  }
  return writeJSON(file, items) ? readJSON(file) : []
}

function restoreItem(file, id) {
  const items = readJSON(file)
  const idx = items.findIndex(item => item.id === String(id))
  if (idx >= 0) {
    items[idx] = normalizeItem({
      ...items[idx],
      deletedAt: null,
      updatedAt: new Date().toISOString()
    })
  }
  return writeJSON(file, items) ? readJSON(file) : []
}

function purgeItem(file, id) {
  const items = readJSON(file).filter(item => item.id !== String(id))
  return writeJSON(file, items) ? readJSON(file) : []
}

ipcMain.handle('get-prompts', () => readJSON(ensureSeedFile('prompts.json', '[]')))
ipcMain.handle('get-notes', () => readJSON(ensureSeedFile('notes.json', '[]')))
ipcMain.handle('get-config', () => getConfig())

ipcMain.handle('save-prompt', (event, prompt) => saveItem(getDataFile('prompts.json'), prompt))
ipcMain.handle('delete-prompt', (event, id) => softDeleteItem(getDataFile('prompts.json'), id))
ipcMain.handle('restore-prompt', (event, id) => restoreItem(getDataFile('prompts.json'), id))
ipcMain.handle('purge-prompt', (event, id) => purgeItem(getDataFile('prompts.json'), id))

ipcMain.handle('save-note', (event, note) => saveItem(getDataFile('notes.json'), note))
ipcMain.handle('delete-note', (event, id) => softDeleteItem(getDataFile('notes.json'), id))
ipcMain.handle('restore-note', (event, id) => restoreItem(getDataFile('notes.json'), id))
ipcMain.handle('purge-note', (event, id) => purgeItem(getDataFile('notes.json'), id))

ipcMain.handle('update-shortcut', (event, newShortcut) => {
  const config = getConfig()
  config.shortcut = newShortcut
  if (saveConfig(config)) {
    registerShortcut()
    return { success: true, shortcut: newShortcut }
  }
  return { success: false }
})

ipcMain.handle('toggle-auto-launch', (event, enable) => {
  const config = getConfig()
  config.autoLaunch = enable
  if (saveConfig(config)) {
    setAutoLaunch(enable)
    return { success: true, autoLaunch: enable }
  }
  return { success: false }
})

ipcMain.on('hide-window', () => {
  if (win) win.hide()
})

app.whenReady().then(() => {
  ensureSeedFile('prompts.json', '[]')
  ensureSeedFile('notes.json', '[]')
  ensureSeedFile('config.json', JSON.stringify(DEFAULT_CONFIG, null, 2))

  createWindow()
  createTray()
  registerShortcut()

  const config = getConfig()
  setAutoLaunch(Boolean(config.autoLaunch))
})

app.on('window-all-closed', () => {
  // 保持运行在托盘
})

app.on('before-quit', () => {
  app.isQuitting = true
})

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})
