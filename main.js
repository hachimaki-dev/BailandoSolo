const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');
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
        // Any response means the server is up
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
    pythonProcess = spawn(binPath, [], {
      env: { ...process.env, PYTHONUNBUFFERED: '1', BAILANDO_PORT: String(port) }
    });
  } else {
    const pythonExecutable = isWin ? 'python.exe' : 'python3';
    const venvPath = isWin ? path.join('venv', 'Scripts') : path.join('venv', 'bin');
    const pythonPath = path.join(__dirname, venvPath, pythonExecutable);
    const scriptPath = path.join(__dirname, 'server.py');

    console.log(`Starting Python server (Dev): ${pythonPath} ${scriptPath} on port ${port}`);
    pythonProcess = spawn(pythonPath, [scriptPath], {
      env: { ...process.env, PYTHONUNBUFFERED: '1', BAILANDO_PORT: String(port) }
    });
  }

  pythonProcess.on('error', (err) => {
    console.error('Failed to start python process:', err);
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
    // Flask only serves the API, not the frontend.
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
    pythonProcess.kill();
    pythonProcess = null;
  }
}

app.on('ready', async () => {
  try {
    const serverPort = await findFreePort(DEFAULT_SERVER_PORT);
    console.log(`Using port: ${serverPort}`);

    startPythonServer(serverPort);
    createWindow(serverPort);

    const serverUrl = `http://127.0.0.1:${serverPort}`;
    try {
      await waitForServer(serverUrl);
      console.log('Server is ready!');
    } catch (err) {
      console.error('Server startup error:', err.message);
    }
  } catch (err) {
    console.error('Failed to find free port:', err.message);
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
