import os
import shutil
import xml.etree.ElementTree as ET


def configure_opengl_libs(vcproj_path, freeglut_dir, glew_dir):
    """
    Configures an MSVC .vcxproj file to include paths and dependencies for
    OpenGL libraries like FreeGLUT and GLEW.
    """
    if not os.path.isfile(vcproj_path):
        print(f"❌ ERROR: Project file not found at '{vcproj_path}'")
        return

    project_dir = os.path.dirname(vcproj_path)

    # --- Library Definitions ---
    # Define all libraries to be configured here. The script will loop through them.
    libs_to_configure = [
        {
            "name": "FreeGLUT",
            "root_dir": freeglut_dir,
            "lib_name": "freeglut.lib",
            "dll_name": "freeglut.dll",
            "lib_subdir": os.path.join("lib", "x64"),
            "dll_subdir": os.path.join("bin", "x64")
        },
        {
            "name": "GLEW",
            "root_dir": glew_dir,
            "lib_name": "glew32.lib",
            "dll_name": "glew32.dll",
            # GLEW binary releases often have this structure
            "lib_subdir": os.path.join("lib", "Release", "x64"),
            "dll_subdir": os.path.join("bin", "Release", "x64")
        }
    ]

    # --- Load and Prepare XML Document ---
    try:
        tree = ET.parse(vcproj_path)
        root = tree.getroot()
    except ET.ParseError:
        print(f"❌ ERROR: Could not parse the XML file. Is '{vcproj_path}' a valid .vcxproj file?")
        return

    # Extract the XML namespace (crucial for MSVC projects)
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0].strip("{")
    ET.register_namespace("", ns)

    def qname(tag):
        return f"{{{ns}}}{tag}" if ns else tag

    # --- Process Each Library ---
    libs_were_configured = False
    for lib_info in libs_to_configure:
        name = lib_info["name"]
        root_dir = lib_info["root_dir"]

        if not root_dir or not os.path.isdir(root_dir):
            print(f"ℹ️ Path for {name} not provided or invalid. Skipping.")
            continue

        print(f"\n--- Configuring {name} ---")
        libs_were_configured = True

        # Construct paths from root directory
        include_path = os.path.join(root_dir, "include")
        lib_path = os.path.join(root_dir, lib_info["lib_subdir"])
        dll_path = os.path.join(root_dir, lib_info["dll_subdir"], lib_info["dll_name"])
        linker_lib = lib_info["lib_name"]

        # 1. Copy DLL to the project's output directory
        if os.path.isfile(dll_path):
            shutil.copy(dll_path, project_dir)
            print(f"✅ Copied {lib_info['dll_name']} to project directory.")
        else:
            print(f"⚠️ WARNING: DLL not found at '{dll_path}'. Please copy it manually.")

        # 2. Add Include and Library paths to all x64 configurations
        for item_group in root.findall(qname("ItemDefinitionGroup")):
            condition = item_group.attrib.get("Condition", "")
            if "x64" not in condition:
                continue

            # Add Include Path
            cl_compile = item_group.find(qname("ClCompile"))
            if cl_compile is not None:
                inc_dirs = cl_compile.find(qname("AdditionalIncludeDirectories"))
                if inc_dirs is None:
                    inc_dirs = ET.SubElement(cl_compile, qname("AdditionalIncludeDirectories"))
                    inc_dirs.text = f"{include_path};%(AdditionalIncludeDirectories)"
                elif include_path not in (inc_dirs.text or ""):
                    inc_dirs.text = f"{include_path};{inc_dirs.text}"

            # Add Library Path
            link = item_group.find(qname("Link"))
            if link is not None:
                lib_dirs = link.find(qname("AdditionalLibraryDirectories"))
                if lib_dirs is None:
                    lib_dirs = ET.SubElement(link, qname("AdditionalLibraryDirectories"))
                    lib_dirs.text = f"{lib_path};%(AdditionalLibraryDirectories)"
                elif lib_path not in (lib_dirs.text or ""):
                    lib_dirs.text = f"{lib_path};{lib_dirs.text}"

        print(f"✅ Added Include and Library paths for {name}.")

        # 3. Add Linker Dependency
        for item_group in root.findall(qname("ItemDefinitionGroup")):
            condition = item_group.attrib.get("Condition", "")
            if "x64" not in condition:
                continue

            link = item_group.find(qname("Link"))
            if link is not None:
                deps = link.find(qname("AdditionalDependencies"))
                if deps is None:
                    deps = ET.SubElement(link, qname("AdditionalDependencies"))
                    deps.text = f"{linker_lib};%(AdditionalDependencies)"
                elif linker_lib not in (deps.text or ""):
                    deps.text = f"{linker_lib};{deps.text}"

        print(f"✅ Added '{linker_lib}' to linker dependencies.")

    # --- Finalize and Save ---
    if libs_were_configured:
        backup_path = vcproj_path + ".bak"
        print(f"\nSaving changes...")
        shutil.copy2(vcproj_path, backup_path)
        print(f"✅ Backup of original project file saved to '{backup_path}'")

        tree.write(vcproj_path, encoding="utf-8", xml_declaration=True)
        print("🎉 Configuration applied successfully!")
    else:
        print("\nNo libraries were configured.")


if __name__ == "__main__":
    print("=== Visual Studio OpenGL Library Configurator ===")
    print("This script will modify your .vcxproj file to link FreeGLUT and GLEW.")
    print("Leave a path blank to skip configuration for that library.\n")

    vcproj = input("Enter the path to your .vcxproj file: ").strip('" ')
    freeglut = input("Enter the path to the FreeGLUT root folder: ").strip('" ')
    glew = input("Enter the path to the GLEW root folder: ").strip('" ')

    configure_opengl_libs(vcproj, freeglut, glew)
