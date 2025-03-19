#!/usr/bin/env python3
"""
GDE GoZen Builder Script

This script handles the compilation of FFmpeg and the GDE GoZen plugin
for multiple platforms and architectures.

NOTE:
    Windows and Linux can be build on Linux or Windows with WSL.
    For MacOS you need to use MacOS itself else building fails.
"""


import os
import sys
import platform as os_platform
import subprocess
import glob
import shutil


THREADS = os.cpu_count() or 4
PATH_BUILD_WINDOWS = 'build_on_windows.py'


def _print_options(a_title, a_options):
    print(f'{a_title}:')

    i = 1

    for l_option in a_options:
        if i == 1:
            print(f'{i}. {l_option}; (default)')
        else:
            print(f'{i}. {l_option};')
        i += 1

    return input('> ')


def compile_ffmpeg(a_platform, a_arch):
    match _print_options('Do you want to (re)compile ffmpeg?', ['yes', 'no']):
        case '2':
            return

    if os.path.exists('./ffmpeg/ffbuild/config.mak'):
        print('Cleaning FFmpeg...')

        subprocess.run(['make', 'distclean'], cwd='./ffmpeg/')
        subprocess.run(['rm', '-rf', 'bin'], cwd='./ffmpeg/')

    if a_platform == 'linux':
        compile_ffmpeg_linux(a_arch)
    elif a_platform == 'windows':
        compile_ffmpeg_windows(a_arch)
    elif a_platform == 'macos':
        compile_ffmpeg_macos(a_arch)


def compile_ffmpeg_linux(a_arch):
    print('Configuring FFmpeg for Linux ...')

    l_path = f'bin/linux_{a_arch}'
    os.environ['PKG_CONFIG_PATH'] = '/usr/lib/pkgconfig'

    os.makedirs(l_path, exist_ok=True)
    os.environ["PKG_CONFIG_PATH"] = "/usr/lib/pkgconfig"

    subprocess.run([
        './configure',
        '--prefix=./bin',
        '--enable-shared',
        '--enable-gpl',
        '--enable-version3',
        f'--arch={a_arch}',
        '--target-os=linux',
        '--quiet',
        '--enable-pic',
        '--extra-cflags="-fPIC"',
        '--extra-ldflags="-fPIC"',
        '--disable-postproc',
        '--disable-avfilter',
        '--disable-sndio',
        '--disable-doc',
        '--disable-programs',
        '--disable-ffprobe',
        '--disable-htmlpages',
        '--disable-manpages',
        '--disable-podpages',
        '--disable-txtpages',
        '--disable-ffplay',
        '--disable-ffmpeg',
        '--enable-libx264',
        '--enable-libx265'
    ], cwd='./ffmpeg/')

    print('Compiling FFmpeg for Linux ...')

    subprocess.run(['make', f'-j{THREADS}'], cwd='./ffmpeg/')
    subprocess.run(['make', 'install'], cwd='./ffmpeg/')

    print('Copying lib files ...')

    for l_file in glob.glob('ffmpeg/bin/lib/*.so*'):
        shutil.copy2(l_file, l_path)
    for l_file in glob.glob('/usr/lib/libx26*.so'):
        shutil.copy2(l_file, l_path)

    print('Compiling FFmpeg for Linux finished!')


def compile_ffmpeg_windows(a_arch):
    print('Configuring FFmpeg for Windows ...')

    l_path = f'bin/windows_{a_arch}'
    os.environ['PKG_CONFIG_LIBDIR'] = f'/usr/{a_arch}-w64-mingw32/lib/pkgconfig'
    os.environ['PKG_CONFIG_PATH'] = f'/usr/{a_arch}-w64-mingw32/lib/pkgconfig'

    os.makedirs(l_path, exist_ok=True)

    subprocess.run([
        './configure',
        '--prefix=./bin',
        '--enable-shared',
        '--enable-gpl',
        '--enable-version3',
        f'--arch={a_arch}',
        '--target-os=mingw32',
        '--enable-cross-compile',
        f'--cross-prefix={a_arch}-w64-mingw32-',
        '--quiet',
        '--extra-libs=-lpthread',
        '--extra-ldflags="-static"',
        '--extra-ldflags="-fpic"',
        '--extra-cflags="-fPIC"',
        '--disable-postproc',
        '--disable-avfilter',
        '--disable-sndio',
        '--disable-doc',
        '--disable-programs',
        '--disable-ffprobe',
        '--disable-htmlpages',
        '--disable-manpages',
        '--disable-podpages',
        '--disable-txtpages',
        '--disable-ffplay',
        '--disable-ffmpeg',
        '--enable-libx264',
        '--enable-libx265'
    ], cwd='./ffmpeg/')

    print('Compiling FFmpeg for Windows ...')

    subprocess.run(['make', f'-j{THREADS}'], cwd='./ffmpeg/')
    subprocess.run(['make', 'install'], cwd='./ffmpeg/')

    print('Copying lib files ...')

    for l_file in glob.glob('ffmpeg/bin/bin/*.dll'):
        shutil.copy2(l_file, l_path)

    os.system(f'cp /usr/x86_64-w64-mingw32/bin/libwinpthread-1.dll {l_path}')
    os.system(f'cp /usr/x86_64-w64-mingw32/bin/libstdc++-6.dll {l_path}')

    print('Compiling FFmpeg for Windows finished!')


