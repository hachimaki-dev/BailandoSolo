const { app, BrowserWindow, screen } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

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
    titleBarStyle: 'hiddenInset', // Estilo nativo de Mac
    backgroundColor: '#0f0c29',
    show: false // Don't show until ready
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    // Open DevTools for debugging only in dev mode
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'ui', 'dist', 'index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

function startPythonServer() {
  const isWin = process.platform === 'win32';
  const binName = isWin ? 'bailandosolo-server.exe' : 'bailandosolo-server';

  if (app.isPackaged) {
    // En producción, ejecutamos el binario empaquetado (PyInstaller)
    const binPath = path.join(process.resourcesPath, binName);
    console.log(`Iniciando servidor compilado: ${binPath}`);
    pythonProcess = spawn(binPath, [], {
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });
  } else {
    // En desarrollo, usamos el entorno virtual
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
