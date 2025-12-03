const { app, BrowserWindow, screen } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: Math.round(width * 0.9),
    height: Math.round(height * 0.9),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    titleBarStyle: 'hiddenInset', // Estilo nativo de Mac
    backgroundColor: '#0f0c29',
    show: false // Don't show until ready
  });

  mainWindow.loadFile(path.join(__dirname, 'ui', 'dist', 'index.html'));

  // Open DevTools for debugging
  mainWindow.webContents.openDevTools();

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

function startPythonServer() {
  // Asumimos que el venv ya está creado en la carpeta del proyecto
  // Determine python path based on platform
  const isWin = process.platform === 'win32';
  const pythonExecutable = isWin ? 'python.exe' : 'python3';
  const venvPath = isWin ? path.join('venv', 'Scripts') : path.join('venv', 'bin');
  const pythonPath = path.join(__dirname, venvPath, pythonExecutable);
  const scriptPath = path.join(__dirname, 'server.py');

  console.log(`Iniciando servidor Python: ${pythonPath} ${scriptPath}`);

  pythonProcess = spawn(pythonPath, [scriptPath]);

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
