import zipfile, glob

def check_jars():
    for f in glob.glob("talend_jobs/*.jar"):
        try:
            with zipfile.ZipFile(f) as z:
                for info in z.infolist():
                    if 'context' in info.filename and 'Default.properties' in info.filename:
                        content = z.read(info.filename).decode('utf-8').strip()
                        if len(content.split('\n')) > 3: # Ignore empty standard ones
                            print(f"\n--- Context inside {f} ({info.filename}) ---")
                            print(content)
        except Exception as e:
            pass

if __name__ == "__main__":
    check_jars()
