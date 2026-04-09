"""
UPM by the universeOS project
Thriving to create distros that don't suck harder than Gentoo
"""


import os
import platform
import json
import subprocess
from pathlib import Path
import urllib.request
import ctypes
import time

class upm_mini:
    error = {
        1: "UPM_INSFAIL_UNKNOWN",
        2: "UPM_INSFAIL_RWFAIL",
        3: "UPM_INSFAIL_INCOMPAT",
        4: "UPM_INSFAIL_NOT_AN_ADMIN",
        5: "UPM_INSFAIL_INCORRECTARCH"
    }
    system = platform.system().lower()
    def __init__(self, root, debug):
        self.root = root
        system = self.system
        # It's a nasty fix but it gets upmd to initalize without errors

        if self.root == "" or self.root == "defaults":
            """
            We use the default path if none specified by upm-front.py
            If one is specified we set uniroot to it instead of /opt/upm or C:\\Windows\\System32\\drivers\\opt\\upm which are the default
            """
            if system == "linux":
                uniroot = Path("/opt/upm") # UNIX root
            elif system == "windows":
                uniroot = Path("C:/Windows/System32/drivers/opt/upm") # Windows root (because System32\drivers\etc is a little lonely)
        else:
            uniroot = Path(self.root)

        """
        Assign the cache, config and binary folders cuz I'm a cheesecake- what?
        """
        unicache = Path(f"{uniroot}/var/cache") # Keep the cache
        unibin = Path(f"{uniroot}/usr/bin")     # and binaries where upm-front expects them
        unicfg = Path(f"{uniroot}/etc/upm")

        if debug == 1 or debug == True:
            self.debug = 1
        elif debug == 0 or debug == False:
            self.debug = 0
        else:
            return """{
  "type": "unrecoverable",
  "where": {
    "file": "main.py",
    "linebegin": "44",
    "lineend": "49"
  },
  "stack": [
    "in class upm:",
    "def __init__(self, root, debug):",
    "...",
    "    self.debug = 0",
    "else",
    "    return ...    <",
    "Expected boolean or 0/1 but invalid data was provided"
  ]
}"""

        if not unicfg.exists():
            try:
                unicfg.mkdir(parents=True, exist_ok=True)
            except:
                ec = error[250]
                err = strings["error"][ec]
                print(f"UPM panicked in init!")
                if self.debug == 1:
                    debugerr = ", " + 250
                else:
                    debugerr = ""
                print(f"{err} [{ec}{debugerr}]")
                exit(250)

        if not uniroot.exists():
            try:
                uniroot.mkdir(parents=True, exist_ok=True)
            except:
                ec = error[250]
                err = strings["error"][ec]
                print(f"UPM panicked in init!")
                if self.debug == 1:
                    debugerr = ", " + 250
                else:
                    debugerr = ""
                print(f"{err} [{ec}{debugerr}]")
                exit(250)

        repo_config = Path(f"{unicfg}/repos.json")
        if not repo_config.exists():
            with open(repo_config, 'w') as out: # Writes the Team Zen defaults if the user nukes their repos.json somehow
                out.write("""{
    "donottouch": "lemon",
    "repos": {
        "tzor": "https://universeOS-project.github.io/packages/tzor"
    }
}""")

        """
        Finish by moving everything to global
        """
        self.uniroot = uniroot
        self.unicache = unicache
        self.unibin = unibin
        self.unicfg = unicfg

        unicache.mkdir(parents=True, exist_ok=True)
        unibin.mkdir(parents=True, exist_ok=True)

        self.strings = json.loads(self.get("https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/strings.json", "coconut", "uncached").read().decode())

    def get(self, url, filename, type):
        target = self.unicache / filename
        """
        For example, if the cache is /opt/upm/var/cache and the filename is lemon, it gets saved to /opt/upm/var/cache/lemon.
        """
        #print(f"Downloading {url} to {target}")
        try:
            # We use a user-agent because some idiots block python's default. Plus we just look better with one
            req = urllib.request.Request(url, headers={'User-Agent': 'universeOS-UPM'})
            if type == "uncached":
                package = urllib.request.urlopen(req)
                return(package)
                """
                If you actually use the non-cached version for
                actual packages and not some manifest, god help ya.
                """
            elif type == "cached":
                with urllib.request.urlopen(req) as response, open(target, 'wb') as out:
                    out.write(response.read())
            return(f"{target}")
        except Exception as e:
            return(e)

    def execute(self, manifest, base, script, package_name):
        """
        This reads the manifest of a package and executes it.
        """
        error = self.error
        strings = self.strings
        import tempfile

        if self.debug == 1:
            print(manifest)

        if self.system == "windows":
            suffix = ".bat"
            header = "@echo off\n"
            setvar = "set"
            runwith = "cmd"
            args = "/c"
        else:
            suffix = ""
            header = "#!/bin/bash\n"
            setvar = "export"
            runwith = "bash"
            args = ""

        # "I'M GONNA MAKE MY ENGINEERS MAKE A COMBUSTABLE LEMON THAT BURNS YOUR HOUSE DOWN"
        #    - Cave Johnson

        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            spath = f.name
            f.write(header)

            for key, value in manifest[f'installenv_{self.system}'].items():
                f.write(f"{setvar} {key}={value}\n")

            for i in manifest[f"{script}script_{self.system}"]:
                f.write(f"\n{i}")
        if self.system != "windows":
            os.chmod(spath, 0o755)

        try:
            if self.system == "windows":
                subprocess.run([runwith, args, spath], check=True)
            else:
                subprocess.run([runwith, spath], check=True)
        except:
            ec = error[1]
            err = strings["error"][ec]
            #if self.debug == 0:
            print(f"Could not install the package {package_name}:")
            if self.debug == 1:
                debugerr = ", " + 1
            else:
                debugerr = ""
            print(f"{err} [{ec}{debugerr}]")
            exit(1)

        os.remove(spath)

