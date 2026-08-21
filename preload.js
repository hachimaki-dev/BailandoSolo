/**
 * Bailando Solo — Preload Script
 * Exposes a safe bridge between the Electron main process and the renderer.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getServerPort: () => ipcRenderer.invoke('get-server-port')
});
