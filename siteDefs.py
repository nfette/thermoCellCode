from __future__ import print_function
import platform

data_base_dir = "./data"

if platform.node() == "EN4055502":
    data_base_dir = "C:/Users/p2admin/Google Drive/2015-spring-data/"

if __name__ == "__main__":
    print(platform.node())
    print(data_base_dir)
