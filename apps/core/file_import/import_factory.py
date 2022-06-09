from inspect import getmembers, isclass

from core.file_import import base_import


class ExportFactory:

    def __init__(self):
        pass
    

class ImportFactory:

    def __init__(self):
        self.class_map = self._create_class_map()

    @staticmethod
    def _create_class_map():
        class_dict = {}
        for import_file in [base_import]:

            concrete_classes = getmembers(import_file, lambda m: isclass(m)
                                                                 # and not isabstract(m) 父类没有抽象方法, 这里无法进行判断
                                                                 and hasattr(m, 'COLUMN_MAP')
                                                                 and getattr(m, 'COLUMN_MAP')
                                                                 and issubclass(m, base_import.CsvImport))

            for class_name, concrete_class in concrete_classes:
                class_dict.setdefault(class_name, concrete_class)
        return class_dict

    def get_import(self, class_name, csv_file, **kwargs):
        import_class = self.class_map.get(class_name, None)
        if import_class is None:
            raise Exception(f'错误的导入类型：{class_name}')

        return import_class(csv_file, **kwargs)

# import os
# from pathlib import Path
#
# BASE_DIR = Path(__file__).resolve(strict=True).parent
# bill_factory = BillImportFactory()
# cc = bill_factory.get_import('TimeLine', os.path.join(BASE_DIR, '时间线.xlsx'))
# print(cc.df)