error = {
    1: "UPM_INSFAIL_UNKNOWN",
    2: "UPM_INSFAIL_RWFAIL",
    3: "UPM_INSFAIL_INCOMPAT",
    4: "UPM_INSFAIL_NOT_AN_ADMIN",
    5: "UPM_INSFAIL_INCORRECTARCH"
}
print("--- UPM Installation Tool ---")
print("\n[*] Welcome to the UPM installer.")
debug = os.environ.get("DEBUG")
if debug == "1":
    print("[!] Warning: You are entering debug mode.")
    print("[!] This is intended for developers. It **will** create a messy output designed for debugging.")
    print("[?] Do you still want to enter debug mode?")
    response = input("[Y/N] ").lower()
    if response == "y":
        print("Entering debug mode...")
        debugSet = 1
    else:
        debugSet = 0
else:
    debugSet = 0

if platform.machine().lower() == "aarch64":
    print("[!] UPM does not support ARM at the moment.")
    print("[!] ARM support will be addressed in the future.")
    print("[!] That will **not** be today however.")
    req = urllib.request.Request(f"https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/strings.json?v={time.time()}", headers={'User-Agent': 'universeOS-UPM'})
    package = urllib.request.urlopen(req)
    strings = json.loads(package.read().decode())
    rc = 5
    ec = error[rc]
    if debugSet == 1:
        print(strings)
    err = strings["error"][ec]
    debugerr = ""
    print(f"[!] {err} [{ec}{debugerr}]")
    exit(rc)
elif platform.machine().lower() == "i386":
    print("[!] UPM does not support x86.")
    print("[!] We will not support x86 ever.")
    print("[!] Also why are you still using x86 it's literally gonna expire in like 2032")
    req = urllib.request.Request(f"https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/strings.json?v={time.time()}", headers={'User-Agent': 'universeOS-UPM'})
    package = urllib.request.urlopen(req)
    strings = json.loads(package.read().decode())
    rc = 5
    ec = error[rc]
    if debugSet == 1:
        print(strings)
    err = strings["error"][ec]
    debugerr = ""
    print(f"[!] {err} [{ec}{debugerr}]")
    exit(rc)

if platform.system().lower() == "linux":
    if os.getuid() != 0:
        req = urllib.request.Request(f"https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/strings.json?v={time.time()}", headers={'User-Agent': 'universeOS-UPM'})
        package = urllib.request.urlopen(req)
        strings = json.loads(package.read().decode())
        rc = 4
        ec = error[rc]
        if debugSet == 1:
            print(strings)
        err = strings["error"][ec]
        debugerr = ""
        print(f"[!] {err} [{ec}{debugerr}]")
        exit(rc)
elif platform.system().lower() == "windows":
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        req = urllib.request.Request(f"https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/strings.json?v={time.time()}", headers={'User-Agent': 'universeOS-UPM'})
        package = urllib.request.urlopen(req)
        strings = json.loads(package.read().decode())
        rc = 4
        ec = error[rc]
        if debugSet == 1:
            print(strings)
        err = strings["error"][ec]
        debugerr = ""
        print(f"[!] {err} [{ec}{debugerr}]")
        exit(rc)
elif platform.system().lower() == "android":
    print("""[!] Android support is coming soon. When?
    ¯\\_(ツ)_/¯
""")
    req = urllib.request.Request(f"https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/strings.json?v={time.time()}", headers={'User-Agent': 'universeOS-UPM'})
    package = urllib.request.urlopen(req)
    strings = json.loads(package.read().decode())
    rc = 3
    ec = error[rc]
    err = strings["error"][ec]
    debugerr = ""
    print(f"[!] {err}{platform.system()} [{ec}{debugerr}]")
    exit(rc)
else:
    print("""[!] You appear to be on either macOS or FreeBSD.
    We do not support macOS/BSD and we have no plans to.
""")
    req = urllib.request.Request(f"https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/strings.json?v={time.time()}", headers={'User-Agent': 'universeOS-UPM'})
    package = urllib.request.urlopen(req)
    strings = json.loads(package.read().decode())
    rc = 3
    ec = error[rc]
    err = strings["error"][ec]
    debugerr = ""
    print(f"[!] {err}{platform.system()} [{ec}{debugerr}]")
    exit(rc)

print("[?] Do you want to install UPM right now?")
response = input("[Y/N]: ")
if response.lower() != "y":
    print("[!] Aborted by user.")
    exit()

print("[*] Starting UPM mini...")

try:
    uMini = upm_mini("defaults", debugSet)
except Exception as e:
    print(f"[!] UPM mini panicked during startup!")
    print(f"[!] {e}")
    exit()

uManifest = uMini.get(f"https://raw.githubusercontent.com/universeOS-project/upm/refs/heads/main/installer/manifest.json?v={time.time()}", "coconut", "uncached")
print("[*] Executing UPM installer...")
uMini.execute(json.loads(uManifest.read().decode()), None, "install", "upm")
print("[*] All done!")
print("[*] Restart your terminal and then run upm. It should work.")
print("[*] Or not. I didn't check if it worked. The installer should've exited if it failed however.")
print("[*] Keyword if.")

