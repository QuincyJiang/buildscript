import sys
import getopt
import json
import os
import getpass
import random
import time
import shutil
import datetime
import glob
print(" ========================================== ")
print(" ==                                      == ")
print(" ==       BuildScript  Version 1.0       == ")
print(" ==           Run -h for help            == ")
print(" ==                                      == ")
print(" ========================================== ")
HELP = "-h"
EMMC = "-e"
OUT = "-o"
TARGET = "-t"
CLEAN_PATH = "-c"
RUN_INSTANT = "-i"
REPLACE_EMMC = "-E"
REPLACE_OUT = "-O"
REPLACE_TARGET = "-T"
PATH_FILE_NAME = "path.json"
EMMC_FILE_PATH = ""
OUT_DIR_PATH = ""
TARGET_DIR_PATH = ""
TEMP_PATH = "/tmp/"+getpass.getuser()+"/"+str(random.randint(10000, 20000))
RAW_PROGRAM = "rawprogram0.xml"
DATA = dict(emmcPath="", outdir="", targetPath="")


def print_help():
    print("执行脚本文件可直接传参 也可随后在命令行中根据提示输入\n"
          "buildScript.py -[h] 显示帮助文本\n"
          "buildScript.py -[i] 直接执行打包脚本（默认使用上次输入过的路径）\n"
          "buildScript.py -[c] 清空上次输入路径以及产品名\n"
          "buildScript.py -[E] <new_emmc_path> 替换已有的emmc目录 \n"
          "buildScript.py -[O] <new_out_path> 替换已有的out目录 \n"
          "buildScript.py -[T] <new_target_path> 替换已有的target目录 \n"
          "命令行传入参数请参考如下格式："
          "buildScript.py (-e <emmcPath> -o <outDirPath> -t <target>\n"
          "比如：\n"
          "buildScript.py -e /data/jiangxq/msm8909_emmc_img  emmc文件夹路径 \n "
          "-o /data/jiangxq/repo/msm8909/v101/out/target/product/TOS_IP out目录 \n"
          "-t /data/jiangxq/release 打包结果存放目录\n")


def save_data(bean):
    # 保存上次输入的路径数据
    with open(PATH_FILE_NAME, 'w') as jsonFile:
     jsonFile.write(json.dumps(bean))


def clean_data():
    # 清空数据
    try:
        os.remove(PATH_FILE_NAME)
    except OSError:
        return


def read_file():
    # 读取本地数据
    bean = dict(emmcPath="", outdir="", targetPath="")
    try:
        with open(PATH_FILE_NAME)as pathFile:
            bean = json.load(pathFile)
            return bean
    except FileNotFoundError:
        return None


def remove_hypen_and_adjust_path(path):
    # 清除空格，同时格式化路径
    format = "".join(path.split(' '))
    if format[0] != "/":
        str_list = list(format)
        str_list.insert(0, '/')
        format = "".join(str_list)
    if format[len(format)-1] == "/":
        format = format[:-1]
    return format


