import os
from bs4 import BeautifulSoup

# --- 配置项 ---
# 你的 Chat_bot 脚本所在的目录 (当前脚本也应在此目录)
CHATBOT_DIR = os.path.dirname(os.path.abspath(__file__))

# HTML 源文件所在的父目录
HTML_PARENT_DIR = os.path.join(CHATBOT_DIR, '..', 'CyberCJ-main') # '..' 表示上一级目录

# 需要扫描的HTML子文件夹名称
HTML_SOURCE_FOLDERS = [
    os.path.join(HTML_PARENT_DIR, 'CyberCJ'),
    os.path.join(HTML_PARENT_DIR, 'CyberCJ_Challenges')
]

# 输出的知识库文件名
KNOWLEDGE_FILE_NAME = 'knowledge.txt'
KNOWLEDGE_FILE_PATH = os.path.join(CHATBOT_DIR, KNOWLEDGE_FILE_NAME)

# --- HTML 解析与文本提取函数 ---
def extract_text_from_html_content(html_content, source_file_path=""):
    """
    从给定的HTML内容中提取纯文本。
    可以根据需要定制选择器来获取更精确的内容。
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 移除不需要的标签 (脚本, 样式, 导航, 页眉, 页脚等)
    for element_type in ["script", "style", "nav", "header", "footer", "aside", "form", "button"]:
        for element in soup.find_all(element_type):
            element.decompose()

    # 2. (可选) 如果内容主要在特定标签内 (例如 <main>, <article>, 或者某个特定id/class的div)
    #    你可以取消注释并调整下面的代码
    # main_content = soup.find('main') # 示例：查找 <main> 标签
    # if main_content:
    #     text = main_content.get_text(separator=' ', strip=True)
    # else:
    #     # 如果没有找到主要内容区域，就获取整个 body 的文本 (去除脚本等之后)
    #     body = soup.find('body')
    #     if body:
    #         text = body.get_text(separator=' ', strip=True)
    #     else:
    #         text = soup.get_text(separator=' ', strip=True) # 最后的备选方案

    # 简化版：直接获取整个 soup 对象处理后的文本 (通常 body 内容)
    text = soup.get_text(separator=' ', strip=True)

    # 3. (可选) 进一步的文本清洗，例如移除过短的文本片段
    # lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 20] # 保留长度大于20的行
    # cleaned_text = " ".join(lines)
    # return cleaned_text

    return text

# --- 主逻辑 ---
def main():
    print(f"Chatbot directory: {CHATBOT_DIR}")
    print(f"HTML parent directory: {HTML_PARENT_DIR}")
    print(f"Knowledge file will be saved to: {KNOWLEDGE_FILE_PATH}")

    all_extracted_texts = []
    file_count = 0

    for source_folder in HTML_SOURCE_FOLDERS:
        if not os.path.isdir(source_folder):
            print(f"Warning: Source folder not found: {source_folder}")
            continue

        print(f"\nScanning HTML files in: {source_folder}")
        for root, _, files in os.walk(source_folder):
            for file_name in files:
                if file_name.lower().endswith(('.html', '.htm')):
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, HTML_PARENT_DIR) # 获取相对路径，用于标识来源
                    print(f"  Processing: {relative_path}")
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f: # errors='ignore' 以防有编码问题
                            html_content = f.read()
                            extracted_text = extract_text_from_html_content(html_content, source_file_path=relative_path)

                            if extracted_text and len(extracted_text) > 50: # 只添加有实质内容且长度超过50的文本
                                # (可选) 在文本前添加来源信息
                                # source_info = f"[Source: {relative_path}]\n"
                                # all_extracted_texts.append(source_info + extracted_text)
                                all_extracted_texts.append(extracted_text)
                                file_count += 1
                            else:
                                print(f"    Skipped (empty or too short): {relative_path}")
                    except Exception as e:
                        print(f"    Error processing {relative_path}: {e}")

    if not all_extracted_texts:
        print("\nNo text was extracted. Knowledge file will not be created/updated.")
        return

    print(f"\nExtracted text from {file_count} HTML files.")

    try:
        with open(KNOWLEDGE_FILE_PATH, 'w', encoding='utf-8') as outfile:
            for i, text_content in enumerate(all_extracted_texts):
                outfile.write(text_content)
                # 在不同文件提取的内容之间添加两个换行符作为分隔
                if i < len(all_extracted_texts) - 1:
                    outfile.write("\n\n")
        print(f"\nKnowledge base '{KNOWLEDGE_FILE_NAME}' created/updated successfully at '{KNOWLEDGE_FILE_PATH}'.")
        print("Important: Remember to delete the old FAISS index folder for your chatbot to use the new knowledge.")
    except Exception as e:
        print(f"\nError writing knowledge file: {e}")

if __name__ == '__main__':
    main()