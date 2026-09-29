import sys, os
print(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/")))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/")))
mock_path_folder = './mocks'
#os.chdir('../../src/')
os.getcwd()