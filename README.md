# AutoFGLUT

AutoFGLUT is a lightweight automation tool that configures [FreeGLUT](https://www.transmissionzero.co.uk/software/freeglut-devel/) for Visual Studio C++ projects.  
It saves you from the manual hassle of setting up include directories, library paths, and linker dependencies.

## ✨ Features
- Automatically updates your `.vcxproj` file:
  - Adds FreeGLUT include path
  - Adds FreeGLUT library path
  - Injects linker dependencies (`freeglut.lib`, `opengl32.lib`, `glu32.lib`)
- Copies `freeglut.dll` into your project directory
- Creates a `.bak` backup of your project before modifying it
- Works for both **Debug|x64** and **Release|x64**

## 📦 Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/AutoFGLUT.git
   cd AutoFGLUT
