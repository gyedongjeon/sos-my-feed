[Setup]
AppId=local.sos-my-feed.reader-app
AppName=SOS My Feed
AppVersion={#Version}
DefaultDirName={localappdata}\Programs\SOS My Feed
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\release
OutputBaseFilename=SOS-My-Feed-Setup-{#Version}-x64
Compression=lzma2
SolidCompression=yes
DisableProgramGroupPage=yes

[Files]
Source: "{#PythonDir}\*"; DestDir: "{app}\python"; Flags: recursesubdirs ignoreversion
Source: "..\..\backend\desktop.py"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "..\..\backend\feeds.py"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "..\..\backend\server.py"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "..\..\frontend\dist\*"; DestDir: "{app}\frontend\dist"; Flags: recursesubdirs ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\SOS My Feed"; Filename: "{app}\python\python.exe"; Parameters: "-E -s -B ""{app}\backend\desktop.py"" --browser"; WorkingDir: "{app}"
