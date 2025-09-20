import os
import shutil
import xml.etree.ElementTree as ET

def configure_freeglut(vcproj_path, freeglut_dir):
    if not os.path.isfile(vcproj_path):
        print(f"ERROR: {vcproj_path} does not exist")
        return

    project_dir = os.path.dirname(vcproj_path)
    include_path = os.path.join(freeglut_dir, "include")
    lib_path = os.path.join(freeglut_dir, "lib", "x64")
    dll_path = os.path.join(freeglut_dir, "bin", "x64", "freeglut.dll")

    # Copy DLL into project folder
    if os.path.isfile(dll_path):
        shutil.copy(dll_path, project_dir)
        print(f"Copied DLL -> {project_dir}")
    else:
        print(f"WARNING: {dll_path} not found, skipping DLL copy.")

    # Load and parse XML
    tree = ET.parse(vcproj_path)
    root = tree.getroot()

    # Extract namespace
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0].strip("{")
    ET.register_namespace("", ns)

    def qname(tag):
        return f"{{{ns}}}{tag}" if ns else tag

    configs = ["'$(Configuration)|$(Platform)'=='Debug|x64'",
               "'$(Configuration)|$(Platform)'=='Release|x64'"]

    for cond in configs:
        pg = None
        for group in root.findall(qname("PropertyGroup")):
            if group.attrib.get("Condition") == cond and group.attrib.get("Label", "") != "Configuration":
                pg = group
                break

        if pg is None:
            pg = ET.SubElement(root, qname("PropertyGroup"))
            pg.set("Condition", cond)

        # Add include/lib paths
        include_elem = pg.find(qname("IncludePath"))
        if include_elem is None:
            include_elem = ET.SubElement(pg, qname("IncludePath"))
            include_elem.text = f"{include_path};$(IncludePath)"
        elif include_path not in include_elem.text:
            include_elem.text = f"{include_path};" + include_elem.text

        lib_elem = pg.find(qname("LibraryPath"))
        if lib_elem is None:
            lib_elem = ET.SubElement(pg, qname("LibraryPath"))
            lib_elem.text = f"{lib_path};$(LibraryPath)"
        elif lib_path not in lib_elem.text:
            lib_elem.text = f"{lib_path};" + lib_elem.text

    # Add linker dependencies into Debug/Release x64
    for idg in root.findall(qname("ItemDefinitionGroup")):
        cond = idg.attrib.get("Condition", "")
        if "x64" not in cond:
            continue

        link = idg.find(qname("Link"))
        if link is None:
            link = ET.SubElement(idg, qname("Link"))

        deps = link.find(qname("AdditionalDependencies"))
        if deps is None:
            deps = ET.SubElement(link, qname("AdditionalDependencies"))
            deps.text = "freeglut.lib;opengl32.lib;glu32.lib;%(AdditionalDependencies)"
        else:
            current = deps.text or "%(AdditionalDependencies)"
            if "freeglut.lib" not in current:
                current = "freeglut.lib;" + current
            if "opengl32.lib" not in current:
                current = "opengl32.lib;" + current
            if "glu32.lib" not in current:
                current = "glu32.lib;" + current
            deps.text = current

    # Backup and save
    backup = vcproj_path + ".bak"
    shutil.copy2(vcproj_path, backup)
    print(f"Backup saved as {backup}")

    tree.write(vcproj_path, encoding="utf-8", xml_declaration=True)
    print("✅ FreeGLUT configuration applied successfully.")

if __name__ == "__main__":
    print("=== FreeGLUT Visual Studio Configurator ===\nCreated by: VanjDev")
    vcproj = input("Enter path to your .vcxproj file: ").strip('" ')
    freeglut = input("Enter path to FreeGLUT root folder: ").strip('" ')

    configure_freeglut(vcproj, freeglut)
