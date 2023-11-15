import aspose.words as aw
import os
import ChatFileConfig
from shutil import copyfile
from PyPDF2 import PdfReader, PdfWriter

config = ChatFileConfig.Config("./config.json")
config.get_init()


# 分割pdf
def pdf_splitter(input_path,output_path):
    pdf = PdfReader(input_path)
    for page in range(len(pdf.pages)):
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf.pages[page]) 
        output_filename = output_path+'{}.pdf'.format(page+1) 
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)         
            # print('Created: {}'.format(output_filename)) 


# md生成并合并
def md_merger(file_path,output_path):
    if os.path.exists(file_path):
        files = os.listdir(file_path)
        md = aw.Document(file_path+files[0])
        for f in range(1,len(files)):
            doc = aw.Document(file_path+files[f])
            md.append_document(doc, aw.ImportFormatMode.USE_DESTINATION_STYLES)
        md.save(output_path)
    else:
        print(f"{file_path}不存在")

# 将文件转为MD，并存储
def file_transform(file_path):
    if os.path.exists(config.data_path):
        file_name = os.path.basename(file_path)
        split_path = file_name.split(".")
        # 新文件夹存储路径
        new_folder = config.data_path+"/"+".".join(split_path[0:-1])
        # 转换后MD文件名称
        new_file = ".".join(split_path[0:-1])+".md"
        # 文件类型
        file_type = split_path[-1]
        
        # 创建存储路径
        if os.path.exists(new_folder) == False:
            os.mkdir(new_folder)
        elif os.path.exists(new_folder+"/"+new_file):
            # 读取文件内容
            with open(new_folder+"/"+new_file, "r", encoding="utf-8") as f:
                content = f.read()
            return content, new_folder+"/dialogue.json", split_path[-2]
        else:
            print("Folder already exists but no file.")
            return None

        # 将文件进行转换并存储
        if file_type == "pdf":
            # pdf分割
            new_ini = new_folder+"/init/"
            os.mkdir(new_ini)
            pdf_splitter(file_path,new_ini)
            # md 生成 合并 保存
            md_merger(new_ini, new_folder+"/"+new_file)
        elif file_type == "md":
            # md保存
            copyfile(file_path, new_folder+"/"+new_file)
        else:
            print("File type is not supported.")
            os.remove(new_folder)
        
        # 读取文件内容
        with open(new_folder+"/"+new_file, "r", encoding="utf-8") as f:
            content = f.read()
        return content, new_folder+"/dialogue.json", split_path[-2]
    else:
        print("No data path to save file cache.")
        return None