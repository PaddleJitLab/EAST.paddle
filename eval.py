import paddle
import time
import subprocess
import os
from model import EAST
from detect import detect_dataset
import numpy as np
import shutil


def eval_model(model_name, test_img_path, submit_path, save_flag=True):
    if os.path.exists(submit_path):
        shutil.rmtree(submit_path)
    os.mkdir(submit_path)
    device = str("cuda:0" if paddle.device.cuda.device_count() >= 1 else "cpu").replace(
        "cuda", "gpu"
    )
    model = EAST(False).to(device)
    model.set_state_dict(state_dict=paddle.load(path=model_name))
    model.eval()
    start_time = time.time()
    detect_dataset(model, device, test_img_path, submit_path)
    os.chdir(submit_path)
    res = subprocess.getoutput("zip -q submit.zip *.txt")
    res = subprocess.getoutput("mv submit.zip ../")
    os.chdir("../")
    res = subprocess.getoutput(
        "python ./evaluate/script.py –g=./evaluate/gt.zip –s=./submit.zip"
    )
    print(res)
    os.remove("./submit.zip")
    print("eval time is {}".format(time.time() - start_time))
    if not save_flag:
        shutil.rmtree(submit_path)


if __name__ == "__main__":
    model_name = "./pths/east_vgg16.pth"
    test_img_path = os.path.abspath("../ICDAR_2015/test_img")
    submit_path = "./submit"
    eval_model(model_name, test_img_path, submit_path)
