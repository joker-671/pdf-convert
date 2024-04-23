import os
import click

from apis.query import to_excel, to_word

def convert_to_absolute_path(path):
    if os.path.isabs(path):
        return path  # 如果是绝对路径，直接返回
    else:
        return os.path.abspath(path)  # 如果是相对路径，转换为绝对路径


@click.command()
@click.option('--path','-p',help="The pdf file path!",required=True)
@click.option('--type','-t',help="The target file type!",required=True,type=click.Choice(['word','excel']))
def main(path:str,type:str):
    if path and type:
        file_path = convert_to_absolute_path(path)
        if not '.pdf' in path:
            print('仅支持pdf文件转换')
            return
        if type == 'word':
           output = to_word(file_path)
           print(f'ounput path：{output}')
           return
        if type == 'excel':
            output = to_excel(file_path)
            print(f'ounput path：{output}')
            return 

if __name__ == "__main__":
    main()