import shutil
import time
import click
import os
import subprocess

root = os.path.dirname(os.sep)
webRoot = os.path.join(os.getcwd(), "public\\web")

def onStart():
    print("run start...")
    subprocess.Popen(["uvicorn", "src.main:app", "--reload"], cwd=os.getcwd(),shell=True)

def onWebsite():
    print("run website...")
    subprocess.Popen("npm run dev", cwd=webRoot,shell=True)

# 打包前端代码
def onBuild():
    print('run build web project...')
    subprocess.run("npm run build",cwd=webRoot,shell=True)
    copy_files(os.path.join(webRoot,'dist'),os.path.join(os.getcwd(),'public\\assets'))

def copy_files(source_dir, dest_dir):
    # 检查目标目录是否存在，如果不存在则创建
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 获取源目录下的所有文件
    files = os.listdir(source_dir)

    for file in files:
        source_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)

        # 复制文件
        shutil.copy(source_file, dest_file)
        print(f"Copied {source_file} to {dest_file}")

def onInstall():
    print('install...')
    subprocess.Popen('pip install -r requirements.txt',cwd=root,shell=True, check=True)
    subprocess.Popen('pnpm i',cwd=webRoot,shell=True, check=True)

@click.command()
@click.option("--server", "-s", is_flag=True, help="Start the server project!")
@click.option("--website","-w",is_flag=True,help="Start the website project!")
@click.option("--build","-b",is_flag=True,help="Build the website project!")
@click.option('--install','-i',is_flag=True,help="Install dependencies!")
def run(**args):
    mapOption={
        "server":onStart,
        "website":onWebsite,
        "build":onBuild,
        "install":onInstall
    }
    flg = False
    for key in args:
        if args.get(key):
            method = mapOption.get(key)
            if method:
                method()
                flg=True
            else:
                print("this command is not exists")
    if not flg:
        onStart()

if __name__ == "__main__":
    run()
