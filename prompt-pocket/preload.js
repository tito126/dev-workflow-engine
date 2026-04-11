const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('api', {
  getPrompts: () => ipcRenderer.invoke('get-prompts'),
  getNotes: () => ipcRenderer.invoke('get-notes'),
  getConfig: () => ipcRenderer.invoke('get-config'),

  savePrompt: (prompt) => ipcRenderer.invoke('save-prompt', prompt),
  deletePrompt: (id) => ipcRenderer.invoke('delete-prompt', id),
  restorePrompt: (id) => ipcRenderer.invoke('restore-prompt', id),
  purgePrompt: (id) => ipcRenderer.invoke('purge-prompt', id),

  saveNote: (note) => ipcRenderer.invoke('save-note', note),
  deleteNote: (id) => ipcRenderer.invoke('delete-note', id),
  restoreNote: (id) => ipcRenderer.invoke('restore-note', id),
  purgeNote: (id) => ipcRenderer.invoke('purge-note', id),

  updateShortcut: (shortcut) => ipcRenderer.invoke('update-shortcut', shortcut),
  toggleAutoLaunch: (enable) => ipcRenderer.invoke('toggle-auto-launch', enable),

  hideWindow: () => ipcRenderer.send('hide-window')
})
