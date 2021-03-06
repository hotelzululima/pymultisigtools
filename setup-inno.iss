; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "pymultsigtools"
#define MyAppVersion "0.02.01"
#define MyAppExeName "pymultisigtool.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5FC97E7A-CF1B-45C5-94A2-385B3D2D532F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
DefaultDirName={pf}\pymultisigtools
DefaultGroupName=pymultisigtools
AllowNoIcons=yes
LicenseFile=E:\pymultisigtools\LICENSE
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "E:\pymultisigtools\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "E:\pymultisigtools\vcredist_x86.exe"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall
Source: "E:\pymultisigtools\vcredist_x86_2010.exe"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{tmp}\vcredist_x86.exe"; Parameters: "/q"; StatusMsg: "Installing Visual C++ Runtime redistributable..."
Filename: "{tmp}\vcredist_x86_2010.exe"; Parameters: "/q"; StatusMsg: "Installing Visual C++ Runtime redistributable..."
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

