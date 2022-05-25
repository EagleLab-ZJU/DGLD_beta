import pandas as pd
import os.path as osp
import os
from colautils import get_parse, train_epoch, test_epoch, train_model, multi_round_test, get_staticpseudolabel, get_staticpseudolabel_mask
class ExpRecord():
    def __init__(self, filepath='result.csv'):
        self.filepath = filepath

    def add_record(self, dict_record):
        self.load_record()
        print(dict_record)
        if not self.record:
            self.record = {k:[v] for k, v in dict_record.items()}
        else:
            for k in dict_record:
                if k not in self.record:
                    self.record[k] = [''] * (len(self.record[list(self.record.keys())[0]])-1)
                self.record[k].append(dict_record[k])
            # check out parameters
            for k in self.record:
                if k not in dict_record:
                    self.record[k].append('')
        self.save_record()


    def save_record(self):
        result = pd.DataFrame(self.record).to_csv(self.filepath, index=None)
        # print(result.head(10))

    def load_record(self):
        if osp.exists(self.filepath):
            csv_file = pd.read_csv(self.filepath)
            self.record = {k:list(csv_file[k]) for k in csv_file.columns}
        else:
            self.record = None
        

if __name__ == "__main__":
    args = get_parse()
    args.lr = 1
    exprecord = ExpRecord()
    argsdict = vars(args)
    argsdict['auc'] = 1.0
    argsdict['info'] = "test"
    exprecord.add_record(argsdict)
