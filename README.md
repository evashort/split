## Test cases
- [colors.json](colors.json) from
https://www.sitepoint.com/colors-json-example/

- [WhoisRIR.java](WhoisRIR.java) from
https://mkyong.com/java/java-enum-example/

- [RSVPAgent.log](RSVPAgent.log) from
https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2.hald001/exmlogfile.htm

- [colors2.json](colors2.json) from https://jonasjacek.github.io/colors/

## Building the web version (based on the [MDN WebAssembly docs](https://developer.mozilla.org/en-US/docs/WebAssembly/C_to_wasm))
### First-time setup
Run this wherever your git repos normally live:
```bash
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh
```
`emsdk_env.sh` needs to be run via the `source` command as shown in order
for the changes to persist after the script exits. Confusingly, the
`emsdk activate` command also claims to be setting the same environment
variables but the changes don't persist after it exits.

Note: When I first ran the install command, it failed with an error about not
being able to access `python3`. I ran
```bash
which python3
```
and saw that it referred to a Python installation in a Windows system folder.
I fixed the error by copying `python.exe` and renaming it to `python3.exe`

### Future terminal sessions
You will have to re-run this command
```bash
source ./emsdk_env.sh
```
at the beginning of every terminal session before you can build the code.
`emsdk` provides a command to set the environment permanently but I wouldn't
recommend it because it overrides the locations of `python`, `java`,
and `npm`.

Instead, I recommend editing `~/.bashrc` to create an alias like this:
```bash
alias emsdk_env='source ~/git/emsdk/emsdk_env.sh'
```

Note: I use [Git Bash](https://gitforwindows.org/) on Windows, and after
creating `~/.bashrc` I got a warning that `.bashrc` was found but
`.bash_profile` was not. Fortunately, Git Bash automatically created
`~/.bash_profile` and the warning did not reappear.

### Building on Windows
The [Emscripten docs](https://emscripten.org/docs/getting_started/downloads.html)
point out that the setup commands can be run from Command Prompt or Powershell
on Windows with some slight modifications. Personally I use
[Git Bash](https://gitforwindows.org/) on Windows which allows me to run the
Unix commands as-is.

### Keeping emsdk up to date
Run this from the root of the `emsdk` repo:
```bash
git pull
./emsdk install latest
./emsdk activate latest
```

### Compiling
Run this from the `src` folder in this repo:
```bash
emcc main.cpp bestRepeatedPaths.cpp repeatedPaths.cpp -s WASM=1 -o main.html
```

### Running
If you open the generated `.html` file directly, it will not be able to load
the `.wasm` file because of browser restrictions on `file://` URLs.
Fortunately, Python has a built-in module that acts as a web server.

First, open a second terminal window to run the web server in.
Then run this command from the `src` folder in this repo:
```bash
python3 -m http.server
```

Finally, navigate to [localhost:8000](localhost:8000) in your browser
and click the link to open the generated `.html` file.

### Development
In order for VS Code to properly detect errors in your code, you will need to
install a normal, non-WebAssembly compiler.
#### Windows
1. Download [Microsoft C++ Build Tools](
    https://visualstudio.microsoft.com/visual-cpp-build-tools
)
1. Run the installer and check the box for "C++ build tools"
in the Workloads tab. The installation will take about 10 minutes
and you will have to restart your computer afterward.
1. From VS Code, install the C/C++ extension. It should be able to autodetect
the newly-installed MSVC compiler.

Note: I'm not sure what would happen if you installed the C/C++ extension
before the compiler. If you do that and it causes problems, try re-installing
the C/C++ extension.
