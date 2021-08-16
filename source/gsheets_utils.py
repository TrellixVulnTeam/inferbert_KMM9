import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials
# from gspread_formatting import *
import sys
import time
import repository as repo
import os
import wandb


def sys_args_from_args(args, sys_argv):
    # Getting data row from command line and args
    data = {}
    for a in sys_argv:
        if a and a[0] == '-' and a[1] == '-':  # argument name (starts with '--')
            arg = a[2:]
            val = eval('args.%s' % arg)
            data['cmdline_' + arg] = str(val)
    return data

def now_str():
    return str(datetime.datetime.now())[:-7]


def get_exp_id(repo_dir, id_filename = 'experiments_ids.txt', force_id=None, increase_index=True):
    filename = os.path.join(repo_dir, id_filename)

    # In case of first experiment
    if not os.path.exists(repo_dir):
        os.mkdir(repo_dir)
        with open (filename, 'w') as exp_f:
            exp_f.write('0')

    with open(filename, "r+") as f:
        lines = f.read()
        prev_id = int(lines.strip())
        next_id = prev_id + (increase_index*1) if force_id is None else force_id
        f.seek(0)
        f.write(str(next_id))
        f.truncate()
    return next_id


class WandbExperiment():
    # This class wraps the wandb class, to enable my own version control and add status more easily. That's it.

    def __init__(self, project_name, args, start_runtime, server_name, repository_dir_and_files, wandb_off=False):
        # Input:
        #   start_runtime, server_name - to identify the specific experiment and row. srart_runtime is generated by now_str(). e.g. start_time="2020-01-27 19:05:53.2", server_name='nlp02'
        #   args: taken from args = argparse.ArgumentParser().parse_args(). Will use all off the arguments, unless sys_argv is inputed. In this case,
        #       only the args of sys_argv will be taken from args.
        #   sys_argv: sys.argv


        self.first_call=True
        self.last_update_time = 0
        self.repository_dir_and_files = repository_dir_and_files
        self.exp_id = get_exp_id(repository_dir_and_files[0])
        self.wandb_off = wandb_off

        self.data = {}
        self.data['ExpID'] = self.exp_id
        self.data['Server'] = server_name
        self.data['Date'], self.data['Time'] = start_runtime.split()
        self.data['File'] = sys.argv[0].split('/')[-1]
        self.data['Command'] = 'python ' + ' '.join(sys.argv)
        config = self.data
        config.update(args.__dict__)
        if wandb_off:
            return
        wandb.init(config=config, project=project_name, notes=args.notes)


    def update(self, data_in=None, status=None):
        if self.wandb_off:
            return
        data = {
        'Last Updated': now_str().split()[1],
        }
        if status:
            data.update({'Status':status})
        if data_in is not None:
            data.update(data_in)
        try:
            if self.first_call: # add a row if this is the first call for update(). only update it otherwise.
                ### version control and differences
                code_diffs, data['Changed files'] = repo.new_version_and_compare(self.repository_dir_and_files[1], self.repository_dir_and_files[0], exp_id=self.exp_id)
                if code_diffs != '':
                    data['Code diff'] = code_diffs.replace('\n', ' -- ')
                    data['Code changed'] = 'Yes'
            wandb.log(data)
            self.first_call = False
            return 1
        except Exception as e:
            print("Error with WanDB: %s"%(e))
            return -1


if __name__ == '__main__':
    # Instructions:
    # to add a spreedsheet to this API, simply share the sheet with the following email address: "testpythonapi@testpython-251907.iam.gserviceaccount.com",
    # and change the input argument 'MySheetName' according to the sheet name
    key_filename = 'testpython-4005dcd556f7.json'
    MySheetName = "pythonapi"
    MySheetName = "ExtK_experiments"
    start_time= now_str()
    server_name = 'test_server'
    repository_dir_and_files = ('my_repo', ['modeling_edited.py', 'train_classifier_from_scratch.py', 'train_ext_emb.py',])
    gse = GSpreadExperiment(MySheetName, key_filename, start_time, server_name, repository_dir_and_files)
    gse.update({'Comments':'Test'}, status='First Update')
    gse.update({'Comments':'Test2'}, status='2nd Update')
    gse.update({'Comments':'Test3'}, status='3rd Update')
    exit(0)

    gs.gs_update_row({'Date':"2020-01-27", 'Time':"00:11:22.3", 'Server':'nlp02', 'Comments': 'test11'})
    exit(0)

    gs = GSpread(MySheetName, key_filename)
    gs.gs_add_row({'Date':"2000-00-00", 'Time':"00:00:00", 'Server':'test','OOO':5})

    # gs_add_row(sheet, {'Date':"2019-09-03", 'Time':"21:35:36", 'File':'test','HHH':4})
    # print(list_of_hashes)

    # gs.diff_rows(7)
    # pop_col(sheet, 12)
    # switch_columns(sheet, (1,5))