def compile_ffmpeg_macos(a_arch):
    print('Configuring FFmpeg for MacOS ...')

    l_path_debug = f'bin/macos_{a_arch}/debug/lib'
    l_path_release = f'bin/macos_{a_arch}/release/lib'

    os.makedirs(l_path_debug, exist_ok=True)
    os.makedirs(l_path_release, exist_ok=True)

    subprocess.run([
        './configure',
        '--prefix=./bin',
        '--enable-shared',
        '--enable-gpl',
        '--enable-version3',
        f'--arch={a_arch}',
        '--extra-ldflags="-mmacosx-version-min=10.13"',
        '--quiet',
        '--extra-cflags="-fPIC -mmacosx-version-min=10.13"',
        '--disable-postproc',
        '--disable-avfilter',
        '--disable-sndio',
        '--disable-doc',
        '--disable-programs',
        '--disable-ffprobe',
        '--disable-htmlpages',
        '--disable-manpages',
        '--disable-podpages',
        '--disable-txtpages',
        '--disable-ffplay',
        '--disable-ffmpeg',
        '--enable-libx264',
        '--enable-libx265'
    ], cwd='./ffmpeg/')

    print('Compiling FFmpeg for MacOS ...')

    subprocess.run(['make', f'-j{THREADS}'], cwd='./ffmpeg/')
    subprocess.run(['make', 'install'], cwd='./ffmpeg/')

    print('Copying lib files ...')

    for l_file in glob.glob('./ffmpeg/bin/lib/*.dylib'):
        shutil.copy2(l_file, l_path_debug)
        shutil.copy2(l_file, l_path_release)

    print('Compiling FFmpeg for MacOS finished!')


def macos_fix(a_arch):
    # This is a fix for the MacOS builds to get the libraries to properly connect to
    # the gdextension library. Without it, the FFmpeg libraries can't be found.
    print('Running fix for MacOS builds ...')

    l_debug_binary = f'./test_room/addons/gde_gozen/bin/macos_{a_arch}/debug/libgozen.macos.template_debug.dev.{a_arch}.dylib'
    l_release_binary = f'./test_room/addons/gde_gozen/bin/macos_{a_arch}/release/libgozen.macos.template_release.{a_arch}.dylib'
    l_debug_bin_folder = f'./test_room/addons/gde_gozen/bin/macos_{a_arch}/debug/lib'
    l_release_bin_folder = f'./test_room/addons/gde_gozen/bin/macos_{a_arch}/release/lib'

    print("Updating @loader_path for MacOS builds")

    if os.path.exists(l_debug_binary):
        for l_file in os.listdir(l_debug_bin_folder):
            os.system(f'install_name_tool -change ./bin/lib/{l_file} @loader_path/lib/{l_file} {l_debug_binary}')
        subprocess.run(['otool', '-L', l_debug_binary], cwd='./')

    if os.path.exists(l_release_binary):
        for l_file in os.listdir(l_release_bin_folder):
            os.system(f'install_name_tool -change ./bin/lib/{l_file} @loader_path/lib/{l_file} {l_release_binary}')
        subprocess.run(['otool', '-L', l_release_binary], cwd='./')


def main():
    print()
    print('v===================v')
    print('| GDE GoZen builder |')
    print('^===================^')
    print()

    if sys.version_info < (3, 10):
        print("Python 3.10+ is required to run this script!")
        sys.exit(2)

    if os_platform.system() == 'Windows':
        # Oh no, Windows detected. ^^"
        subprocess.run([sys.executable, PATH_BUILD_WINDOWS], cwd='./', check=True)
        sys.exit(3)

    l_platform = 'linux'

    match _print_options('Select platform', ['linux', 'windows', 'macos']):
        case '2':
            l_platform = 'windows'
        case '3':
            l_platform = 'macos'

    # arm64 isn't supported yet by mingw for Windows, so x86_64 only.
    l_arch = 'x86_64' if l_platform != 'macos' else 'arm64'

    match l_platform:
        case 'linux':
            if _print_options('Choose architecture', ['x86_64', 'arm64']) == '2':
                l_arch = 'arm64'
        case 'macos':
            if _print_options('Select target', ['arm64', 'x86_64']) == '2':
                l_arch = 'x86_64'

    # When selecting the target, we set dev_build to yes to get more debug info
    # which is helpful when debugging to get something useful of an error msg.
    l_target = 'debug'
    l_dev_build = ''

    match _print_options('Select target', ['debug', 'release']):
        case '2':
            l_target = 'release'
        case _:
            l_dev_build = 'dev_build=yes'

    compile_ffmpeg(l_platform, l_arch)
    subprocess.run([
        'scons',
        f'-j{THREADS}',
        f'target=template_{l_target}',
        f'platform={l_platform}',
        f'arch={l_arch}',
        l_dev_build
    ], cwd='./')

    if l_platform == 'macos':
        macos_fix(l_arch)

    print()
    print('v=========================v')
    print('| Done building GDE GoZen |')
    print('^=========================^')
    print()


if __name__ == '__main__':
    main()
