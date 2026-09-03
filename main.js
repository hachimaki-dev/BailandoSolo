const { app, BrowserWindow, screen, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const http = require('http');
const net = require('net');

let mainWindow;
let pythonProcess;

const DEV_FRONTEND_URL = 'http://localhost:5173';
const DEFAULT_SERVER_PORT = 5001;

/**
 * Find a free TCP port starting from the preferred port.
 * Tries up to 20 ports sequentially before giving up.
 */
function findFreePort(preferredPort) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 20;

    function tryPort(port) {
      const server = net.createServer();
      server.listen(port, '127.0.0.1', () => {
        server.close(() => resolve(port));
      });
      server.on('error', () => {
        attempts++;
        if (attempts >= maxAttempts) {
          reject(new Error(`Could not find a free port after ${maxAttempts} attempts`));
        } else {
          tryPort(port + 1);
        }
      });
    }

    tryPort(preferredPort);
  });
}

/**
 * Wait for the Flask server to be ready.
 * Retries every 300ms up to ~30 seconds.
 */
function waitForServer(serverUrl, retries = 100) {
  return new Promise((resolve, reject) => {
    const check = () => {
      const req = http.get(`${serverUrl}/api/stats`, (res) => {
        // Any HTTP response means the Flask server is up and listening
        resolve();
      });
      req.on('error', () => {
        if (retries > 0) {
          retries--;
          setTimeout(check, 300);
        } else {
          reject(new Error('Server failed to start after 30s'));
        }
      });
      req.end();
    };
    check();
  });
}

function startPythonServer(port) {
  const isWin = process.platform === 'win32';
  const binName = isWin ? 'bailandosolo-server.exe' : 'bailandosolo-server';

  if (app.isPackaged) {
    const binPath = path.join(process.resourcesPath, binName);
    console.log(`Starting compiled server: ${binPath} on port ${port}`);

    // Ensure executable permissions on macOS / Linux
    if (!isWin) {
      try {
        if (fs.existsSync(binPath)) {
          fs.chmodSync(binPath, 0o755);
        }
        const ffmpegPath = path.join(process.resourcesPath, 'ffmpeg');
        if (fs.existsSync(ffmpegPath)) {
          fs.chmodSync(ffmpegPath, 0o755);
        }
      } catch (e) {
        console.warn('[main] Warning adjusting binary permissions:', e);
      }
    }

    pythonProcess = spawn(binPath, [], {
      env: { ...process.env, PYTHONUNBUFFERED: '1', BAILANDO_PORT: String(port) },
      windowsHide: true
    });
  } else {
    const pythonExecutable = isWin ? 'python.exe' : 'python3';
    const venvPath = isWin ? path.join('venv', 'Scripts') : path.join('venv', 'bin');
    const pythonPath = path.join(__dirname, venvPath, pythonExecutable);
    const scriptPath = path.join(__dirname, 'server.py');

    console.log(`Starting Python server (Dev): ${pythonPath} ${scriptPath} on port ${port}`);
    pythonProcess = spawn(pythonPath, [scriptPath], {
      env: { ...process.env, PYTHONUNBUFFERED: '1', BAILANDO_PORT: String(port) },
      windowsHide: true
    });
  }

  pythonProcess.on('error', (err) => {
    console.error('Failed to start python process:', err);
    dialog.showErrorBox(
      'Error de servidor',
      `No se pudo iniciar el backend de Bailando Solo:\n${err.message}`
    );
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}

function createWindow(serverPort) {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  const isDev = process.argv.includes('--dev');
  const iconPath = isDev
    ? path.join(__dirname, 'ui', 'public', 'favicon.png')
    : path.join(__dirname, 'ui', 'dist', 'favicon.png');

  mainWindow = new BrowserWindow({
    width: Math.round(width * 0.9),
    height: Math.round(height * 0.9),
    icon: iconPath,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#0f0c29',
    show: false
  });

  // Expose the server port to the renderer via IPC
  ipcMain.handle('get-server-port', () => serverPort);

  if (isDev) {
    mainWindow.loadURL(DEV_FRONTEND_URL);
    mainWindow.webContents.openDevTools();
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
    });
  } else {
    // In production: load the frontend directly from the asar archive.
    const indexPath = path.join(__dirname, 'ui', 'dist', 'index.html');
    mainWindow.loadFile(indexPath);
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
    });
  }

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

function killPythonProcess() {
  if (pythonProcess) {
    const pid = pythonProcess.pid;
    if (process.platform === 'win32') {
      try {
        // Kill the full process tree on Windows to prevent orphaned zombies
        spawn('taskkill', ['/pid', pid.toString(), '/T', '/F']);
      } catch (e) {
        console.error('Error stopping Windows process tree:', e);
      }
    } else {
      try {
        pythonProcess.kill('SIGTERM');
      } catch (e) {}
    }
    pythonProcess = null;
  }
}

app.on('ready', async () => {
  try {
    const serverPort = await findFreePort(DEFAULT_SERVER_PORT);
    console.log(`Using port: ${serverPort}`);

    startPythonServer(serverPort);

    const isDev = process.argv.includes('--dev');
    const serverUrl = `http://127.0.0.1:${serverPort}`;

    // In production, wait for the server before creating the window to avoid startup race conditions
    if (!isDev) {
      try {
        await waitForServer(serverUrl);
        console.log('Server is ready and verified!');
      } catch (err) {
        console.error('Server startup error:', err.message);
        dialog.showErrorBox(
          'Tiempo de espera agotado',
          'El servidor interno no respondió a tiempo. Intenta reiniciar la aplicación.'
        );
      }
    }

    createWindow(serverPort);

    if (isDev) {
      try {
        await waitForServer(serverUrl);
        console.log('Dev server ready!');
      } catch (err) {
        console.error('Server startup error (dev):', err.message);
      }
    }
  } catch (err) {
    console.error('Failed to find free port:', err.message);
    dialog.showErrorBox(
      'Error de red',
      'No se encontró ningún puerto disponible para iniciar Bailando Solo.'
    );
    app.quit();
  }
});

app.on('window-all-closed', function () {
  killPythonProcess();
  app.quit();
});

app.on('will-quit', () => {
  killPythonProcess();
});
