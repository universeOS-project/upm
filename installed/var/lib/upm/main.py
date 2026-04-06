"""
upmd by the universeOS project
Thriving to create distros that don't suck harder than Gentoo
"""

import os 
import platform 
import json     
import subprocess 
from pathlib import Path
import urllib.request
import socket

class upm:
    error = {
        1: "UPM_INSFAIL_UNKNOWN",
        2: "UPM_INSFAIL_NOTFOUND",
        3: "UPM_INSFAIL_INCOMPAT",
        10: "UPM_UPDFAIL_READFAIL",
        250: "UPM_INTFAIL_WRITEFAIL",
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

        with open(f"{unicfg}/repos.json", "r") as dnttl:
            dntthl = json.load(dnttl)
            self.lemon = dntthl["donottouch"]
            if self.lemon != "lemon":
                exit(257)

        """
        Finish by moving everything to global
        """
        self.uniroot = uniroot
        self.unicache = unicache
        self.unibin = unibin
        self.unicfg = unicfg

        unicache.mkdir(parents=True, exist_ok=True)
        unibin.mkdir(parents=True, exist_ok=True)

    def cheesecake(self):
        print("Development info:")
        print(f"UniBIN: {self.unibin}\nUniCACHE: {self.unicache}\nUniROOT: {self.uniroot}")

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

    def install(self, package):
        """
        The exciting part. This actually installs packages
        """
        error = self.error
        uniroot = self.uniroot
        unicache = self.unicache
        unibin = self.unibin

        repo, pkg = self.search(package)
        if self.debug == 1:
            print(repo, pkg)

        with open("strings.json", "r") as strings_js:
            strings = json.load(strings_js)

        if pkg == None:
            ec = error[repo]
            err = strings["error"][ec]
            #if self.debug == 0:
            print(f"Could not install the package {package}:")
            if self.debug == 1: 
                debugerr = ", " + repo
            else:
                debugerr = ""
            print(f"{err} [{ec}{debugerr}]")
            return

        with open(f"{uniroot}/etc/upm/repos.json", "r") as reposa:
            repolist = json.load(reposa)
            if self.debug == 1:
                print(f"{reposa}\n\n{repolist}")

        if self.debug == 1:
            print(repolist)

        for y, z in repolist["repos"].items():
            if y == repo:
                base_url = z
                if self.debug == 1:
                    print(base_url)

        with open(f"{unicache}/{repo}/packages.json", "r") as pkglistj:
            pkglist = json.load(pkglistj)
            if self.debug == 1:
                print(f"{pkglistj}\n\n{pkglist}")

        """
        for y, z in pkglist.items():
            if self.debug == 1:
                print(y, z)
            if y == pkg:
                full_url = f"{base_url}{z}"
                if self.debug == 1:
                    print(z, full_url)
                break
        """

        full_url = f"{base_url}{pkg}"
        if self.debug == 1:
            print(base_url, pkg, full_url)

        manifestj = self.get(full_url, "", "uncached")
        manifest = json.loads(manifestj.read().decode('utf-8'))

        if self.debug == 1:
            print(f"Raw JSON: {manifestj}\n\nPython: {manifest}")

        if self.system in manifest["workswith"]:
            rc = 0
        else:
            rc = 3
            ec = error[rc]
            err = strings["error"][ec]

        if rc != 0:
            print(f"{err} [{ec}]")
            return

        self.execute(manifest, base_url, "install", package)

    def execute(self, manifest, base, script, package_name):
        """
        This reads the manifest of a package and executes it.
        """
        error = self.error
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
            f.write(f"""
{setvar} REPO_SOURCE=\"{base}\"
{setvar} UNIROOT=\"{self.uniroot}\"
{setvar} UNICACHE=\"{self.unicache}\"
{setvar} UNIBIN=\"{self.unibin}\"""")

            f.write("\n\n")

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
            print(f"Could not install the package {package}:")
            if self.debug == 1:
                debugerr = ", " + 1
            else:
                debugerr = ""
            print(f"{err} [{ec}{debugerr}]")
            return

        os.remove(spath)

        self.updatedb("add", package_name, manifest['version'])

    def updatedb(self, opt, package, pkgver):
        uniroot = self.uniroot

        uniins = Path(f"{uniroot}/etc/upm/packages.json")
        if os.path.exists(uniins):
            with open (uniins, "r") as f:
                db = json.load(f)
        else:
            db = {}

        if opt == "add":
            db[package] = pkgver
            rc = 0
        elif opt == "rm":
            if self.updatedb("fi", package, 0) != 21:
                del db[package]
                rc = 0
            else:
                rc = 20
        elif opt == "fi":
            if package in db:
                rc = db[package]
            else:
                rc = 21

        with open(uniins, "w") as f:
            json.dump(db, f)

        return rc


    def search(self, package):
        packagerepos = []
        for file_path in self.unicache.glob("*/packages.json"):
            packagerepos.append(file_path)

        for i in packagerepos:
            with open(i, 'r') as a:
                packagerepo = json.load(a)
            pkg = packagerepo.get(package)
            if pkg:
                repo_short = i.parent.name
                return repo_short, pkg
        return 2, None

    def update(self):
        """
        Refreshes local package index
        """

        unicache = self.unicache
        uniroot = self.uniroot
        unibin = self.unibin

        repo_config = self.uniroot / "etc" / "upm" / "repos.json" 

        if not repo_config.exists():
            with open(repo_config, 'w') as out: # Writes the Team Zen defaults if the user nukes their repos.json somehow
                out.write("""{
    "donottouch": "lemon",
    "repos": {
        "tzor": "https://universeOS-project.github.io/packages/tzor"
    }
}""")

        with open(repo_config, 'r') as repolist:
            try:
                cfg = json.load(repolist)
            except:
                ec = self.error[10]
                with open("strings.json", "r") as strings_js:
                    strings = json.load(strings_js)
                err = strings["error"][ec]
                if self.debug == 1: 
                    debugerr = ", " + repo
                print(f"{err} [{ec}{debugerr}]")


        # o i'M a pOTaTo

        for k, v in cfg["repos"].items():
            print(f"Updating {k}...")
        
            repopath = self.unicache / k
            repopath.mkdir(parents=True, exist_ok=True)

            self.get(f"{v}/packages.json", repopath / "packages.json", "cached")

        print("All packages up to date.")

#upmd = upm("defaults")
#print(upmd.cheesecake())
