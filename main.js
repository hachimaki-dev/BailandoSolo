const { app, BrowserWindow, screen } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow;
let pythonProcess;

const SERVER_PORT = 5001;
const SERVER_URL = `http://127.0.0.1:${SERVER_PORT}`;

function createWindow() {
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
      nodeIntegration: true,
      contextIsolation: false
    },
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#0f0c29',
    show: false
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // En producción, cargamos desde el servidor Flask (same-origin).
    // Esto elimina todos los problemas de CORS y audio silenciado.
    waitForServer(() => {
      if (mainWindow) {
        mainWindow.loadURL(SERVER_URL);
      }
    });
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

/**
 * Espera a que el servidor Flask esté listo antes de cargar la UI.
 * Reintenta cada 300ms hasta 30 segundos máximo.
 */
function waitForServer(callback, retries = 100) {
  const check = () => {
    const req = http.get(SERVER_URL, (res) => {
      if (res.statusCode === 200) {
        callback();
      } else if (retries > 0) {
        setTimeout(check, 300);
        retries--;
      }
    });
    req.on('error', () => {
      if (retries > 0) {
        setTimeout(check, 300);
        retries--;
      } else {
        console.error('Server failed to start after 30s');
      }
    });
    req.end();
  };
  check();
}

function startPythonServer() {
  const isWin = process.platform === 'win32';
  const binName = isWin ? 'bailandosolo-server.exe' : 'bailandosolo-server';

  if (app.isPackaged) {
    const binPath = path.join(process.resourcesPath, binName);
    console.log(`Iniciando servidor compilado: ${binPath}`);
    pythonProcess = spawn(binPath, [], {
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });
  } else {
    const pythonExecutable = isWin ? 'python.exe' : 'python3';
    const venvPath = isWin ? path.join('venv', 'Scripts') : path.join('venv', 'bin');
    const pythonPath = path.join(__dirname, venvPath, pythonExecutable);
    const scriptPath = path.join(__dirname, 'server.py');

    console.log(`Iniciando servidor Python (Dev): ${pythonPath} ${scriptPath}`);
    pythonProcess = spawn(pythonPath, [scriptPath], {
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
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

app.on('ready', () => {
  startPythonServer();
  createWindow();
});

app.on('window-all-closed', function () {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  app.quit();
});

app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
