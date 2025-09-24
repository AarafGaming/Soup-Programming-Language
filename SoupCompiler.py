import sys
import os
import json
import time
import random
import webbrowser
import requests
import subprocess
import getpass
import argparse

# Map SoupLang commands to Python equivalents
SOUP_COMMAND_MAP = {
    "log": "print",
    "file_read": "open",
    "file_write": "open",
    "file_delete": "os.remove",
    "exists": "os.path.exists",
    "create": "open",
    "read_json": "json.load",
    "write_json": "json.dump",
    "time_read": "time.time",
    "wait": "time.sleep",
    "format_time": "time.strftime",
    "current_time": "time.strftime",
    "current_time_int": "int(time.strftime)",
    "random_int": "random.randint",
    "url_open": "webbrowser.open",
    "url_new_tab": "webbrowser.open_new_tab",
    "url_open_new": "webbrowser.open_new",
    "url_new_window": "webbrowser.open_new_window",
    "url_get": "requests.get",
    "log_clear": "os.system",
    "cmd": "subprocess.run",
    "length": "len",
    "clear_screen": "print",
    "getcwd": "os.getcwd",
    "change_dir": "os.chdir",
    "list_dir": "os.listdir",
    "make_dir": "os.makedirs",
    "remove_dir": "os.rmdir",
    "rename": "os.rename",
    "join_path": "os.path.join",
    "split_path": "os.path.split",
    "get_env": "os.getenv",
    "set_env": "os.environ.__setitem__",
    "del_env": "os.environ.__delitem__",
    "is_file": "os.path.isfile",
    "is_dir": "os.path.isdir",
    "file_size": "os.path.getsize",
    "file_copy": "shutil.copy",
    "file_move": "shutil.move",
    "file_stat": "os.stat",
    "file_abspath": "os.path.abspath",
    "file_basename": "os.path.basename",
    "file_dirname": "os.path.dirname",
    "file_splitext": "os.path.splitext",
    "file_walk": "os.walk",
    "system_platform": "sys.platform",
    "system_version": "sys.version",
    "system_exit": "sys.exit",
    "system_argv": "sys.argv",
    "system_argc": "len(sys.argv)",
    "system_python": "sys.executable",
    "python_version": "sys.version",
    "python_implementation": "sys.implementation.name",
    "python_executable": "sys.executable",
    "python_path": "sys.path",
    "python_modules": "list(sys.modules.keys())",
    "python_exit": "sys.exit",
    "python_argv": "sys.argv",
    "python_argc": "len(sys.argv)",
    "python_getframe": "sys._getframe",
    "python_recursionlimit": "sys.getrecursionlimit",
    "python_setrecursionlimit": "sys.setrecursionlimit",
    "python_getrefcount": "sys.getrefcount",
    "python_getsizeof": "sys.getsizeof",
    "python_getdefaultencoding": "sys.getdefaultencoding",
    "python_getfilesystemencoding": "sys.getfilesystemencoding",
    "python_getwindowsversion": "sys.getwindowsversion",
    "python_getprofile": "sys.getprofile",
    "python_setprofile": "sys.setprofile",
    "python_gettrace": "sys.gettrace",
    "python_settrace": "sys.settrace",
    "python_getallocatedblocks": "sys.getallocatedblocks",
    "python_gettotalrefcount": "sys.gettotalrefcount",
    "python_getobjects": "sys.getobjects",
    "clearcache": "sys._clear_internal_caches",
    "flush": "sys.stdout.flush",
    "stderr_flush": "sys.stderr.flush",
    "stdin_read": "sys.stdin.read",
    "stdin_readline": "sys.stdin.readline",
    "stdin_readlines": "sys.stdin.readlines",
    "stdout_write": "sys.stdout.write",
    "stdout_writelines": "sys.stdout.writelines",
    "stderr_write": "sys.stderr.write",
    "stderr_writelines": "sys.stderr.writelines",
    "getpass_prompt": "getpass.getpass",
    "getuser": "getpass.getuser",
    "getfilename": "os.path.basename(__file__)",
    "getfiledir": "os.path.dirname(os.path.abspath(__file__))",
    "getfilesplit": "os.path.splitext(os.path.basename(__file__))",
    "getfileabspath": "os.path.abspath(__file__)",
    "getfileexists": "os.path.exists(__file__)",
    "getfileisfile": "os.path.isfile(__file__)",
    "getfileisdir": "os.path.isdir(__file__)",
    "getfilesize": "os.path.getsize(__file__)",
    "getfilestat": "os.stat(__file__)",
    "getfilectime": "os.path.getctime(__file__)",
    "getfilemtime": "os.path.getmtime(__file__)",
    "getfileatime": "os.path.getatime(__file__)",
    "getfilebasename": "os.path.basename(__file__)",
    "getfiledirname": "os.path.dirname(__file__)",
    "clear": "os.system",
    "pause": "os.system",
    "arguments": "argparse.ArgumentParser",
}