def getprop(argv):
    # 读取命令行参数
    emmcPath = ""
    outdir = ""
    targetPath = ""
    try:
        opts, args = getopt.getopt(argv, "hicEOTe:o:t:", ["help", "runInstant", "clean", "replaceEmmc", "replaceOut", "replaceTarget", "emmcPath=", "outPath=", "target="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in (HELP, "--help"):
            print_help()
            sys.exit(2)
        elif opt in (RUN_INSTANT, "--runInstant"):
            return None
        elif opt in (CLEAN_PATH, "--clean"):
            clean_data()
            return None
        elif opt in (EMMC, "--emmcPath"):
            emmcPath = remove_hypen_and_adjust_path(arg[0])
        elif opt in (OUT, "--outPath"):
            outdir = remove_hypen_and_adjust_path(arg[0])
        elif opt in (TARGET_DIR_PATH, "--target"):
            targetPath = remove_hypen_and_adjust_path(arg[0])
        elif opt in(REPLACE_EMMC, "--replaceEmmc"):
            new_emmc = input("请输入新的emmc文件路径：\n")
            do_replace("emmcPath", new_emmc)
            return None
        elif opt in(REPLACE_OUT, "--replaceOut"):
            new_out = input("请输入新的out文件路径：\n")
            do_replace("outdir", new_out)
            return None
        elif opt in(REPLACE_TARGET, "--replaceTarget"):
            new_target = input("请输入新的打包结果存放路径：\n")
            do_replace("targetPath", new_target)
            return None
    return dict(emmcPath=emmcPath, outdir=outdir, targetPath=targetPath)


def check_file_is_exist(files):
    for i in files:
        if not os.path.exists(i):
            print("缺少必要文件："+i)
            if input("按q退出程序，按其他任意键继续\n") == "q":
                sys.exit(0)
            else:
                check_file_is_exist(files)


def retry_or_not(exit_code, tgz_file_name, TEMP_PATH):
    if exit_code != 0:
        if input("压缩文件出错，按q键终止程序，按其他任意键重试\n") != "q":
            retry_or_not(os.system("tar -czPf "+tgz_file_name+" -C "+TEMP_PATH), tgz_file_name, TEMP_PATH)
        else:
            sys.exit(0)
    else:
        print("===========压缩包打包完成============")
        pass


def check_out_dir(out_dir_path):
    path = out_dir_path
    if path == "":
        path = input("请输入out目录路径，以回车结束，q退出：\n")
        if path == "q":
            sys.exit(2)
        else:
            path = remove_hypen_and_adjust_path(path)
    else:
        path = remove_hypen_and_adjust_path(path)
    try:
        product_name = path.split("/target/product/")[1]
        return path
    except IndexError:
        out_path2 = input("输入的out路径非法，必须精确到最后一个目录级别 /out/target/product/TOP_IP\n"
                          "当前保存的out路径为： "+path + "\n"
                          "请重新输入out目录，退出按q\n")
        if out_path2 == "q":
            sys.exit(0)
        else:
            return check_out_dir(out_path2)


def do_replace(key, value):
    if key == "outdir":
        value = check_out_dir(value)
    file_data = read_file()
    if file_data is None:
        file_data = dict(emmcPath="", outdir="", targetPath="")
    file_data[key] = remove_hypen_and_adjust_path(value)
    print(key+"：" + file_data.get(key, ""))
    clean_data()
    save_data(file_data)


def do_copy(data):
    # 执行打包操作
    date = time.strftime("%Y%m%d")
    date1 = datetime.datetime.now()
    date2 = datetime.datetime(2017, 6, 1, 00, 00, 00, 000000)
    build_version = "1.0."+str(int(round((date1-date2).days/7)))
    product_name = str(data.get("outdir", "").split("/target/product/")[1])
    release_dir = data.get("targetPath", "")+"/"+product_name+"/DailyBuild/"+date
    tgz_file_name = release_dir+"/"+product_name+"_"+build_version+"_"+date+".tgz"
    ota_file_name = product_name+"_OTA_all_"+build_version+"_"+date+".zip"
    emmcPath = data.get("emmcPath", "")
    outdir  = data.get("outdir", "")
    appsboot = outdir+"/emmc_appsboot.mbn"
    boot = outdir+"/boot.img"
    recover = outdir+"/recovery.img"
    emmc_firehose = emmcPath + "/prog_emmc_firehose_8909_ddr.mbn"
    patch0 = emmcPath + "/patch0.xml"
    gpt_backup0 = emmcPath + "/gpt_backup0.bin"
    gpt_main0 = emmcPath + "/gpt_main0.bin"
    sbl1 = emmcPath + "/sbl1.mbn"

    if os.path.exists(release_dir):
        if input("发布路径已被创建，是否覆盖？Y/N\n") == "N":
            print("打包已终止")
            sys.exit(0)
    try:
        shutil.rmtree(release_dir)
    except FileNotFoundError:
        pass
    os.makedirs(TEMP_PATH)
    os.makedirs(release_dir)
    print("=========checking sparse==========")
    return_code = os.system("python3 checksparse.py -i %s -s %s -s %s -o %s -t %s" % (emmcPath+"/"+RAW_PROGRAM, outdir, emmcPath, TEMP_PATH+"/rawprogram_unsparse.xml", TEMP_PATH))
    # 返回码为空 中断执行
    if return_code != 0:
        sys.exit(0)
    try:
        os.remove(RAW_PROGRAM+".bak")
    except OSError:
        print("未找到文件\n")
        return
    # 非sparse镜像
    print("==========拷贝必要镜像文件===========")
    files_need_to_copy = [appsboot, boot, recover, emmc_firehose, patch0, gpt_backup0, gpt_main0, sbl1]
    check_file_is_exist(files_need_to_copy)
    shutil.copy(appsboot, TEMP_PATH)
    shutil.copy(boot, TEMP_PATH)
    shutil.copy(recover, TEMP_PATH)
    shutil.copy(emmc_firehose, TEMP_PATH)
    shutil.copy(patch0, TEMP_PATH)
    shutil.copy(gpt_backup0, TEMP_PATH)
    shutil.copy(gpt_main0, TEMP_PATH)
    shutil.copy(sbl1, TEMP_PATH)
    files = os.listdir(TEMP_PATH)
    # 删除rawprogram
    for file in files:
        if "rawprogram0" in file:
            try:
                os.remove(file)
            except OSError:
                pass
    print("============压缩镜像文件=============")
    # 压缩镜像目录
    tgz_code = os.system("tar -czPf "+tgz_file_name+" -C "+TEMP_PATH+" .")
    retry_or_not(tgz_code, tgz_file_name, TEMP_PATH)
    # shutil.make_archive(tgz_file_name, "tar", root_dir=TEMP_PATH)
    # 拷贝ota升级包
    print("===========拷贝ota升级包=============")
    for ota_file in glob.glob(os.path.join(outdir, product_name+'-ota-eng.*.zip')):
        shutil.copyfile(ota_file, release_dir + "/" + ota_file_name)
    print("=============拷贝完成================")
    print("===========镜像打包完成===============")
    # 删除temp目录
    try:
        os.remove(TEMP_PATH)
    except OSError:
        pass
    return
try:
    shutil.rmtree("tmp")
except FileNotFoundError:
    pass
DATA = getprop(sys.argv[1:])
if DATA is not None:
    # DATA 不为空 表示命令行输入的有参数 读取该参数并持久到本地
    if DATA.get("emmcPath", "") != "" or DATA.get("outdir", "") != "" or DATA.get("targetPath", "") != "":
        save_data(DATA)
    else:
        DATA = read_file()
else:
    # DATA为空 尝试读取本地是否有数据 有就使用本地数据
    DATA = read_file()

if DATA is None:
    DATA = dict(emmcPath="", outdir="", targetPath="")

if DATA.get("emmcPath", "") == "":
    emmc= input("请输入emmc镜像文件路径，以回车结束，q退出：\n")
    if emmc == "q":
        sys.exit(2)
    else:
        DATA["emmcPath"] = remove_hypen_and_adjust_path(emmc)
        print("emmcPath：" + DATA.get("emmcPath", ""))
        clean_data()
        save_data(DATA)

out_dir = check_out_dir(DATA.get("outdir", ""))
DATA["outdir"] = remove_hypen_and_adjust_path(out_dir)
print("outdir: "+DATA.get("outdir", ""))
clean_data()
save_data(DATA)
if DATA.get("targetPath", "") == "":
    target = input("请输入打包镜像要存放的目录，以回车结束，q退出：\n")
    if target == "q":
        sys.exit(2)
    else:
        DATA["targetPath"] = remove_hypen_and_adjust_path(target)
        clean_data()
        save_data(DATA)
        print("targetPath： "+DATA.get("targetPath", ""))
do_copy(DATA)



