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
```
Note: You will have to omit the `./` if running from Windows Command Prompt

Note: Make sure `python3` is pointing to the right Python executable
before running the install command. For me, `python` was pointing to the right
executable but `python3` was pointing to some internal Windows Python
installation.

### Keeping emsdk up to date
Run this from the root of the `emsdk` repo:
```bash
git pull
./emsdk install latest
```

### Environment setup (once per terminal session)
Run this from the root of the `emsdk` repo:
#### Unix
```bash
./emsdk activate latest
source ./emsdk_env.sh
```
#### Windows
```bat
emsdk activate latest
emsdk_env.bat
```

### Compiling
Run this from the `src` folder in this repo:
```bash
emcc hello.c -s WASM=1 -o hello.html
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