class SoupLangCompiler:
    def __init__(self):
        self.output = []

    def compile_line(self, line):
        line = line.strip()
        if not line:
            return
        if line.startswith("#"):
            self.output.append(line)
            return
        if line.startswith("let "):
            parts = line[4:].split("=", 1)
            if len(parts) == 2:
                var = parts[0].strip()
                expr = parts[1].strip()
                self.output.append(f"{var} = {expr}")
            else:
                self.output.append(f"# Syntax error in assignment: {line}")
            return
        if line.startswith("print(") and line.endswith(")"):
            expr = line[6:-1].strip()
            self.output.append(f"print({expr})")
            return
        # Function call translation
        if "(" in line and line.endswith(")"):
            func_name = line[:line.find("(")].strip()
            args = line[line.find("(")+1:line.rfind(")")]
            py_func = SOUP_COMMAND_MAP.get(func_name)
            if py_func:
                # Special handling for log
                if func_name == "log":
                    self.output.append(f"print({args})")
                # file_read(path) -> open(path).read()
                elif func_name == "file_read":
                    self.output.append(f"open({args}).read()")
                # file_write(path, data) -> open(path, 'w').write(data)
                elif func_name == "file_write":
                    arglist = [a.strip() for a in args.split(",")]
                    if len(arglist) == 2:
                        self.output.append(f"open({arglist[0]}, 'w').write({arglist[1]})")
                    else:
                        self.output.append(f"# Syntax error in file_write: {line}")
                # file_delete(path) -> os.remove(path)
                elif func_name == "file_delete":
                    self.output.append(f"os.remove({args})")
                # exists(path) -> os.path.exists(path)
                elif func_name == "exists":
                    self.output.append(f"os.path.exists({args})")
                # create(path, data) -> open(path, 'w').write(data)
                elif func_name == "create":
                    arglist = [a.strip() for a in args.split(",")]
                    if len(arglist) == 2:
                        self.output.append(f"open({arglist[0]}, 'w').write({arglist[1]})")
                    elif len(arglist) == 1:
                        self.output.append(f"open({arglist[0]}, 'w').write(\"\")")
                    else:
                        self.output.append(f"# Syntax error in create: {line}")
                # read_json(path) -> json.load(open(path))
                elif func_name == "read_json":
                    self.output.append(f"json.load(open({args}))")
                # write_json(path, data) -> json.dump(data, open(path, 'w'))
                elif func_name == "write_json":
                    arglist = [a.strip() for a in args.split(",")]
                    if len(arglist) == 2:
                        self.output.append(f"json.dump({arglist[1]}, open({arglist[0]}, 'w'))")
                    else:
                        self.output.append(f"# Syntax error in write_json: {line}")
                # wait(seconds) -> time.sleep(seconds)
                elif func_name == "wait":
                    self.output.append(f"time.sleep({args})")
                # url_open(url) -> webbrowser.open(url)
                elif func_name == "url_open":
                    self.output.append(f"webbrowser.open({args})")
                # url_new_tab(url) -> webbrowser.open_new_tab(url)
                elif func_name == "url_new_tab":
                    self.output.append(f"webbrowser.open_new_tab({args})")
                # url_open_new(url) -> webbrowser.open_new({args})
                elif func_name == "url_open_new":
                    self.output.append(f"webbrowser.open_new({args})")
                # url_new_window(url) -> webbrowser.open_new_window({args})
                elif func_name == "url_new_window":
                    self.output.append(f"webbrowser.open_new_window({args})")
                # url_get(url) -> requests.get(url).text
                elif func_name == "url_get":
                    self.output.append(f"requests.get({args}).text")
                # log_clear() -> os.system('cls' if os.name == 'nt' else 'clear')
                elif func_name == "log_clear":
                    self.output.append("os.system('cls' if os.name == 'nt' else 'clear')")
                # cmd(command) -> subprocess.run(command, shell=True, capture_output=True, text=True).stdout
                elif func_name == "cmd":
                    self.output.append(f"subprocess.run({args}, shell=True, capture_output=True, text=True).stdout")
                # length(item) -> len(item)
                elif func_name == "length":
                    self.output.append(f"len({args})")
                # clear_screen() -> print('\\033[H\\033[3J', end=\"\")
                elif func_name == "clear_screen":
                    self.output.append("print('\\033[H\\033[3J', end=\"\")")
                # getcwd() -> os.getcwd()
                elif func_name == "getcwd":
                    self.output.append("os.getcwd()")
                # change_dir(path) -> os.chdir(path)
                elif func_name == "change_dir":
                    self.output.append(f"os.chdir({args})")
                # list_dir(path) -> os.listdir(path)
                elif func_name == "list_dir":
                    self.output.append(f"os.listdir({args})")
                # make_dir(path) -> os.makedirs(path, exist_ok=True)
                elif func_name == "make_dir":
                    self.output.append(f"os.makedirs({args}, exist_ok=True)")
                # remove_dir(path) -> os.rmdir(path)
                elif func_name == "remove_dir":
                    self.output.append(f"os.rmdir({args})")
                # rename(old, new) -> os.rename(old, new)
                elif func_name == "rename":
                    self.output.append(f"os.rename({args})")
                # join_path(*args) -> os.path.join(*args)
                elif func_name == "join_path":
                    self.output.append(f"os.path.join({args})")
                # split_path(path) -> os.path.split(path)
                elif func_name == "split_path":
                    self.output.append(f"os.path.split({args})")
                # get_env(var) -> os.getenv(var)
                elif func_name == "get_env":
                    self.output.append(f"os.getenv({args})")
                # set_env(var, value) -> os.environ[var] = value
                elif func_name == "set_env":
                    arglist = [a.strip() for a in args.split(",")]
                    if len(arglist) == 2:
                        self.output.append(f"os.environ[{arglist[0]}] = {arglist[1]}")
                    else:
                        self.output.append(f"# Syntax error in set_env: {line}")
                # del_env(var) -> del os.environ[var]
                elif func_name == "del_env":
                    self.output.append(f"del os.environ[{args}]")
                # is_file(path) -> os.path.isfile(path)
                elif func_name == "is_file":
                    self.output.append(f"os.path.isfile({args})")
                # is_dir(path) -> os.path.isdir(path)
                elif func_name == "is_dir":
                    self.output.append(f"os.path.isdir({args})")
                # file_size(path) -> os.path.getsize(path)
                elif func_name == "file_size":
                    self.output.append(f"os.path.getsize({args})")
                # file_copy(src, dst) -> shutil.copy(src, dst)
                elif func_name == "file_copy":
                    self.output.append(f"shutil.copy({args})")
                # file_move(src, dst) -> shutil.move(src, dst)
                elif func_name == "file_move":
                    self.output.append(f"shutil.move({args})")
                # file_stat(path) -> os.stat(path)
                elif func_name == "file_stat":
                    self.output.append(f"os.stat({args})")
                # file_abspath(path) -> os.path.abspath(path)
                elif func_name == "file_abspath":
                    self.output.append(f"os.path.abspath({args})")
                # file_basename(path) -> os.path.basename(path)
                elif func_name == "file_basename":
                    self.output.append(f"os.path.basename({args})")
                # file_dirname(path) -> os.path.dirname(path)
                elif func_name == "file_dirname":
                    self.output.append(f"os.path.dirname({args})")
                # file_splitext(path) -> os.path.splitext(path)
                elif func_name == "file_splitext":
                    self.output.append(f"os.path.splitext({args})")
                # file_walk(path) -> os.walk(path)
                elif func_name == "file_walk":
                    self.output.append(f"os.walk({args})")
                # system_platform() -> sys.platform
                elif func_name == "system_platform":
                    self.output.append("sys.platform")
                # system_version() -> sys.version
                elif func_name == "system_version":
                    self.output.append("sys.version")
                # system_exit(code) -> sys.exit(code)
                elif func_name == "system_exit":
                    self.output.append(f"sys.exit({args})")
                # system_argv() -> sys.argv
                elif func_name == "system_argv":
                    self.output.append("sys.argv")
                # system_argc() -> len(sys.argv)
                elif func_name == "system_argc":
                    self.output.append("len(sys.argv)")
                # system_python() -> sys.executable
                elif func_name == "system_python":
                    self.output.append("sys.executable")
                # python_version() -> sys.version
                elif func_name == "python_version":
                    self.output.append("sys.version")
                # python_implementation() -> sys.implementation.name
                elif func_name == "python_implementation":
                    self.output.append("sys.implementation.name")
                # python_executable() -> sys.executable
                elif func_name == "python_executable":
                    self.output.append("sys.executable")
                # python_path() -> sys.path
                elif func_name == "python_path":
                    self.output.append("sys.path")
                # python_modules() -> list(sys.modules.keys())
                elif func_name == "python_modules":
                    self.output.append("list(sys.modules.keys())")
                # python_exit(code) -> sys.exit(code)
                elif func_name == "python_exit":
                    self.output.append(f"sys.exit({args})")
                # python_argv() -> sys.argv
                elif func_name == "python_argv":
                    self.output.append("sys.argv")
                # python_argc() -> len(sys.argv)
                elif func_name == "python_argc":
                    self.output.append("len(sys.argv)")
                # python_getframe(depth) -> sys._getframe(depth)
                elif func_name == "python_getframe":
                    self.output.append(f"sys._getframe({args})")
                # python_recursionlimit() -> sys.getrecursionlimit()
                elif func_name == "python_recursionlimit":
                    self.output.append("sys.getrecursionlimit()")
                # python_setrecursionlimit(limit) -> sys.setrecursionlimit(limit)
                elif func_name == "python_setrecursionlimit":
                    self.output.append(f"sys.setrecursionlimit({args})")
                # python_getrefcount(obj) -> sys.getrefcount(obj)
                elif func_name == "python_getrefcount":
                    self.output.append(f"sys.getrefcount({args})")
                # python_getsizeof(obj) -> sys.getsizeof(obj)
                elif func_name == "python_getsizeof":
                    self.output.append(f"sys.getsizeof({args})")
                # python_getdefaultencoding() -> sys.getdefaultencoding()
                elif func_name == "python_getdefaultencoding":
                    self.output.append("sys.getdefaultencoding()")
                # python_getfilesystemencoding() -> sys.getfilesystemencoding()
                elif func_name == "python_getfilesystemencoding":
                    self.output.append("sys.getfilesystemencoding()")
                # python_getwindowsversion() -> sys.getwindowsversion()
                elif func_name == "python_getwindowsversion":
                    self.output.append("sys.getwindowsversion()")
                # python_getprofile() -> sys.getprofile()
                elif func_name == "python_getprofile":
                    self.output.append("sys.getprofile()")
                # python_setprofile(func) -> sys.setprofile(func)
                elif func_name == "python_setprofile":
                    self.output.append(f"sys.setprofile({args})")
                # python_gettrace() -> sys.gettrace()
                elif func_name == "python_gettrace":
                    self.output.append("sys.gettrace()")
                # python_settrace(func) -> sys.settrace(func)
                elif func_name == "python_settrace":
                    self.output.append(f"sys.settrace({args})")
                # python_getallocatedblocks() -> sys.getallocatedblocks()
                elif func_name == "python_getallocatedblocks":
                    self.output.append("sys.getallocatedblocks()")
                # python_gettotalrefcount() -> sys.gettotalrefcount()
                elif func_name == "python_gettotalrefcount":
                    self.output.append("sys.gettotalrefcount()")
                # python_getobjects() -> sys.getobjects()
                elif func_name == "python_getobjects":
                    self.output.append("sys.getobjects()")
                # clearcache() -> sys._clear_internal_caches()
                elif func_name == "clearcache":
                    self.output.append("sys._clear_internal_caches()")
                # flush() -> sys.stdout.flush()
                elif func_name == "flush":
                    self.output.append("sys.stdout.flush()")
                # stderr_flush() -> sys.stderr.flush()
                elif func_name == "stderr_flush":
                    self.output.append("sys.stderr.flush()")
                # stdin_read() -> sys.stdin.read()
                elif func_name == "stdin_read":
                    self.output.append("sys.stdin.read()")
                # stdin_readline() -> sys.stdin.readline()
                elif func_name == "stdin_readline":
                    self.output.append("sys.stdin.readline()")
                # stdin_readlines() -> sys.stdin.readlines()
                elif func_name == "stdin_readlines":
                    self.output.append("sys.stdin.readlines()")
                # stdout_write(data) -> sys.stdout.write(data)
                elif func_name == "stdout_write":
                    self.output.append(f"sys.stdout.write({args})")
                # stdout_writelines(data) -> sys.stdout.writelines(data)
                elif func_name == "stdout_writelines":
                    self.output.append(f"sys.stdout.writelines({args})")
                # stderr_write(data) -> sys.stderr.write(data)
                elif func_name == "stderr_write":
                    self.output.append(f"sys.stderr.write({args})")
                # stderr_writelines(data) -> sys.stderr.writelines(data)
                elif func_name == "stderr_writelines":
                    self.output.append(f"sys.stderr.writelines({args})")
                # getpass_prompt(prompt) -> getpass.getpass(prompt)
                elif func_name == "getpass_prompt":
                    self.output.append(f"getpass.getpass({args})")
                # getuser() -> getpass.getuser()
                elif func_name == "getuser":
                    self.output.append("getpass.getuser()")
                # getfilename() -> os.path.basename(__file__)
                elif func_name == "getfilename":
                    self.output.append("os.path.basename(__file__)")
                # getfiledir() -> os.path.dirname(os.path.abspath(__file__))
                elif func_name == "getfiledir":
                    self.output.append("os.path.dirname(os.path.abspath(__file__))")
                # getfilesplit() -> os.path.splitext(os.path.basename(__file__))
                elif func_name == "getfilesplit":
                    self.output.append("os.path.splitext(os.path.basename(__file__))")
                # getfileabspath() -> os.path.abspath(__file__)
                elif func_name == "getfileabspath":
                    self.output.append("os.path.abspath(__file__)")
                # getfileexists() -> os.path.exists(__file__)
                elif func_name == "getfileexists":
                    self.output.append("os.path.exists(__file__)")
                # getfileisfile() -> os.path.isfile(__file__)
                elif func_name == "getfileisfile":
                    self.output.append("os.path.isfile(__file__)")
                # getfileisdir() -> os.path.isdir(__file__)
                elif func_name == "getfileisdir":
                    self.output.append("os.path.isdir(__file__)")
                # getfilesize() -> os.path.getsize(__file__)
                elif func_name == "getfilesize":
                    self.output.append("os.path.getsize(__file__)")
                # getfilestat() -> os.stat(__file__)
                elif func_name == "getfilestat":
                    self.output.append("os.stat(__file__)")
                # getfilectime() -> os.path.getctime(__file__)
                elif func_name == "getfilectime":
                    self.output.append("os.path.getctime(__file__)")
                # getfilemtime() -> os.path.getmtime(__file__)
                elif func_name == "getfilemtime":
                    self.output.append("os.path.getmtime(__file__)")
                # getfileatime() -> os.path.getatime(__file__)
                elif func_name == "getfileatime":
                    self.output.append("os.path.getatime(__file__)")
                # getfilebasename() -> os.path.basename(__file__)
                elif func_name == "getfilebasename":
                    self.output.append("os.path.basename(__file__)")
                # getfiledirname() -> os.path.dirname(__file__)
                elif func_name == "getfiledirname":
                    self.output.append("os.path.dirname(__file__)")
                # clear() -> os.system('cls' if os.name == 'nt' else 'clear')
                elif func_name == "clear":
                    self.output.append("os.system('cls' if os.name == 'nt' else 'clear')")
                # pause() -> os.system('pause') or os.system('read ...')
                elif func_name == "pause":
                    self.output.append("os.system('pause' if os.name == 'nt' else 'read -n 1 -s -r -p \"Press any key to continue...\"')")
                # arguments(arg) -> argparse.ArgumentParser(...)
                elif func_name == "arguments":
                    self.output.append("# argparse.ArgumentParser(...)  # Manual translation needed")
                else:
                    self.output.append(f"# Unhandled Soup command: {line}")
            else:
                self.output.append(f"# Unsupported function: {line}")
            return
        self.output.append(f"# Unsupported: {line}")

    def compile(self, soup_code):
        self.output = []
        for line in soup_code.splitlines():
            self.compile_line(line)
        return "\n".join(self.output)

    def compile_file(self, input_path, output_path):
        with open(input_path, "r") as f:
            soup_code = f.read()
        py_code = self.compile(soup_code)
        with open(output_path, "w") as f:
            f.write(py_code)

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1].endswith(".soup") and sys.argv[2].endswith(".py"):
        compiler = SoupLangCompiler()
        compiler.compile_file(sys.argv[1], sys.argv[2])
        print(f"Compiled {sys.argv[1]} to {sys.argv[2]}")
    else:
        print("Usage: python SoupCompiler.py input.soup output.py")
