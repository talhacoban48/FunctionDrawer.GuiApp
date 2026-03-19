#define AppName      "Function Drawer"
#define AppVersion   "1.0.0"
#define AppPublisher "FunctionDrawer"
#define AppExeName   "FunctionDrawer.exe"
#define AppSrcDir    "dist\FunctionDrawer"

[Setup]
AppId={{8B3F2E4A-C1D5-4A72-B8E9-3F6A2D1C9E45}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={commonpf32}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=FunctionDrawer_Setup_v{#AppVersion}
SetupIconFile=assets\favicon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; \
  Description: "Masaüstüne kısayol oluştur"; \
  GroupDescription: "Ek seçenekler:"; \
  Flags: unchecked

[Files]
Source: "{#AppSrcDir}\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";                         Filename: "{app}\{#AppExeName}"
Name: "{group}\{#AppName} Kaldır";                  Filename: "{uninstallexe}"
Name: "{commondesktop}\{#AppName}";                 Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; \
  Description: "{#AppName} Başlat"; \
  Flags: nowait postinstall skipifsilent
